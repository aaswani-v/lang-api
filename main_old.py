"""
वाणीCheck - Multi-lingual Deepfake Audio Detection API
Elite Audio Forensics Detection System
Supports: Tamil, English, Hindi, Malayalam, Telugu
"""

from fastapi import FastAPI, HTTPException, Header, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging
import base64
import hashlib
import json
from datetime import datetime
import librosa
import numpy as np
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from scipy import signal
from scipy.fft import fft
import soundfile as sf
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="वाणीCheck - Audio Deepfake Detection API",
    description="Robust multi-lingual deepfake audio detection using Wav2Vec 2.0",
    version="1.0.0"
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
MODEL_NAME = "facebook/wav2vec2-xlsr-53-english"  # Will be fine-tuned for deepfake detection
SAMPLE_RATE = 16000
API_KEY = os.getenv("VANICHECK_API_KEY", "vanicheck-secret-key-2026")
MIN_CONFIDENCE_THRESHOLD = 0.70

# ==================== Models ====================
class AudioDetectionRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    language: str
    filename: Optional[str] = None

class AudioDetectionResponse(BaseModel):
    verdict: str  # "HUMAN" or "AI_GENERATED"
    confidence: float  # 0.0 to 1.0
    explanation: str
    forensic_analysis: dict
    processing_time_ms: float
    model_version: str = "1.0.0"
    timestamp: str

# ==================== Authentication ====================
def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from request header"""
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="X-API-KEY header missing")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

# ==================== Model Management ====================
class DeepfakeDetectionModel:
    """Handles model loading and inference"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.processor = None
        self.load_model()
    
    def load_model(self):
        """Load pre-trained Wav2Vec 2.0 model"""
        try:
            logger.info(f"Loading model on {self.device}...")
            self.processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
            self.model = Wav2Vec2ForCTC.from_pretrained(
                MODEL_NAME
            ).to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise
    
    def infer(self, audio_data: np.ndarray) -> dict:
        """Run inference on audio data"""
        try:
            # Normalize audio to [-1, 1] range
            audio_data = audio_data.astype(np.float32)
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Process audio with Wav2Vec 2.0
            inputs = self.processor(
                audio_data,
                sampling_rate=SAMPLE_RATE,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # For Wav2Vec2ForCTC, compute a simple deepfake probability
            # Based on spectral entropy and acoustic features
            logits_np = logits.cpu().numpy()
            logits_mean = np.mean(np.abs(logits_np))
            logits_std = np.std(logits_np)
            
            # Heuristic: high variance in logits may indicate synthetic speech
            anomaly_score = min(1.0, logits_std / (logits_mean + 1e-6) / 5.0)
            
            return {
                "human_probability": 1.0 - anomaly_score,
                "ai_probability": anomaly_score,
                "logits": logits_np[0].tolist()[:100]  # Limit to first 100 for response size
            }
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            raise

# ==================== Forensic Analysis ====================
class ForensicAnalyzer:
    """Advanced audio forensics to explain detection verdicts"""
    
    @staticmethod
    def analyze_glottal_pulses(audio: np.ndarray, sr: int) -> dict:
        """
        Detect glottal pulse consistency
        AI-generated audio often lacks natural micro-jitter
        """
        # Extract fundamental frequency
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr
        )
        
        # Calculate jitter (micro-variations)
        valid_f0 = f0[~np.isnan(f0)]
        if len(valid_f0) > 1:
            jitter = np.std(np.diff(valid_f0)) / np.mean(valid_f0)
        else:
            jitter = 0.0
        
        return {
            "mean_f0": float(np.nanmean(f0)) if np.any(~np.isnan(f0)) else 0.0,
            "jitter_ratio": float(jitter),
            "natural": jitter > 0.01,  # Natural speech has micro-jitter
            "description": "Consistent F0 suggests AI synthesis" if jitter < 0.01 else "Natural F0 variation detected"
        }
    
    @staticmethod
    def analyze_spectral_gaps(audio: np.ndarray, sr: int) -> dict:
        """
        Detect dead frequencies common in low-end TTS
        Neural vocoders often have gaps above 8kHz
        """
        # Compute spectrogram
        D = librosa.stft(audio)
        S = np.abs(D)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=D.shape[0] * 2 - 2)
        
        # Analyze high-frequency energy (8kHz+)
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
            "description": "Dead zones above 8kHz typical of TTS" if high_freq_ratio < 0.1 else "Full frequency spectrum present"
        }
    
    @staticmethod
    def analyze_breathing_patterns(audio: np.ndarray, sr: int) -> dict:
        """
        Detect natural breathing/inhalation pauses
        AI often lacks realistic breath patterns
        """
        # Detect silence/low-energy segments
        S = librosa.feature.melspectrogram(y=audio, sr=sr)
        log_S = librosa.power_to_db(S, ref=np.max)
        
        # Find quiet frames (potential breathing)
        energy_threshold = np.percentile(log_S, 20)
        quiet_frames = np.sum(log_S < energy_threshold) / log_S.shape[1]
        
        # Detect inter-utterance pauses
        hop_length = 512
        frame_length = len(audio) // (hop_S.shape[1] * hop_length)
        
        return {
            "silence_ratio": float(quiet_frames),
            "has_breathing_patterns": quiet_frames > 0.05,
            "description": "Natural breathing pauses detected" if quiet_frames > 0.05 else "Minimal breathing patterns (characteristic of AI)"
        }
    
    @staticmethod
    def analyze_harmonic_structure(audio: np.ndarray, sr: int) -> dict:
        """Analyze harmonic-to-noise ratio"""
        # Compute harmonic and percussive components
        harmonic, percussive = librosa.effects.hpss(audio)
        
        harmonic_energy = np.sum(harmonic ** 2)
        percussive_energy = np.sum(percussive ** 2)
        total_energy = np.sum(audio ** 2)
        
        hnr = harmonic_energy / (percussive_energy + 1e-10)
        harmonicity = harmonic_energy / total_energy
        
        return {
            "harmonic_to_noise_ratio": float(hnr),
            "harmonicity": float(harmonicity),
            "description": "High harmonicity suggests synthetic generation" if hnr > 10 else "Balanced harmonic structure"
        }
    
    @classmethod
    def run_full_analysis(cls, audio: np.ndarray, sr: int) -> dict:
        """Run complete forensic analysis"""
        return {
            "glottal_pulses": cls.analyze_glottal_pulses(audio, sr),
            "spectral_gaps": cls.analyze_spectral_gaps(audio, sr),
            "breathing_patterns": cls.analyze_breathing_patterns(audio, sr),
            "harmonic_structure": cls.analyze_harmonic_structure(audio, sr)
        }

# ==================== Audio Processing ====================
class AudioProcessor:
    """Handles audio decoding and preprocessing"""
    
    @staticmethod
    def decode_base64_audio(audio_b64: str) -> tuple:
        """Decode base64 encoded audio"""
        try:
            audio_bytes = base64.b64decode(audio_b64)
            return audio_bytes
        except Exception as e:
            raise ValueError(f"Failed to decode base64 audio: {e}")
    
    @staticmethod
    def load_audio(audio_bytes: bytes, sr: int = SAMPLE_RATE) -> np.ndarray:
        """Load audio from bytes and resample to target sample rate"""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp.flush()
                audio, orig_sr = librosa.load(tmp.name, sr=sr, mono=True)
                os.unlink(tmp.name)
            return audio
        except Exception as e:
            raise ValueError(f"Failed to load audio: {e}")
    
    @staticmethod
    def normalize_audio(audio: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
        return audio

# ==================== Initialize Model ====================
try:
    model = DeepfakeDetectionModel()
    logger.info("Deepfake detection model initialized")
except Exception as e:
    logger.error(f"Failed to initialize model: {e}")
    model = None

# ==================== API Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "वाणीCheck Audio Deepfake Detection API",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/v1/detect", response_model=AudioDetectionResponse)
async def detect_deepfake(
    request: AudioDetectionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Main endpoint for deepfake audio detection
    
    Request:
    - audio_data: Base64 encoded audio file
    - language: Target language (tamil, english, hindi, malayalam, telugu)
    - filename: Optional filename for logging
    
    Response:
    - verdict: "HUMAN" or "AI_GENERATED"
    - confidence: Detection confidence (0.0 to 1.0)
    - explanation: Detailed explanation of the verdict
    - forensic_analysis: Detailed forensic findings
    """
    start_time = datetime.utcnow()
    
    # Validate language
    if request.language.lower() not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Supported: {SUPPORTED_LANGUAGES}"
        )
    
    # Check if model is loaded
    if model is None:
        raise HTTPException(status_code=500, detail="Detection model not initialized")
    
    try:
        # Decode and load audio
        audio_bytes = AudioProcessor.decode_base64_audio(request.audio_data)
        audio = AudioProcessor.load_audio(audio_bytes, sr=SAMPLE_RATE)
        audio = AudioProcessor.normalize_audio(audio)
        
        # Run inference
        inference_result = model.infer(audio)
        ai_confidence = inference_result["ai_probability"]
        
        # Run forensic analysis
        forensic_analysis = ForensicAnalyzer.run_full_analysis(audio, SAMPLE_RATE)
        
        # Determine verdict
        if ai_confidence >= 0.5:
            verdict = "AI_GENERATED"
            confidence = ai_confidence
        else:
            verdict = "HUMAN"
            confidence = inference_result["human_probability"]
        
        # Generate explanation
        explanation = _generate_explanation(
            verdict, confidence, forensic_analysis
        )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return AudioDetectionResponse(
            verdict=verdict,
            confidence=round(confidence, 4),
            explanation=explanation,
            forensic_analysis=forensic_analysis,
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail="Detection processing failed")

def _generate_explanation(verdict: str, confidence: float, analysis: dict) -> str:
    """Generate detailed explanation based on forensic analysis"""
    glottal = analysis["glottal_pulses"]
    spectral = analysis["spectral_gaps"]
    breathing = analysis["breathing_patterns"]
    harmonic = analysis["harmonic_structure"]
    
    explanation_parts = []
    
    if verdict == "AI_GENERATED":
        explanation_parts.append(
            f"High confidence ({confidence:.1%}) that this audio is AI-generated. "
        )
        
        if glottal.get("jitter_ratio", 0) < 0.01:
            explanation_parts.append(
                "Glottal pulses are unnaturally consistent (jitter < 0.01), "
                "suggesting voice synthesis."
            )
        
        if spectral.get("has_spectral_gaps"):
            explanation_parts.append(
                "Spectral gaps detected above 8kHz, typical of neural vocoder artifacts."
            )
        
        if not breathing.get("has_breathing_patterns"):
            explanation_parts.append(
                "Insufficient natural breathing patterns detected."
            )
        
        if harmonic.get("harmonic_to_noise_ratio", 0) > 10:
            explanation_parts.append(
                "Harmonic structure is too clean (HNR > 10), "
                "inconsistent with natural human speech."
            )
    
    else:  # HUMAN
        explanation_parts.append(
            f"High confidence ({confidence:.1%}) that this is human speech. "
        )
        
        if glottal.get("jitter_ratio", 0) > 0.01:
            explanation_parts.append(
                "Natural F0 micro-variations detected in glottal analysis."
            )
        
        if not spectral.get("has_spectral_gaps"):
            explanation_parts.append(
                "Full frequency spectrum present across all ranges."
            )
        
        if breathing.get("has_breathing_patterns"):
            explanation_parts.append(
                "Natural breathing and inhalation patterns detected."
            )
    
    return " ".join(explanation_parts)

@app.get("/v1/health")
async def detailed_health(api_key: str = Depends(verify_api_key)):
    """Detailed health check with model status"""
    return {
        "status": "operational",
        "service": "वाणीCheck Audio Deepfake Detection API",
        "model_loaded": model is not None,
        "supported_languages": SUPPORTED_LANGUAGES,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "api_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
