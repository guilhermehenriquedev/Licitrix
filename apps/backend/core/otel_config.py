"""
Configuração do OpenTelemetry para observabilidade.
"""

import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from django.conf import settings

def init_opentelemetry():
    """Inicializa o OpenTelemetry para observabilidade."""
    
    # Configuração de traces
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # Exportador de traces (console para desenvolvimento)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
    
    # Configuração de métricas
    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
    
    # Instrumentação automática
    if not settings.DEBUG:
        # Em produção, usar exportadores para sistemas como Jaeger/Prometheus
        pass
    
    # Instrumentação do Django
    DjangoInstrumentor().instrument()
    
    # Instrumentação do Redis
    RedisInstrumentor().instrument()
    
    # Instrumentação do PostgreSQL
    Psycopg2Instrumentor().instrument()
    
    return tracer
