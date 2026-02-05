@echo off
REM Windows verification script for वाणीCheck

setlocal enabledelayedexpansion

set API_URL=%1
if "!API_URL!"=="" set API_URL=http://localhost:8000

set API_KEY=%2
if "!API_KEY!"=="" set API_KEY=vanicheck-secret-key-2026

echo.
echo ==========================================
echo वाणीCheck API Verification Script
echo ==========================================
echo API URL: !API_URL!
echo Testing with API Key: !API_KEY:~0,20!...
echo.

REM Test 1: Health Check
echo [TEST 1] Health Check Endpoint
curl -s -X GET "!API_URL!/health" | findstr /C:"healthy" >nul
if !errorlevel! equ 0 (
    echo [PASS] API is healthy
) else (
    echo [FAIL] Health check failed
    exit /b 1
)
echo.

REM Test 2: Authenticated Health
echo [TEST 2] Authenticated Health Check
curl -s -X GET "!API_URL!/v1/health" ^
    -H "X-API-KEY: !API_KEY!" | findstr /C:"operational" >nul
if !errorlevel! equ 0 (
    echo [PASS] Authenticated health check successful
) else (
    echo [FAIL] Authenticated health check failed
    exit /b 1
)
echo.

REM Test 3-7: Create test audio and run detection tests
echo [TEST 3-7] Running detection tests...
python.exe verify_api.py "!API_URL!" "!API_KEY!"
if !errorlevel! neq 0 (
    exit /b 1
)

echo.
echo ==========================================
echo वाणीCheck Verification Complete!
echo ==========================================
echo.
echo Status: [PASS] All primary tests passed!
echo.

endlocal
