#!/usr/bin/env python3
"""
Test script to verify SynthGen backend is working correctly
Run this AFTER starting backend.py in another terminal
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test if backend is running"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running!")
            print(f"   Version: {data.get('version')}")
            print(f"   Service: {data.get('service')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("   Make sure 'python backend.py' is running in another terminal")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_datasets():
    """Test if datasets are available"""
    print("\n" + "="*60)
    print("TEST 2: Dataset Listing")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/datasets", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} datasets available")
            print(f"   Sample datasets: {list(data.keys())[:3]}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_generation():
    """Test synthetic data generation"""
    print("\n" + "="*60)
    print("TEST 3: Synthetic Data Generation")
    print("="*60)
    print("Generating 50 samples from PIMA Diabetes dataset (this may take 30-60 seconds)...")
    
    try:
        payload = {
            "dataset_id": "pima_diabetes",
            "samples": 50,
            "epochs": 50,  # Lower epochs for faster testing
            "format": "csv",
            "run_ml": False  # Skip ML comparison for faster testing
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            timeout=120  # 2 minutes timeout
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generation successful! (took {elapsed:.1f} seconds)")
            print(f"   Rows generated: {data.get('rows_generated')}")
            print(f"   Columns: {data.get('columns')}")
            print(f"   Column names: {data.get('column_names', [])}")
            print(f"   Categorical columns: {data.get('categorical_columns', [])}")
            print(f"   Quality score: {data.get('quality_score')}%")
            print(f"   File ID: {data.get('file_id')}")
            
            # Check if all features are present
            expected_features = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                               'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome']
            actual_features = data.get('column_names', [])
            
            if len(actual_features) == len(expected_features):
                print(f"   ✅ All {len(expected_features)} features preserved!")
            else:
                print(f"   ⚠️  Expected {len(expected_features)} features, got {len(actual_features)}")
                print(f"   Missing: {set(expected_features) - set(actual_features)}")
            
            return True, data.get('file_id')
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (backend might be too slow)")
        return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


def test_download(file_id):
    """Test file download"""
    print("\n" + "="*60)
    print("TEST 4: File Download")
    print("="*60)
    
    if not file_id:
        print("⏭️  Skipping (no file_id from generation test)")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/download/{file_id}", timeout=10)
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            lines = content.strip().split('\n')
            print(f"✅ Download successful!")
            print(f"   File size: {len(response.content)} bytes")
            print(f"   Lines: {len(lines)}")
            print(f"   Headers: {lines[0]}")
            
            # Count features
            headers = lines[0].split(',')
            print(f"   ✅ Downloaded file has {len(headers)} features")
            
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("SynthGen Backend Test Suite")
    print("="*60)
    print("\nMake sure you have started the backend in another terminal:")
    print("   python backend.py")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print("\n" + "="*60)
        print("⛔ Backend is not running!")
        print("="*60)
        print("\nPlease start the backend first:")
        print("   python backend.py")
        print("\nThen run this test script again.")
        return
    
    # Test 2: Datasets
    results.append(("Dataset Listing", test_datasets()))
    
    # Test 3: Generation
    success, file_id = test_generation()
    results.append(("Data Generation", success))
    
    # Test 4: Download
    results.append(("File Download", test_download(file_id)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
        print("\nYou can now open http://localhost:5000 in your browser.")
        print("The frontend should connect to the backend and show REAL data (not demo).")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
        print("\nCommon issues:")
        print("  1. Backend not running: python backend.py")
        print("  2. Port conflict: try PORT=5001 python backend.py")
        print("  3. Missing dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
