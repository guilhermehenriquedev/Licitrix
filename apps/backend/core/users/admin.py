from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserSession, UserAuditLog, Subscription, Invoice

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'subscription_status', 'plano_ativo', 'is_active', 'created_at')
    list_filter = ('plano_ativo', 'is_active', 'role', 'created_at', 'data_inicio_teste')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        ('Assinatura', {'fields': (
            'plano_ativo', 'data_inicio_teste', 'data_fim_teste',
            'data_inicio_plano', 'data_fim_plano',
            'stripe_customer_id', 'stripe_subscription_id'
        )}),
        ('LGPD', {'fields': ('consent_lgpd_at', 'mfa_enabled', 'mfa_secret')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    def subscription_status(self, obj):
        return obj.subscription_status
    subscription_status.short_description = 'Status da Assinatura'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'plan_name', 'plan_price', 'cancel_at_period_end', 'current_period_end', 'days_until_renewal')
    list_filter = ('status', 'plan_name', 'cancel_at_period_end', 'created_at')
    search_fields = ('user__email', 'stripe_customer_id', 'stripe_subscription_id')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Usuário', {'fields': ('user',)}),
        ('Dados Stripe', {'fields': (
            'stripe_customer_id', 'stripe_subscription_id', 'stripe_price_id'
        )}),
        ('Status', {'fields': (
            'status', 'cancel_at_period_end', 'canceled_at',
            'current_period_start', 'current_period_end'
        )}),
        ('Teste', {'fields': ('trial_start', 'trial_end')}),
        ('Plano', {'fields': ('plan_name', 'plan_price', 'plan_currency', 'plan_interval')}),
        ('Pagamento', {'fields': (
            'default_payment_method_last4', 'default_payment_method_brand',
            'default_payment_method_exp_month', 'default_payment_method_exp_year'
        )}),
        ('Grace Period', {'fields': ('grace_period_until',)}),
        ('Datas', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def days_until_renewal(self, obj):
        return obj.days_until_renewal
    days_until_renewal.short_description = 'Dias até Renovação'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('stripe_invoice_id', 'subscription', 'status', 'amount_due', 'amount_paid', 'due_date', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('stripe_invoice_id', 'subscription__user__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Assinatura', {'fields': ('subscription',)}),
        ('Dados Stripe', {'fields': ('stripe_invoice_id', 'stripe_customer_id')}),
        ('Status e Valores', {'fields': ('status', 'amount_due', 'amount_paid', 'amount_remaining', 'currency')}),
        ('URLs', {'fields': ('hosted_invoice_url', 'invoice_pdf')}),
        ('Datas', {'fields': ('due_date', 'paid_at', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'created_at', 'last_activity', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'ip_address')
    ordering = ('-created_at',)

@admin.register(UserAuditLog)
class UserAuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__email', 'action', 'model_name')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
