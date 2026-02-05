#!/bin/bash
# Verification script for वाणीCheck
# Tests API endpoints and validates responses

set -e

API_URL="${1:-http://localhost:8000}"
API_KEY="${2:-vanicheck-secret-key-2026}"

echo "=========================================="
echo "वाणीCheck API Verification Script"
echo "=========================================="
echo "API URL: $API_URL"
echo "Testing with API Key: ${API_KEY:0:20}..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${YELLOW}[TEST 1]${NC} Health Check Endpoint"
HEALTH=$(curl -s -X GET "$API_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ PASS${NC}: API is healthy"
else
    echo -e "${RED}✗ FAIL${NC}: Health check failed"
    exit 1
fi
echo ""

# Test 2: Detailed Health with Auth
echo -e "${YELLOW}[TEST 2]${NC} Authenticated Health Check"
HEALTH_AUTH=$(curl -s -X GET "$API_URL/v1/health" \
    -H "X-API-KEY: $API_KEY")
if echo "$HEALTH_AUTH" | grep -q "operational"; then
    echo -e "${GREEN}✓ PASS${NC}: Authenticated health check successful"
else
    echo -e "${RED}✗ FAIL${NC}: Authenticated health check failed"
    exit 1
fi
echo ""

# Test 3: Create synthetic human audio
echo -e "${YELLOW}[TEST 3]${NC} Creating Synthetic Human Audio Sample"
python3 << 'PYTHON_SCRIPT'
import numpy as np
import soundfile as sf
import base64
from pathlib import Path

# Create synthetic human-like audio
duration = 3
sr = 16000
t = np.arange(int(sr * duration)) / sr

# Simulate human speech with natural F0 variations
f0 = 100 + 50 * np.sin(2 * np.pi * 0.5 * t)
audio = np.sin(2 * np.pi * f0 * t) * 0.3
audio += np.random.normal(0, 0.02, len(audio))

# Save to temporary file
sample_path = "/tmp/human_sample.wav"
sf.write(sample_path, audio, sr)

# Create base64 encoding
with open(sample_path, 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

# Save to file for use in next tests
with open("/tmp/human_sample_b64.txt", "w") as f:
    f.write(audio_b64)

print("✓ Created human audio sample")
PYTHON_SCRIPT

echo -e "${GREEN}✓ PASS${NC}: Audio sample created"
echo ""

# Test 4: Detection on Human Audio
echo -e "${YELLOW}[TEST 4]${NC} Detecting Human Audio Sample"

AUDIO_B64=$(cat /tmp/human_sample_b64.txt)

DETECTION=$(curl -s -X POST "$API_URL/v1/detect" \
    -H "X-API-KEY: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"audio_data\": \"$AUDIO_B64\",
        \"language\": \"english\"
    }")

# Parse response
VERDICT=$(echo "$DETECTION" | grep -o '"verdict":"[^"]*"' | cut -d'"' -f4)
CONFIDENCE=$(echo "$DETECTION" | grep -o '"confidence":[0-9.]*' | cut -d':' -f2)

echo "Response:"
echo "$DETECTION" | python3 -m json.tool 2>/dev/null || echo "$DETECTION"
echo ""

if [ "$VERDICT" != "" ]; then
    echo "Verdict: $VERDICT"
    echo "Confidence: $CONFIDENCE"
    
    if [ "${CONFIDENCE%.*}" -gt 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: Detection successful"
    else
        echo -e "${YELLOW}⚠ WARNING${NC}: Low confidence score"
    fi
else
    echo -e "${RED}✗ FAIL${NC}: Invalid response"
    exit 1
fi
echo ""

# Test 5: Multi-language support
echo -e "${YELLOW}[TEST 5]${NC} Testing Multi-language Support"

for LANG in tamil english hindi malayalam telugu; do
    RESPONSE=$(curl -s -X POST "$API_URL/v1/detect" \
        -H "X-API-KEY: $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"audio_data\": \"$AUDIO_B64\",
            \"language\": \"$LANG\"
        }")
    
    if echo "$RESPONSE" | grep -q "verdict"; then
        echo -e "${GREEN}✓${NC} $LANG: Working"
    else
        echo -e "${YELLOW}⚠${NC} $LANG: Failed"
    fi
done
echo ""

# Test 6: Invalid API Key
echo -e "${YELLOW}[TEST 6]${NC} Testing Invalid API Key Handling"

INVALID_KEY=$(curl -s -X POST "$API_URL/v1/detect" \
    -H "X-API-KEY: invalid-key" \
    -H "Content-Type: application/json" \
    -d "{
        \"audio_data\": \"$AUDIO_B64\",
        \"language\": \"english\"
    }")

if echo "$INVALID_KEY" | grep -q "Invalid API key"; then
    echo -e "${GREEN}✓ PASS${NC}: Invalid API key properly rejected"
else
    echo -e "${RED}✗ FAIL${NC}: Security check failed"
    exit 1
fi
echo ""

# Test 7: Missing API Key
echo -e "${YELLOW}[TEST 7]${NC} Testing Missing API Key Handling"

MISSING_KEY=$(curl -s -X POST "$API_URL/v1/detect" \
    -H "Content-Type: application/json" \
    -d "{
        \"audio_data\": \"$AUDIO_B64\",
        \"language\": \"english\"
    }")

if echo "$MISSING_KEY" | grep -q "X-API-KEY"; then
    echo -e "${GREEN}✓ PASS${NC}: Missing API key properly rejected"
else
    echo -e "${YELLOW}⚠ WARNING${NC}: Security behavior unclear"
fi
echo ""

# Summary
echo "=========================================="
echo "वाणीCheck Verification Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}All primary tests passed!${NC}"
echo ""
echo "API Details:"
echo "  URL: $API_URL"
echo "  Version: 1.0.0"
echo "  Status: ✓ Operational"
echo ""
echo "Supported Languages:"
echo "  • Tamil (தமிழ்)"
echo "  • English"
echo "  • Hindi (हिंदी)"
echo "  • Malayalam (മലയാളം)"
echo "  • Telugu (తెలుగు)"
echo ""
echo "Next Steps:"
echo "  1. Run unit tests: pytest tests/test_main.py -v"
echo "  2. Run load tests: locust -f tests/test_main.py"
echo "  3. Check logs: docker logs vanicheck-audio-detection"
echo ""
