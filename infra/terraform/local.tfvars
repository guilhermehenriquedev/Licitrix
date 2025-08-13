# Variáveis para ambiente de desenvolvimento local

environment = "local"
aws_region = "us-east-1"

vpc_cidr = "10.0.0.0/16"
public_subnets = ["10.0.1.0/24"]
private_subnets = ["10.0.10.0/24"]
availability_zones = ["us-east-1a"]

db_name = "licitrix_local"
db_username = "licitrix"
db_password = "licitrix"

app_image = "licitrix/app:local"
app_port = 8000

s3_bucket_name = "licitrix-local-files"
domain_name = "localhost"

# Em desenvolvimento local, usar valores padrão
django_secret_key = "local-secret-key-change-in-production"
openai_api_key = "sk-local-openai-key"
enotas_api_key = "local-enotas-key"

app_name = "licitrix-local"
