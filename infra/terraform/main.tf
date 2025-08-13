# Configuração principal do Terraform para Licitrix

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "licitrix-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "Licitrix"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC e Networking
module "vpc" {
  source = "./modules/vpc"
  
  environment = var.environment
  vpc_cidr   = var.vpc_cidr
  
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
  
  availability_zones = var.availability_zones
}

# RDS PostgreSQL
module "rds" {
  source = "./modules/rds"
  
  environment      = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  
  db_name     = var.db_name
  db_username = var.db_username
  db_password = var.db_password
  
  depends_on = [module.vpc]
}

# ElastiCache Redis
module "redis" {
  source = "./modules/redis"
  
  environment      = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  
  depends_on = [module.vpc]
}

# ECS Fargate
module "ecs" {
  source = "./modules/ecs"
  
  environment      = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  public_subnets  = module.vpc.public_subnets
  
  app_image = var.app_image
  app_port  = var.app_port
  
  depends_on = [module.vpc, module.rds, module.redis]
}

# S3 para arquivos
module "s3" {
  source = "./modules/s3"
  
  environment = var.environment
  bucket_name = var.s3_bucket_name
}

# CloudFront para CDN
module "cloudfront" {
  source = "./modules/cloudfront"
  
  environment = var.environment
  s3_bucket  = module.s3.bucket_id
  
  depends_on = [module.s3]
}

# SES para e-mails
module "ses" {
  source = "./modules/ses"
  
  environment = var.environment
  domain     = var.domain_name
}

# Secrets Manager
module "secrets" {
  source = "./modules/secrets"
  
  environment = var.environment
  
  secrets = {
    django_secret_key = var.django_secret_key
    openai_api_key    = var.openai_api_key
    enotas_api_key    = var.enotas_api_key
  }
}

# CloudWatch para monitoramento
module "monitoring" {
  source = "./modules/monitoring"
  
  environment = var.environment
  app_name   = var.app_name
}
