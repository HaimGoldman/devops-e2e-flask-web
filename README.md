# 📊 Flask Visit Counter Service

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Docker](https://img.shields.io/badge/docker-containerized-blue)
![Kubernetes](https://img.shields.io/badge/kubernetes-deployed-326ce5)
![Terraform](https://img.shields.io/badge/terraform-managed-623ce4)

A simple demonstration application used to showcase a production-grade **DevOps** lifecycle. The app itself is a basic visit counter, serving as the payload for the fully automated CI/CD pipeline, infrastructure as code, and comprehensive monitoring setup.

## 🚀 Key Capabilities

- **Automated Deployment**: Zero-downtime rolling updates via Kubernetes.
- **Infrastructure as Code**: Reproducible environments using Terraform.
- **Observability**: Built-in Prometheus metrics and Grafana dashboards.
- **Security**: Automated vulnerability scanning and secret management.

## 🛠️ Architecture

- **Application**: Python Flask (Stateless).
- **Database**: PostgreSQL 15 (Stateful).
- **Orchestration**: Kubernetes (EKS & Minikube).
- **Package Management**: Helm (Charts for Dev/Prod).
- **Infrastructure**: AWS VPC & EKS managed via Terraform.
- **CI/CD**: GitHub Actions.

## 🏁 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) (for local dev)
- [Kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/)

### 🏠 Local Development (Minikube)

1.  **Start Minikube**:
    ```bash
    minikube start
    ```

2.  **Create Namespace & Secret**:
    ```bash
    kubectl create namespace dev
    kubectl create secret generic flask-db-secret \
      --from-literal=password=<PASSWORD> \
      -n dev
    ```

3.  **Deploy with Helm**:
    ```bash
    helm upgrade --install flask-web ./helm \
      -f helm/values-dev.yaml \
      -n dev
    ```

4.  **Access the Application**:
    ```bash
    minikube service flask-web-svc -n dev
    ```

### ☁️ Cloud Deployment (AWS EKS)

1.  **Provision Infrastructure**:
    ```bash
    cd terraform
    terraform init
    terraform apply
    ```

2.  **Configure Kubectl**:
    ```bash
    aws eks update-kubeconfig --region us-east-1 --name flask-web-prod
    ```

3.  **Create Namespace & Secret**:
    ```bash
    kubectl create namespace prod
    kubectl create secret generic flask-db-secret \
      --from-literal=password=<PASSWORD> \
      -n prod
    ```

4.  **Deploy**:
    ```bash
    helm upgrade --install flask-web ./helm \
      -f helm/values-prod.yaml \
      -f helm/values-eks.yaml \
      -n dev
    ```

## 📡 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Logs a new visit and returns "Hello World!". |
| `/stats` | `GET` | Returns JSON statistics (hour, day, week, month counts). |
| `/health` | `GET` | Health check returning status of App and DB connection. |
| `/metrics` | `GET` | Prometheus metrics scrape target. |

## 🧪 Testing

**Unit Tests**:
```bash
pytest tests/test_app.py
```

**Integration Tests**:
Requires a running Kubernetes cluster.
```bash
# Handled automatically by CI/CD pipeline
```

## 🛡️ DevOps Showcase

This project was built to demonstrate a comprehensive **9-Step DevOps Roadmap**:

1.  **Containerization**: Multi-stage Docker build optimized for size and security.
2.  **Kubernetes**: Full deployment manifests including Ingress and Services.
3.  **Helm**: Parameterized charts for multi-environment (Dev/Prod) support.
4.  **CI/CD**: Automated pipeline for Build, Test, Scan, and Deploy.
5.  **Integration Testing**: Ephemeral test environments spun up dynamically in CI.
6.  **IaC**: Terraform modules for VPC and EKS provisioning.
7.  **Monitoring**: Prometheus & Grafana dashboards for real-time insights (see [MONITORING.md](./MONITORING.md)).
8.  **Zero-Downtime**: Rolling update strategy configured for seamless releases.
9.  **Security**: Trivy vulnerability scanning and Kubernetes Secrets management.

## 📄 Challenges & Solutions

Development involves trade-offs. Read about the technical decisions and challenges faced during this project in [CHALLENGES.md](./CHALLENGES.md).
