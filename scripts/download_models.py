import os
import sys
import requests
from urllib.parse import urlparse


def download_file(url: str, out_path: str):
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    total = resp.headers.get('content-length')
    total = int(total) if total is not None else None
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f"File already exists, skipping download: {out_path}")
        return
    print(f"Downloading {url} -> {out_path}")
    with open(out_path, 'wb') as f:
        downloaded = 0
        for chunk in resp.iter_content(chunk_size=8192):
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded * 100 / total
                print(f"\r{downloaded}/{total} bytes ({pct:.1f}%)", end="")
    if total:
        print()
    print(f"Saved: {out_path}")


def main():
    # Accept either MODEL_URL (single) or MODEL_URLS (comma-separated)
    model_url = os.environ.get('MODEL_URL')
    model_urls = os.environ.get('MODEL_URLS')

    if not model_url and not model_urls:
        print("No MODEL_URL or MODEL_URLS environment variable set; skipping model download.")
        return

    urls = []
    if model_url:
        urls.append(model_url.strip())
    if model_urls:
        for u in model_urls.split(','):
            u = u.strip()
            if u:
                urls.append(u)

    for url in urls:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            print(f"Cannot determine filename from URL: {url}")
            continue
        out_path = os.path.join('recommender', 'models', filename)
        try:
            download_file(url, out_path)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
