@echo off
echo ========================================
echo OpenFlights Database Platform
echo ========================================
echo.
echo Starting web server...
echo Web Interface will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python scripts\web_app.py

pause
