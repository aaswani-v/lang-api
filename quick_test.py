#!/usr/bin/env python3
"""Quick test for वाणीCheck API"""

import requests
import json
import sys
import time

API_URL = "http://localhost:8000"
API_KEY = "vanicheck-secret-key-2026"

print("=" * 50)
print("वाणीCheck API Quick Test")
print("=" * 50)

# Test 1: Health check
print("\n[1] Testing health endpoint...")
try:
    r = requests.get(f"{API_URL}/health", timeout=5)
    if r.status_code == 200:
        print("✓ Health check PASSED")
        print(f"  Response: {r.json()}")
    else:
        print(f"✗ Health check FAILED: {r.status_code}")
except Exception as e:
    print(f"✗ Health check ERROR: {e}")

# Test 2: V1 Health with API Key
print("\n[2] Testing v1/health endpoint...")
try:
    headers = {"X-API-KEY": API_KEY}
    r = requests.get(f"{API_URL}/v1/health", headers=headers, timeout=5)
    if r.status_code == 200:
        print("✓ V1 Health check PASSED")
        print(f"  Response: {r.json()}")
    else:
        print(f"✗ V1 Health check FAILED: {r.status_code}")
except Exception as e:
    print(f"✗ V1 Health check ERROR: {e}")

# Test 3: Get supported languages
print("\n[3] Testing languages endpoint...")
try:
    r = requests.get(f"{API_URL}/v1/languages", timeout=5)
    if r.status_code == 200:
        print("✓ Languages endpoint PASSED")
        print(f"  Response: {r.json()}")
    else:
        print(f"✗ Languages endpoint FAILED: {r.status_code}")
except Exception as e:
    print(f"✗ Languages endpoint ERROR: {e}")

print("\n" + "=" * 50)
print("Quick test complete!")
print("=" * 50)
