# XML Validator Web Application

A modern web application for validating and extracting XML files from ZIP archives. Built with Flask and featuring a clean, responsive user interface.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- 📦 Upload ZIP files via drag-and-drop or file browser
- 🔍 Automatic detection of XML files within ZIP archives
- 📄 Extract and view XML file contents
- 🎨 Modern, responsive UI following standard design guidelines
- ⚡ Fast and efficient processing
- 🛡️ Secure file handling with temporary storage

## Project Structure

```
xmlvalidator/
├── app.py                 # Flask web application
├── xmlvalidator.py        # Core XML validation module
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Stylesheet
    └── js/
        └── main.js       # JavaScript functionality
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd xmlvalidator
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   
   On Linux/Mac:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode

Run the application in development mode:

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

For production deployment, use a production WSGI server like Gunicorn:

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

   Or for a single worker:
   ```bash
   gunicorn -b 0.0.0.0:5000 app:app
   ```

## Deployment on Virtual Machine

### Option 1: Using systemd (Linux)

1. **Create a systemd service file** `/etc/systemd/system/xmlvalidator.service`:

   ```ini
   [Unit]
   Description=XML Validator Web Application
   After=network.target

   [Service]
   User=your-username
   WorkingDirectory=/path/to/xmlvalidator
   Environment="PATH=/path/to/xmlvalidator/venv/bin"
   ExecStart=/path/to/xmlvalidator/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

   [Install]
   WantedBy=multi-user.target
   ```

2. **Reload systemd and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable xmlvalidator
   sudo systemctl start xmlvalidator
   ```

3. **Check status:**
   ```bash
   sudo systemctl status xmlvalidator
   ```

### Option 2: Using Docker

1. **Create a Dockerfile:**

   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 5000

   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

2. **Build and run:**
   ```bash
   docker build -t xmlvalidator .
   docker run -d -p 5000:5000 --name xmlvalidator xmlvalidator
   ```

### Option 3: Using Nginx as Reverse Proxy

1. **Install Nginx:**
   ```bash
   sudo apt-get update
   sudo apt-get install nginx
   ```

2. **Create Nginx configuration** `/etc/nginx/sites-available/xmlvalidator`:

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable the site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/xmlvalidator /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Configuration

### Environment Variables

You can configure the application using environment variables:

- `FLASK_ENV`: Set to `production` for production mode
- `FLASK_DEBUG`: Set to `0` to disable debug mode
- `UPLOAD_FOLDER`: Custom upload folder path (default: system temp directory)
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 100MB)

### Example Configuration

Create a `.env` file or set environment variables:

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export MAX_CONTENT_LENGTH=104857600  # 100MB
```

## Usage

1. Open the web application in your browser
2. Drag and drop a ZIP file or click "Browse Files" to select one
3. (Optional) Enter a specific XML filename to extract
4. Click "Validate & Extract"
5. View the results including:
   - List of all extracted files
   - List of XML files found
   - Content of the specified XML file (if provided)

## API Endpoints

- `GET /` - Main web interface
- `POST /upload` - Upload and process ZIP file
- `GET /health` - Health check endpoint

## Security Considerations

- File uploads are limited to 100MB by default
- Only ZIP files are accepted
- Uploaded files are stored temporarily and automatically cleaned up
- Extracted files are stored in temporary directories and cleaned up after processing

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, change it in `app.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=False)
```

### Permission Errors

Ensure the application has write permissions to the temporary directory:

```bash
chmod 755 /tmp
```

### Firewall Configuration

If deploying on a VM, ensure the port is open:

```bash
sudo ufw allow 5000/tcp
```

## License

This project is provided as-is for use in your organization.

## Deployment Options

### ⚠️ GitHub Pages Limitation

**GitHub Pages cannot host this application** because it only serves static files, and this Flask app requires server-side processing (Python backend, file uploads, ZIP extraction).

### ✅ Recommended Free Hosting: Render.com

This Flask application can be easily deployed to **Render.com** (free tier available):

- **See [DEPLOY_RENDER.md](DEPLOY_RENDER.md)** for step-by-step instructions
- Free tier with automatic HTTPS
- Auto-deploys from GitHub
- Includes `render.yaml` for easy setup

**Other deployment options:**
- Your own server/VPS - See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions
- Other platforms: Railway, Fly.io, PythonAnywhere (manual setup required)

### GitHub Repository

This project is ready to be hosted on GitHub. To push to GitHub:

1. **Create a new repository on GitHub**
   - Go to https://github.com/new
   - Create a repository (e.g., `xml-validator`)

2. **Initialize git and push** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: XML Validator Web Application"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/xml-validator.git
   git push -u origin main
   ```

3. **What's included**:
   - ✅ All source code
   - ✅ Requirements file
   - ✅ Documentation
   - ✅ Deployment scripts
   - ❌ Virtual environment (excluded via .gitignore)
   - ❌ Test ZIP files (excluded via .gitignore)
   - ❌ Log files (excluded via .gitignore)

4. **Security Note**:
   - The `SECRET_KEY` is randomly generated on each run, so no secrets are committed
   - All sensitive files are excluded via `.gitignore`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is. Feel free to use and modify as needed.

## Support

For issues or questions, please open an issue on GitHub or contact your system administrator.

