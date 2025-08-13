"""
Health check URLs.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('db/', views.database_check, name='database_check'),
    path('redis/', views.redis_check, name='redis_check'),
]
