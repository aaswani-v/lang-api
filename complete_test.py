#!/usr/bin/env python3
"""Complete testing script with audio generation"""

import requests
import json
import base64
import numpy as np
from scipy.io import wavfile
import tempfile
import os

API_URL = "http://localhost:8000"
API_KEY = "vanicheck-secret-key-2026"

def generate_test_audio(duration=3, frequency=440):
    """Generate a sine wave test audio"""
    sample_rate = 16000
    t = np.linspace(0, duration, sample_rate * duration)
    
    # Generate sine wave
    audio = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Add some harmonics to make it sound more natural
    audio += np.sin(2 * np.pi * frequency * 2 * t) * 0.1
    audio += np.sin(2 * np.pi * frequency * 3 * t) * 0.05
    
    # Add subtle noise
    audio += np.random.normal(0, 0.01, len(audio))
    
    return audio.astype(np.float32), sample_rate

def audio_to_base64(audio, sr):
    """Convert audio array to base64 encoded WAV"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Convert to int16 for WAV format
        audio_int = (audio * 32767).astype(np.int16)
        wavfile.write(tmp_path, sr, audio_int)
        
        with open(tmp_path, 'rb') as f:
            audio_b64 = base64.b64encode(f.read()).decode()
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass
    
    return audio_b64

def test_health():
    """Test health endpoints"""
    print("\n" + "="*60)
    print("TEST 1: Health Check Endpoints")
    print("="*60)
    
    try:
        # Basic health
        r = requests.get(f"{API_URL}/health", timeout=5)
        if r.status_code == 200:
            print("✓ PASS: /health endpoint")
            data = r.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Service: {data.get('service')}")
            print(f"  Version: {data.get('version')}")
        else:
            print(f"✗ FAIL: /health returned {r.status_code}")
            return False
            
        # V1 Health with API key
        headers = {"X-API-KEY": API_KEY}
        r = requests.get(f"{API_URL}/v1/health", headers=headers, timeout=5)
        if r.status_code == 200:
            print("\n✓ PASS: /v1/health endpoint")
            data = r.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Model: {data.get('model_status')}")
            print(f"  Languages: {', '.join(data.get('supported_languages', []))}")
        else:
            print(f"✗ FAIL: /v1/health returned {r.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    
    return True

def test_languages():
    """Test supported languages"""
    print("\n" + "="*60)
    print("TEST 2: Supported Languages")
    print("="*60)
    
    try:
        r = requests.get(f"{API_URL}/v1/languages", timeout=5)
        if r.status_code == 200:
            print("✓ PASS: /v1/languages endpoint")
            data = r.json()
            langs = data.get('supported_languages', [])
            print(f"  Total languages: {len(langs)}")
            for lang in langs:
                print(f"    - {lang.upper()}")
        else:
            print(f"✗ FAIL: returned {r.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    
    return True

def test_detection(language="english"):
    """Test audio detection"""
    print("\n" + "="*60)
    print(f"TEST 3: Audio Detection ({language.upper()})")
    print("="*60)
    
    try:
        # Generate test audio
        print("  [1] Generating test audio...")
        audio, sr = generate_test_audio(duration=2)
        audio_b64 = audio_to_base64(audio, sr)
        print(f"      ✓ Generated {len(audio)} samples at {sr} Hz")
        
        # Send detection request
        print("  [2] Sending detection request...")
        headers = {"X-API-KEY": API_KEY}
        payload = {
            "audio_data": audio_b64,
            "language": language
        }
        
        r = requests.post(
            f"{API_URL}/v1/detect",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if r.status_code == 200:
            data = r.json()
            print(f"      ✓ Detection successful")
            
            # Display results
            print("\n  [3] Results:")
            print(f"      Verdict: {data.get('verdict')}")
            print(f"      Confidence: {data.get('confidence'):.2%}")
            print(f"      Explanation: {data.get('explanation')}")
            print(f"      Processing Time: {data.get('processing_time_ms'):.2f}ms")
            
            # Display forensic analysis
            forensics = data.get('forensic_analysis', {})
            if forensics:
                print("\n  [4] Forensic Analysis:")
                
                glottal = forensics.get('glottal_pulses', {})
                if glottal:
                    print(f"      Glottal Pulses:")
                    print(f"        - Mean F0: {glottal.get('mean_f0'):.1f} Hz")
                    print(f"        - Jitter: {glottal.get('jitter_ratio'):.4f}")
                    print(f"        - Natural: {glottal.get('natural')}")
                
                spectral = forensics.get('spectral_gaps', {})
                if spectral:
                    print(f"      Spectral Gaps:")
                    print(f"        - High-Freq Ratio: {spectral.get('high_frequency_ratio'):.3f}")
                    print(f"        - Has Gaps: {spectral.get('has_spectral_gaps')}")
                
                breathing = forensics.get('breathing', {})
                if breathing:
                    print(f"      Breathing Patterns:")
                    print(f"        - Breathing Ratio: {breathing.get('breathing_ratio'):.3f}")
                    print(f"        - Has Pauses: {breathing.get('has_pauses')}")
                
                harmonics = forensics.get('harmonics', {})
                if harmonics:
                    print(f"      Harmonics:")
                    print(f"        - Richness: {harmonics.get('harmonic_richness'):.3f}")
                    print(f"        - Energy Concentration: {harmonics.get('energy_concentration'):.1f}")
            
            print("\n  ✓ PASS: Detection working correctly")
            return True
        else:
            print(f"  ✗ FAIL: returned {r.status_code}")
            print(f"      Response: {r.text}")
            return False
            
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def test_all_languages():
    """Test detection in all supported languages"""
    print("\n" + "="*60)
    print("TEST 4: Multi-Language Support")
    print("="*60)
    
    languages = ["tamil", "english", "hindi", "malayalam", "telugu"]
    results = []
    
    # Generate audio once
    audio, sr = generate_test_audio(duration=1)
    audio_b64 = audio_to_base64(audio, sr)
    
    for lang in languages:
        try:
            headers = {"X-API-KEY": API_KEY}
            payload = {
                "audio_data": audio_b64,
                "language": lang
            }
            
            r = requests.post(
                f"{API_URL}/v1/detect",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if r.status_code == 200:
                data = r.json()
                verdict = data.get('verdict')
                confidence = data.get('confidence')
                print(f"  ✓ {lang.upper():12} - Verdict: {verdict:12} (Confidence: {confidence:.1%})")
                results.append(True)
            else:
                print(f"  ✗ {lang.upper():12} - Failed ({r.status_code})")
                results.append(False)
        except Exception as e:
            print(f"  ✗ {lang.upper():12} - Error: {e}")
            results.append(False)
    
    return all(results)

def test_invalid_key():
    """Test API key validation"""
    print("\n" + "="*60)
    print("TEST 5: API Key Validation")
    print("="*60)
    
    try:
        # Test with wrong API key
        audio, sr = generate_test_audio(duration=1)
        audio_b64 = audio_to_base64(audio, sr)
        
        headers = {"X-API-KEY": "invalid-key"}
        payload = {
            "audio_data": audio_b64,
            "language": "english"
        }
        
        r = requests.post(
            f"{API_URL}/v1/detect",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        if r.status_code == 403:
            print("  ✓ PASS: Invalid API key correctly rejected")
            return True
        else:
            print(f"  ✗ FAIL: Expected 403, got {r.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("#" * 60)
    print("# वाणीCheck - Complete API Test Suite")
    print("#" * 60)
    
    results = {
        "Health Checks": test_health(),
        "Languages": test_languages(),
        "English Detection": test_detection("english"),
        "Multi-Language": test_all_languages(),
        "API Key Validation": test_invalid_key(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! API is working perfectly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
