# Variáveis para ambiente de produção

environment = "production"
aws_region = "us-east-1"

vpc_cidr = "10.0.0.0/16"
public_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnets = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

db_name = "licitrix_prod"
db_username = "licitrix"
# db_password deve ser definido via variável de ambiente ou secrets

app_image = "licitrix/app:latest"
app_port = 8000

s3_bucket_name = "licitrix-prod-files"
domain_name = "licitrix.com"

# As chaves sensíveis devem ser definidas via variáveis de ambiente
# django_secret_key
# openai_api_key
# enotas_api_key

app_name = "licitrix"
