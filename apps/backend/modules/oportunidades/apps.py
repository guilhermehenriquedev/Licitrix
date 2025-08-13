"""
Configuração do app oportunidades.
"""
from django.apps import AppConfig

class OportunidadesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.oportunidades'
    verbose_name = 'Oportunidades'
