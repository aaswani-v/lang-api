# वाणीCheck API - Testing & API Keys Guide

## 📋 External APIs Required

**Good news!** ✅ **NO external APIs or API keys are required** to run this system!

The current implementation uses only:
- **Local audio processing**: librosa, scipy, soundfile, numpy
- **Local deep learning**: PyTorch (no model downloads required)
- **Local spectral analysis**: Custom algorithms (no external calls)
- **Local HTTP server**: FastAPI + Uvicorn

### Summary of Dependencies

| Component | Type | Location | API Key Needed |
|-----------|------|----------|---|
| Audio Processing | Local Library | librosa, scipy | ❌ No |
| Deep Learning Framework | Local Library | PyTorch, TorchAudio | ❌ No |
| Web Server | Local Library | FastAPI, Uvicorn | ❌ No |
| Model Inference | Local Algorithm | Spectral Analysis | ❌ No |
| Forensics Analysis | Local Algorithm | Custom algorithms | ❌ No |

---

## 🧪 How to Test the API

### **Method 1: Using Interactive Docs (Easiest)**

1. **Start the server** (in a separate Command Prompt):
```powershell
cd C:\Programming\project\lang-api
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py
```

2. **Open browser** and go to:
```
sk
http://localhost:8000/docs
```

3. **Test endpoints directly:**
   - Click on `/health` → Click "Try it out" → Click "Execute"
   - Click on `/v1/health` → Click "Try it out" → Enter API Key → Click "Execute"
   - Click on `/v1/detect` → Click "Try it out" → Enter sample audio data → Click "Execute"

---

### **Method 2: Using Python Script**

```python
import requests
import base64
import numpy as np
from scipy.io import wavfile

# Start with: C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py

API_URL = "http://localhost:8000"
API_KEY = "vanicheck-secret-key-2026"

# Create a sample audio (sine wave)
sample_rate = 16000
duration = 3
frequency = 440  # Hz

t = np.linspace(0, duration, sample_rate * duration)
audio = np.sin(2 * np.pi * frequency * t) * 0.3
audio = audio.astype(np.float32)

# Convert to WAV
import tempfile
import os
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    wavfile.write(f.name, sample_rate, (audio * 32767).astype(np.int16))
    
    with open(f.name, 'rb') as wav:
        audio_b64 = base64.b64encode(wav.read()).decode()
    os.remove(f.name)

# Test detection
headers = {"X-API-KEY": API_KEY}
payload = {
    "audio_data": audio_b64,
    "language": "english"
}

response = requests.post(
    f"{API_URL}/v1/detect",
    json=payload,
    headers=headers,
    timeout=10
)

print("Status Code:", response.status_code)
print("Response:", response.json())
```

---

### **Method 3: Using Quick Test Script** (Recommended)

Already created in the project:

```powershell
# Terminal 1: Start server
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py

# Terminal 2: Run quick test
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe quick_test.py
```

**Output:**
```
==================================================
वाणीCheck API Quick Test
==================================================

[1] Testing health endpoint...
✓ Health check PASSED

[2] Testing v1/health endpoint...
✓ V1 Health check PASSED

[3] Testing languages endpoint...
✓ Languages endpoint PASSED
```

---

### **Method 4: Using cURL**

```bash
# Health check (no API key needed)
curl http://localhost:8000/health

# V1 Health (API key required)
curl -H "X-API-KEY: vanicheck-secret-key-2026" http://localhost:8000/v1/health

# Get supported languages
curl http://localhost:8000/v1/languages

# Test detection (with audio)
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "SUQzBAAAI1RTU0UAAAAPAAADTGF2ZjU4LjI5LjEwMAAAAAAAAAAAAAAA...",
    "language": "english"
  }'
```

---

### **Method 5: Using Postman**

1. **Install Postman** from https://www.postman.com/downloads/
2. **Create New Request:**
   - Method: `POST`
   - URL: `http://localhost:8000/v1/detect`
   - Headers:
     - Key: `X-API-KEY`
     - Value: `vanicheck-secret-key-2026`
   - Body (raw JSON):
   ```json
   {
     "audio_data": "SUQzBAAAI1RTU0VVAAAA...",
     "language": "english"
   }
   ```

---

## 🔐 Configuration

### Environment Variables (Optional)

Create a `.env` file in the project root:

```
VANICHECK_API_KEY=your-custom-api-key-here
```

Or set via command line:

```powershell
# Windows PowerShell
$env:VANICHECK_API_KEY="your-custom-key"
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py
```

**Default API Key:** `vanicheck-secret-key-2026`

---

## 📊 API Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health` | GET | ❌ | Health check (no key) |
| `/v1/health` | GET | ✅ | Health check (with key) |
| `/v1/languages` | GET | ❌ | Get supported languages |
| `/v1/detect` | POST | ✅ | Detect deepfake |
| `/docs` | GET | ❌ | Interactive API docs |
| `/redoc` | GET | ❌ | ReDoc documentation |

---

## 🎯 Full Test Workflow

```powershell
# Step 1: Start server in Command Prompt
cmd /k "C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py"

# Step 2: In PowerShell, run quick test
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe quick_test.py

# Step 3: Open browser for interactive testing
# http://localhost:8000/docs

# Step 4: Run full verification
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe verify_api.py
```

---

## 🚀 Production Deployment

### No External API Dependencies ✅

This means:
- ✅ No Hugging Face token needed
- ✅ No AWS/GCP/Azure credentials needed  
- ✅ No third-party API calls
- ✅ Works completely offline after deployment
- ✅ No rate limiting issues
- ✅ No API costs

### Can be deployed to:
- Docker container
- Kubernetes
- AWS ECS
- Google Cloud Run
- Railway
- Heroku
- Any server with Python 3.13

---

## 📝 Example Response

```json
{
  "verdict": "HUMAN",
  "confidence": 0.87,
  "explanation": "Audio appears to be authentic human speech",
  "forensic_analysis": {
    "glottal_pulses": {
      "mean_f0": 156.3,
      "jitter_ratio": 0.045,
      "natural": true,
      "description": "Natural F0 variation detected"
    },
    "spectral_gaps": {
      "high_frequency_ratio": 0.42,
      "has_spectral_gaps": false,
      "description": "Full spectrum present"
    },
    "breathing": {
      "breathing_ratio": 0.08,
      "has_pauses": true,
      "description": "Detected natural breathing patterns"
    },
    "harmonics": {
      "harmonic_richness": 0.15,
      "energy_concentration": 8.5,
      "is_synthetic": false,
      "description": "Natural harmonic distribution"
    },
    "detection_scores": {
      "ai_probability": 0.13,
      "human_probability": 0.87
    }
  },
  "processing_time_ms": 125.5,
  "model_version": "1.0.0-lite",
  "timestamp": "2026-02-06T20:16:02.322816"
}
```

---

## ✅ All Tests Passing

```
✓ Health check endpoint working
✓ V1 health endpoint with API key working  
✓ Languages endpoint showing all 5 supported languages
✓ Detection endpoint working
✓ Multi-language support (Tamil, English, Hindi, Malayalam, Telugu)
✓ API running on http://localhost:8000
```

---

## 🎉 You're All Set!

**No external APIs needed. Everything runs locally!**

Start testing now:
1. Open Command Prompt
2. Run: `C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py`
3. Open: http://localhost:8000/docs
4. Start testing!
