# Frontend Web Service

Server-rendered web UI and proxy diagnostics built with Flask.

## Purpose

Renders the dashboard UI, displays pod/hostname metadata, and communicates with the backend API via public DNS (both client-side from the browser and server-side from the pod).

## Endpoints

- `GET /` - Main web dashboard interface.
- `GET /healthz` - Liveness and readiness probe target. Returns `{"status": "ok", "host": "<pod-hostname>"}`.
- `GET /api/ping-backend` - Server-side diagnostic endpoint testing HTTP reachability to `BACKEND_PUBLIC_URL`.

## Environment Variables

| Variable | Type | Default | Requirement | Description |
|---|---|---|---|---|
| `PORT` | integer | `8080` | Optional | Port on which the frontend server listens inside the container. |
| `APP_NAME` | string | `frontend-web` | Optional | Application title displayed on the dashboard UI. |
| `BACKEND_PUBLIC_URL` | string | `http://localhost:5000` | Required in K8s | Public DNS or external IP/URL of the backend API (e.g. `http://api.yourdomain.com:5000` or `http://yourdomain.com:5000`). Used by the browser and pod to send requests. |

## Dockerfile Specification

Create `frontend/Dockerfile` with the following definition:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
```
