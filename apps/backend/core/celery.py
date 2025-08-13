"""
Configuração do Celery para o projeto Licitrix.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('licitrix')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'processar-editais-pendentes': {
        'task': 'modules.oportunidades.tasks.processar_editais_pendentes',
        'schedule': 300.0,  # 5 minutos
    },
    'enviar-lembretes-cobranca': {
        'task': 'modules.financeiro.tasks.enviar_lembretes_cobranca',
        'schedule': 3600.0,  # 1 hora
    },
    'atualizar-status-contratos': {
        'task': 'modules.contratos.tasks.atualizar_status_contratos',
        'schedule': 86400.0,  # 1 dia
    },
    'limpar-logs-antigos': {
        'task': 'core.tasks.limpar_logs_antigos',
        'schedule': 604800.0,  # 1 semana
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Task de debug para testar o Celery."""
    print(f'Request: {self.request!r}')
