# Variáveis para ambiente de desenvolvimento

environment = "development"
aws_region = "us-east-1"

vpc_cidr = "10.0.0.0/16"
public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnets = ["10.0.10.0/24", "10.0.11.0/24"]
availability_zones = ["us-east-1a", "us-east-1b"]

db_name = "licitrix_dev"
db_username = "licitrix"
db_password = "dev_password_change_me"

app_image = "licitrix/app:dev"
app_port = 8000

s3_bucket_name = "licitrix-dev-files"
domain_name = "dev.licitrix.local"

# Em desenvolvimento, usar valores padrão para as chaves sensíveis
django_secret_key = "dev-secret-key-change-in-production"
openai_api_key = "sk-dev-openai-key"
enotas_api_key = "dev-enotas-key"

app_name = "licitrix-dev"
