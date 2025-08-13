"""
Modelos de usuários.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import uuid

class User(AbstractUser):
    """Modelo de usuário customizado."""
    
    ROLE_CHOICES = [
        ('superadmin', 'Super Administrador'),
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
        ('financeiro', 'Financeiro'),
        ('juridico', 'Jurídico'),
        ('fiscal', 'Fiscal'),
    ]
    
    # Campos básicos
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('Nome', max_length=150)
    last_name = models.CharField('Sobrenome', max_length=150)
    
    # Multi-tenancy
    tenant = models.ForeignKey(
        'tenancy.Tenant',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    
    # Perfil e permissões
    role = models.CharField('Perfil', max_length=20, choices=ROLE_CHOICES, default='operador')
    is_tenant_admin = models.BooleanField('Admin do Tenant', default=False)
    
    # Contato
    phone = models.CharField(
        'Telefone',
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Telefone deve estar no formato: +999999999'
            )
        ]
    )
    whatsapp = models.CharField('WhatsApp', max_length=15, blank=True)
    
    # Segurança
    mfa_enabled = models.BooleanField('MFA Ativado', default=False)
    mfa_secret = models.CharField('Segredo MFA', max_length=32, blank=True)
    last_login_ip = models.GenericIPAddressField('Último IP de Login', null=True, blank=True)
    
    # LGPD
    lgpd_consent = models.BooleanField('Consentimento LGPD', default=False)
    lgpd_consent_at = models.DateTimeField('Data do Consentimento', null=True, blank=True)
    data_retention_until = models.DateTimeField('Retenção até', null=True, blank=True)
    
    # Campos de assinatura e teste
    data_inicio_teste = models.DateTimeField('Início do Teste', null=True, blank=True)
    data_fim_teste = models.DateTimeField('Fim do Teste', null=True, blank=True)
    plano_ativo = models.BooleanField('Plano Ativo', default=False)
    data_inicio_plano = models.DateTimeField('Início do Plano', null=True, blank=True)
    data_fim_plano = models.DateTimeField('Fim do Plano', null=True, blank=True)
    
    # Campos Stripe
    stripe_customer_id = models.CharField('Stripe Customer ID', max_length=100, null=True, blank=True)
    stripe_subscription_id = models.CharField('Stripe Subscription ID', max_length=100, null=True, blank=True)
    
    # Campos MFA e LGPD
    consent_lgpd_at = models.DateTimeField('Consentimento LGPD', null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    last_activity = models.DateTimeField('Última Atividade', null=True, blank=True)
    last_login_at = models.DateTimeField('Último login', null=True, blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    # Campos do AbstractUser que não usamos
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'users_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['tenant', 'role']),
            models.Index(fields=['is_active', 'last_activity']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Retorna o nome completo do usuário."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Retorna o primeiro nome do usuário."""
        return self.first_name
    
    @property
    def is_superuser_or_admin(self):
        """Verifica se é superusuário ou admin do tenant."""
        return self.is_superuser or self.is_tenant_admin
    
    @property
    def can_manage_users(self):
        """Verifica se pode gerenciar usuários."""
        return self.is_superuser or (self.is_tenant_admin and self.role in ['admin', 'superadmin'])
    
    @property
    def can_access_financial(self):
        """Verifica se pode acessar módulo financeiro."""
        return self.role in ['admin', 'financeiro', 'superadmin']
    
    @property
    def can_access_legal(self):
        """Verifica se pode acessar módulo jurídico."""
        return self.role in ['admin', 'juridico', 'superadmin']
    
    def update_last_activity(self):
        """Atualiza timestamp de última atividade."""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def consent_lgpd(self):
        """Registra consentimento LGPD."""
        self.lgpd_consent = True
        self.lgpd_consent_at = timezone.now()
        self.data_retention_until = timezone.now() + timezone.timedelta(days=2555)  # 7 anos
        self.save(update_fields=['lgpd_consent', 'lgpd_consent_at', 'data_retention_until'])

    def save(self, *args, **kwargs):
        # Se é um novo usuário e não tem data de início do teste, definir
        if not self.pk and not self.data_inicio_teste:
            self.data_inicio_teste = timezone.now()
            self.data_fim_teste = self.data_inicio_teste + timedelta(days=7)
        super().save(*args, **kwargs)
    
    @property
    def is_in_trial_period(self):
        """Verifica se o usuário está no período de teste"""
        if not self.data_fim_teste:
            return False
        return timezone.now() <= self.data_fim_teste
    
    @property
    def has_active_access(self):
        """Verifica se o usuário tem acesso ativo (teste ou plano)"""
        return self.plano_ativo or self.is_in_trial_period
    
    @property
    def subscription_status(self):
        """Retorna o status da assinatura"""
        if self.plano_ativo:
            return 'ativo'
        elif self.is_in_trial_period:
            return 'teste'
        else:
            return 'expirado'
    
    def activate_subscription(self, stripe_customer_id, stripe_subscription_id):
        """Ativa a assinatura do usuário"""
        self.plano_ativo = True
        self.data_inicio_plano = timezone.now()
        self.data_fim_plano = timezone.now() + timedelta(days=30)  # 30 dias
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.save()
    
    def deactivate_subscription(self):
        """Desativa a assinatura do usuário"""
        self.plano_ativo = False
        self.data_fim_plano = timezone.now()
        self.save()

class UserSession(models.Model):
    """Modelo para rastrear sessões de usuário."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField('Chave da Sessão', max_length=40, unique=True)
    ip_address = models.GenericIPAddressField('Endereço IP')
    user_agent = models.TextField('User Agent', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    last_activity = models.DateTimeField('Última Atividade', auto_now=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Sessão do Usuário'
        verbose_name_plural = 'Sessões dos Usuários'
        db_table = 'users_user_session'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"Sessão de {self.user.email} - {self.ip_address}"
    
    def deactivate(self):
        """Desativa a sessão."""
        self.is_active = False
        self.save(update_fields=['is_active'])

class UserAuditLog(models.Model):
    """Log de auditoria para ações dos usuários."""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Criação'),
        ('update', 'Atualização'),
        ('delete', 'Exclusão'),
        ('view', 'Visualização'),
        ('export', 'Exportação'),
        ('import', 'Importação'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField('Ação', max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField('Modelo', max_length=100)
    object_id = models.CharField('ID do Objeto', max_length=100, blank=True)
    object_repr = models.CharField('Representação do Objeto', max_length=200, blank=True)
    
    # Dados da mudança
    old_data = models.JSONField('Dados Anteriores', null=True, blank=True)
    new_data = models.JSONField('Dados Novos', null=True, blank=True)
    
    # Metadados
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    timestamp = models.DateTimeField('Timestamp', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        db_table = 'users_user_audit_log'
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} por {self.user} em {self.model_name} - {self.timestamp}"

class Subscription(models.Model):
    """Modelo para gerenciar assinaturas Stripe"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    
    # Dados Stripe
    stripe_customer_id = models.CharField('Stripe Customer ID', max_length=100, unique=True)
    stripe_subscription_id = models.CharField('Stripe Subscription ID', max_length=100, unique=True)
    stripe_price_id = models.CharField('Stripe Price ID', max_length=100)
    
    # Status da assinatura
    status = models.CharField('Status', max_length=20, choices=[
        ('trialing', 'Em Teste'),
        ('active', 'Ativa'),
        ('past_due', 'Pagamento Atrasado'),
        ('canceled', 'Cancelada'),
        ('unpaid', 'Não Pago'),
        ('incomplete', 'Incompleta'),
        ('incomplete_expired', 'Incompleta Expirada'),
    ], default='active')
    
    # Controle de cancelamento
    cancel_at_period_end = models.BooleanField('Cancelar ao Fim do Período', default=False)
    canceled_at = models.DateTimeField('Cancelada em', null=True, blank=True)
    
    # Datas
    current_period_start = models.DateTimeField('Início do Período Atual')
    current_period_end = models.DateTimeField('Fim do Período Atual')
    trial_start = models.DateTimeField('Início do Teste', null=True, blank=True)
    trial_end = models.DateTimeField('Fim do Teste', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    # Dados do plano
    plan_name = models.CharField('Nome do Plano', max_length=100, default='Plano Mensal Licitrix')
    plan_price = models.DecimalField('Preço do Plano', max_digits=10, decimal_places=2, default=59.90)
    plan_currency = models.CharField('Moeda', max_length=3, default='BRL')
    plan_interval = models.CharField('Intervalo', max_length=20, default='month')
    
    # Método de pagamento
    default_payment_method_last4 = models.CharField('Últimos 4 dígitos', max_length=4, null=True, blank=True)
    default_payment_method_brand = models.CharField('Bandeira', max_length=20, null=True, blank=True)
    default_payment_method_exp_month = models.IntegerField('Mês de Expiração', null=True, blank=True)
    default_payment_method_exp_year = models.IntegerField('Ano de Expiração', null=True, blank=True)
    
    # Grace period para pagamentos em atraso
    grace_period_until = models.DateTimeField('Grace Period até', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        db_table = 'subscriptions'
    
    def __str__(self):
        return f"Assinatura de {self.user.email} - {self.status}"
    
    @property
    def is_active(self):
        """Verifica se a assinatura está ativa"""
        return self.status in ['active', 'trialing']
    
    @property
    def is_canceled(self):
        """Verifica se a assinatura está cancelada"""
        return self.status == 'canceled' or self.cancel_at_period_end
    
    @property
    def is_past_due(self):
        """Verifica se a assinatura está em atraso"""
        return self.status == 'past_due'
    
    @property
    def has_grace_period(self):
        """Verifica se ainda está no grace period"""
        if not self.grace_period_until:
            return False
        return timezone.now() <= self.grace_period_until
    
    @property
    def days_until_renewal(self):
        """Retorna dias até a renovação"""
        if self.current_period_end:
            delta = self.current_period_end - timezone.now()
            return max(0, delta.days)
        return 0
    
    @property
    def days_until_trial_end(self):
        """Retorna dias até o fim do teste"""
        if self.trial_end:
            delta = self.trial_end - timezone.now()
            return max(0, delta.days)
        return 0
    
    def start_grace_period(self, days=3):
        """Inicia o grace period para pagamentos em atraso"""
        self.grace_period_until = timezone.now() + timedelta(days=days)
        self.save()
    
    def end_grace_period(self):
        """Finaliza o grace period"""
        self.grace_period_until = None
        self.save()
    
    def cancel_subscription(self, at_period_end=True):
        """Cancela a assinatura"""
        if at_period_end:
            self.cancel_at_period_end = True
        else:
            self.status = 'canceled'
            self.canceled_at = timezone.now()
            self.cancel_at_period_end = False
        self.save()
    
    def reactivate_subscription(self):
        """Reativa uma assinatura cancelada"""
        if self.cancel_at_period_end:
            self.cancel_at_period_end = False
            self.save()
        elif self.status == 'canceled':
            # Para reativação de assinatura cancelada, será necessário criar nova via Stripe
            pass

class Invoice(models.Model):
    """Modelo para cache de faturas Stripe"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    
    # Dados Stripe
    stripe_invoice_id = models.CharField('Stripe Invoice ID', max_length=100, unique=True)
    stripe_customer_id = models.CharField('Stripe Customer ID', max_length=100)
    
    # Status e valores
    status = models.CharField('Status', max_length=20, choices=[
        ('draft', 'Rascunho'),
        ('open', 'Aberta'),
        ('paid', 'Paga'),
        ('uncollectible', 'Não Cobrável'),
        ('void', 'Anulada'),
    ], default='open')
    
    amount_due = models.DecimalField('Valor Devido', max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField('Valor Pago', max_digits=10, decimal_places=2, default=0)
    amount_remaining = models.DecimalField('Valor Restante', max_digits=10, decimal_places=2, default=0)
    currency = models.CharField('Moeda', max_length=3, default='BRL')
    
    # URLs para download
    hosted_invoice_url = models.URLField('URL da Fatura', max_length=500, null=True, blank=True)
    invoice_pdf = models.URLField('PDF da Fatura', max_length=500, null=True, blank=True)
    
    # Datas
    due_date = models.DateTimeField('Data de Vencimento', null=True, blank=True)
    paid_at = models.DateTimeField('Paga em', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Fatura {self.stripe_invoice_id} - {self.subscription.user.email}"
    
    @property
    def is_paid(self):
        """Verifica se a fatura foi paga"""
        return self.status == 'paid'
    
    @property
    def is_overdue(self):
        """Verifica se a fatura está em atraso"""
        if not self.due_date:
            return False
        return not self.is_paid and timezone.now() > self.due_date
