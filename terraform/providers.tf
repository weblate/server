# Install required providers
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.80.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.12.1"
    }
  }

  required_version = "~> 1.10.0"
}

# Configure AWS provider
provider "aws" {
  region = var.region
}
