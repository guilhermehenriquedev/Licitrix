from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class SubscriptionAccessMiddleware(MiddlewareMixin):
    """
    Middleware para verificar acesso baseado no status da assinatura
    """
    
    # URLs que não precisam de verificação de assinatura
    EXEMPT_URLS = [
        '/auth/login/',
        '/auth/register/',
        '/auth/password-reset/',
        '/auth/password-reset/confirm/',
        '/subscription/webhook/',
        '/health/',
        '/admin/',
        '/api/docs/',
        '/api/redoc/',
    ]
    
    # URLs que redirecionam para página de assinatura
    SUBSCRIPTION_REQUIRED_URLS = [
        '/api/',
        '/dashboard/',
        '/oportunidades/',
        '/precificacao/',
        '/contratos/',
        '/financeiro/',
        '/documentos/',
    ]
    
    def process_request(self, request):
        # Verificar se é uma URL que precisa de verificação
        path = request.path_info
        
        # URLs de API que não precisam de verificação
        if path.startswith('/api/auth/') or path.startswith('/api/health/'):
            return None
        
        # Verificar se é uma URL que precisa de verificação de assinatura
        if not self._needs_subscription_check(path):
            return None
        
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return None
        
        # Verificar se o usuário tem acesso ativo
        if not self._has_active_access(request.user):
            # Se for uma requisição de API, retornar erro JSON
            if path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Acesso bloqueado. Verifique sua assinatura.',
                    'subscription_status': self._get_subscription_status(request.user),
                    'redirect_url': '/subscription'
                }, status=403)
            
            # Se for uma requisição de página, redirecionar
            return redirect('/subscription')
        
        return None
    
    def _needs_subscription_check(self, path):
        """Verifica se a URL precisa de verificação de assinatura"""
        # URLs que não precisam de verificação
        for exempt_url in self.EXEMPT_URLS:
            if path.startswith(exempt_url):
                return False
        
        # URLs que precisam de verificação
        for required_url in self.SUBSCRIPTION_REQUIRED_URLS:
            if path.startswith(required_url):
                return True
        
        return False
    
    def _has_active_access(self, user):
        """Verifica se o usuário tem acesso ativo considerando grace period"""
        # Verificar período de teste
        if user.is_in_trial_period:
            return True
        
        # Verificar se tem plano ativo
        if user.plano_ativo:
            return True
        
        # Verificar se tem assinatura com grace period
        if hasattr(user, 'subscription') and user.subscription:
            subscription = user.subscription
            
            # Se está em grace period, permitir acesso
            if subscription.has_grace_period:
                return True
            
            # Se está cancelada mas ainda no período atual
            if subscription.cancel_at_period_end and subscription.current_period_end > timezone.now():
                return True
        
        return False
    
    def _get_subscription_status(self, user):
        """Retorna o status detalhado da assinatura"""
        if user.is_in_trial_period:
            return {
                'type': 'trial',
                'active': True,
                'days_remaining': user.days_until_trial_end
            }
        
        if hasattr(user, 'subscription') and user.subscription:
            subscription = user.subscription
            
            if subscription.status == 'active':
                return {
                    'type': 'active',
                    'active': True,
                    'days_until_renewal': subscription.days_until_renewal
                }
            
            elif subscription.status == 'past_due':
                if subscription.has_grace_period:
                    return {
                        'type': 'past_due_grace',
                        'active': True,
                        'grace_period_until': subscription.grace_period_until
                    }
                else:
                    return {
                        'type': 'past_due_blocked',
                        'active': False,
                        'message': 'Pagamento em atraso. Acesso bloqueado.'
                    }
            
            elif subscription.cancel_at_period_end:
                if subscription.current_period_end > timezone.now():
                    return {
                        'type': 'canceled_period_end',
                        'active': True,
                        'current_period_end': subscription.current_period_end
                    }
                else:
                    return {
                        'type': 'canceled_expired',
                        'active': False,
                        'message': 'Período de assinatura expirado.'
                    }
            
            elif subscription.status == 'canceled':
                return {
                    'type': 'canceled',
                    'active': False,
                    'message': 'Assinatura cancelada.'
                }
        
        return {
            'type': 'no_subscription',
            'active': False,
            'message': 'Nenhuma assinatura ativa.'
        }

class TrialExpirationMiddleware(MiddlewareMixin):
    """
    Middleware para verificar expiração do período de teste
    """
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        
        # Verificar se o usuário está no período de teste e próximo do fim
        if request.user.is_in_trial_period:
            days_left = request.user.days_until_trial_end
            
            # Se faltam 2 dias ou menos, adicionar aviso
            if days_left <= 2:
                request.trial_warning = {
                    'days_left': days_left,
                    'message': f'Seu período de teste termina em {days_left} dia(s). Faça upgrade para continuar.'
                }
        
        return None

class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware para rastrear atividade do usuário
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Atualizar última atividade
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
            
            # Log de auditoria para ações importantes
            if request.method in ['POST', 'PUT', 'DELETE']:
                logger.info(f"Usuário {request.user.email} executou {request.method} em {request.path}")
        
        return None
