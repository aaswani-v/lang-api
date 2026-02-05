# वाणीCheck API Specification v1.0

**Base URL**: `http://localhost:8000` (or your deployed instance)

**Authentication**: `X-API-KEY` header (required for `/v1/*` endpoints)

---

## Endpoints

### 1. Health Check (Public)

**Endpoint**: `GET /health`

**Authentication**: Not required

**Description**: Basic health status check - accessible without API key

**Response**: 
```json
{
  "status": "healthy",
  "service": "वाणीCheck Audio Deepfake Detection API",
  "timestamp": "2026-02-06T10:30:45.123456"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `500 Internal Server Error`: Service is down

**Example**:
```bash
curl -X GET http://localhost:8000/health
```

---

### 2. Detailed Health Check (Authenticated)

**Endpoint**: `GET /v1/health`

**Authentication**: Required (`X-API-KEY`)

**Description**: Detailed health status including model status and configuration

**Headers**:
```
X-API-KEY: vanicheck-secret-key-2026
```

**Response**:
```json
{
  "status": "operational",
  "service": "वाणीCheck Audio Deepfake Detection API",
  "model_loaded": true,
  "supported_languages": ["tamil", "english", "hindi", "malayalam", "telugu"],
  "device": "cuda",
  "api_version": "1.0.0",
  "timestamp": "2026-02-06T10:30:45.123456"
}
```

**Status Codes**:
- `200 OK`: API is operational
- `401 Unauthorized`: Missing API key
- `403 Forbidden`: Invalid API key
- `500 Internal Server Error`: Service error

**Example**:
```bash
curl -X GET http://localhost:8000/v1/health \
  -H "X-API-KEY: vanicheck-secret-key-2026"
```

---

### 3. Audio Deepfake Detection (Main Endpoint)

**Endpoint**: `POST /v1/detect`

**Authentication**: Required (`X-API-KEY`)

**Description**: Detect if audio is human or AI-generated with forensic analysis

**Headers**:
```
X-API-KEY: vanicheck-secret-key-2026
Content-Type: application/json
```

**Request Body**:
```json
{
  "audio_data": "base64_encoded_audio_string",
  "language": "english",
  "filename": "optional_filename.mp3"
}
```

**Request Parameters**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `audio_data` | string | Yes | Base64-encoded audio file | `SUQzBAAAAAAAI1...` |
| `language` | string | Yes | Target language | `english`, `hindi`, `tamil`, `telugu`, `malayalam` |
| `filename` | string | No | Original filename for logging | `voice_message.mp3` |

**Response**:
```json
{
  "verdict": "AI_GENERATED",
  "confidence": 0.9847,
  "explanation": "High confidence (98.47%) that this audio is AI-generated. Glottal pulses are unnaturally consistent (jitter < 0.01), suggesting voice synthesis. Spectral gaps detected above 8kHz, typical of neural vocoder artifacts. Insufficient natural breathing patterns detected.",
  "forensic_analysis": {
    "glottal_pulses": {
      "mean_f0": 125.3,
      "jitter_ratio": 0.008,
      "natural": false,
      "description": "Consistent F0 suggests AI synthesis"
    },
    "spectral_gaps": {
      "high_frequency_ratio": 0.082,
      "has_spectral_gaps": true,
      "description": "Dead zones above 8kHz typical of TTS"
    },
    "breathing_patterns": {
      "silence_ratio": 0.032,
      "has_breathing_patterns": false,
      "description": "Minimal breathing patterns (characteristic of AI)"
    },
    "harmonic_structure": {
      "harmonic_to_noise_ratio": 12.5,
      "harmonicity": 0.78,
      "description": "High harmonicity suggests synthetic generation"
    }
  },
  "processing_time_ms": 234.5,
  "model_version": "1.0.0",
  "timestamp": "2026-02-06T10:30:45.123456"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `verdict` | string | `HUMAN` or `AI_GENERATED` |
| `confidence` | number | Confidence score (0.0 to 1.0) |
| `explanation` | string | Detailed forensic explanation |
| `forensic_analysis` | object | Detailed forensic findings |
| `processing_time_ms` | number | API processing time in milliseconds |
| `model_version` | string | Model version used for detection |
| `timestamp` | string | ISO 8601 timestamp of detection |

**Forensic Analysis Details**:

```json
{
  "glottal_pulses": {
    "mean_f0": "Average fundamental frequency in Hz",
    "jitter_ratio": "Pitch variation ratio (0-1), higher = more natural",
    "natural": "Boolean: has natural micro-variations",
    "description": "Interpretation of glottal analysis"
  },
  "spectral_gaps": {
    "high_frequency_ratio": "Ratio of high-freq to low-freq energy",
    "has_spectral_gaps": "Boolean: presence of dead frequency zones",
    "description": "Interpretation of spectral analysis"
  },
  "breathing_patterns": {
    "silence_ratio": "Ratio of silent frames (0-1)",
    "has_breathing_patterns": "Boolean: natural breathing detected",
    "description": "Interpretation of breathing analysis"
  },
  "harmonic_structure": {
    "harmonic_to_noise_ratio": "HNR value (higher = more synthetic)",
    "harmonicity": "Harmonic energy ratio (0-1)",
    "description": "Interpretation of harmonic analysis"
  }
}
```

**Status Codes**:
- `200 OK`: Detection successful
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing API key
- `403 Forbidden`: Invalid API key
- `500 Internal Server Error`: Processing error

**Error Responses**:

```json
{
  "detail": "Unsupported language. Supported: ['tamil', 'english', 'hindi', 'malayalam', 'telugu']"
}
```

```json
{
  "detail": "Failed to decode base64 audio"
}
```

```json
{
  "detail": "Detection model not initialized"
}
```

**Example Request**:
```bash
# Encode audio to base64
AUDIO_B64=$(base64 -i audio.mp3)

# Send request
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_data\": \"$AUDIO_B64\",
    \"language\": \"english\",
    \"filename\": \"audio.mp3\"
  }"
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing API key |
| 403 | Forbidden | Invalid API key |
| 404 | Not Found | Endpoint not found |
| 500 | Internal Error | Server error |
| 503 | Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### Common Error Scenarios

**Missing API Key**:
```
Status: 401
{
  "detail": "X-API-KEY header missing"
}
```

**Invalid API Key**:
```
Status: 403
{
  "detail": "Invalid API key"
}
```

**Unsupported Language**:
```
Status: 400
{
  "detail": "Unsupported language. Supported: ['tamil', 'english', 'hindi', 'malayalam', 'telugu']"
}
```

**Invalid Audio Data**:
```
Status: 400
{
  "detail": "Failed to decode base64 audio: Incorrect padding"
}
```

**Model Not Initialized**:
```
Status: 500
{
  "detail": "Detection model not initialized"
}
```

---

## Request/Response Examples

### Example 1: Human Speech Detection

**Request**:
```bash
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "audio_data": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4LjI5LjEwMAAAAAAAAAAAAAAA//NJwAAA...",
  "language": "hindi"
}
EOF
```

**Response**:
```json
{
  "verdict": "HUMAN",
  "confidence": 0.9234,
  "explanation": "High confidence (92.34%) that this is human speech. Natural F0 micro-variations detected in glottal analysis. Full frequency spectrum present across all ranges. Natural breathing and inhalation patterns detected.",
  "forensic_analysis": {
    "glottal_pulses": {
      "mean_f0": 95.2,
      "jitter_ratio": 0.045,
      "natural": true,
      "description": "Natural F0 variation detected"
    },
    "spectral_gaps": {
      "high_frequency_ratio": 0.42,
      "has_spectral_gaps": false,
      "description": "Full frequency spectrum present"
    },
    "breathing_patterns": {
      "silence_ratio": 0.085,
      "has_breathing_patterns": true,
      "description": "Natural breathing pauses detected"
    },
    "harmonic_structure": {
      "harmonic_to_noise_ratio": 4.2,
      "harmonicity": 0.45,
      "description": "Balanced harmonic structure"
    }
  },
  "processing_time_ms": 198.7,
  "model_version": "1.0.0",
  "timestamp": "2026-02-06T11:45:32.456789"
}
```

### Example 2: AI-Generated Audio Detection

**Request**:
```bash
curl -X POST http://localhost:8000/v1/detect \
  -H "X-API-KEY: vanicheck-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "audio_data": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4LjI5LjEwMAAAAAAAAAAAAAAA...",
  "language": "tamil"
}
EOF
```

**Response**:
```json
{
  "verdict": "AI_GENERATED",
  "confidence": 0.9658,
  "explanation": "High confidence (96.58%) that this audio is AI-generated. Glottal pulses are unnaturally consistent (jitter < 0.01), suggesting voice synthesis. Spectral gaps detected above 8kHz, typical of neural vocoder artifacts.",
  "forensic_analysis": {
    "glottal_pulses": {
      "mean_f0": 110.0,
      "jitter_ratio": 0.005,
      "natural": false,
      "description": "Consistent F0 suggests AI synthesis"
    },
    "spectral_gaps": {
      "high_frequency_ratio": 0.065,
      "has_spectral_gaps": true,
      "description": "Dead zones above 8kHz typical of TTS"
    },
    "breathing_patterns": {
      "silence_ratio": 0.02,
      "has_breathing_patterns": false,
      "description": "Minimal breathing patterns (characteristic of AI)"
    },
    "harmonic_structure": {
      "harmonic_to_noise_ratio": 18.5,
      "harmonicity": 0.85,
      "description": "High harmonicity suggests synthetic generation"
    }
  },
  "processing_time_ms": 245.3,
  "model_version": "1.0.0",
  "timestamp": "2026-02-06T11:46:15.789012"
}
```

---

## Rate Limiting (Optional)

When rate limiting is enabled:

**Headers in Response**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1644154800
```

**Rate Limit Exceeded Response**:
```
Status: 429
{
  "detail": "Rate limit exceeded. Retry after 60 seconds."
}
```

---

## Supported Audio Formats

- **MP3** (.mp3)
- **WAV** (.wav)
- **OGG** (.ogg)
- **FLAC** (.flac)
- **AAC** (.aac, .m4a)
- **OPUS** (.opus)

**Constraints**:
- Max file size: 10 MB
- Duration: 1-120 seconds
- Mono or stereo (will be converted to mono)
- Any sample rate (will be resampled to 16 kHz)

---

## Language Support

| Language Code | Language | Script |
|---|---|---|
| `tamil` | Tamil | தமிழ் |
| `telugu` | Telugu | తెలుగు |
| `hindi` | Hindi | हिंदी |
| `malayalam` | Malayalam | മലയാളം |
| `english` | English | - |

---

## Confidence Score Interpretation

| Score Range | Interpretation | Recommendation |
|---|---|---|
| 0.90 - 1.00 | Very High Confidence | Trust verdict |
| 0.75 - 0.89 | High Confidence | Trust verdict |
| 0.60 - 0.74 | Moderate Confidence | Manual review recommended |
| 0.50 - 0.59 | Low Confidence | Manual review required |
| < 0.50 | Uncertain | Request re-analysis |

---

## Performance Metrics

**Expected Processing Times** (on standard hardware):
- 3-second audio: ~200-300ms
- 5-second audio: ~300-400ms
- 10-second audio: ~500-700ms

**Throughput**:
- Single instance: ~10-15 requests/second
- With load balancing: Scales linearly

---

## Changelog

### v1.0.0 (2026-02-06)
- Initial release
- Support for 5 languages (Tamil, English, Hindi, Malayalam, Telugu)
- Binary classification (Human vs. AI)
- Advanced forensic analysis
- Base64 audio input

---

## API Versioning

Current version: **v1.0.0**

Version policy:
- **Major versions** (v2, v3): Breaking changes
- **Minor versions** (v1.1, v1.2): New features, backward compatible
- **Patch versions** (v1.0.1, v1.0.2): Bug fixes

---

For SDK implementations and integration examples, see [INTEGRATION.md](INTEGRATION.md)
