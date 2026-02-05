# वाणीCheck - Quick Reference

## 🎯 NO External APIs Needed ✅

All processing is **100% local**:
- ❌ No Hugging Face API keys
- ❌ No AWS/GCP/Azure keys
- ❌ No third-party API calls
- ✅ Completely offline capable
- ✅ No rate limits
- ✅ Zero API costs

---

## 🚀 Quick Start (2 Steps)

### Step 1: Start Server
```powershell
# Open Command Prompt (cmd.exe)
cd C:\Programming\project\lang-api
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py
```

Server will run on: **http://localhost:8000**

### Step 2: Test It
```powershell
# Open PowerShell (in another window)
cd C:\Programming\project\lang-api
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe complete_test.py
```

---

## 🌐 Access Points

| What | URL | Auth |
|------|-----|------|
| Interactive Docs | http://localhost:8000/docs | ❌ |
| ReDoc | http://localhost:8000/redoc | ❌ |
| Health Check | http://localhost:8000/health | ❌ |
| Swagger UI | http://localhost:8000/swagger | ❌ |

---

## 🔐 Configuration

### Default API Key
```
vanicheck-secret-key-2026
```

### Change API Key (Optional)
Create `.env` file:
```
VANICHECK_API_KEY=your-custom-key-here
```

Or via PowerShell:
```powershell
$env:VANICHECK_API_KEY="your-key"
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py
```

---

## 📝 API Endpoints

### 1. Health Check (No Auth)
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "वाणीCheck Audio Deepfake Detection API",
  "version": "1.0.0-lite",
  "timestamp": "2026-02-06T..."
}
```

---

### 2. V1 Health (With Auth)
```bash
curl -H "X-API-KEY: vanicheck-secret-key-2026" \
  http://localhost:8000/v1/health
```

---

### 3. Get Languages
```bash
curl http://localhost:8000/v1/languages
```

**Response:**
```json
{
  "supported_languages": [
    "tamil",
    "english",
    "hindi",
    "malayalam",
    "telugu"
  ],
  "total_languages": 5
}
```

---

### 4. Detect Deepfake
```bash
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "SUQzBAAAI1RSU0U...",
    "language": "english"
  }'
```

**Response:**
```json
{
  "verdict": "HUMAN",
  "confidence": 0.87,
  "explanation": "Audio appears to be authentic human speech",
  "forensic_analysis": {
    "glottal_pulses": {
      "mean_f0": 156.3,
      "jitter_ratio": 0.045,
      "natural": true
    },
    "spectral_gaps": {
      "high_frequency_ratio": 0.42,
      "has_spectral_gaps": false
    },
    "breathing": {
      "breathing_ratio": 0.08,
      "has_pauses": true
    },
    "harmonics": {
      "harmonic_richness": 0.15,
      "energy_concentration": 8.5,
      "is_synthetic": false
    }
  },
  "processing_time_ms": 125.5,
  "model_version": "1.0.0-lite",
  "timestamp": "2026-02-06T..."
}
```

---

## 📊 Testing Scripts

### 1. Quick Test (Basic Health Checks)
```powershell
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe quick_test.py
```

**Tests:**
- Health endpoint
- V1 Health with API key
- Languages endpoint

---

### 2. Complete Test (Full Suite)
```powershell
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe complete_test.py
```

**Tests:**
- ✓ Health checks
- ✓ Supported languages
- ✓ Audio detection
- ✓ Multi-language support (all 5 languages)
- ✓ API key validation
- ✓ Forensic analysis details

---

### 3. Verify Installation
```powershell
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe check_installation.py
```

---

## 🐛 Troubleshooting

### Server won't start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process (if needed)
taskkill /PID <PID> /F
```

### "Connection refused"
- Make sure server is running in a separate window
- Start with: `C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py`

### Wrong API Key error
- Use: `vanicheck-secret-key-2026`
- Pass in header: `X-API-KEY: vanicheck-secret-key-2026`

### Module import errors
```powershell
# Verify all packages
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe check_installation.py

# Reinstall if needed
pip install -r requirements.txt
```

---

## 📦 Dependencies (All Local)

| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.128.2 | Web framework |
| Uvicorn | 0.40.0 | ASGI server |
| Pydantic | 2.12.5 | Data validation |
| PyTorch | 2.10.0 | Deep learning |
| TorchAudio | 2.10.0 | Audio processing |
| Librosa | 0.11.0 | Audio analysis |
| SciPy | 1.17.0 | Scientific computing |
| NumPy | 1.26.0 | Numerical computing |
| SoundFile | 0.13.1 | WAV file handling |
| Requests | 2.32.5 | HTTP client (testing) |
| PyTest | 9.0.2 | Testing (dev) |

**No external API dependencies!** ✅

---

## 🎓 Example Python Integration

```python
import requests
import base64
from scipy.io import wavfile
import numpy as np

# Your audio file
audio, sr = wavfile.read("speech.wav")
audio = audio.astype(np.float32) / 32767.0

# Encode to base64
with open("temp.wav", "wb") as f:
    wavfile.write(f.name, sr, (audio * 32767).astype(np.int16))
    with open(f.name, "rb") as wav:
        audio_b64 = base64.b64encode(wav.read()).decode()

# Call API
response = requests.post(
    "http://localhost:8000/v1/detect",
    headers={"X-API-KEY": "vanicheck-secret-key-2026"},
    json={
        "audio_data": audio_b64,
        "language": "english"
    }
)

# Get result
result = response.json()
print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']:.1%}")
```

---

## 🎉 You're All Set!

No APIs to configure. No keys to enter. **Just run and test!**

**Start now:**
```powershell
C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe main.py
```

Then visit: **http://localhost:8000/docs**
