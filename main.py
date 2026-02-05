"""
वाणीCheck - Multi-lingual Deepfake Audio Detection API
Simplified version without heavy dependencies
"""

from fastapi import FastAPI, HTTPException, Header, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
import os
import logging
import base64
import numpy as np
from scipy import signal
from scipy.fft import fft
import librosa
import soundfile as sf
import tempfile
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="वाणीCheck - Audio Deepfake Detection API",
    description="Robust multi-lingual deepfake audio detection using spectral analysis",
    version="1.0.1"  # Updated to support hackathon form field names
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Configuration ====================
SUPPORTED_LANGUAGES = ["tamil", "english", "hindi", "malayalam", "telugu"]
SAMPLE_RATE = 16000
API_KEY = os.getenv("VANICHECK_API_KEY", "vanicheck-secret-key-2026")
MIN_CONFIDENCE_THRESHOLD = 0.70
MAX_AUDIO_SECONDS = float(os.getenv("MAX_AUDIO_SECONDS", "20"))

# ==================== Utilities ====================
def convert_numpy_types(obj):
    """Convert all numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.bool_, np.integer, np.floating)):
        return obj.item()
    else:
        return obj

# ==================== Models ====================
class AudioDetectionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    audio_data: Optional[str] = Field(None, alias="audioBase64")
    language: str
    audioFormat: Optional[str] = None
    filename: Optional[str] = None
    
    @field_validator('language')
    @classmethod
    def normalize_language(cls, v):
        return v.lower() if v else v
    
    @field_validator('audio_data', mode='before')
    @classmethod
    def check_audio_data(cls, v):
        if not v:
            raise ValueError('audio_data or audioBase64 is required')
        return v

class AudioDetectionResponse(BaseModel):
    verdict: str  # "HUMAN" or "AI_GENERATED"
    confidence: float  # 0.0 to 1.0
    explanation: str
    forensic_analysis: dict
    processing_time_ms: float
    duration_seconds: float
    language_detected: str
    model_version: str = "1.0.0-lite"
    timestamp: str

# ==================== Authentication ====================
def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from request header"""
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="X-API-KEY header missing")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

# ==================== Forensic Analysis ====================
class ForensicAnalyzer:
    """Advanced audio forensics to explain detection verdicts"""
    
    @staticmethod
    def analyze_glottal_pulses(audio: np.ndarray, sr: int) -> dict:
        """
        Detect glottal pulse consistency
        AI-generated audio often lacks natural micro-jitter
        """
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=sr
            )
            
            valid_f0 = f0[~np.isnan(f0)]
            if len(valid_f0) > 1:
                jitter = np.std(np.diff(valid_f0)) / (np.mean(valid_f0) + 1e-10)
            else:
                jitter = 0.0
            
            return {
                "mean_f0": float(np.nanmean(f0)) if np.any(~np.isnan(f0)) else 0.0,
                "jitter_ratio": float(jitter),
                "natural": jitter > 0.01,
                "description": "Consistent F0 suggests AI synthesis" if jitter < 0.01 else "Natural F0 variation detected"
            }
        except:
            return {
                "mean_f0": 0.0,
                "jitter_ratio": 0.0,
                "natural": False,
                "description": "F0 analysis unavailable"
            }
    
    @staticmethod
    def analyze_spectral_gaps(audio: np.ndarray, sr: int) -> dict:
        """
        Detect dead frequencies common in low-end TTS
        """
        try:
            D = librosa.stft(audio)
            S = np.abs(D)
            freqs = librosa.fft_frequencies(sr=sr, n_fft=D.shape[0] * 2 - 2)
            
            high_freq_idx = np.where(freqs >= 8000)[0]
            if len(high_freq_idx) > 0:
                high_freq_energy = np.mean(S[high_freq_idx, :])
                low_freq_energy = np.mean(S[:len(high_freq_idx), :])
                high_freq_ratio = high_freq_energy / (low_freq_energy + 1e-10)
            else:
                high_freq_ratio = 1.0
            
            return {
                "high_frequency_ratio": float(high_freq_ratio),
                "has_spectral_gaps": high_freq_ratio < 0.1,
                "description": "Dead zones above 8kHz typical of TTS" if high_freq_ratio < 0.1 else "Full spectrum"
            }
        except:
            return {
                "high_frequency_ratio": 1.0,
                "has_spectral_gaps": False,
                "description": "Spectral analysis unavailable"
            }
    
    @staticmethod
    def analyze_breathing_patterns(audio: np.ndarray, sr: int) -> dict:
        """
        Detect breathing and mouth clicks (artifacts)
        AI speech lacks these natural pauses
        """
        try:
            # Analyze silence patterns
            S = librosa.feature.melspectrogram(y=audio, sr=sr)
            S_db = librosa.power_to_db(S, ref=np.max)
            
            # Find quiet frames (potential breathing)
            quiet_threshold = np.percentile(S_db, 20)
            quiet_frames = np.sum(np.min(S_db, axis=0) < quiet_threshold)
            
            total_frames = S_db.shape[1]
            breathing_ratio = quiet_frames / (total_frames + 1)
            
            return {
                "breathing_ratio": float(breathing_ratio),
                "has_pauses": breathing_ratio > 0.05,
                "description": f"Detected natural breathing patterns" if breathing_ratio > 0.05 else "Minimal breathing artifacts"
            }
        except:
            return {
                "breathing_ratio": 0.0,
                "has_pauses": False,
                "description": "Breathing analysis unavailable"
            }
    
    @staticmethod
    def analyze_harmonic_structure(audio: np.ndarray, sr: int) -> dict:
        """
        Analyze harmonic richness
        Natural speech has rich harmonics; TTS often lacks them
        """
        try:
            # Compute spectrogram
            D = librosa.stft(audio)
            S = np.abs(D)
            freqs = librosa.fft_frequencies(sr=sr, n_fft=D.shape[0] * 2 - 2)
            
            # Analyze harmonic structure
            harmonic_richness = np.sum(S) / (S.shape[0] * S.shape[1] + 1)
            
            # Check for energy concentration (synthetic speech is more concentrated)
            energy_concentration = np.max(S) / (np.mean(S) + 1e-10)
            
            return {
                "harmonic_richness": float(harmonic_richness),
                "energy_concentration": float(energy_concentration),
                "is_synthetic": energy_concentration > 50,
                "description": f"High energy concentration suggests TTS" if energy_concentration > 50 else "Natural harmonic distribution"
            }
        except:
            return {
                "harmonic_richness": 0.0,
                "energy_concentration": 1.0,
                "is_synthetic": False,
                "description": "Harmonic analysis unavailable"
            }

    @classmethod
    def comprehensive_analysis(cls, audio: np.ndarray, sr: int) -> dict:
        """Run all forensic analyses"""
        return {
            "glottal_pulses": cls.analyze_glottal_pulses(audio, sr),
            "spectral_gaps": cls.analyze_spectral_gaps(audio, sr),
            "breathing": cls.analyze_breathing_patterns(audio, sr),
            "harmonics": cls.analyze_harmonic_structure(audio, sr),
        }

# ==================== Audio Processing ====================
class AudioProcessor:
    """Handle audio data extraction and processing"""
    
    @staticmethod
    def decode_audio(audio_base64: str) -> np.ndarray:
        """Decode base64 audio data"""
        try:
            audio_bytes = base64.b64decode(audio_base64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            audio, sr = librosa.load(tmp_path, sr=SAMPLE_RATE)
            os.remove(tmp_path)
            return audio
        except Exception as e:
            logger.error(f"Audio decoding failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid audio data")
    
    @staticmethod
    def preprocess_audio(audio: np.ndarray) -> np.ndarray:
        """Preprocess audio data"""
        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        # Remove DC offset
        audio = audio - np.mean(audio)
        
        return audio

# ==================== Detection Model ====================
class DeepfakeDetectionModel:
    """Lightweight deepfake detection using spectral analysis"""
    
    def __init__(self):
        logger.info("Initializing lightweight detection model...")
    
    def infer(self, audio_data: np.ndarray) -> dict:
        """Run inference on audio data using spectral analysis"""
        try:
            # Extract spectral features
            D = librosa.stft(audio_data)
            S = np.abs(D)
            S_db = librosa.power_to_db(S, ref=np.max)
            
            # Feature 1: Spectral entropy (higher = more noise/synthetic)
            S_norm = S / (np.sum(S) + 1e-10)
            spectral_entropy = -np.sum(S_norm * np.log2(S_norm + 1e-10))
            spectral_entropy = min(1.0, spectral_entropy / 10.0)  # Normalize to [0, 1]
            
            # Feature 2: Harmonic-to-Noise Ratio
            hnr = np.max(S) / (np.mean(S) + 1e-10)
            hnr_norm = min(1.0, (hnr - 1) / 50.0)  # Normalize
            
            # Feature 3: Frequency stability
            freq_stability = np.std(np.max(S, axis=0)) / (np.mean(np.max(S, axis=0)) + 1e-10)
            freq_stability_norm = min(1.0, freq_stability * 2)
            
            # Combined deepfake probability
            ai_probability = (spectral_entropy * 0.3 + hnr_norm * 0.4 + freq_stability_norm * 0.3)
            
            return {
                "human_probability": 1.0 - ai_probability,
                "ai_probability": min(1.0, max(0.0, ai_probability)),
                "spectral_entropy": float(spectral_entropy),
                "hnr": float(hnr_norm),
                "frequency_stability": float(freq_stability_norm)
            }
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return {
                "human_probability": 0.5,
                "ai_probability": 0.5,
                "spectral_entropy": 0.0,
                "hnr": 0.0,
                "frequency_stability": 0.0
            }

# ==================== Global Model Instance ====================
try:
    detection_model = DeepfakeDetectionModel()
    logger.info("✓ Detection model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load detection model: {e}")
    detection_model = None

# ==================== Endpoints ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "वाणीCheck Audio Deepfake Detection API",
        "version": "1.0.0-lite",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/v1/health", tags=["Health"])
async def v1_health_check():
    """V1 API health check"""
    return {
        "status": "operational",
        "model_status": "ready" if detection_model else "error",
        "supported_languages": SUPPORTED_LANGUAGES,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/v1/detect", response_model=AudioDetectionResponse, tags=["Detection"])
async def detect_deepfake(request: AudioDetectionRequest, x_api_key: Optional[str] = Header(None)):
    """Main deepfake detection endpoint"""
    start_time = time.time()
    
    # Verify API key
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="X-API-KEY header missing")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    try:
        # Validate audio_data is present
        if not request.audio_data:
            raise HTTPException(status_code=400, detail="audio_data field is required")
        
        # Validate language
        if request.language.lower() not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Language {request.language} not supported")
        
        # Decode and preprocess audio
        audio_data = AudioProcessor.decode_audio(request.audio_data)
        duration_seconds = len(audio_data) / float(SAMPLE_RATE)
        if duration_seconds > MAX_AUDIO_SECONDS:
            raise HTTPException(
                status_code=413,
                detail=f"Audio too long. Max allowed is {MAX_AUDIO_SECONDS:.0f}s"
            )

        audio_data = AudioProcessor.preprocess_audio(audio_data)
        
        # Run detection
        detection_result = detection_model.infer(audio_data)
        
        # Run forensic analysis
        forensic_result = ForensicAnalyzer.comprehensive_analysis(audio_data, SAMPLE_RATE)
        
        # Determine verdict
        ai_prob = detection_result["ai_probability"]
        
        if ai_prob > (1 - MIN_CONFIDENCE_THRESHOLD):
            verdict = "AI_GENERATED"
            confidence = ai_prob
            explanation = "Audio contains characteristics typical of AI-generated speech"
        elif ai_prob < MIN_CONFIDENCE_THRESHOLD:
            verdict = "HUMAN"
            confidence = 1.0 - ai_prob
            explanation = "Audio appears to be authentic human speech"
        else:
            verdict = "UNCERTAIN"
            confidence = 0.5
            explanation = "Unable to make definitive determination"
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Prepare forensic analysis with converted types
        forensic_data = convert_numpy_types({
            "glottal_pulses": forensic_result["glottal_pulses"],
            "spectral_gaps": forensic_result["spectral_gaps"],
            "breathing": forensic_result["breathing"],
            "harmonics": forensic_result["harmonics"],
            "detection_scores": {
                "ai_probability": float(ai_prob),
                "human_probability": float(1.0 - ai_prob)
            }
        })
        
        return AudioDetectionResponse(
            verdict=verdict,
            confidence=float(confidence),
            explanation=explanation,
            forensic_analysis=forensic_data,
            processing_time_ms=processing_time_ms,
            duration_seconds=float(duration_seconds),
            language_detected=request.language.lower(),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.get("/v1/languages", tags=["Info"])
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "total_languages": len(SUPPORTED_LANGUAGES)
    }

@app.get("/docs", tags=["Documentation"])
async def docs():
    """API documentation"""
    return {
        "title": "वाणीCheck - Audio Deepfake Detection API",
        "version": "1.0.0-lite",
        "endpoints": {
            "health": "/health",
            "v1_health": "/v1/health",
            "detect": "/v1/detect",
            "languages": "/v1/languages"
        }
    }

# ==================== Main ====================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("वाणीCheck API Server")
    print("="*50)
    print("\nStarting FastAPI server on http://localhost:8000")
    print("Access API Documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
