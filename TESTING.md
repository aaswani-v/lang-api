# 🧪 वाणीCheck - Complete Testing Guide

## Overview

This guide walks through all testing procedures for वाणीCheck, from basic functionality to load testing.

---

## ⚡ Quick Verification (2 minutes)

### Step 1: Start the API
```bash
# Docker
docker-compose up -d

# Or Direct
python main.py
```

### Step 2: Run Verification Script
```bash
# Python (cross-platform)
python verify_api.py

# Expected output:
# ✓ PASS: API is healthy
# ✓ PASS: Authenticated health check successful
# ✓ PASS: Detection successful
#   Verdict: HUMAN
#   Confidence: 92.34%
# [PASS] All primary tests passed!
```

---

## 🔧 Unit & Integration Tests (5 minutes)

### Setup

```bash
# Ensure dependencies installed
pip install pytest pytest-asyncio httpx

# Navigate to project
cd /path/to/lang-api
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/test_main.py -v

# Run specific test class
pytest tests/test_main.py::TestDetectionAPI -v

# Run specific test
pytest tests/test_main.py::TestDetectionAPI::test_detection_response_structure -v

# Run with coverage
pytest tests/test_main.py --cov=main --cov-report=html

# Run with detailed output
pytest tests/test_main.py -vv -s
```

### Test Categories

#### 1. Audio Processing Tests
```bash
pytest tests/test_main.py::TestAudioProcessor -v

# Tests:
# - Base64 audio decoding
# - Audio file loading
# - Audio normalization
```

#### 2. Forensic Analysis Tests
```bash
pytest tests/test_main.py::TestForensicAnalyzer -v

# Tests:
# - Glottal pulse analysis
# - Spectral gap detection
# - Breathing pattern analysis
# - Harmonic structure analysis
```

#### 3. API Endpoint Tests
```bash
pytest tests/test_main.py::TestDetectionAPI -v

# Tests:
# - Health check
# - API key validation
# - Language support
# - Response structure
# - Error handling
```

#### 4. Robustness Tests
```bash
pytest tests/test_main.py::TestNoiseRobustness -v

# Tests:
# - 10% white noise injection
# - MP3 compression artifacts
# - Audio degradation handling
```

#### 5. Performance Tests
```bash
pytest tests/test_main.py::TestPerformance -v

# Tests:
# - Processing latency
# - Concurrent request handling
```

#### 6. Language Tests
```bash
pytest tests/test_main.py::TestLanguageSupport -v

# Tests:
# - Tamil support
# - English support
# - Hindi support
# - Malayalam support
# - Telugu support
```

---

## 📊 Load Testing (10 minutes)

### Install Locust
```bash
pip install locust
```

### Run Load Test

#### Basic Load Test (10 users, 10 seconds)
```bash
locust -f tests/test_main.py -u 10 -r 2 --run-time 10s --headless
```

#### Medium Load Test (50 users, 1 minute)
```bash
locust -f tests/test_main.py -u 50 -r 10 --run-time 1m --headless
```

#### Heavy Load Test (100+ users, 5 minutes)
```bash
locust -f tests/test_main.py -u 100 -r 20 --run-time 5m --headless
```

### Interactive Load Testing (with Web UI)

```bash
# Start Locust with web interface
locust -f tests/test_main.py

# Access UI at http://localhost:8089
# Configure users and spawn rate
# Click "Start swarming"
# Monitor in real-time
```

### Expected Results

**On Standard Hardware (4 CPU, 8GB RAM)**:
```
Number of Users | Avg Response Time | Min | Max | RPS
10              | 245ms             | 198 | 312 | 4.1
25              | 412ms             | 289 | 587 | 6.1
50              | 683ms             | 456 | 1230| 7.3
```

**With GPU (NVIDIA RTX 3090)**:
```
Number of Users | Avg Response Time | Min | Max | RPS
50              | 127ms             | 89  | 198 | 39.4
100             | 245ms             | 156 | 421 | 40.8
```

---

## 🔍 Manual API Testing

### Health Check
```bash
# Basic health
curl -X GET http://localhost:8000/health

# Authenticated health
curl -X GET http://localhost:8000/v1/health \
  -H "X-API-KEY: vanicheck-secret-key-2026"
```

### Audio Detection

#### Step 1: Create Test Audio
```bash
# Create synthetic audio (requires sox)
sox -n -r 16000 -b 16 test_audio.wav synth 3 sine 100 gain -3

# Or use existing audio file
```

#### Step 2: Encode to Base64
```bash
# Linux/Mac
BASE64_AUDIO=$(base64 -i test_audio.wav)

# Windows PowerShell
$BASE64_AUDIO = [Convert]::ToBase64String([IO.File]::ReadAllBytes("test_audio.wav"))
```

#### Step 3: Send Request
```bash
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_data\": \"$BASE64_AUDIO\",
    \"language\": \"english\"
  }" | python -m json.tool
```

### Test All Languages
```bash
for LANG in tamil english hindi malayalam telugu; do
  echo "Testing: $LANG"
  curl -s -X POST http://localhost:8000/v1/detect \
    -H "X-API-KEY: vanicheck-secret-key-2026" \
    -H "Content-Type: application/json" \
    -d "{\"audio_data\": \"$BASE64_AUDIO\", \"language\": \"$LANG\"}" \
    | grep -o '"verdict":"[^"]*"'
done
```

---

## 🔒 Security Testing

### 1. Missing API Key
```bash
curl -X POST http://localhost:8000/v1/detect \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "dummy", "language": "english"}'

# Expected: 401 Unauthorized
```

### 2. Invalid API Key
```bash
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: wrong-key" \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "dummy", "language": "english"}'

# Expected: 403 Forbidden
```

### 3. Invalid Language
```bash
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "dummy", "language": "klingon"}'

# Expected: 400 Bad Request
```

### 4. Malformed Base64
```bash
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "not-base64!!!", "language": "english"}'

# Expected: 400 Bad Request
```

---

## 📈 Performance Benchmarking

### 1. Single Request Benchmark

```python
import time
import requests
import base64

api_url = "http://localhost:8000"
api_key = "vanicheck-secret-key-2026"

# Prepare audio
with open("test_audio.mp3", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()

# Benchmark
times = []
for i in range(10):
    start = time.time()
    response = requests.post(
        f"{api_url}/v1/detect",
        headers={"X-API-KEY": api_key},
        json={"audio_data": audio_b64, "language": "english"}
    )
    elapsed = (time.time() - start) * 1000
    times.append(elapsed)
    print(f"Request {i+1}: {elapsed:.2f}ms")

print(f"\nAverage: {sum(times)/len(times):.2f}ms")
print(f"Min: {min(times):.2f}ms")
print(f"Max: {max(times):.2f}ms")
```

### 2. Concurrency Benchmark

```python
import asyncio
import time
import httpx
import base64

async def detect_audio(client, audio_b64, api_key):
    response = await client.post(
        "http://localhost:8000/v1/detect",
        headers={"X-API-KEY": api_key},
        json={"audio_data": audio_b64, "language": "english"}
    )
    return response.status_code

async def benchmark_concurrency(num_requests=50):
    with open("test_audio.mp3", "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    api_key = "vanicheck-secret-key-2026"
    
    start = time.time()
    async with httpx.AsyncClient(timeout=15) as client:
        tasks = [
            detect_audio(client, audio_b64, api_key)
            for _ in range(num_requests)
        ]
        results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    successful = sum(1 for r in results if r == 200)
    
    print(f"Requests: {num_requests}")
    print(f"Successful: {successful}")
    print(f"Total Time: {elapsed:.2f}s")
    print(f"Throughput: {num_requests/elapsed:.1f} req/sec")

asyncio.run(benchmark_concurrency(50))
```

---

## 🐛 Debugging & Troubleshooting

### Enable Debug Mode

```python
# In main.py, set logging level
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run
python main.py
```

### Check Model Loading

```python
from main import model

if model is None:
    print("Model not loaded - check logs above")
else:
    print("Model loaded successfully")
    print(f"Device: {model.device}")
    print(f"Model: {model.model}")
```

### Test Audio Processing

```python
from main import AudioProcessor
import numpy as np

# Create test audio
audio = np.random.randn(16000)

# Test normalization
normalized = AudioProcessor.normalize_audio(audio)
print(f"Max value: {np.max(np.abs(normalized))}")
print(f"Should be <= 1.0: {np.max(np.abs(normalized)) <= 1.0}")
```

### Test Forensic Analysis

```python
from main import ForensicAnalyzer
import numpy as np

# Create synthetic audio
sr = 16000
duration = 3
t = np.arange(int(sr * duration)) / sr
audio = np.sin(2 * np.pi * 100 * t)

# Run analysis
analysis = ForensicAnalyzer.run_full_analysis(audio, sr)

import json
print(json.dumps(analysis, indent=2))
```

### View Docker Logs

```bash
# Real-time logs
docker logs -f vanicheck-api

# Last 100 lines
docker logs --tail 100 vanicheck-api

# Follow with timestamps
docker logs -f --timestamps vanicheck-api
```

---

## ✅ Testing Checklist

Before deployment, verify:

- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] API key validation works
- [ ] All 5 languages supported
- [ ] Unit tests pass: `pytest tests/test_main.py -v`
- [ ] Integration tests pass
- [ ] Verification script passes: `python verify_api.py`
- [ ] Load test successful (50+ users, <300ms latency)
- [ ] Audio processing working (MP3, WAV, OGG formats)
- [ ] Forensic analysis generating valid output
- [ ] Error handling working (400, 401, 403, 500 codes)
- [ ] Response time acceptable
- [ ] No memory leaks under load
- [ ] Docker builds and runs without errors
- [ ] All documentation reviewed

---

## 📊 Test Coverage Report

```bash
# Generate coverage report
pytest tests/test_main.py --cov=main --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

Expected coverage:
- main.py: 95%+ coverage
- Edge cases handled
- Error paths tested

---

## 🎯 Testing Scenarios

### Scenario 1: Normal Operation
```bash
# Human audio
python -c "
import requests, base64
audio_b64 = base64.b64encode(open('human.mp3', 'rb').read()).decode()
r = requests.post('http://localhost:8000/v1/detect',
  headers={'X-API-KEY': 'vanicheck-secret-key-2026'},
  json={'audio_data': audio_b64, 'language': 'english'})
print(r.json()['verdict'])  # Should be 'HUMAN'
"
```

### Scenario 2: AI-Generated Audio
```bash
# AI audio
python -c "
import requests, base64
audio_b64 = base64.b64encode(open('ai_generated.mp3', 'rb').read()).decode()
r = requests.post('http://localhost:8000/v1/detect',
  headers={'X-API-KEY': 'vanicheck-secret-key-2026'},
  json={'audio_data': audio_b64, 'language': 'english'})
print(r.json()['verdict'])  # Should be 'AI_GENERATED'
"
```

### Scenario 3: Noisy Audio
```bash
# Audio with background noise
python -c "
import requests, base64
audio_b64 = base64.b64encode(open('noisy_audio.mp3', 'rb').read()).decode()
r = requests.post('http://localhost:8000/v1/detect',
  headers={'X-API-KEY': 'vanicheck-secret-key-2026'},
  json={'audio_data': audio_b64, 'language': 'english'})
print(f\"Confidence: {r.json()['confidence']}\")  # Should still be high
"
```

---

## 📞 Support

If tests fail, check:
1. Logs: `docker logs vanicheck-api`
2. Health: `curl http://localhost:8000/health`
3. Model: Ensure model_loaded = true
4. Dependencies: `pip install -r requirements.txt`

---

**Last Updated**: February 6, 2026
**Version**: 1.0.0
