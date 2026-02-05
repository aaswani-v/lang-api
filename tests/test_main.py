"""
Comprehensive test suite for वाणीCheck
Covers baseline accuracy, noise robustness, compression handling, and load testing
"""

import pytest
import numpy as np
import base64
import io
import asyncio
from pathlib import Path
import librosa
import soundfile as sf
import tempfile
from httpx import AsyncClient
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, AudioProcessor, ForensicAnalyzer

# ==================== Test Fixtures ====================

def create_synthetic_human_audio(duration=3, sr=16000):
    """Create synthetic human-like audio for testing"""
    t = np.arange(int(sr * duration)) / sr
    f0 = 100 + 50 * np.sin(2 * np.pi * 0.5 * t)  # Varying pitch
    audio = np.sin(2 * np.pi * f0 * t) * 0.3
    audio += np.random.normal(0, 0.02, len(audio))  # Natural variation
    return audio.astype(np.float32)

def create_synthetic_ai_audio(duration=3, sr=16000):
    """Create synthetic AI-generated audio for testing"""
    t = np.arange(int(sr * duration)) / sr
    f0 = np.full_like(t, 120)  # Constant pitch (typical of TTS)
    audio = np.sin(2 * np.pi * f0 * t) * 0.3
    audio += np.random.normal(0, 0.005, len(audio))  # Less natural variation
    return audio.astype(np.float32)

def audio_to_base64(audio_array, sr=16000):
    """Convert numpy audio array to base64"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio_array, sr)
        with open(tmp.name, "rb") as f:
            audio_bytes = f.read()
        Path(tmp.name).unlink()
    return base64.b64encode(audio_bytes).decode()

@pytest.fixture
def client():
    """Create async test client"""
    return AsyncClient(app=app, base_url="http://test")

@pytest.fixture
def human_audio_b64():
    """Fixture for human audio"""
    audio = create_synthetic_human_audio()
    return audio_to_base64(audio)

@pytest.fixture
def ai_audio_b64():
    """Fixture for AI audio"""
    audio = create_synthetic_ai_audio()
    return audio_to_base64(audio)

@pytest.fixture
def valid_api_key():
    """Valid API key for testing"""
    return "vanicheck-secret-key-2026"

# ==================== Unit Tests ====================

class TestAudioProcessor:
    """Test audio processing functions"""
    
    def test_base64_decode(self, human_audio_b64):
        """Test base64 decoding"""
        audio_bytes = AudioProcessor.decode_base64_audio(human_audio_b64)
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
    
    def test_load_audio(self, human_audio_b64):
        """Test audio loading"""
        audio_bytes = AudioProcessor.decode_base64_audio(human_audio_b64)
        audio = AudioProcessor.load_audio(audio_bytes, sr=16000)
        assert isinstance(audio, np.ndarray)
        assert len(audio) > 0
    
    def test_normalize_audio(self):
        """Test audio normalization"""
        audio = np.array([0.5, 1.0, -0.5, 0.2])
        normalized = AudioProcessor.normalize_audio(audio)
        assert np.max(np.abs(normalized)) <= 1.0
        assert np.allclose(normalized[-1], 0.2)

class TestForensicAnalyzer:
    """Test forensic analysis functions"""
    
    def test_glottal_pulses(self):
        """Test glottal pulse analysis"""
        audio = create_synthetic_human_audio(duration=2)
        result = ForensicAnalyzer.analyze_glottal_pulses(audio, sr=16000)
        assert "mean_f0" in result
        assert "jitter_ratio" in result
        assert "natural" in result
        assert result["mean_f0"] > 0
    
    def test_spectral_gaps(self):
        """Test spectral gap detection"""
        audio = create_synthetic_ai_audio(duration=2)
        result = ForensicAnalyzer.analyze_spectral_gaps(audio, sr=16000)
        assert "high_frequency_ratio" in result
        assert "has_spectral_gaps" in result
        assert 0 <= result["high_frequency_ratio"] <= 1
    
    def test_breathing_patterns(self):
        """Test breathing pattern detection"""
        audio = create_synthetic_human_audio(duration=2)
        result = ForensicAnalyzer.analyze_breathing_patterns(audio, sr=16000)
        assert "silence_ratio" in result
        assert "has_breathing_patterns" in result
        assert 0 <= result["silence_ratio"] <= 1
    
    def test_harmonic_structure(self):
        """Test harmonic structure analysis"""
        audio = create_synthetic_human_audio(duration=2)
        result = ForensicAnalyzer.analyze_harmonic_structure(audio, sr=16000)
        assert "harmonic_to_noise_ratio" in result
        assert "harmonicity" in result
        assert result["harmonic_to_noise_ratio"] > 0

# ==================== Integration Tests ====================

class TestDetectionAPI:
    """Test the main detection API"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_missing_api_key(self, client, human_audio_b64):
        """Test missing API key"""
        response = await client.post(
            "/v1/detect",
            json={
                "audio_data": human_audio_b64,
                "language": "english"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self, client, human_audio_b64):
        """Test invalid API key"""
        response = await client.post(
            "/v1/detect",
            headers={"X-API-KEY": "invalid-key"},
            json={
                "audio_data": human_audio_b64,
                "language": "english"
            }
        )
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_unsupported_language(self, client, human_audio_b64, valid_api_key):
        """Test unsupported language"""
        response = await client.post(
            "/v1/detect",
            headers={"X-API-KEY": valid_api_key},
            json={
                "audio_data": human_audio_b64,
                "language": "klingon"
            }
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_detection_response_structure(self, client, human_audio_b64, valid_api_key):
        """Test detection response structure"""
        response = await client.post(
            "/v1/detect",
            headers={"X-API-KEY": valid_api_key},
            json={
                "audio_data": human_audio_b64,
                "language": "english"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "verdict" in data
        assert data["verdict"] in ["HUMAN", "AI_GENERATED"]
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1
        assert "explanation" in data
        assert "forensic_analysis" in data
        assert "processing_time_ms" in data
        assert "timestamp" in data

# ==================== Robustness Tests ====================

class TestNoiseRobustness:
    """Test API robustness to audio degradation"""
    
    def add_white_noise(audio, snr_db=20):
        """Add white noise to audio"""
        signal_power = np.mean(audio ** 2)
        noise_power = signal_power / (10 ** (snr_db / 10))
        noise = np.random.normal(0, np.sqrt(noise_power), len(audio))
        return (audio + noise).astype(np.float32)
    
    def add_compression_artifacts(audio, bitrate=64):
        """Simulate MP3 compression artifacts"""
        # Simple simulation: reduce bit depth
        bit_depth = max(8, 16 - (bitrate // 32))
        max_val = 2 ** (bit_depth - 1)
        audio_quantized = np.round(audio * max_val) / max_val
        return audio_quantized.astype(np.float32)
    
    @pytest.mark.asyncio
    async def test_noise_injection_10percent(self, client, human_audio_b64, valid_api_key):
        """Test with 10% white noise"""
        audio = create_synthetic_human_audio()
        noisy_audio = TestNoiseRobustness.add_white_noise(audio, snr_db=20)
        noisy_b64 = audio_to_base64(noisy_audio)
        
        response = await client.post(
            "/v1/detect",
            headers={"X-API-KEY": valid_api_key},
            json={
                "audio_data": noisy_b64,
                "language": "english"
            }
        )
        assert response.status_code == 200
        assert response.json()["confidence"] > 0.5
    
    @pytest.mark.asyncio
    async def test_compression_artifacts(self, client, human_audio_b64, valid_api_key):
        """Test with compression artifacts (simulating WhatsApp)"""
        audio = create_synthetic_human_audio()
        compressed_audio = TestNoiseRobustness.add_compression_artifacts(audio, bitrate=64)
        compressed_b64 = audio_to_base64(compressed_audio)
        
        response = await client.post(
            "/v1/detect",
            headers={"X-API-KEY": valid_api_key},
            json={
                "audio_data": compressed_b64,
                "language": "english"
            }
        )
        assert response.status_code == 200
        # Should still work with compression

# ==================== Performance Tests ====================

class TestPerformance:
    """Test API performance metrics"""
    
    @pytest.mark.asyncio
    async def test_processing_time(self, client, human_audio_b64, valid_api_key):
        """Test that processing completes within acceptable time"""
        response = await client.post(
            "/v1/detect",
            headers={"X-API-KEY": valid_api_key},
            json={
                "audio_data": human_audio_b64,
                "language": "english"
            }
        )
        assert response.status_code == 200
        processing_time = response.json()["processing_time_ms"]
        assert processing_time < 5000, "Processing should complete within 5 seconds"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client, human_audio_b64, ai_audio_b64, valid_api_key):
        """Test handling multiple concurrent requests"""
        tasks = []
        for _ in range(5):
            task = client.post(
                "/v1/detect",
                headers={"X-API-KEY": valid_api_key},
                json={
                    "audio_data": human_audio_b64,
                    "language": "english"
                }
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        for response in responses:
            assert response.status_code == 200

# ==================== Language Support Tests ====================

class TestLanguageSupport:
    """Test all supported languages"""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("language", ["tamil", "english", "hindi", "malayalam", "telugu"])
    async def test_all_languages(self, client, human_audio_b64, valid_api_key, language):
        """Test detection for all supported languages"""
        response = await client.post(
            "/v1/detect",
            headers={"X-API-KEY": valid_api_key},
            json={
                "audio_data": human_audio_b64,
                "language": language
            }
        )
        assert response.status_code == 200
        assert response.json()["verdict"] in ["HUMAN", "AI_GENERATED"]

# ==================== Load Testing with Locust ====================

# To run load tests: locust -f tests/test_main.py -u 50 -r 10 --run-time 1m
from locust import HttpUser, task, between

class DetectionLoadTest(HttpUser):
    """Locust load test for API"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup before test"""
        self.audio_b64 = audio_to_base64(create_synthetic_human_audio())
        self.api_key = "vanicheck-secret-key-2026"
    
    @task
    def detect_deepfake(self):
        """Load test task"""
        self.client.post(
            "/v1/detect",
            headers={"X-API-KEY": self.api_key},
            json={
                "audio_data": self.audio_b64,
                "language": "english"
            }
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
