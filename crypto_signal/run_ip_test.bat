@echo off
title IP Connection Test Runner
echo.
echo ========================================
echo    IP CONNECTION TEST RUNNER
echo ========================================
echo.

cd /d "%~dp0"

echo Starting IP connection tests...
echo.

python run_ip_test.py

echo.
echo Press any key to exit...
pause >nul 