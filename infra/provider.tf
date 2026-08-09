provider "aws" {
  region  = var.aws_region
  profile = "caro-terraform-s3-process"

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}