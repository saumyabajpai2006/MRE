# Environment Variables Reference

This document lists all environment variables used by the Movie Recommendation Engine app.

## Required for Production (Render)

| Variable | Purpose | Example / Default |
|----------|---------|-------------------|
| `PORT` | HTTP port for Flask/Gunicorn to listen on | `5000` (default if not set) |
| `MODEL_URL` | Public URL to download `similarity.joblib` from (Hugging Face Hub, etc.) | `https://huggingface.co/user/repo/resolve/main/similarity.joblib` |
| `TMDB_BEARER` | TMDB API Bearer token for movie data fetches | Your TMDB token (defaults to embedded token if not set) |
| `SECRET_KEY` | Flask secret key for session encryption | A strong random string (defaults to `supersecretmre` if not set) |

## Optional

| Variable | Purpose | Example / Default |
|----------|---------|-------------------|
| `FLASK_DEBUG` | Enable/disable Flask debug mode (set to `True` on local, `False` on Render) | `False` (default) |
| `MODEL_URLS` | Alternative: comma-separated list of model URLs (if downloading multiple artifacts) | `url1,url2,url3` |

---

## How to set on Render

1. Open your Render service dashboard.
2. Go to **Environment** (in the left sidebar).
3. Add each variable:
   - Click **Add Environment Variable**
   - Enter the **Key** (e.g., `PORT`)
   - Enter the **Value** (e.g., `5000` or your token)
   - Click **Save**

Example configuration for Render:
```
PORT=5000
MODEL_URL=https://huggingface.co/your-username/your-model-repo/resolve/main/similarity.joblib
TMDB_BEARER=eyJhbGc... (your TMDB token)
SECRET_KEY=your-super-secret-random-string-here
FLASK_DEBUG=False
```

---

## How to set locally (Windows cmd)

For local testing, set variables before running the app:

```cmd
set PORT=5000
set TMDB_BEARER=your_tmdb_token_here
set SECRET_KEY=your_secret_key_here
set FLASK_DEBUG=True
set MODEL_URL=https://your-hugging-face-url/similarity.joblib

python app.py
```

Or with Gunicorn (Render-like):
```cmd
python scripts/download_models.py
gunicorn app:app --bind 0.0.0.0:%PORT%
```

---

## Security Notes

- **Never commit secrets** to git (tokens, keys, passwords).
- Use Render's Environment settings to store sensitive values.
- The `TMDB_BEARER` token has a fallback embedded in the code for development; replace it in production.
- Generate a strong `SECRET_KEY` (e.g., `python -c "import secrets; print(secrets.token_urlsafe(32))"`) and store it in Render only.

---

## Checking variables at runtime

To verify environment variables are set correctly, you can inspect them in the app logs or add a debug endpoint. Render shows build & runtime logs in the dashboard.
