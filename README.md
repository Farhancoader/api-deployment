# Effective Config API

FastAPI implementation of `GET /effective-config` with precedence:

1. Hardcoded defaults
2. `config.development.yaml`
3. `.env` (`NUM_WORKERS` aliases to `workers`)
4. OS environment variables prefixed with `APP_`
5. Repeated `?set=key=value` query overrides

The `api_key` is always returned as `"****"`. CORS is enabled for browser requests.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
uvicorn main:app --host 0.0.0.0 --port 8000
```

Test:

```text
http://localhost:8000/effective-config
http://localhost:8000/effective-config?set=port=9000&set=debug=true
```

## Deploy

Deploy this directory as a Python web service on a host that supports persistent web processes. Build command: `pip install -r requirements.txt`. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT` (use the platform's port variable). Ensure `config.development.yaml` is included in the deployed files. The host's environment variables become the OS-env layer; keep `.env` as a file only if you specifically need that layer in production.
# api-deployment
