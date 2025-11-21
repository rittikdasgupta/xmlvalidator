# Deploy to Render.com (Free Tier)

Render.com offers free hosting for Flask applications with automatic deployments from GitHub.

## Steps

1. **Push your code to GitHub** (if not already done)

2. **Create a Render account**
   - Go to https://render.com
   - Sign up with your GitHub account

3. **Create a new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

4. **Configure the service:**
   - **Name**: `xml-validator` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or paid for more resources)

5. **Add Environment Variables** (optional):
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=0`

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Your app will be available at: `https://xml-validator.onrender.com` (or your custom domain)

## Notes

- Free tier spins down after 15 minutes of inactivity (first request may be slow)
- Free tier includes 750 hours/month
- Automatic HTTPS
- Automatic deployments on git push

## Create render.yaml (Optional)

Create `render.yaml` in your repo root for easier setup:

```yaml
services:
  - type: web
    name: xml-validator
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: 0
```

