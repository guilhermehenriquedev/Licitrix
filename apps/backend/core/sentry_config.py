"""
Configuração do Sentry para monitoramento de erros.
"""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from django.conf import settings

def init_sentry():
    """Inicializa o Sentry se a DSN estiver configurada."""
    if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.DJANGO_ENV if hasattr(settings, 'DJANGO_ENV') else 'development',
            
            # Integrações
            integrations=[
                DjangoIntegration(),
                CeleryIntegration(),
                RedisIntegration(),
            ],
            
            # Configurações de performance
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            
            # Configurações de contexto
            send_default_pii=False,
            
            # Filtros
            before_send=lambda event, hint: event,
            
            # Configurações de release
            release="1.0.0",
        )
