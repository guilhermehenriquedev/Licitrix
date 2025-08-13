"""
Models para multi-tenancy.
"""
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.core.validators import RegexValidator

class Tenant(TenantMixin):
    """Modelo de tenant (empresa)."""
    
    PLAN_CHOICES = [
        ('free', 'Gratuito'),
        ('basic', 'Básico'),
        ('professional', 'Profissional'),
        ('enterprise', 'Empresarial'),
    ]
    
    BILLING_STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('past_due', 'Vencido'),
        ('canceled', 'Cancelado'),
        ('suspended', 'Suspenso'),
    ]
    
    name = models.CharField('Nome da Empresa', max_length=200)
    cnpj = models.CharField(
        'CNPJ',
        max_length=18,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
                message='CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX'
            )
        ]
    )
    razao_social = models.CharField('Razão Social', max_length=200)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=200, blank=True)
    
    # Segmentos de atuação
    cnae_principal = models.CharField('CNAE Principal', max_length=7)
    cnae_secundarios = models.JSONField('CNAEs Secundários', default=list, blank=True)
    
    # Localização
    uf = models.CharField('UF', max_length=2)
    municipio = models.CharField('Município', max_length=100)
    cep = models.CharField('CEP', max_length=9, blank=True)
    endereco = models.TextField('Endereço', blank=True)
    
    # Configurações
    plan = models.CharField('Plano', max_length=20, choices=PLAN_CHOICES, default='free')
    billing_status = models.CharField(
        'Status de Cobrança',
        max_length=20,
        choices=BILLING_STATUS_CHOICES,
        default='active'
    )
    
    # LGPD
    lgpd_consent = models.BooleanField('Consentimento LGPD', default=False)
    lgpd_consent_at = models.DateTimeField('Data do Consentimento', null=True, blank=True)
    dpo_email = models.EmailField('Email do DPO', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        db_table = 'tenancy_tenant'
    
    def __str__(self):
        return f"{self.name} ({self.cnpj})"
    
    @property
    def is_billing_active(self):
        """Verifica se o tenant está com cobrança ativa."""
        return self.billing_status == 'active'
    
    @property
    def can_access_features(self):
        """Verifica se o tenant pode acessar funcionalidades premium."""
        if self.plan == 'free':
            return self.is_billing_active
        return self.is_billing_active and self.is_active

class Domain(DomainMixin):
    """Modelo de domínio para tenant."""
    
    class Meta:
        verbose_name = 'Domínio'
        verbose_name_plural = 'Domínios'
        db_table = 'tenancy_domain'

class TenantConfiguration(models.Model):
    """Configurações específicas do tenant."""
    
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='config')
    
    # Integrações
    enotas_api_key = models.CharField('Chave API eNotas', max_length=255, blank=True)
    nfeio_api_key = models.CharField('Chave API NFE.io', max_length=255, blank=True)
    
    # Notificações
    email_notifications = models.BooleanField('Notificações por Email', default=True)
    whatsapp_notifications = models.BooleanField('Notificações WhatsApp', default=False)
    sms_notifications = models.BooleanField('Notificações SMS', default=False)
    
    # Configurações de negócio
    default_markup = models.DecimalField(
        'Markup Padrão (%)',
        max_digits=5,
        decimal_places=2,
        default=20.00
    )
    risk_factor = models.DecimalField(
        'Fator de Risco (%)',
        max_digits=5,
        decimal_places=2,
        default=5.00
    )
    
    # Templates
    custom_templates = models.JSONField('Templates Customizados', default=dict, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração do Tenant'
        verbose_name_plural = 'Configurações dos Tenants'
        db_table = 'tenancy_tenant_configuration'
    
    def __str__(self):
        return f"Configuração de {self.tenant.name}"
