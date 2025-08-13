"""
Configuração do Unleash para feature flags.
"""

import os
from unleash import Client
from django.conf import settings

# Cliente Unleash para feature flags
unleash_client = None

def init_unleash():
    """Inicializa o cliente Unleash."""
    global unleash_client
    
    if hasattr(settings, 'UNLEASH_URL') and settings.UNLEASH_URL:
        try:
            unleash_client = Client(
                url=settings.UNLEASH_URL,
                app_name=settings.UNLEASH_APP_NAME,
                instance_id=settings.UNLEASH_INSTANCE_ID,
                refresh_interval=15,
                metrics_interval=60,
                disable_metrics=False,
                disable_registration=False,
                custom_headers={},
                custom_options={},
                cache_directory=None,
                project_name=None,
                environment=None,
            )
        except Exception as e:
            print(f"Erro ao inicializar Unleash: {e}")
            unleash_client = None

def is_feature_enabled(feature_name: str, user_id: str = None, context: dict = None) -> bool:
    """
    Verifica se uma feature está habilitada.
    
    Args:
        feature_name: Nome da feature
        user_id: ID do usuário (opcional)
        context: Contexto adicional (opcional)
    
    Returns:
        True se a feature estiver habilitada, False caso contrário
    """
    if not unleash_client:
        return False
    
    try:
        return unleash_client.is_enabled(
            feature_name,
            user_id=user_id,
            properties=context or {}
        )
    except Exception:
        return False

def get_feature_variant(feature_name: str, user_id: str = None, context: dict = None):
    """
    Obtém a variante de uma feature.
    
    Args:
        feature_name: Nome da feature
        user_id: ID do usuário (opcional)
        context: Contexto adicional (opcional)
    
    Returns:
        Variante da feature ou None se não estiver habilitada
    """
    if not unleash_client:
        return None
    
    try:
        return unleash_client.get_variant(
            feature_name,
            user_id=user_id,
            properties=context or {}
        )
    except Exception:
        return None
