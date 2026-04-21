# SynthGen 





## 📦 Package Contents

This package contains:

1. **model.py** - Fixed CTGAN engine (preserves ALL features)
2. **backend.py** - Fixed Flask API (with verification)
3. **requirements.txt** - Python dependencies
4. **index.html** - Frontend interface
5. **open_in_chrome.html** - Browser helper
6. **FIXES_README.md** - Technical details of all fixes
7. **STARTUP_GUIDE.md** - Detailed troubleshooting guide
8. **test_backend.py** - Backend testing script
9. **start.sh** - Quick-start script (Linux/Mac)
10. **README.md** - This file

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start Backend Server

**Option A: Use the quick-start script (Linux/Mac)**
```bash
chmod +x start.sh
./start.sh
```

**Option B: Manual start (Windows/Linux/Mac)**
```bash
python backend.py
```

You should see:
```
==========================================================
  SynthGen v4.1 FIXED — CTGAN Synthetic Data Generator
  Running at http://localhost:5000
==========================================================
```

**⚠️ KEEP THIS TERMINAL OPEN!** The server must stay running.

### Step 3: Open in Browser

Open your browser and go to:
```
http://localhost:5000
```

**DO NOT** open `index.html` as a file (file:///) - this will cause CORS errors!

---

## ✅ How to Verify It's Working

### Test 1: Check if Backend is Running

In a new terminal:
```bash
curl http://localhost:5000/health
```

Expected output:
```json
{"status":"ok","version":"4.1","service":"SynthGen"}
```

### Test 2: Run the Test Script

```bash
python test_backend.py
```

This will test:
- ✅ Backend connectivity
- ✅ Dataset availability
- ✅ Data generation
- ✅ File download
- ✅ Feature preservation

### Test 3: Generate Real Data

1. Open http://localhost:5000
2. Choose "Upload File" or "Choose by Sector"
3. Configure and generate
4. Download button should say: "⬇ Download synthetic_data.csv" (NOT "demo")
5. Statistics should show ALL your features

---



## 🐛 Troubleshooting


**Diagnosis:**
```bash
# Check if backend is running
curl http://localhost:5000/health

# If this fails, backend is not running!
```

**Solution:**
1. Make sure `python backend.py` is running in a terminal
2. Don't close that terminal
3. Refresh your browser at http://localhost:5000








## 📊 Expected Behavior


**Browser Display:**
- ✅ "⬇ Download synthetic_data.csv" (not "demo")
- ✅ Statistics for ALL features
- ✅ Different data each generation
- ✅ Quality scores updating

**Downloaded File:**
- ✅ All numerical columns present
- ✅ All categorical columns present
- ✅ Unique values each time

---

## 💡 Usage Tips

### For Best Results:

1. **Use adequate epochs:**
   - Small datasets (<1000 rows): 200-300 epochs
   - Medium datasets (1000-10000 rows): 150-200 epochs
   - Large datasets (>10000 rows): 100-150 epochs

2. **Sample size:**
   - Can be different from original (more or less)
   - Recommended: 50-5000 samples for testing
   - Maximum: 10000 samples

3. **File formats:**
   - CSV: Best for data analysis
   - JSON: Best for APIs
   - Excel: Best for business users

4. **ML Comparison:**
   - Enable for classification tasks
   - Disable for faster generation
   - Shows how well synthetic data preserves patterns

---

## 📁 File Descriptions

### Core Files:
- **backend.py** - Flask API server (must be running)
- **model.py** - CTGAN training and statistics engine
- **index.html** - Web interface (served by backend)

### Configuration:
- **requirements.txt** - Python dependencies

### Documentation:
- **README.md** - This file (quick start)
- **FIXES_README.md** - Technical details of fixes
- **STARTUP_GUIDE.md** - Detailed troubleshooting

### Utilities:
- **test_backend.py** - Automated testing script
- **start.sh** - Quick-start helper (Linux/Mac)
- **open_in_chrome.html** - Browser launch helper

---

## 🎯 Common Use Cases

### Case 1: Augmenting Small Datasets
```
1. Upload your CSV (e.g., 100 rows)
2. Generate 1000 samples
3. Download and combine with original
4. Train ML models on augmented data
```

### Case 2: Privacy-Preserving Data Sharing
```
1. Upload sensitive data
2. Generate synthetic version
3. Share synthetic data (no real records)
4. Maintains statistical properties
```

### Case 3: Testing and Development
```
1. Generate test data from production schema
2. Use for development/QA
3. No privacy concerns
4. Realistic distributions
```

---

## 📞 Support

### If you're stuck:

1. **Read STARTUP_GUIDE.md** - Detailed troubleshooting
2. **Run test_backend.py** - Automated diagnostics
3. **Check browser console** - F12 for errors
4. **Check backend logs** - Look at terminal output

### Debug Checklist:

- [ ] Backend running: `python backend.py`
- [ ] Health check works: `curl http://localhost:5000/health`
- [ ] Browser opened: http://localhost:5000 (not file:///)
- [ ] No CORS errors in console
- [ ] Dependencies installed: `pip install -r requirements.txt`

---

## 🎉 Success Criteria

You'll know everything is working when:

1. ✅ Backend terminal shows incoming requests
2. ✅ Browser shows "Download synthetic_data.csv" (not "demo")
3. ✅ Statistics display ALL features from your dataset
4. ✅ Each generation produces different data
5. ✅ Downloaded files contain ALL original features

---

## 📊 Example Workflow

```bash
# Terminal 1: Start backend
python backend.py

# Terminal 2: Test it (optional)
python test_backend.py

# Browser: Go to
http://localhost:5000

# Generate data:
1. Choose "Upload File"
2. Select your CSV (or use built-in dataset)
3. Configure: 500 samples, 200 epochs
4. Click "Generate"
5. Wait 30-60 seconds
6. Download your synthetic data!
```

---

## Version History

**v4.0** (Original)
- 20 built-in datasets
- Basic CTGAN generation
- Statistics for subset of features

**v4.1** (This Version - Fixed)
- ✅ Unique outputs every time
- ✅ ALL features preserved
- ✅ Statistics for ALL features
- ✅ Better verification and logging
- ✅ Comprehensive testing tools

---

## License & Credits

- CTGAN: https://github.com/sdv-dev/CTGAN
- Datasets: UCI ML Repository, Kaggle
- Framework: Flask, Chart.js

---

**Now start your backend and enjoy generating synthetic data! 🚀**
