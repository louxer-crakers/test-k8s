# Backend API Service

Lightweight REST API service built with Flask and `flask-cors`.

## Purpose

Provides health checks, system diagnostic metadata, and in-memory message persistence. Serves as the upstream API consumed by the frontend over public DNS.

## Endpoints

- `GET /healthz` - Liveness and readiness probe target. Returns `{"status": "ok", "host": "<pod-hostname>"}`.
- `GET /api/info` - Service metadata (host, port, env, client IP, timestamp).
- `GET /api/messages` - Returns list of stored messages.
- `POST /api/messages` - Creates a new message payload (`{"text": "string"}`).

## Environment Variables

| Variable | Type | Default | Requirement | Description |
|---|---|---|---|---|
| `PORT` | integer | `5000` | Optional | Port on which the Flask server listens inside the container. |
| `APP_NAME` | string | `backend-api` | Optional | Service identifier reported in API responses and logs. |
| `ENVIRONMENT` | string | `production` | Optional | Runtime environment tag (e.g. `production`, `staging`). |

## Dockerfile Specification

Create `backend/Dockerfile` with the following definition:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```
