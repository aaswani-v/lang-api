"""
Python-based verification script for वाणीCheck
Can be run on Windows, Mac, or Linux
"""

import sys
import requests
import json
import base64
import numpy as np
import soundfile as sf
import tempfile
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def create_human_audio():
    """Create synthetic human-like audio"""
    duration = 3
    sr = 16000
    t = np.arange(int(sr * duration)) / sr
    
    # Simulate human speech with natural F0 variations
    f0 = 100 + 50 * np.sin(2 * np.pi * 0.5 * t)
    audio = np.sin(2 * np.pi * f0 * t) * 0.3
    audio += np.random.normal(0, 0.02, len(audio))
    
    return audio.astype(np.float32), sr

def audio_to_base64(audio, sr):
    """Convert audio array to base64"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio, sr)
        with open(tmp.name, 'rb') as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        Path(tmp.name).unlink()
    return audio_b64

def test_health_check(api_url):
    """Test health check endpoint"""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200 and "healthy" in response.text:
            print(f"{Colors.GREEN}✓ PASS{Colors.RESET}: API is healthy")
            return True
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET}: Health check failed - {e}")
    return False

def test_authenticated_health(api_url, api_key):
    """Test authenticated health endpoint"""
    try:
        headers = {"X-API-KEY": api_key}
        response = requests.get(f"{api_url}/v1/health", headers=headers, timeout=5)
        if response.status_code == 200 and "operational" in response.text:
            print(f"{Colors.GREEN}✓ PASS{Colors.RESET}: Authenticated health check successful")
            return True
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET}: Authenticated health check failed - {e}")
    return False

def test_detection(api_url, api_key, audio_b64):
    """Test audio detection"""
    try:
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        payload = {
            "audio_data": audio_b64,
            "language": "english"
        }
        response = requests.post(
            f"{api_url}/v1/detect",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            verdict = data.get("verdict", "")
            confidence = data.get("confidence", 0)
            
            print(f"{Colors.GREEN}✓ PASS{Colors.RESET}: Detection successful")
            print(f"  Verdict: {verdict}")
            print(f"  Confidence: {confidence:.2%}")
            print(f"  Processing Time: {data.get('processing_time_ms', 'N/A')}ms")
            return True
    except Exception as e:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET}: Detection failed - {e}")
    return False

def test_languages(api_url, api_key, audio_b64):
    """Test all supported languages"""
    languages = ["tamil", "english", "hindi", "malayalam", "telugu"]
    results = []
    
    for lang in languages:
        try:
            headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
            payload = {"audio_data": audio_b64, "language": lang}
            response = requests.post(
                f"{api_url}/v1/detect",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"  {Colors.GREEN}✓{Colors.RESET} {lang.upper()}: Working")
                results.append(True)
            else:
                print(f"  {Colors.YELLOW}⚠{Colors.RESET} {lang.upper()}: Failed")
                results.append(False)
        except Exception as e:
            print(f"  {Colors.YELLOW}⚠{Colors.RESET} {lang.upper()}: Error - {e}")
            results.append(False)
    
    return all(results)

def test_invalid_key(api_url, audio_b64):
    """Test invalid API key rejection"""
    try:
        headers = {"X-API-KEY": "invalid-key", "Content-Type": "application/json"}
        payload = {"audio_data": audio_b64, "language": "english"}
        response = requests.post(
            f"{api_url}/v1/detect",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 403:
            print(f"{Colors.GREEN}✓ PASS{Colors.RESET}: Invalid API key properly rejected")
            return True
    except Exception:
        pass
    
    return False

def main():
    """Run all verification tests"""
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    else:
        api_url = "http://localhost:8000"
    
    if len(sys.argv) > 2:
        api_key = sys.argv[2]
    else:
        api_key = "vanicheck-secret-key-2026"
    
    print("\n" + "=" * 50)
    print("वाणीCheck API Verification Script")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"API Key: {api_key[:20]}...")
    print()
    
    # Create test audio
    print("[SETUP] Creating synthetic human audio sample...")
    audio, sr = create_human_audio()
    audio_b64 = audio_to_base64(audio, sr)
    print(f"{Colors.GREEN}✓{Colors.RESET} Audio sample created\n")
    
    # Run tests
    test_results = []
    
    print("[TEST 1] Health Check Endpoint")
    test_results.append(test_health_check(api_url))
    print()
    
    print("[TEST 2] Authenticated Health Check")
    test_results.append(test_authenticated_health(api_url, api_key))
    print()
    
    print("[TEST 3] Audio Detection")
    test_results.append(test_detection(api_url, api_key, audio_b64))
    print()
    
    print("[TEST 4] Multi-language Support")
    test_results.append(test_languages(api_url, api_key, audio_b64))
    print()
    
    print("[TEST 5] Invalid API Key Handling")
    test_results.append(test_invalid_key(api_url, audio_b64))
    print()
    
    # Summary
    print("=" * 50)
    print("वाणीCheck Verification Complete!")
    print("=" * 50)
    
    if all(test_results):
        print(f"\n{Colors.GREEN}✓ All tests passed!{Colors.RESET}\n")
        print("API Status: OPERATIONAL ✓")
        print("Supported Languages: Tamil, English, Hindi, Malayalam, Telugu")
        return 0
    else:
        print(f"\n{Colors.RED}✗ Some tests failed{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
