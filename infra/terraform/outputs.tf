# Outputs do Terraform para Licitrix

output "vpc_id" {
  description = "ID da VPC criada"
  value       = module.vpc.vpc_id
}

output "public_subnets" {
  description = "IDs das subnets públicas"
  value       = module.vpc.public_subnets
}

output "private_subnets" {
  description = "IDs das subnets privadas"
  value       = module.vpc.private_subnets
}

output "rds_endpoint" {
  description = "Endpoint do RDS PostgreSQL"
  value       = module.rds.endpoint
}

output "redis_endpoint" {
  description = "Endpoint do ElastiCache Redis"
  value       = module.redis.endpoint
}

output "ecs_cluster_name" {
  description = "Nome do cluster ECS"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "Nome do serviço ECS"
  value       = module.ecs.service_name
}

output "alb_dns_name" {
  description = "DNS do Application Load Balancer"
  value       = module.ecs.alb_dns_name
}

output "s3_bucket_name" {
  description = "Nome do bucket S3"
  value       = module.s3.bucket_name
}

output "cloudfront_domain" {
  description = "Domínio do CloudFront"
  value       = module.cloudfront.domain_name
}

output "ses_domain" {
  description = "Domínio configurado no SES"
  value       = module.ses.domain
}

output "secrets_arn" {
  description = "ARN dos secrets no Secrets Manager"
  value       = module.secrets.secrets_arn
}

output "monitoring_dashboard" {
  description = "URL do dashboard CloudWatch"
  value       = module.monitoring.dashboard_url
}
