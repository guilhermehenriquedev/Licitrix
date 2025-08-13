import stripe
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from ..models import User, Subscription, Invoice

logger = logging.getLogger(__name__)

class StripeService:
    """Serviço para gerenciar operações do Stripe"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.price_id = settings.STRIPE_PRICE_ID
    
    def create_customer(self, user):
        """Cria ou recupera um customer no Stripe"""
        try:
            if user.stripe_customer_id:
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
                # Atualizar informações do customer
                customer = stripe.Customer.modify(
                    user.stripe_customer_id,
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}",
                    metadata={'user_id': str(user.id)}
                )
            else:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}",
                    metadata={'user_id': str(user.id)}
                )
                user.stripe_customer_id = customer.id
                user.save(update_fields=['stripe_customer_id'])
            
            return customer
        except Exception as e:
            logger.error(f"Erro ao criar/recuperar customer: {e}")
            raise
    
    def create_checkout_session(self, user, success_url, cancel_url):
        """Cria uma sessão de checkout para assinatura"""
        try:
            customer = self.create_customer(user)
            
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': self.price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={'user_id': str(user.id)},
                subscription_data={
                    'metadata': {'user_id': str(user.id)},
                },
                allow_promotion_codes=True,
            )
            
            logger.info(f"Checkout session criada para usuário: {user.email}")
            return checkout_session
            
        except Exception as e:
            logger.error(f"Erro ao criar checkout session: {e}")
            raise
    
    def create_customer_portal_session(self, user, return_url):
        """Cria uma sessão do Customer Portal"""
        try:
            if not user.stripe_customer_id:
                raise ValueError("Usuário não possui customer ID do Stripe")
            
            portal_session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=return_url,
            )
            
            logger.info(f"Portal session criada para usuário: {user.email}")
            return portal_session
            
        except Exception as e:
            logger.error(f"Erro ao criar portal session: {e}")
            raise
    
    def cancel_subscription(self, subscription_id, at_period_end=True):
        """Cancela uma assinatura"""
        try:
            if at_period_end:
                # Cancelar ao fim do período
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                # Cancelar imediatamente
                subscription = stripe.Subscription.cancel(subscription_id)
            
            logger.info(f"Assinatura {subscription_id} cancelada")
            return subscription
            
        except Exception as e:
            logger.error(f"Erro ao cancelar assinatura: {e}")
            raise
    
    def reactivate_subscription(self, subscription_id):
        """Reativa uma assinatura cancelada ao fim do período"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
            
            logger.info(f"Assinatura {subscription_id} reativada")
            return subscription
            
        except Exception as e:
            logger.error(f"Erro ao reativar assinatura: {e}")
            raise
    
    def update_payment_method(self, subscription_id, payment_method_id):
        """Atualiza o método de pagamento de uma assinatura"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                default_payment_method=payment_method_id
            )
            
            logger.info(f"Método de pagamento atualizado para assinatura: {subscription_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Erro ao atualizar método de pagamento: {e}")
            raise
    
    def get_subscription(self, subscription_id):
        """Recupera uma assinatura do Stripe"""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except Exception as e:
            logger.error(f"Erro ao recuperar assinatura: {e}")
            raise
    
    def get_customer(self, customer_id):
        """Recupera um customer do Stripe"""
        try:
            return stripe.Customer.retrieve(customer_id)
        except Exception as e:
            logger.error(f"Erro ao recuperar customer: {e}")
            raise
    
    def get_invoice(self, invoice_id):
        """Recupera uma fatura do Stripe"""
        try:
            return stripe.Invoice.retrieve(invoice_id)
        except Exception as e:
            logger.error(f"Erro ao recuperar fatura: {e}")
            raise
    
    def list_invoices(self, customer_id, limit=10):
        """Lista faturas de um customer"""
        try:
            return stripe.Invoice.list(
                customer=customer_id,
                limit=limit,
                status='all'
            )
        except Exception as e:
            logger.error(f"Erro ao listar faturas: {e}")
            raise
    
    def create_invoice(self, customer_id, subscription_id):
        """Cria uma fatura para um customer"""
        try:
            invoice = stripe.Invoice.create(
                customer=customer_id,
                subscription=subscription_id,
                auto_advance=True
            )
            
            logger.info(f"Fatura criada: {invoice.id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Erro ao criar fatura: {e}")
            raise
    
    def finalize_invoice(self, invoice_id):
        """Finaliza uma fatura para envio"""
        try:
            invoice = stripe.Invoice.finalize_invoice(invoice_id)
            
            logger.info(f"Fatura finalizada: {invoice_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Erro ao finalizar fatura: {e}")
            raise
    
    def send_invoice(self, invoice_id):
        """Envia uma fatura por email"""
        try:
            invoice = stripe.Invoice.send_invoice(invoice_id)
            
            logger.info(f"Fatura enviada: {invoice_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Erro ao enviar fatura: {e}")
            raise
    
    def mark_invoice_as_paid(self, invoice_id):
        """Marca uma fatura como paga"""
        try:
            invoice = stripe.Invoice.pay(invoice_id)
            
            logger.info(f"Fatura marcada como paga: {invoice_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Erro ao marcar fatura como paga: {e}")
            raise
    
    def create_refund(self, charge_id, amount=None, reason='requested_by_customer'):
        """Cria um reembolso"""
        try:
            refund_data = {
                'charge': charge_id,
                'reason': reason
            }
            
            if amount:
                refund_data['amount'] = amount
            
            refund = stripe.Refund.create(**refund_data)
            
            logger.info(f"Reembolso criado: {refund.id}")
            return refund
            
        except Exception as e:
            logger.error(f"Erro ao criar reembolso: {e}")
            raise
    
    def get_payment_intent(self, payment_intent_id):
        """Recupera um Payment Intent"""
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except Exception as e:
            logger.error(f"Erro ao recuperar Payment Intent: {e}")
            raise
    
    def confirm_payment_intent(self, payment_intent_id, payment_method_id):
        """Confirma um Payment Intent"""
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method_id
            )
            
            logger.info(f"Payment Intent confirmado: {payment_intent_id}")
            return payment_intent
            
        except Exception as e:
            logger.error(f"Erro ao confirmar Payment Intent: {e}")
            raise
