"""
Configuração do app financeiro.
"""
from django.apps import AppConfig

class FinanceiroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.financeiro'
    verbose_name = 'Financeiro'
