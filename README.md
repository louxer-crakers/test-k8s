# k8s-python-services

Minimal Python frontend and backend architecture designed for Kubernetes, communicating over public DNS.

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions CI/CD for Amazon EKS
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── README.md              # Backend docs and env specifications
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/
│   │   └── index.html
│   └── README.md              # Frontend docs and env specifications
├── .gitignore
└── README.md
```

## 1. Containerization (Dockerfile Requirements)

Dockerfiles are not pre-packaged. You must create them manually inside each service directory before building images.

### Backend (`backend/Dockerfile`)
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

### Frontend (`frontend/Dockerfile`)
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

### Build and Push
Replace `<REGISTRY>` with your Docker Hub username or container registry:
```bash
docker build -t <REGISTRY>/backend:v1 ./backend
docker push <REGISTRY>/backend:v1

docker build -t <REGISTRY>/frontend:v1 ./frontend
docker push <REGISTRY>/frontend:v1
```

If using local Minikube:
```bash
minikube image load <REGISTRY>/backend:v1
minikube image load <REGISTRY>/frontend:v1
```

---

## 2. Kubernetes Requirements & Specifications

Kubernetes manifests are intentionally not included. You must write the manifests (`Deployment` and `Service` only) according to the specifications below:

### Architecture & Public DNS Communication
Frontend and backend do **not** use internal cluster DNS names (`http://backend-service:5000`). Instead, they communicate via **Public DNS**:
- The browser fetches API endpoints directly from the public DNS address assigned to the backend.
- The frontend pod also uses the public DNS address for server-side verification.
- Backend has CORS enabled to accept requests from any origin/domain.
- DNS names can be:
  - Different domains: Frontend on `http://app.domain.com`, Backend on `http://api.domain.com:5000`.
  - Same domain, different ports: Frontend on `http://domain.com:8080`, Backend on `http://domain.com:5000`.
  - Public NodePort/LoadBalancer IP for local clusters.

### A. Backend Kubernetes Specification
Create manifests for Backend Deployment and Service:

1. **Deployment (`kind: Deployment`)**:
   - `replicas`: At least `2`
   - `image`: `<REGISTRY>/backend:v1`
   - `containerPort`: `5000`
   - `env`: Check [backend/README.md](backend/README.md) for required/optional variables (`PORT`, `APP_NAME`, `ENVIRONMENT`).
   - `livenessProbe` & `readinessProbe`: HTTP GET to `/healthz` on port `5000`.
   - Resource requests and limits (recommended: 50m CPU / 64Mi RAM request).

2. **Service (`kind: Service`)**:
   - `type`: `LoadBalancer` (or `NodePort` depending on cluster setup).
   - `port`: `5000`
   - `targetPort`: `5000`
   - `selector`: Must match backend deployment pod labels (`app: backend`).

### B. Frontend Kubernetes Specification
Create manifests for Frontend Deployment and Service:

1. **Deployment (`kind: Deployment`)**:
   - `replicas`: At least `2`
   - `image`: `<REGISTRY>/frontend:v1`
   - `containerPort`: `8080`
   - `env`: Check [frontend/README.md](frontend/README.md) for variable specifications.
     - **Mandatory variable**: `BACKEND_PUBLIC_URL` must point to the Backend Public DNS / external IP (e.g. `http://api.example.com:5000`).
   - `livenessProbe` & `readinessProbe`: HTTP GET to `/healthz` on port `8080`.
   - Resource requests and limits (recommended: 50m CPU / 64Mi RAM request).

2. **Service (`kind: Service`)**:
   - `type`: `LoadBalancer` (or `NodePort`).
   - `port`: `8080`
   - `targetPort`: `8080`
   - `selector`: Must match frontend deployment pod labels (`app: frontend`).

---

## 3. Environment Variables Reference

Detailed descriptions and requirement statuses are documented inside each application folder:
- **Backend Environment Variables**: See [backend/README.md](backend/README.md)
- **Frontend Environment Variables**: See [frontend/README.md](frontend/README.md)

---

## 4. Verification

After applying your manifests:
1. Verify pod status:
   ```bash
   kubectl get pods -o wide
   ```
2. Verify external public endpoint:
   ```bash
   kubectl get svc -o wide
   ```
3. Open the Frontend external URL in your browser and click **Test Client** and **Test Server** to verify public DNS communication.

---

## 5. CI/CD: Deploy to Amazon EKS (GitHub Actions)

Workflow at `.github/workflows/deploy.yml`:
1. Authenticates to AWS using credentials and session token.
2. Logs into Amazon ECR.
3. Builds and pushes `backend:latest` and `frontend:latest`.
4. Connects to Amazon EKS and executes `kubectl rollout restart deployment/backend-deployment deployment/frontend-deployment` to pull the latest images.

### Required GitHub Secrets

Configure these under **Settings > Secrets and variables > Actions**:

| Secret Name | Required | Description |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | Yes | AWS IAM Access Key ID. |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS IAM Secret Access Key. |
| `AWS_SESSION_TOKEN` | Optional | AWS Session Token (for STS / temporary credentials). |
| `AWS_REGION` | Yes | Target AWS Region (e.g. `us-east-1`). |
| `EKS_CLUSTER_NAME` | Yes | Target Amazon EKS cluster name. |
