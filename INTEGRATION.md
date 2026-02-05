# Integration Examples for वाणीCheck API

## Quick Integration Examples

### Python (Recommended)

```python
import requests
import base64
from pathlib import Path

class VaniCheckClient:
    def __init__(self, api_url="http://localhost:8000", api_key="vanicheck-secret-key-2026"):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
    
    def detect(self, audio_path: str, language: str = "english"):
        """
        Detect if audio is human or AI-generated
        
        Args:
            audio_path: Path to audio file (MP3, WAV, OGG)
            language: One of [tamil, english, hindi, malayalam, telugu]
        
        Returns:
            dict: Detection verdict with forensic analysis
        """
        # Read and encode audio
        with open(audio_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        
        # Make request
        response = requests.post(
            f"{self.api_url}/v1/detect",
            json={
                "audio_data": audio_b64,
                "language": language,
                "filename": Path(audio_path).name
            },
            headers=self.headers,
            timeout=15
        )
        
        response.raise_for_status()
        return response.json()
    
    def health_check(self):
        """Check API health status"""
        response = requests.get(
            f"{self.api_url}/v1/health",
            headers=self.headers,
            timeout=5
        )
        return response.json()

# Usage
if __name__ == "__main__":
    client = VaniCheckClient()
    
    # Check health
    print("Health:", client.health_check())
    
    # Detect audio
    result = client.detect("audio_sample.mp3", language="hindi")
    print("\nDetection Result:")
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Explanation: {result['explanation']}")
    
    # Check forensic analysis
    forensics = result['forensic_analysis']
    print("\nForensic Analysis:")
    print(f"F0 Jitter: {forensics['glottal_pulses']['jitter_ratio']:.4f}")
    print(f"High Freq Ratio: {forensics['spectral_gaps']['high_frequency_ratio']:.4f}")
    print(f"Breathing Patterns: {forensics['breathing_patterns']['has_breathing_patterns']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');
const path = require('path');

class VaniCheckClient {
    constructor(apiUrl = "http://localhost:8000", apiKey = "vanicheck-secret-key-2026") {
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.client = axios.create({
            baseURL: apiUrl,
            headers: {
                "X-API-KEY": apiKey,
                "Content-Type": "application/json"
            },
            timeout: 15000
        });
    }

    async detect(audioPath, language = "english") {
        /**
         * Detect if audio is human or AI-generated
         */
        // Read and encode audio
        const audioBuffer = fs.readFileSync(audioPath);
        const audioB64 = audioBuffer.toString('base64');

        const response = await this.client.post('/v1/detect', {
            audio_data: audioB64,
            language: language,
            filename: path.basename(audioPath)
        });

        return response.data;
    }

    async healthCheck() {
        const response = await this.client.get('/v1/health');
        return response.data;
    }
}

// Usage
(async () => {
    const client = new VaniCheckClient();

    // Check health
    const health = await client.healthCheck();
    console.log("Health:", health);

    // Detect audio
    const result = await client.detect("audio_sample.mp3", "english");
    console.log("\nDetection Result:");
    console.log(`Verdict: ${result.verdict}`);
    console.log(`Confidence: ${(result.confidence * 100).toFixed(2)}%`);
    console.log(`Explanation: ${result.explanation}`);

    console.log("\nForensic Analysis:");
    console.log(`Processing Time: ${result.processing_time_ms}ms`);
})();
```

### cURL (Simple Testing)

```bash
#!/bin/bash

API_URL="http://localhost:8000"
API_KEY="vanicheck-secret-key-2026"
AUDIO_FILE="audio_sample.mp3"

# Step 1: Check health
echo "=== Health Check ==="
curl -X GET "$API_URL/health" | python -m json.tool

echo ""
echo "=== Authenticated Health Check ==="
curl -X GET "$API_URL/v1/health" \
  -H "X-API-KEY: $API_KEY" | python -m json.tool

# Step 2: Detect audio
echo ""
echo "=== Audio Detection ==="

# Encode audio to base64
AUDIO_B64=$(base64 -i "$AUDIO_FILE")

# Send detection request
curl -X POST "$API_URL/v1/detect" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_data\": \"$AUDIO_B64\",
    \"language\": \"english\",
    \"filename\": \"$AUDIO_FILE\"
  }" | python -m json.tool
```

### React.js Integration

```javascript
// api/vanicheck.js
import axios from 'axios';

const VANICHECK_API = process.env.REACT_APP_VANICHECK_API || "http://localhost:8000";
const API_KEY = process.env.REACT_APP_VANICHECK_KEY;

export const detectAudio = async (audioFile, language = "english") => {
    // Convert file to base64
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = async () => {
            const audioB64 = reader.result.split(',')[1];
            
            try {
                const response = await axios.post(`${VANICHECK_API}/v1/detect`, {
                    audio_data: audioB64,
                    language: language,
                    filename: audioFile.name
                }, {
                    headers: {
                        "X-API-KEY": API_KEY,
                        "Content-Type": "application/json"
                    },
                    timeout: 15000
                });
                
                resolve(response.data);
            } catch (error) {
                reject(error);
            }
        };
        
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(audioFile);
    });
};

// Component usage
import React, { useState } from 'react';
import { detectAudio } from './api/vanicheck';

export default function AudioDetector() {
    const [file, setFile] = useState(null);
    const [language, setLanguage] = useState('english');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleDetect = async () => {
        if (!file) return;
        
        setLoading(true);
        setError(null);
        
        try {
            const detectionResult = await detectAudio(file, language);
            setResult(detectionResult);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="detector">
            <h2>वाणीCheck Audio Detection</h2>
            
            <div>
                <input
                    type="file"
                    accept="audio/*"
                    onChange={(e) => setFile(e.target.files[0])}
                />
                
                <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                    <option value="english">English</option>
                    <option value="hindi">Hindi (हिंदी)</option>
                    <option value="tamil">Tamil (தமிழ்)</option>
                    <option value="telugu">Telugu (తెలుగు)</option>
                    <option value="malayalam">Malayalam (മലയാളം)</option>
                </select>
                
                <button onClick={handleDetect} disabled={!file || loading}>
                    {loading ? 'Detecting...' : 'Detect'}
                </button>
            </div>

            {error && <div className="error">{error}</div>}
            
            {result && (
                <div className="result">
                    <h3>{result.verdict}</h3>
                    <p>Confidence: {(result.confidence * 100).toFixed(2)}%</p>
                    <p>{result.explanation}</p>
                    
                    <details>
                        <summary>Forensic Analysis</summary>
                        <pre>{JSON.stringify(result.forensic_analysis, null, 2)}</pre>
                    </details>
                </div>
            )}
        </div>
    );
}
```

### Flutter/Dart Integration

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class VaniCheckClient {
    final String apiUrl;
    final String apiKey;

    VaniCheckClient({
        this.apiUrl = "http://localhost:8000",
        this.apiKey = "vanicheck-secret-key-2026"
    });

    Future<Map<String, dynamic>> detect(
        File audioFile,
        String language = "english"
    ) async {
        // Read and encode audio
        List<int> audioBytes = await audioFile.readAsBytes();
        String audioB64 = base64.encode(audioBytes);

        // Make request
        final response = await http.post(
            Uri.parse('$apiUrl/v1/detect'),
            headers: {
                'X-API-KEY': apiKey,
                'Content-Type': 'application/json',
            },
            body: jsonEncode({
                'audio_data': audioB64,
                'language': language,
                'filename': audioFile.path.split('/').last,
            }),
        ).timeout(Duration(seconds: 15));

        if (response.statusCode == 200) {
            return jsonDecode(response.body);
        } else {
            throw Exception('Detection failed: ${response.statusCode}');
        }
    }

    Future<Map<String, dynamic>> healthCheck() async {
        final response = await http.get(
            Uri.parse('$apiUrl/v1/health'),
            headers: {'X-API-KEY': apiKey},
        ).timeout(Duration(seconds: 5));

        if (response.statusCode == 200) {
            return jsonDecode(response.body);
        } else {
            throw Exception('Health check failed');
        }
    }
}

// Usage
void main() async {
    final client = VaniCheckClient();
    
    final audioFile = File('audio_sample.mp3');
    final result = await client.detect(audioFile, 'hindi');
    
    print('Verdict: ${result['verdict']}');
    print('Confidence: ${(result['confidence'] * 100).toFixed(2)}%');
    print('Explanation: ${result['explanation']}');
}
```

## Authentication Best Practices

### Secure API Key Storage

**Never commit API keys to version control!**

```python
# Use environment variables
import os
API_KEY = os.getenv("VANICHECK_API_KEY")

# Or use .env files
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("VANICHECK_API_KEY")
```

### Key Rotation

```bash
# Generate new key
NEW_KEY=$(openssl rand -hex 32)

# Update environment
export VANICHECK_API_KEY=$NEW_KEY

# Update in AWS Secrets Manager, Vault, etc.
aws secretsmanager update-secret \
    --secret-id vanicheck-api-key \
    --secret-string $NEW_KEY
```

## Error Handling

### Common Errors and Solutions

```python
try:
    result = client.detect("audio.mp3", "english")
except requests.exceptions.Timeout:
    print("API request timed out - audio may be too long")
except requests.exceptions.ConnectionError:
    print("Cannot connect to API - check URL and API status")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed - check API key")
    elif e.response.status_code == 403:
        print("Invalid API key")
    elif e.response.status_code == 400:
        print("Invalid request - check parameters")
except ValueError as e:
    print(f"Invalid response: {e}")
```

## Response Interpretation Guide

### Verdict Types

| Verdict | Confidence | Interpretation |
|---------|-----------|-----------------|
| `HUMAN` | 0.90+ | Very confident audio is human speech |
| `HUMAN` | 0.70-0.89 | Likely human speech |
| `AI_GENERATED` | 0.90+ | Very confident audio is AI-generated |
| `AI_GENERATED` | 0.70-0.89 | Likely AI-generated |

### Forensic Flags

```python
result = client.detect("audio.mp3")
analysis = result['forensic_analysis']

# Check for AI markers
if not analysis['glottal_pulses']['natural']:
    print("⚠️ Unnaturally consistent pitch detected")

if analysis['spectral_gaps']['has_spectral_gaps']:
    print("⚠️ Dead zones in high frequency spectrum")

if not analysis['breathing_patterns']['has_breathing_patterns']:
    print("⚠️ Missing natural breathing patterns")

if analysis['harmonic_structure']['harmonic_to_noise_ratio'] > 10:
    print("⚠️ Overly clean harmonic structure")
```

## Performance Tips

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

def detect_batch(audio_files, language="english", max_workers=4):
    client = VaniCheckClient()
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(client.detect, f, language): f 
            for f in audio_files
        }
        
        for future in futures:
            filename = futures[future]
            try:
                results[filename] = future.result()
            except Exception as e:
                results[filename] = {"error": str(e)}
    
    return results
```

### Caching Results

```python
import json
from pathlib import Path

class VaniCheckClientWithCache(VaniCheckClient):
    def __init__(self, *args, cache_dir=".cache", **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, audio_path, language):
        import hashlib
        content = Path(audio_path).read_bytes()
        return hashlib.md5(f"{content}{language}".encode()).hexdigest()
    
    def detect(self, audio_path, language="english", use_cache=True):
        cache_key = self._get_cache_key(audio_path, language)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if use_cache and cache_file.exists():
            return json.loads(cache_file.read_text())
        
        result = super().detect(audio_path, language)
        cache_file.write_text(json.dumps(result))
        return result
```

---

For more examples and advanced usage, see the [main documentation](README.md).
