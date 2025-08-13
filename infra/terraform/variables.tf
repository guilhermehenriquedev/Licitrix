# Variáveis do Terraform para Licitrix

variable "aws_region" {
  description = "Região AWS para deploy"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente de deploy"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR da VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "CIDRs das subnets públicas"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  description = "CIDRs das subnets privadas"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "availability_zones" {
  description = "Zonas de disponibilidade"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_name" {
  description = "Nome do banco de dados"
  type        = string
  default     = "licitrix"
}

variable "db_username" {
  description = "Usuário do banco de dados"
  type        = string
  default     = "licitrix"
}

variable "db_password" {
  description = "Senha do banco de dados"
  type        = string
  sensitive   = true
}

variable "app_image" {
  description = "Imagem Docker da aplicação"
  type        = string
  default     = "licitrix/app:latest"
}

variable "app_port" {
  description = "Porta da aplicação"
  type        = number
  default     = 8000
}

variable "s3_bucket_name" {
  description = "Nome do bucket S3"
  type        = string
  default     = "licitrix-files"
}

variable "domain_name" {
  description = "Nome do domínio"
  type        = string
  default     = "licitrix.com"
}

variable "django_secret_key" {
  description = "Chave secreta do Django"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "Chave da API OpenAI"
  type        = string
  sensitive   = true
}

variable "enotas_api_key" {
  description = "Chave da API eNotas"
  type        = string
  sensitive   = true
}

variable "app_name" {
  description = "Nome da aplicação"
  type        = string
  default     = "licitrix"
}
