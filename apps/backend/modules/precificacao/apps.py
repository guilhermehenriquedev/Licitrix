"""
Configuração do app precificação.
"""
from django.apps import AppConfig

class PrecificacaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.precificacao'
    verbose_name = 'Precificação'
