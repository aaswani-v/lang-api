@echo off
REM Start वाणीCheck API with correct Python version
title वाणीCheck - Audio Deepfake Detection API

REM Use Python 3.13
set PYTHON=C:\Users\Ash\AppData\Local\Programs\Python\Python313\python.exe

echo ====================================
echo वाणीCheck API Server
echo ====================================
echo.
echo Python: %PYTHON%
echo.

REM Start the server
echo Starting FastAPI server on http://localhost:8000
echo.
echo Access API Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

%PYTHON% main.py

pause
