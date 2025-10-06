#!/bin/bash

echo "========================================"
echo "OpenFlights Database Platform"
echo "========================================"
echo ""
echo "Starting web server..."
echo "Web Interface: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"

if command -v python3 &> /dev/null; then
    python3 scripts/web_app.py
else
    python scripts/web_app.py
fi
