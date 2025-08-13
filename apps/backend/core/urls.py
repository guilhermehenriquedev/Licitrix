"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls
from django_prometheus import exports

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('docs/', include('rest_framework.urls')),
    path('api/docs/', include_docs_urls(title='Licitrix API')),
    path('api/redoc/', include('rest_framework.urls')),
    
    # Prometheus metrics
    path('metrics/', exports.ExportToDjangoView, name='prometheus-django-metrics'),
    
    # Health check
    path('health/', include('core.health.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include tenant URLs
# path('api/', include('core.api.urls')),  # Removido - diretório não existe
    
# URLs de autenticação
urlpatterns += [
    path('api/users/', include('core.users.urls')),
]
