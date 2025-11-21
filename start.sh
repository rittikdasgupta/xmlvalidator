#!/bin/bash
# Startup script for XML Validator

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if gunicorn is installed
if command -v gunicorn &> /dev/null; then
    echo "Starting XML Validator with Gunicorn..."
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
else
    echo "Gunicorn not found. Starting with Flask development server..."
    echo "For production, install gunicorn: pip install gunicorn"
    python app.py
fi

