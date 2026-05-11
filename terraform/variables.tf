variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "flask-web"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

variable "eks_cluster_version" {
  description = "EKS cluster version"
  type        = string
  default     = "1.29"
}

variable "eks_node_instance_types" {
  description = "EKS node instance types"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "eks_node_desired_size" {
  description = "Desired number of EKS nodes"
  type        = number
  default     = 2
}

variable "eks_node_min_size" {
  description = "Minimum number of EKS nodes"
  type        = number
  default     = 1
}

variable "eks_node_max_size" {
  description = "Maximum number of EKS nodes"
  type        = number
  default     = 3
}

variable "github_repo" {
  description = "GitHub repo in format OWNER/REPO for OIDC trust policy"
  type        = string
  default     = "HaimGoldman/devops-e2e-flask-web"
}

variable "github_owner" {
  description = "GitHub organization or username"
  type        = string
  default     = "HaimGoldman"
}

variable "github_repo_name" {
  description = "GitHub repository name (without owner prefix)"
  type        = string
  default     = "devops-e2e-flask-web"
}

variable "github_token" {
  description = "GitHub personal access token for managing repository secrets"
  type        = string
  sensitive   = true
}

variable "allowed_cidr_blocks" {
  description = "CIDRs allowed to reach the EKS public endpoint. Override in terraform.tfvars with your IP."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
