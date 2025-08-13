"""
Configurações adicionais do Celery.
"""

from celery import Celery
from django.conf import settings

# Configurações de retry
CELERY_TASK_ANNOTATIONS = {
    '*': {
        'retry_backoff': True,
        'retry_backoff_max': 600,
        'max_retries': 3,
    }
}

# Configurações de rate limiting
CELERY_TASK_ROUTES = {
    'modules.oportunidades.tasks.processar_edital_task': {'queue': 'edital_processing'},
    'modules.oportunidades.tasks.criar_oportunidades_para_tenants': {'queue': 'oportunidade_creation'},
    'modules.documentos.tasks.gerar_documento_task': {'queue': 'document_generation'},
    'modules.financeiro.tasks.enviar_lembretes_cobranca': {'queue': 'notifications'},
}

# Configurações de filas
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_CREATE_MISSING_QUEUES = True

# Configurações de worker
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Configurações de resultado
CELERY_RESULT_EXPIRES = 3600  # 1 hora
CELERY_RESULT_PERSISTENT = True

# Configurações de beat
CELERY_BEAT_SCHEDULER = 'celery.beat.PersistentScheduler'
CELERY_BEAT_MAX_LOOP_INTERVAL = 300  # 5 minutos

# Configurações de monitoramento
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
