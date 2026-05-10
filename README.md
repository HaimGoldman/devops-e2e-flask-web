# Flask Budget Manager

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Docker](https://img.shields.io/badge/docker-containerized-blue)
![Kubernetes](https://img.shields.io/badge/kubernetes-deployed-326ce5)
![Terraform](https://img.shields.io/badge/terraform-managed-623ce4)

A home budget management application used to showcase a production-grade **DevOps** lifecycle. The app tracks income and expenses stored in PostgreSQL, serving as the payload for a fully automated CI/CD pipeline, infrastructure as code, and comprehensive monitoring setup.

## 🚀 Key Capabilities

- **Automated Deployment**: Zero-downtime rolling updates via Kubernetes, including cloud deployment to AWS EKS.
- **Infrastructure as Code**: Reproducible environments using Terraform, including GitHub OIDC role provisioning.
- **Observability**: Built-in Prometheus metrics and Grafana dashboards.
- **Security**: Automated vulnerability scanning, secret management, and keyless AWS authentication via OIDC.

## 🛠️ Architecture

- **Application**: Python Flask with PostgreSQL 15 backend.
- **Orchestration**: Kubernetes (EKS & Minikube).
- **Package Management**: Helm (Charts for Dev/Prod/EKS).
- **Infrastructure**: AWS VPC & EKS managed via Terraform.
- **CI/CD**: GitHub Actions with OIDC-based AWS authentication.

## 🏁 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) (for local dev)
- [Kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/)

### 🏠 Local Development (Minikube)

1. **Start Minikube**:
   ```bash
   minikube start
   ```

2. **Create Namespace & Secrets**:
   ```bash
   kubectl create namespace dev
   kubectl create secret generic flask-db-secret \
     --from-literal=password=<DB_PASSWORD> -n dev
   kubectl create secret generic grafana-admin-secret \
     --from-literal=admin-password=<GRAFANA_PASSWORD> -n dev
   ```

3. **Deploy with Helm**:
   ```bash
   helm upgrade --install flask-web ./helm \
     -f helm/values-dev.yaml -n dev
   ```

4. **Access the Application**:
   ```bash
   minikube service flask-web-svc -n dev
   ```

### ☁️ Cloud Deployment (AWS EKS)

1. **Provision Infrastructure** (includes GitHub OIDC role):
   ```bash
   cd terraform
   export GITHUB_TOKEN=<your-github-pat>
   terraform init
   terraform apply
   ```
   This provisions the VPC, EKS cluster, and automatically sets the `AWS_ROLE_ARN` GitHub Secret.

2. **Configure Kubectl**:
   ```bash
   aws eks update-kubeconfig --region us-east-1 --name flask-web-dev
   ```

3. **Create Namespace & Secrets**:
   ```bash
   kubectl create namespace eks
   kubectl create secret generic flask-db-secret \
     --from-literal=password=<DB_PASSWORD> -n eks
   kubectl create secret generic grafana-admin-secret \
     --from-literal=admin-password=<GRAFANA_PASSWORD> -n eks
   ```

4. **Deploy**:
   ```bash
   helm upgrade --install flask-web ./helm \
     -f helm/values-eks.yaml -n eks
   ```

### 🔑 Required GitHub Secrets

| Secret | Description |
| :--- | :--- |
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token |
| `DB_PASSWORD` | PostgreSQL password |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password |
| `AWS_ROLE_ARN` | Set automatically by `terraform apply` |

GitHub variable (not secret): `DOCKER_REPOSITORY`, `EKS_CLUSTER_NAME`

## 📡 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Budget dashboard — shows balance, income, expenses, and transaction list. |
| `/transactions` | `POST` | Add a transaction (fields: `amount`, `category`, `description`, `type`). |
| `/transactions/<id>/delete` | `POST` | Delete a transaction by ID. |
| `/stats` | `GET` | Returns JSON summary: `total_income`, `total_expenses`, `balance`. |
| `/health` | `GET` | Health check returning status of app and DB connection. |
| `/metrics` | `GET` | Prometheus metrics scrape target. |

## 🧪 Testing

**Unit Tests**:
```bash
pytest tests/test_app.py
```

**Integration Tests**:
Handled automatically by the CI/CD pipeline in an ephemeral Minikube environment.

## 🛡️ DevOps Showcase

This project demonstrates a comprehensive **DevOps lifecycle**:

1. **Containerization**: Multi-stage Docker build optimized for size and security.
2. **Kubernetes**: Full deployment manifests including Ingress, Services, and blue/green strategy.
3. **Helm**: Parameterized charts for multi-environment (Dev/Prod/EKS) support.
4. **CI/CD with Cloud Deployment**: Automated pipeline for Build, Test, Scan, and Deploy — including keyless deployment to AWS EKS via GitHub OIDC (no stored credentials).
5. **Integration Testing**: Ephemeral test environments spun up dynamically in CI.
6. **IaC**: Terraform modules for VPC, EKS, and GitHub OIDC role provisioning.
7. **Monitoring**: Prometheus & Grafana dashboards for real-time insights.
8. **Zero-Downtime**: Rolling update strategy configured for seamless releases.
9. **Security**: Trivy vulnerability scanning, Kubernetes Secrets management, and resource limits on all containers.
