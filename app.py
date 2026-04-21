"""
=============================================================================
  SynthGen — Flask Backend API  (backend.py)  v4.1 FIXED
=============================================================================
  FIXES:
  - All features preserved in synthetic data
  - Better verification and logging
  - Improved statistics for all features
  
  Endpoints:
    GET  /              → Serve frontend (index.html)
    POST /generate      → Run CTGAN pipeline (built-in dataset), return stats + file_id
    POST /generate-custom → Run CTGAN pipeline on uploaded CSV/Excel file
    GET  /download/<id> → Stream generated file to browser
    GET  /datasets      → List all registered datasets
    GET  /health        → Health check

  Run:
    pip install -r requirements.txt
    python backend.py
    Open: http://localhost:5000
=============================================================================
"""

import io
import os
import uuid
import logging
import traceback

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

from model import DATASET_REGISTRY, train_and_generate, compute_all_statistics, run_ml_comparison

app = Flask(__name__, static_folder='.', template_folder='.')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

FILE_STORE: dict = {}
UPLOAD_FOLDER = '/tmp/synthgen_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _safe(v, d=3):
    try:
        f = float(v)
        return None if (f != f or abs(f) == float('inf')) else round(f, d)
    except Exception:
        return None


def _serialise(synthetic: pd.DataFrame, fmt: str) -> tuple:
    """Serialize synthetic dataframe to requested format."""
    if fmt == 'csv':
        return synthetic.to_csv(index=False).encode('utf-8'), 'text/csv', 'csv'
    elif fmt == 'json':
        return (synthetic.to_json(orient='records', indent=2).encode('utf-8'),
                'application/json', 'json')
    elif fmt == 'excel':
        buf = io.BytesIO()
        synthetic.to_excel(buf, index=False, engine='openpyxl')
        return (buf.getvalue(),
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx')
    return synthetic.to_csv(index=False).encode('utf-8'), 'text/csv', 'csv'


def _build_response(real_df, synthetic, cat_cols, meta, out_format, run_ml=False):
    """Build the JSON response with stats and file download link."""
    
    # Verify all columns are present
    log.info(f"[RESPONSE] Real data columns: {real_df.columns.tolist()}")
    log.info(f"[RESPONSE] Synthetic data columns: {synthetic.columns.tolist()}")
    log.info(f"[RESPONSE] Categorical columns: {cat_cols}")
    
    # Compute statistics for ALL features
    stats    = compute_all_statistics(real_df, synthetic, cat_cols)
    ml_stats = run_ml_comparison(real_df, synthetic, cat_cols) if run_ml else None

    # Serialize synthetic data
    file_bytes, mime, ext = _serialise(synthetic, out_format)
    file_id = str(uuid.uuid4())
    FILE_STORE[file_id] = (file_bytes, mime, ext)

    # Preview (first 5 rows)
    preview_rows = synthetic.head(5).values.tolist()
    preview_rows = [[_safe(v) if isinstance(v, float) else v for v in row]
                    for row in preview_rows]

    log.info(f"[RESPONSE] Generated {len(synthetic)} rows with {len(synthetic.columns)} features")
    log.info(f"[RESPONSE] Quality score: {stats['overall_similarity']}%")

    return {
        'rows_generated' : len(synthetic),
        'real_rows'      : len(real_df),
        'columns'        : len(synthetic.columns),
        'column_names'   : synthetic.columns.tolist(),  # Added for verification
        'categorical_columns': cat_cols,  # Added for verification
        'numerical_columns': [c for c in synthetic.columns if c not in cat_cols],  # Added
        'quality_score'  : stats['overall_similarity'],
        'file_id'        : file_id,
        'dataset_name'   : meta['name'],
        'source'         : meta['source'],
        'agency'         : meta['agency'],
        'citation'       : meta.get('citation', 'N/A'),
        'preview'        : {
            'columns': synthetic.columns.tolist(),
            'rows'   : preview_rows,
        },
        'stats'          : stats,
        'ml_comparison'  : ml_stats,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}


@app.route('/generate', methods=['POST'])
def generate():
    """Generate synthetic data from a built-in dataset."""
    try:
        body       = request.get_json(force=True)
        dataset_id = body.get('dataset_id', '')
        n_samples  = min(int(body.get('samples', 500)), 10000)
        n_epochs   = int(body.get('epochs', 200))
        out_format = body.get('format', 'csv').lower()
        run_ml     = bool(body.get('run_ml', True))

        if not dataset_id or dataset_id not in DATASET_REGISTRY:
            return jsonify({'error': f'Unknown dataset_id: {dataset_id}'}), 400

        log.info(f"[API] /generate  dataset={dataset_id}  n={n_samples}  epochs={n_epochs}")
        
        # Train and generate
        real_df, synthetic, cat_cols, meta = train_and_generate(dataset_id, n_samples, n_epochs)
        
        # Verify all features are present
        if len(synthetic.columns) != len(real_df.columns):
            log.warning(f"[API] Column mismatch! Real: {len(real_df.columns)}, Synthetic: {len(synthetic.columns)}")
            log.warning(f"[API] Missing columns: {set(real_df.columns) - set(synthetic.columns)}")
        else:
            log.info(f"[API] ✓ All {len(synthetic.columns)} features preserved in synthetic data")
        
        result = _build_response(real_df, synthetic, cat_cols, meta, out_format, run_ml)
        log.info(f"[API] Done → file_id={result['file_id']}  similarity={result['quality_score']}%")
        return jsonify(result)

    except Exception as exc:
        log.error(traceback.format_exc())
        return jsonify({'error': str(exc)}), 500


@app.route('/generate-custom', methods=['POST'])
def generate_custom():
    """Generate synthetic data from a user-uploaded CSV or Excel file."""
    try:
        # File must be in multipart/form-data
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded. Use multipart/form-data with key "file".'}), 400

        f           = request.files['file']
        n_samples   = min(int(request.form.get('samples', 500)), 10000)
        n_epochs    = int(request.form.get('epochs', 200))
        out_format  = request.form.get('format', 'csv').lower()
        run_ml      = request.form.get('run_ml', 'true').lower() == 'true'
        fname       = secure_filename(f.filename or 'upload.csv')

        log.info(f"[API] /generate-custom  file={fname}  n={n_samples}  epochs={n_epochs}")

        # Parse uploaded file
        raw = f.read()
        if not raw:
            return jsonify({'error': 'Uploaded file is empty.'}), 400

        try:
            if fname.endswith('.csv'):
                custom_df = pd.read_csv(io.BytesIO(raw))
            elif fname.endswith(('.xlsx', '.xls')):
                custom_df = pd.read_excel(io.BytesIO(raw))
            else:
                # Try CSV as fallback
                try:
                    custom_df = pd.read_csv(io.BytesIO(raw))
                except Exception:
                    return jsonify({'error': 'Unsupported file format. Use CSV or Excel (.xlsx/.xls).'}), 400
        except Exception as parse_err:
            return jsonify({'error': f'Failed to parse file: {str(parse_err)}'}), 400

        if len(custom_df) < 10:
            return jsonify({'error': f'Dataset too small ({len(custom_df)} rows). Need at least 10 rows.'}), 400

        if len(custom_df.columns) < 2:
            return jsonify({'error': 'Dataset must have at least 2 columns.'}), 400

        log.info(f"[API] Uploaded file: {len(custom_df)} rows, {len(custom_df.columns)} columns")
        log.info(f"[API] Columns: {custom_df.columns.tolist()}")
        log.info(f"[API] Dtypes: {custom_df.dtypes.to_dict()}")

        # Train and generate
        real_df, synthetic, cat_cols, meta = train_and_generate(
            dataset_id=None, n_samples=n_samples, n_epochs=n_epochs, custom_df=custom_df)

        # Verify all features are present
        missing = set(real_df.columns) - set(synthetic.columns)
        if missing:
            log.warning(f"[API] Column mismatch! Missing: {missing}")
        else:
            log.info(f"[API] ✓ All {len(synthetic.columns)} features preserved in synthetic data")

        meta['name']   = f"Custom: {fname}"
        meta['source'] = f"User Upload ({fname})"
        result = _build_response(real_df, synthetic, cat_cols, meta, out_format, run_ml)
        log.info(f"[API] Custom done → file_id={result['file_id']}  "
                 f"rows={result['rows_generated']}  cols={result['columns']}")
        return jsonify(result)

    except ValueError as ve:
        log.error(f"[API] Validation error: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as exc:
        log.error(traceback.format_exc())
        return jsonify({'error': f'Generation failed: {str(exc)}'}), 500


@app.route('/download/<file_id>')
def download(file_id: str):
    if file_id not in FILE_STORE:
        return jsonify({'error': 'File not found or expired. Generate again.'}), 404
    file_bytes, mime, ext = FILE_STORE[file_id]
    return send_file(
        io.BytesIO(file_bytes),
        mimetype=mime,
        as_attachment=True,
        download_name=f'synthetic_data.{ext}',
    )


@app.route('/datasets')
def list_datasets():
    return jsonify({
        k: {
            'name'      : v['name'],
            'sector'    : v['sector'],
            'rows'      : v['rows'],
            'source'    : v['source'],
            'agency'    : v['agency'],
            'source_url': v['source_url'],
            'citation'  : v['citation'],
        }
        for k, v in DATASET_REGISTRY.items()
    })


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'version': '4.1', 'service': 'SynthGen'})


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print()
    print("=" * 58)
    print("  SynthGen v4.1 FIXED — CTGAN Synthetic Data Generator")
    print(f"  Running at http://localhost:{port}")
    print("  ✓ All features preserved (numerical + categorical)")
    print("  ✓ Unique outputs each generation")
    print("  ✓ Complete statistics for all features")
    print("=" * 58)
    print()
    app.run(debug=True, port=port, host='0.0.0.0')
