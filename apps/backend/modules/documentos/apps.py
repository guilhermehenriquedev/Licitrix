"""
Configuração do app documentos.
"""
from django.apps import AppConfig

class DocumentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.documentos'
    verbose_name = 'Documentos'
