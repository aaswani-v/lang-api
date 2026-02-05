"""Generate realistic human voice-like test audio"""
import numpy as np
import soundfile as sf
import base64
import io
from scipy import signal as scipy_signal

# Generate 3 seconds of audio at 16kHz
sr = 16000
duration = 3  # seconds
t = np.linspace(0, duration, sr * duration)

# Create realistic voice signal
voice_signal = np.zeros_like(t)

# Natural pitch variation (speech pitch contour)
pitch_contour = 110 + 40 * np.sin(2 * np.pi * 0.4 * t)  # Pitch varies naturally

# Generate voiced signal with formants
for i in range(len(t)):
    f0 = pitch_contour[i]
    
    # Voice source: fundamental + harmonics
    harmonics = 0.5 * np.sin(2 * np.pi * f0 * t[i])
    for h in range(2, 6):
        harmonics += (0.25 / h) * np.sin(2 * np.pi * h * f0 * t[i])
    
    # Vocal tract resonances (formants - vowel-like sounds)
    # Approximate F1 (~700Hz), F2 (~1200Hz), F3 (~2500Hz) with varying emphasis
    f1_amp = 0.2 + 0.1 * np.sin(2 * np.pi * 1.2 * t[i])  # Formant 1 variation
    f2_amp = 0.15 + 0.08 * np.sin(2 * np.pi * 0.8 * t[i])  # Formant 2 variation
    f3_amp = 0.08
    
    formants = (f1_amp * np.sin(2 * np.pi * 700 * t[i]) +
                f2_amp * np.sin(2 * np.pi * 1220 * t[i]) +
                f3_amp * np.sin(2 * np.pi * 2600 * t[i]))
    
    # Combine voice source and formants
    voice_signal[i] = harmonics + formants

# Add breathy noise (realistic voice has 15-20% noise)
noise = np.random.normal(0, 0.12, len(t))
voice_signal = voice_signal + noise

# Create natural speech-like envelope (bursts with pauses)
envelope = np.ones_like(t)
segment_len = int(0.2 * sr)  # 200ms speech segments
pause_len = int(0.08 * sr)  # 80ms pauses

pos = 0
while pos < len(t):
    seg_end = min(pos + segment_len, len(t))
    
    # Create attack (50ms) and release (50ms) within segment
    attack = int(0.05 * sr)
    release = int(0.05 * sr)
    sustain = seg_end - pos - attack - release
    
    if attack > 0 and pos + attack <= seg_end:
        envelope[pos:pos + attack] *= np.linspace(0, 1, attack)
    if sustain > 0 and pos + attack + sustain <= seg_end:
        envelope[pos + attack:pos + attack + sustain] *= 1.0
    if release > 0 and pos + attack + sustain + release <= seg_end:
        envelope[pos + attack + sustain:seg_end] *= np.linspace(1, 0, release)
    
    # Add pause
    pause_end = min(pos + segment_len + pause_len, len(t))
    if pause_end - (seg_end) > 0:
        envelope[seg_end:pause_end] = 0
    
    pos = pause_end

voice_signal = voice_signal * envelope

# Apply high-pass filter (remove low rumble, enhance voice clarity)
b, a = scipy_signal.butter(4, 80, btype='high', fs=sr)
voice_signal = scipy_signal.filtfilt(b, a, voice_signal)

# Normalize to [-1, 1] with 0.75 amplitude
voice_signal = voice_signal / (np.max(np.abs(voice_signal)) + 1e-8)
voice_signal = voice_signal * 0.75

# Save to WAV in memory
wav_buffer = io.BytesIO()
sf.write(wav_buffer, voice_signal, sr, format='WAV', subtype='PCM_16')
wav_bytes = wav_buffer.getvalue()

# Convert to base64
audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')

print("=" * 80)
print("Generated 3-second realistic human voice-like test audio")
print("=" * 80)
print("\nVoice Characteristics:")
print("  ✓ Natural pitch contour (varies 110-150 Hz)")
print("  ✓ Multiple harmonics (voice source)")
print("  ✓ Vocal formants (F1, F2, F3 - vowel-like resonances)")
print("  ✓ Breathy noise (15-20% for realism)")
print("  ✓ Speech bursts with natural pauses")
print("  ✓ Attack/release envelope (realistic speech)")
print("  ✓ High-pass filtered (80Hz, removes rumble)")
print("=" * 80)
print("\nAudio Base64 (use this for testing):")
print(audio_base64)
print("\n" + "=" * 80)
print(f"Audio size: {len(wav_bytes)} bytes")
print(f"Duration: 3 seconds")
print(f"Sample rate: 16 kHz")
print("=" * 80)

# Also save to file for reference
sf.write('test_audio.wav', voice_signal, sr, subtype='PCM_16')
print("\nAlso saved to: test_audio.wav")
