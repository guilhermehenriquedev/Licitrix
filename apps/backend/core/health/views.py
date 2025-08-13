"""
Health check views.
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import redis
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """Basic health check."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'licitrix-api',
        'version': '1.0.0'
    })

def database_check(request):
    """Database health check."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'postgresql',
            'message': 'Database connection successful'
        })
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'postgresql',
            'error': str(e)
        }, status=500)

def redis_check(request):
    """Redis health check."""
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        
        return JsonResponse({
            'status': 'healthy',
            'redis': 'connected',
            'message': 'Redis connection successful'
        })
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'redis': 'disconnected',
            'error': str(e)
        }, status=500)
