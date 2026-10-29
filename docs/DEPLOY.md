# Inquest Demo Deployment and Execution Guide

This document describes how to install, run, and test Inquest locally, execute via Docker containers, and deploy to cloud platforms (Render and Fly.io) with zero required credentials.

---

## 1. Local Run in 3 Commands

From the repository root with Python 3.12:

```bash
# 1. Install editable package and dependencies
pip install -e . && pip install fastapi uvicorn httpx playwright

# 2. Run the interactive web server on port 8000
uvicorn demo.api:app --host 0.0.0.0 --port 8000

# 3. In another terminal, run the complete verification suite
pytest
```

Once running, navigate to:
- Landing Page (Strata AI Hero Spec): `http://localhost:8000/`
- Interactive Incident Investigation Demo: `http://localhost:8000/demo`
- Comprehensive Benchmark Results: `http://localhost:8000/results`
- Limitations & Boundaries: `http://localhost:8000/limitations`
- Healthcheck: `http://localhost:8000/health`

---

## 2. Containerized Execution (Docker & Docker Compose)

### Using Docker Directly

```bash
# Build the multi-stage image
docker build -t inquest-demo .

# Run the container as non-root user on port 8000
docker run -p 8000:8000 --rm --name inquest-demo inquest-demo

# Verify health
curl -f http://localhost:8000/health
```

### Using Docker Compose

```bash
# Start container in background
docker compose up -d

# Check health and logs
docker compose ps
docker compose logs -f

# Stop container
docker compose down
```

---

## 3. Cloud Deployment (Zero Credentials)

Both Render and Fly.io configurations are configured with `autoDeploy: false` to ensure no unexpected automated deployments occur.

### A. Render (Free Tier Web Service)

1. Connect your git repository to Render.
2. Select **New Web Service** and choose **Blueprint** (pointing to `render.yaml`).
3. Set optional environment variables in the Render Dashboard under **Environment**:
   - `DEMO_BASIC_AUTH_USERNAME`: desired username for basic auth protection.
   - `DEMO_BASIC_AUTH_PASSWORD`: desired password for basic auth protection.
4. Click **Create Web Service**. Render builds the multi-stage Docker container and starts the server with healthcheck probing `/health`.

### B. Fly.io (512MB Shared CPU)

1. Install the Fly CLI: `curl -L https://fly.io/install.sh | sh`.
2. Launch the application without deploying immediately:
   ```bash
   fly launch --no-deploy --config fly.toml
   ```
3. Set optional HTTP basic authentication secrets:
   ```bash
   fly secrets set DEMO_BASIC_AUTH_USERNAME=admin DEMO_BASIC_AUTH_PASSWORD=your_secure_password
   ```
4. Deploy the application:
   ```bash
   fly deploy
   ```
   Fly starts a single shared-cpu-1x VM with 512MB RAM and automatically stops the machine when idle (`auto_stop_machines = "stop"`).

---

## 4. Security Configuration

- **Security Headers & Strict CSP:** The API middleware automatically attaches strict `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Referrer-Policy: strict-origin-when-cross-origin`.
- **CORS:** Cross-Origin Resource Sharing is disabled by default.
- **Rate Limiting:** Sliding-window rate limiter restricts requests to 120 per minute per IP, responding with `HTTP 429 Too Many Requests`.
- **Payload Limit:** Request bodies larger than 1 MB are rejected with `HTTP 413`.
- **Optional Basic Auth:** Setting `DEMO_BASIC_AUTH_USERNAME` and `DEMO_BASIC_AUTH_PASSWORD` locks all routes except `/health` behind standard HTTP Basic Auth.
