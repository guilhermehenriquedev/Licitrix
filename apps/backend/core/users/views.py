from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.core.cache import cache
import json
import logging

from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer,
    SubscriptionSerializer, StripeCheckoutSessionSerializer
)
from .models import User, Subscription, Invoice
from .services.stripe_service import StripeService

logger = logging.getLogger(__name__)
User = get_user_model()
stripe_service = StripeService()

class UserRegistrationView(generics.CreateAPIView):
    """View para registro de usuários"""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Log de auditoria
        logger.info(f"Novo usuário registrado: {user.email}")
        
        return Response({
            'message': 'Usuário criado com sucesso! Você tem 7 dias de teste gratuito.',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    """View para login de usuários"""
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Verificar se o usuário tem acesso ativo
        if not user.has_active_access:
            return Response({
                'error': 'Período de teste expirado. Faça upgrade para continuar.',
                'subscription_status': user.subscription_status
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Log de auditoria
        logger.info(f"Usuário logado: {user.email}")
        
        return Response({
            'message': 'Login realizado com sucesso!',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })

class UserLogoutView(generics.GenericAPIView):
    """View para logout de usuários"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log de auditoria
            logger.info(f"Usuário deslogado: {request.user.email}")
            
            return Response({'message': 'Logout realizado com sucesso!'})
        except Exception as e:
            logger.error(f"Erro no logout: {e}")
            return Response({'error': 'Erro no logout'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """View para perfil do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class UserStatusView(generics.GenericAPIView):
    """View para verificar status da assinatura"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Verificar se tem assinatura
        subscription = None
        if hasattr(user, 'subscription'):
            subscription = user.subscription
        
        response_data = {
            'trial': {
                'start': user.data_inicio_teste,
                'end': user.data_fim_teste,
                'active': user.is_in_trial_period,
                'days_remaining': user.days_until_trial_end if user.is_in_trial_period else 0
            },
            'subscription': {
                'active': user.plano_ativo,
                'status': user.subscription_status,
                'has_active_access': user.has_active_access
            }
        }
        
        if subscription:
            response_data['subscription'].update({
                'stripe_subscription_id': subscription.stripe_subscription_id,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'current_period_end': subscription.current_period_end,
                'grace_period_until': subscription.grace_period_until,
                'has_grace_period': subscription.has_grace_period,
                'days_until_renewal': subscription.days_until_renewal,
                'payment_method': {
                    'last4': subscription.default_payment_method_last4,
                    'brand': subscription.default_payment_method_brand,
                    'exp_month': subscription.default_payment_method_exp_month,
                    'exp_year': subscription.default_payment_method_exp_year
                } if subscription.default_payment_method_last4 else None
            })
        
        return Response(response_data)

class PasswordResetView(generics.GenericAPIView):
    """View para solicitar reset de senha"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Gerar token temporário
        token = get_random_string(64)
        cache_key = f"password_reset_{token}"
        cache.set(cache_key, user.id, timeout=3600)  # 1 hora
        
        # Enviar email (implementar template)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        try:
            send_mail(
                'Redefinição de Senha - Licitrix',
                f'Clique no link para redefinir sua senha: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            logger.info(f"Email de reset enviado para: {email}")
            return Response({'message': 'Email de redefinição enviado com sucesso!'})
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de reset: {e}")
            return Response({'error': 'Erro ao enviar email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetConfirmView(generics.GenericAPIView):
    """View para confirmar reset de senha"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        cache_key = f"password_reset_{token}"
        user_id = cache.get(cache_key)
        
        if not user_id:
            return Response({'error': 'Token inválido ou expirado'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            
            # Remover token do cache
            cache.delete(cache_key)
            
            logger.info(f"Senha alterada para usuário: {user.email}")
            return Response({'message': 'Senha alterada com sucesso!'})
            
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class SubscriptionListView(generics.ListAPIView):
    """View para listar assinaturas do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stripe_checkout_session(request):
    """Cria sessão de checkout no Stripe"""
    serializer = StripeCheckoutSessionSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    success_url = serializer.validated_data['success_url']
    cancel_url = serializer.validated_data['cancel_url']
    
    try:
        checkout_session = stripe_service.create_checkout_session(user, success_url, cancel_url)
        
        return Response({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar sessão de checkout: {e}")
        return Response({'error': 'Erro ao criar sessão de checkout'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_customer_portal_session(request):
    """Cria sessão do Customer Portal do Stripe"""
    user = request.user
    return_url = request.data.get('return_url', f"{settings.FRONTEND_URL}/dashboard")
    
    try:
        portal_session = stripe_service.create_customer_portal_session(user, return_url)
        
        return Response({
            'portal_url': portal_session.url
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar sessão do portal: {e}")
        return Response({'error': 'Erro ao criar sessão do portal'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancela a assinatura do usuário"""
    user = request.user
    
    try:
        if not hasattr(user, 'subscription') or not user.subscription:
            return Response({'error': 'Usuário não possui assinatura ativa'}, status=status.HTTP_400_BAD_REQUEST)
        
        mode = request.data.get('mode', 'period_end')  # 'immediate' ou 'period_end'
        at_period_end = mode == 'period_end'
        
        # Cancelar no Stripe
        stripe_subscription = stripe_service.cancel_subscription(
            user.subscription.stripe_subscription_id, 
            at_period_end
        )
        
        # Atualizar no banco local
        if at_period_end:
            user.subscription.cancel_at_period_end = True
        else:
            user.subscription.status = 'canceled'
            user.subscription.canceled_at = timezone.now()
            user.subscription.cancel_at_period_end = False
        
        user.subscription.save()
        
        # Se cancelamento imediato, desativar usuário
        if not at_period_end:
            user.plano_ativo = False
            user.data_fim_plano = timezone.now()
            user.save()
        
        message = "Assinatura cancelada ao fim do período" if at_period_end else "Assinatura cancelada imediatamente"
        
        logger.info(f"Assinatura cancelada para usuário: {user.email} - Modo: {mode}")
        
        return Response({
            'message': message,
            'cancel_at_period_end': at_period_end,
            'current_period_end': user.subscription.current_period_end
        })
        
    except Exception as e:
        logger.error(f"Erro ao cancelar assinatura: {e}")
        return Response({'error': 'Erro ao cancelar assinatura'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactivate_subscription(request):
    """Reativa a assinatura do usuário"""
    user = request.user
    
    try:
        if not hasattr(user, 'subscription') or not user.subscription:
            return Response({'error': 'Usuário não possui assinatura'}, status=status.HTTP_400_BAD_REQUEST)
        
        subscription = user.subscription
        
        if subscription.cancel_at_period_end:
            # Reativar assinatura cancelada ao fim do período
            stripe_subscription = stripe_service.reactivate_subscription(subscription.stripe_subscription_id)
            subscription.cancel_at_period_end = False
            subscription.save()
            
            message = "Assinatura reativada com sucesso!"
            
        elif subscription.status == 'canceled':
            # Para assinaturas completamente canceladas, criar nova via checkout
            return Response({
                'error': 'Assinatura completamente cancelada. Crie uma nova assinatura.',
                'redirect_to_checkout': True
            }, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({'error': 'Assinatura não pode ser reativada'}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Assinatura reativada para usuário: {user.email}")
        
        return Response({
            'message': message,
            'subscription_status': subscription.status
        })
        
    except Exception as e:
        logger.error(f"Erro ao reativar assinatura: {e}")
        return Response({'error': 'Erro ao reativar assinatura'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_invoices(request):
    """Lista faturas do usuário"""
    user = request.user
    
    try:
        if not hasattr(user, 'subscription') or not user.subscription:
            return Response({'error': 'Usuário não possui assinatura'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar faturas do banco local
        invoices = Invoice.objects.filter(subscription=user.subscription).order_by('-created_at')
        
        # Se não houver faturas locais, buscar do Stripe
        if not invoices.exists() and user.subscription.stripe_customer_id:
            stripe_invoices = stripe_service.list_invoices(user.subscription.stripe_customer_id)
            
            # Criar registros locais
            for stripe_invoice in stripe_invoices.data:
                Invoice.objects.get_or_create(
                    stripe_invoice_id=stripe_invoice.id,
                    defaults={
                        'subscription': user.subscription,
                        'stripe_customer_id': stripe_invoice.customer,
                        'status': stripe_invoice.status,
                        'amount_due': stripe_invoice.amount_due / 100,  # Stripe usa centavos
                        'amount_paid': stripe_invoice.amount_paid / 100,
                        'amount_remaining': stripe_invoice.amount_remaining / 100,
                        'currency': stripe_invoice.currency.upper(),
                        'hosted_invoice_url': stripe_invoice.hosted_invoice_url,
                        'invoice_pdf': stripe_invoice.invoice_pdf,
                        'due_date': timezone.datetime.fromtimestamp(stripe_invoice.due_date) if stripe_invoice.due_date else None,
                        'paid_at': timezone.datetime.fromtimestamp(stripe_invoice.status_transitions.paid_at) if hasattr(stripe_invoice.status_transitions, 'paid_at') and stripe_invoice.status_transitions.paid_at else None,
                    }
                )
            
            # Recarregar faturas
            invoices = Invoice.objects.filter(subscription=user.subscription).order_by('-created_at')
        
        # Serializar faturas
        invoice_data = []
        for invoice in invoices:
            invoice_data.append({
                'id': invoice.id,
                'stripe_invoice_id': invoice.stripe_invoice_id,
                'status': invoice.status,
                'amount_due': float(invoice.amount_due),
                'amount_paid': float(invoice.amount_paid),
                'currency': invoice.currency,
                'hosted_invoice_url': invoice.hosted_invoice_url,
                'invoice_pdf': invoice.invoice_pdf,
                'due_date': invoice.due_date,
                'paid_at': invoice.paid_at,
                'created_at': invoice.created_at,
                'is_overdue': invoice.is_overdue
            })
        
        return Response({
            'invoices': invoice_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar faturas: {e}")
        return Response({'error': 'Erro ao listar faturas'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Webhook para receber eventos do Stripe"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Verificar assinatura do webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Processar eventos
        if event['type'] == 'checkout.session.completed':
            handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'customer.subscription.created':
            handle_subscription_created(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_deleted(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])
        elif event['type'] == 'payment_method.attached':
            handle_payment_method_attached(event['data']['object'])
        
        return Response({'status': 'success'})
        
    except ValueError as e:
        logger.error(f"Payload inválido: {e}")
        return Response({'error': 'Payload inválido'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Assinatura inválida: {e}")
        return Response({'error': 'Assinatura inválida'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return Response({'error': 'Erro interno'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def handle_checkout_completed(session):
    """Processa checkout completado"""
    user_id = session.metadata.get('user_id')
    if not user_id:
        return
    
    try:
        user = User.objects.get(id=user_id)
        subscription = stripe.Subscription.retrieve(session.subscription)
        
        # Criar ou atualizar registro de assinatura
        subscription_obj, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'stripe_customer_id': session.customer,
                'stripe_subscription_id': session.subscription,
                'stripe_price_id': subscription.items.data[0].price.id,
                'status': subscription.status,
                'current_period_start': timezone.datetime.fromtimestamp(subscription.current_period_start),
                'current_period_end': timezone.datetime.fromtimestamp(subscription.current_period_end),
                'trial_start': timezone.datetime.fromtimestamp(subscription.trial_start) if subscription.trial_start else None,
                'trial_end': timezone.datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None,
                'plan_name': 'Plano Mensal Licitrix',
                'plan_price': 59.90,
                'plan_currency': 'BRL',
                'plan_interval': 'month'
            }
        )
        
        if not created:
            # Atualizar assinatura existente
            subscription_obj.stripe_customer_id = session.customer
            subscription_obj.stripe_subscription_id = session.subscription
            subscription_obj.status = subscription.status
            subscription_obj.current_period_start = timezone.datetime.fromtimestamp(subscription.current_period_start)
            subscription_obj.current_period_end = timezone.datetime.fromtimestamp(subscription.current_period_end)
            subscription_obj.save()
        
        # Ativar usuário
        user.activate_subscription(session.customer, session.subscription)
        
        logger.info(f"Assinatura ativada para usuário: {user.email}")
        
    except Exception as e:
        logger.error(f"Erro ao processar checkout: {e}")

def handle_subscription_created(subscription):
    """Processa assinatura criada"""
    try:
        user_id = subscription.metadata.get('user_id')
        if not user_id:
            return
        
        user = User.objects.get(id=user_id)
        
        # Atualizar assinatura local
        if hasattr(user, 'subscription'):
            user.subscription.status = subscription.status
            user.subscription.current_period_start = timezone.datetime.fromtimestamp(subscription.current_period_start)
            user.subscription.current_period_end = timezone.datetime.fromtimestamp(subscription.current_period_end)
            user.subscription.save()
        
        logger.info(f"Assinatura criada para usuário: {user.email}")
        
    except Exception as e:
        logger.error(f"Erro ao processar assinatura criada: {e}")

def handle_subscription_updated(subscription):
    """Processa assinatura atualizada"""
    try:
        # Buscar assinatura pelo ID do Stripe
        subscription_obj = Subscription.objects.get(stripe_subscription_id=subscription.id)
        
        # Atualizar campos
        subscription_obj.status = subscription.status
        subscription_obj.cancel_at_period_end = subscription.cancel_at_period_end
        subscription_obj.current_period_start = timezone.datetime.fromtimestamp(subscription.current_period_start)
        subscription_obj.current_period_end = timezone.datetime.fromtimestamp(subscription.current_period_end)
        
        # Atualizar método de pagamento se disponível
        if subscription.default_payment_method:
            payment_method = stripe.PaymentMethod.retrieve(subscription.default_payment_method)
            subscription_obj.default_payment_method_last4 = payment_method.card.last4
            subscription_obj.default_payment_method_brand = payment_method.card.brand
            subscription_obj.default_payment_method_exp_month = payment_method.card.exp_month
            subscription_obj.default_payment_method_exp_year = payment_method.card.exp_year
        
        subscription_obj.save()
        
        # Atualizar usuário se necessário
        user = subscription_obj.user
        if subscription.status == 'canceled' and not subscription.cancel_at_period_end:
            user.plano_ativo = False
            user.data_fim_plano = timezone.now()
            user.save()
        
        logger.info(f"Assinatura atualizada para usuário: {user.email}")
        
    except Subscription.DoesNotExist:
        logger.error(f"Assinatura não encontrada: {subscription.id}")
    except Exception as e:
        logger.error(f"Erro ao processar assinatura atualizada: {e}")

def handle_subscription_deleted(subscription):
    """Processa assinatura cancelada"""
    try:
        subscription_obj = Subscription.objects.get(stripe_subscription_id=subscription.id)
        subscription_obj.status = 'canceled'
        subscription_obj.canceled_at = timezone.now()
        subscription_obj.save()
        
        # Desativar usuário
        user = subscription_obj.user
        user.deactivate_subscription()
        
        logger.info(f"Assinatura cancelada: {subscription.id}")
        
    except Subscription.DoesNotExist:
        logger.error(f"Assinatura não encontrada: {subscription.id}")
    except Exception as e:
        logger.error(f"Erro ao processar assinatura cancelada: {e}")

def handle_payment_succeeded(invoice):
    """Processa pagamento bem-sucedido"""
    subscription_id = invoice.subscription
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = 'active'
        subscription.current_period_start = timezone.datetime.fromtimestamp(invoice.period_start)
        subscription.current_period_end = timezone.datetime.fromtimestamp(invoice.period_end)
        subscription.grace_period_until = None  # Remover grace period
        subscription.save()
        
        # Atualizar usuário
        user = subscription.user
        user.data_fim_plano = subscription.current_period_end
        user.save()
        
        # Criar/atualizar fatura local
        Invoice.objects.update_or_create(
            stripe_invoice_id=invoice.id,
            defaults={
                'subscription': subscription,
                'stripe_customer_id': invoice.customer,
                'status': invoice.status,
                'amount_due': invoice.amount_due / 100,
                'amount_paid': invoice.amount_paid / 100,
                'amount_remaining': invoice.amount_remaining / 100,
                'currency': invoice.currency.upper(),
                'hosted_invoice_url': invoice.hosted_invoice_url,
                'invoice_pdf': invoice.invoice_pdf,
                'due_date': timezone.datetime.fromtimestamp(invoice.due_date) if invoice.due_date else None,
                'paid_at': timezone.now(),
            }
        )
        
        logger.info(f"Pagamento processado para assinatura: {subscription_id}")
        
    except Subscription.DoesNotExist:
        logger.error(f"Assinatura não encontrada: {subscription_id}")
    except Exception as e:
        logger.error(f"Erro ao processar pagamento: {e}")

def handle_payment_failed(invoice):
    """Processa pagamento falhado"""
    subscription_id = invoice.subscription
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = 'past_due'
        subscription.start_grace_period(days=3)  # Grace period de 3 dias
        subscription.save()
        
        # Criar/atualizar fatura local
        Invoice.objects.update_or_create(
            stripe_invoice_id=invoice.id,
            defaults={
                'subscription': subscription,
                'stripe_customer_id': invoice.customer,
                'status': invoice.status,
                'amount_due': invoice.amount_due / 100,
                'amount_paid': invoice.amount_paid / 100,
                'amount_remaining': invoice.amount_remaining / 100,
                'currency': invoice.currency.upper(),
                'hosted_invoice_url': invoice.hosted_invoice_url,
                'invoice_pdf': invoice.invoice_pdf,
                'due_date': timezone.datetime.fromtimestamp(invoice.due_date) if invoice.due_date else None,
            }
        )
        
        logger.warning(f"Pagamento falhou para assinatura: {subscription_id}")
        
    except Subscription.DoesNotExist:
        logger.error(f"Assinatura não encontrada: {subscription_id}")
    except Exception as e:
        logger.error(f"Erro ao processar pagamento falhado: {e}")

def handle_payment_method_attached(payment_method):
    """Processa método de pagamento anexado"""
    try:
        customer_id = payment_method.customer
        
        # Buscar assinatura pelo customer ID
        subscription = Subscription.objects.get(stripe_customer_id=customer_id)
        
        # Atualizar informações do método de pagamento
        subscription.default_payment_method_last4 = payment_method.card.last4
        subscription.default_payment_method_brand = payment_method.card.brand
        subscription.default_payment_method_exp_month = payment_method.card.exp_month
        subscription.default_payment_method_exp_year = payment_method.card.exp_year
        subscription.save()
        
        logger.info(f"Método de pagamento atualizado para assinatura: {subscription.id}")
        
    except Subscription.DoesNotExist:
        logger.error(f"Assinatura não encontrada para customer: {customer_id}")
    except Exception as e:
        logger.error(f"Erro ao processar método de pagamento: {e}")
