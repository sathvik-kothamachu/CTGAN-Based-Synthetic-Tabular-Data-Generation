# SynthGen - Startup and Debugging Guide

## IMPORTANT: The "Download Demo" Issue

### Why You're Seeing "Download Demo Synthetic Data"

The frontend has a **DEMO MODE** that activates when it **cannot connect to the backend**. This is why you're seeing:
- "Download demo synthetic data" instead of real data
- Only 3-4 features in statistics (hardcoded demo data)
- Same dataset every time

### The Real Problem

**Your backend (Python Flask server) is NOT running or NOT reachable!**

---

## How to Fix This - Step by Step

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
# Navigate to your project folder
cd /path/to/your/project

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the backend server
python backend.py
```

You should see:
```
==========================================================
  SynthGen v4.1 FIXED — CTGAN Synthetic Data Generator
  Running at http://localhost:5000
  ✓ All features preserved (numerical + categorical)
  ✓ Unique outputs each generation
  ✓ Complete statistics for all features
==========================================================

 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

**Keep this terminal window open!** The server must stay running.

---

### Step 2: Open the Frontend

**IMPORTANT:** Open the frontend in one of these ways:

**Option A: Direct URL (Recommended)**
```
http://localhost:5000
```
The backend serves the HTML directly.

**Option B: File Opening (NOT Recommended)**
If you open `index.html` as a file (file:///...), the browser will block API calls to localhost for security reasons (CORS). This causes demo mode!

---

### Step 3: Verify Connection

1. Open http://localhost:5000 in Chrome/Firefox
2. Open Developer Console (F12)
3. Go to the Console tab
4. You should see: "SynthGen initialized" or similar
5. You should NOT see: "Backend not running, using demo mode"

---

### Step 4: Test with Data Generation

1. Choose a mode (Upload or Sector)
2. Select a dataset
3. Configure settings
4. Click "Generate"
5. Watch the console for errors

**If it works:** You'll see real download button with actual data
**If demo mode:** Check the console for error messages

---

## Common Issues and Solutions

### Issue 1: "Backend not running, using demo mode"

**Cause:** Python server is not running or not reachable

**Solution:**
```bash
# Make sure backend.py is running
python backend.py

# Check if server is responding
curl http://localhost:5000/health
# Should return: {"status":"ok","version":"4.1","service":"SynthGen"}
```

---

### Issue 2: CORS Error in Browser Console

**Error Message:**
```
Access to fetch at 'http://localhost:5000/generate' from origin 'file://' has been blocked by CORS policy
```

**Cause:** Opening index.html as a file instead of through the server

**Solution:** 
- DON'T open `file:///path/to/index.html`
- DO open `http://localhost:5000`

---

### Issue 3: Port 5000 Already in Use

**Error Message:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process (replace PID with actual number)
kill -9 PID

# OR use a different port
PORT=5001 python backend.py
# Then open http://localhost:5001
```

---

### Issue 4: Missing Dependencies

**Error Message:**
```
ModuleNotFoundError: No module named 'ctgan'
```

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# If that fails, install individually:
pip install ctgan flask numpy pandas scipy scikit-learn openpyxl werkzeug
```

---

### Issue 5: Still Showing Demo Mode

**Debugging Steps:**

1. **Check if backend is running:**
   ```bash
   curl http://localhost:5000/health
   ```
   Should return JSON with status "ok"

2. **Check browser console (F12):**
   Look for red error messages about network failures

3. **Check backend terminal:**
   Look for incoming requests like:
   ```
   127.0.0.1 - - [date] "POST /generate HTTP/1.1" 200 -
   ```

4. **Try a different browser:**
   Chrome, Firefox, or Edge - sometimes browser extensions block requests

5. **Disable browser extensions:**
   Ad blockers or privacy extensions might block localhost

---

## Verifying the Fix Works

### Test 1: Backend is Running
```bash
# In terminal:
curl http://localhost:5000/health

# Expected output:
{"status":"ok","version":"4.1","service":"SynthGen"}
```

### Test 2: Frontend Connects
1. Open http://localhost:5000
2. Press F12 (Developer Console)
3. Go to Network tab
4. Generate synthetic data
5. You should see requests to `/generate` or `/generate-custom`
6. Status should be 200 (green)

### Test 3: All Features Present
1. Upload a CSV with 10 features
2. Generate synthetic data
3. Download the file
4. Open it - should have ALL 10 features
5. Check statistics - should show ALL 10 features

---

## Quick Checklist

Before generating data, verify:

- [ ] Terminal shows "Running at http://localhost:5000"
- [ ] Browser opened http://localhost:5000 (NOT file:///)
- [ ] No CORS errors in console (F12)
- [ ] /health endpoint works: `curl http://localhost:5000/health`
- [ ] Backend terminal shows incoming requests

If ALL checkboxes are ticked, you should get REAL data, not demo data!

---

## Still Having Issues?

### Collect Debug Information:

1. **Backend logs:**
   Copy everything from the terminal running `python backend.py`

2. **Browser console:**
   F12 → Console tab → Copy all red error messages

3. **Network tab:**
   F12 → Network tab → Screenshot any failed requests

4. **Test with curl:**
   ```bash
   curl -X POST http://localhost:5000/generate \
     -H "Content-Type: application/json" \
     -d '{"dataset_id":"pima_diabetes","samples":100,"epochs":50,"format":"csv","run_ml":false}'
   ```
   This tests if the backend API works at all

---

## Expected Behavior (When Working Correctly)

### Backend Terminal:
```
[2024-02-26 10:30:15] [INFO] [API] /generate  dataset=pima_diabetes  n=500  epochs=200
[2024-02-26 10:30:15] [INFO] [CTGAN] Loading: PIMA Indians Diabetes Dataset
[2024-02-26 10:30:15] [INFO] [CTGAN] Training on 768 rows, 9 features, epochs=200
[2024-02-26 10:30:15] [INFO] [CTGAN] Categorical columns: ['Outcome']
[2024-02-26 10:30:15] [INFO] [CTGAN] All columns: ['Pregnancies', 'Glucose', ...]
[2024-02-26 10:30:45] [INFO] [CTGAN] Sampling 500 synthetic rows
[2024-02-26 10:30:45] [INFO] [CTGAN] Synthetic data shape: (500, 9)
[2024-02-26 10:30:45] [INFO] [RESPONSE] ✓ All 9 features preserved in synthetic data
[2024-02-26 10:30:46] [INFO] [API] Done → file_id=abc-123  similarity=87.3%
```

### Browser Display:
- Download button says: "⬇ Download synthetic_data.csv" (NOT "demo")
- Statistics shows ALL features
- Each generation produces different data
- Quality scores update with each run

---

## Summary

**The demo mode is a FALLBACK when the backend isn't reachable.**

To get real data:
1. Run `python backend.py` and keep it running
2. Open `http://localhost:5000` in your browser
3. Generate data
4. Download real synthetic data with ALL features

The fixed code (v4.1) will then work perfectly, preserving all features and generating unique data each time!
