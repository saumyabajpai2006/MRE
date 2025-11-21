# Deploying large model artifacts (free) — Hugging Face Hub guide

This project uses a large `similarity.joblib` artifact which is too big to keep in the git repo. The easiest free option is to host the file on the Hugging Face Hub as a public model repo and download it at build time on Render.

This guide covers two upload methods (CLI / Python), how to get a raw download URL, and how to set `MODEL_URL` for Render.

---

## 1) Create a Hugging Face repo (web)

1. Create a free account at https://huggingface.co/
2. Click your avatar -> `New repository` -> choose `Model` and make it `Public`.
3. Upload `recommender/models/similarity.joblib` using the web UI (drag & drop) — for large files, use the CLI or API below.

After upload, the file will be available at a URL like:

```
https://huggingface.co/<username>/<repo>/resolve/main/similarity.joblib
```

Use that full URL as `MODEL_URL` in Render.

---

## 2) Upload using `huggingface_hub` (Python API)

Recommended for large files. First, install and login locally:

```bash
pip install huggingface_hub
huggingface-cli login
```

Then upload via a short Python script (run from project root):

```python
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj="recommender/models/similarity.joblib",
    path_in_repo="similarity.joblib",
    repo_id="<username>/<repo>",
    token=os.environ.get('HF_TOKEN')
)
```

`HF_TOKEN` can be obtained from your Hugging Face account settings (Access Tokens).

After upload, the raw URL will be:

```
https://huggingface.co/<username>/<repo>/resolve/main/similarity.joblib
```

---

## 3) Upload using Git LFS (alternative)

If you prefer Git LFS, follow these steps (note quotas):

```bash
git lfs install
git clone https://huggingface.co/<username>/<repo>
cp recommender/models/similarity.joblib <repo>/
cd <repo>
git add similarity.joblib
git commit -m "Add similarity joblib"
git push
```

This will upload via LFS. Be mindful of bandwidth/storage limits.

---

## 4) Configure Render to download the model at build time

1. In Render dashboard, open your Service -> `Environment` and add an environment variable:
   - `MODEL_URL` = `https://huggingface.co/<username>/<repo>/resolve/main/similarity.joblib`

2. Ensure `requests` appears in `requirements.txt` (it already does in this repo).

3. The repo includes `scripts/download_models.py` which will download `MODEL_URL` into `recommender/models/` during build.

If you used `render.yaml` the build command now runs the downloader automatically. Otherwise, set your `Build Command` to:

```bash
pip install -r requirements.txt && python scripts/download_models.py
```

Or set `Start Command` to run the downloader before starting gunicorn (not recommended for production start times).

---

## 5) Verifying locally

Before pushing, you can test the downloader locally (recommended):

```bash
set MODEL_URL=https://huggingface.co/saumya1001/similarity/resolve/main/similarity.joblib
python scripts/download_models.py
```

Check that `recommender/models/similarity.joblib` is present.

---

## 6) Next steps (recommended)

- Consider reducing artifact size by storing top-k neighbors or a compact ANN index (Annoy / FAISS) — this is better long-term.
- Do not commit secrets to the repo; use Render environment variables for tokens.

If you want, I can also:
- Add a one-shot script to convert a dense similarity array into a `top_k` neighbor representation (you'd run it locally), or
- Add Hugging Face upload script that uses `huggingface_hub` directly (requires `pip install huggingface_hub`).
