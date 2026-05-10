provider "aws" {
  region = var.aws_region
}

data "aws_secretsmanager_secret_value" "github_token" {
  secret_id = "github-token"
}

provider "github" {
  owner = var.github_owner
  token = data.aws_secretsmanager_secret_value.github_token.secret_string
}

data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}
