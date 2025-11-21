# Quick Deployment Guide

## Quick Start (5 minutes)

### 1. On Your Virtual Machine

```bash
# Navigate to project directory
cd /path/to/xmlvalidator

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For production, install gunicorn
pip install gunicorn

# Start the application
./start.sh
```

### 2. Access the Application

Open your browser and navigate to:
- `http://your-vm-ip:5000` (if running directly)
- `http://your-domain.com` (if using Nginx reverse proxy)

## Production Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Gunicorn installed (`pip install gunicorn`)
- [ ] Firewall configured (port 5000 or 80/443)
- [ ] Application tested locally
- [ ] Systemd service configured (optional, for auto-start)
- [ ] Nginx reverse proxy configured (optional, for production)

## Common Commands

### Start Application
```bash
./start.sh
```

### Start with Gunicorn (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Start with Flask (Development)
```bash
python app.py
```

### Check if Application is Running
```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

### Permission Denied
```bash
# Make script executable
chmod +x start.sh

# Check file permissions
ls -la
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Testing the Application

1. Upload the included `xml_samples.zip` file
2. Try extracting without specifying a target XML (lists all files)
3. Try extracting with a specific XML filename (e.g., `sample1.xml`)

## Next Steps

- Configure systemd service for auto-start on boot
- Set up Nginx reverse proxy for HTTPS
- Configure firewall rules
- Set up monitoring and logging

