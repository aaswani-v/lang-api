// Configuration
const API_ENDPOINT = 'https://lang-api-production.up.railway.app/v1/detect';
const API_KEY = 'vanicheck-secret-key-2026';

let selectedFile = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const audioInput = document.getElementById('audioInput');
const languageSelect = document.getElementById('language');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultCard = document.getElementById('resultCard');
const closeResultBtn = document.getElementById('closeResultBtn');
const loadingOverlay = document.getElementById('loadingOverlay');

// Upload Area Events
uploadArea.addEventListener('click', () => audioInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

audioInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// File Selection Handler
function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/webm', 'audio/flac'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(wav|mp3|ogg|webm|flac)$/i)) {
        showError('Please select a valid audio file (WAV, MP3, OGG, WebM, FLAC)');
        return;
    }

    // Validate file size (30MB max)
    const maxSize = 30 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File size exceeds 30MB limit');
        return;
    }

    selectedFile = file;
    uploadArea.innerHTML = `
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <p class="upload-text">${file.name}</p>
        <p class="upload-hint">${(file.size / 1024 / 1024).toFixed(2)} MB</p>
    `;
    uploadArea.style.borderColor = 'var(--success)';
    analyzeBtn.disabled = false;
}

// Analyze Button
analyzeBtn.addEventListener('click', analyzeAudio);

// Close Result
closeResultBtn.addEventListener('click', () => {
    resultCard.style.display = 'none';
});

// Main Analysis Function
async function analyzeAudio() {
    if (!selectedFile) {
        showError('Please select an audio file');
        return;
    }

    try {
        // Show loading
        loadingOverlay.style.display = 'flex';
        analyzeBtn.disabled = true;

        // Read file and convert to base64
        const base64Audio = await fileToBase64(selectedFile);

        // Prepare request
        const payload = {
            audio_data: base64Audio,
            language: languageSelect.value,
            filename: selectedFile.name
        };

        // Call API
        const startTime = Date.now();
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
        const startRecordBtn = document.getElementById('startRecordBtn');
        const stopRecordBtn = document.getElementById('stopRecordBtn');
        const recordStatus = document.getElementById('recordStatus');
        const recordedAudio = document.getElementById('recordedAudio');

        let mediaRecorder = null;
        let recordedChunks = [];
                'Content-Type': 'application/json',
                'X-API-KEY': API_KEY,
                'Authorization': `Bearer ${API_KEY}`
            },
            body: JSON.stringify(payload)
        });

        const processingTime = ((Date.now() - startTime) / 1000).toFixed(2);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();

        // Hide loading
        loadingOverlay.style.display = 'none';

        // Display results
        displayResults(result, processingTime);

    } catch (error) {
        loadingOverlay.style.display = 'none';
        analyzeBtn.disabled = false;
        showError(`Error: ${error.message}`);
    }
}

// Convert File to Base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            // Remove data:audio/...; base64, prefix if present
            const base64 = reader.result.split(',')[1] || reader.result;
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Get Audio Format from Filename
function getAudioFormat(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const formatMap = {
        'wav': 'wav',
        'mp3': 'mp3',
        'ogg': 'ogg',
        'webm': 'webm',
        'flac': 'flac'
    };
    return formatMap[ext] || 'wav';
}

// Display Results
function displayResults(result, processingTime) {
    // Extract data

        // Recording Controls
        if (startRecordBtn && stopRecordBtn) {
            startRecordBtn.addEventListener('click', startRecording);
            stopRecordBtn.addEventListener('click', stopRecording);
        }
    const isFake = result.is_deepfake || false;
    const confidence = (result.confidence * 100).toFixed(1);
    const language = result.language_detected || languageSelect.value;

    // Determine verdict
    let verdictType, verdictText;
    if (confidence > 70) {
        verdictType = 'deepfake';
        verdictText = 'High probability of deepfake audio detected. Treat with caution.';
    } else if (confidence > 40) {
        verdictType = 'uncertain';
        verdictText = 'Uncertain results. Manual review recommended.';
    } else {
        verdictType = 'genuine';
        verdictText = 'Audio appears to be authentic with high confidence.';
    }

    // Update UI
    document.getElementById('confidenceFill').style.width = `${confidence}%`;
    document.getElementById('confidenceValue').textContent = `${confidence}%`;

    const badge = document.getElementById('verdictBadge');
    badge.className = `verdict-badge ${verdictType}`;
    badge.textContent = verdictType.charAt(0).toUpperCase() + verdictType.slice(1);

    document.getElementById('verdictText').textContent = verdictText;

    document.getElementById('detailConfidence').textContent = `${confidence}% Confidence`;
    document.getElementById('detailDuration').textContent = result.duration_seconds ? `${result.duration_seconds.toFixed(2)}s` : 'N/A';
    document.getElementById('detailLanguage').textContent = language.charAt(0).toUpperCase() + language.slice(1);
    document.getElementById('detailTime').textContent = `${processingTime}s`;

    // Explanation
    let explanation = '';
    if (verdictType === 'deepfake') {
        explanation = 'The audio exhibits characteristics commonly found in AI-generated or synthesized speech. This could indicate voice cloning, text-to-speech synthesis, or voice conversion technology.';
    } else if (verdictType === 'uncertain') {
        explanation = 'The analysis detected some unusual patterns but cannot definitively classify the audio. Factors like background noise, accents, or recording quality may affect accuracy.';
    } else {
        explanation = 'The audio analysis did not detect significant signs of deepfake manipulation. This appears to be naturally recorded or authentic human speech.';
    }
    document.getElementById('explanationText').textContent = explanation;

    // Show result card
    resultCard.style.display = 'block';
    analyzeBtn.disabled = false;

    // Scroll to results
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Error Handler
function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--danger);
        color: white;
        async function startRecording() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                showError('Recording is not supported in this browser. Please upload a file instead.');
                return;
            }

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                recordedChunks = [];

                const options = MediaRecorder.isTypeSupported('audio/webm')
                    ? { mimeType: 'audio/webm' }
                    : MediaRecorder.isTypeSupported('audio/ogg')
                        ? { mimeType: 'audio/ogg' }
                        : {};

                mediaRecorder = new MediaRecorder(stream, options);

                mediaRecorder.ondataavailable = (event) => {
                    if (event.data && event.data.size > 0) {
                        recordedChunks.push(event.data);
                    }
                };

                mediaRecorder.onstop = () => {
                    const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
                    const fileName = `recording-${Date.now()}.${blob.type.includes('ogg') ? 'ogg' : 'webm'}`;
                    const file = new File([blob], fileName, { type: blob.type });

                    selectedFile = file;
                    uploadArea.innerHTML = `
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        <p class="upload-text">${file.name}</p>
                        <p class="upload-hint">Recorded from mic</p>
                    `;
                    uploadArea.style.borderColor = 'var(--success)';
                    analyzeBtn.disabled = false;

                    recordedAudio.src = URL.createObjectURL(blob);
                    recordedAudio.style.display = 'block';

                    recordStatus.textContent = 'Recording saved. You can analyze it now.';
                    recordStatus.classList.remove('recording');
                };

                mediaRecorder.start();
                startRecordBtn.disabled = true;
                stopRecordBtn.disabled = false;
                analyzeBtn.disabled = true;
                recordStatus.textContent = 'Recording... Speak now.';
                recordStatus.classList.add('recording');
            } catch (error) {
                showError('Microphone access denied or unavailable.');
            }
        }

        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach((track) => track.stop());
            }
            startRecordBtn.disabled = false;
            stopRecordBtn.disabled = true;
        }
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 999;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => errorDiv.remove(), 300);
    }, 5000);
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            opacity: 0;
            transform: translateX(400px);
        }
    }
`;
document.head.appendChild(style);
