from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Autenticação
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # Perfil e status
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('status/', views.UserStatusView.as_view(), name='status'),
    
    # Reset de senha
    path('auth/password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('auth/password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Assinaturas
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscription_list'),
    path('subscription/create-checkout-session/', views.create_stripe_checkout_session, name='create_checkout_session'),
    path('subscription/create-portal-session/', views.create_customer_portal_session, name='create_portal_session'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('subscription/reactivate/', views.reactivate_subscription, name='reactivate_subscription'),
    path('subscription/invoices/', views.list_invoices, name='list_invoices'),
    
    # Webhook Stripe
    path('subscription/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
