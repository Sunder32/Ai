"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import os
import requests
import logging

logger = logging.getLogger(__name__)

# AI Server configuration
AI_SERVER_URL = os.environ.get('AI_SERVER_URL', 'http://localhost:5050')


def serve_react_app(request):
    """Serve React SPA index.html for all frontend routes"""
    index_path = os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except FileNotFoundError:
        return HttpResponse('<h1>Frontend not built</h1><p>Run: cd frontend && npm run build</p>', status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint - проверка состояния всех сервисов
    Проверяет: Django API, База данных, AI-сервер (FastAPI/Ollama)
    """
    from django.db import connection
    
    health_status = {
        'status': 'healthy',
        'services': {
            'django_api': {'status': 'up', 'message': 'Django API is running'},
            'database': {'status': 'unknown', 'message': ''},
            'ai_server': {'status': 'unknown', 'message': ''},
            'ollama': {'status': 'unknown', 'message': ''}
        }
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = {
            'status': 'up',
            'message': 'Database connection is healthy',
            'backend': settings.DATABASES['default']['ENGINE']
        }
    except Exception as e:
        health_status['services']['database'] = {
            'status': 'down',
            'message': f'Database error: {str(e)}'
        }
        health_status['status'] = 'degraded'
    
    # Check AI server (FastAPI)
    try:
        response = requests.get(f'{AI_SERVER_URL}/', timeout=5)
        if response.status_code == 200:
            health_status['services']['ai_server'] = {
                'status': 'up',
                'message': 'AI server (FastAPI) is running',
                'url': AI_SERVER_URL
            }
        else:
            health_status['services']['ai_server'] = {
                'status': 'degraded',
                'message': f'AI server returned status {response.status_code}',
                'url': AI_SERVER_URL
            }
    except requests.exceptions.ConnectionError:
        health_status['services']['ai_server'] = {
            'status': 'down',
            'message': 'AI server is not running or unreachable',
            'url': AI_SERVER_URL,
            'hint': 'Start the AI server with: python AI/server/main.py'
        }
        health_status['status'] = 'degraded'
    except requests.exceptions.Timeout:
        health_status['services']['ai_server'] = {
            'status': 'timeout',
            'message': 'AI server request timed out',
            'url': AI_SERVER_URL
        }
        health_status['status'] = 'degraded'
    except Exception as e:
        health_status['services']['ai_server'] = {
            'status': 'error',
            'message': f'AI server error: {str(e)}'
        }
        health_status['status'] = 'degraded'
    
    # Check Ollama service
    try:
        ollama_response = requests.get('http://localhost:11434/api/version', timeout=5)
        if ollama_response.status_code == 200:
            version_info = ollama_response.json()
            health_status['services']['ollama'] = {
                'status': 'up',
                'message': 'Ollama is running',
                'version': version_info.get('version', 'unknown')
            }
        else:
            health_status['services']['ollama'] = {
                'status': 'degraded',
                'message': f'Ollama returned status {ollama_response.status_code}'
            }
    except requests.exceptions.ConnectionError:
        health_status['services']['ollama'] = {
            'status': 'down',
            'message': 'Ollama is not running',
            'hint': 'Start Ollama with: ollama serve'
        }
        health_status['status'] = 'degraded'
    except Exception as e:
        health_status['services']['ollama'] = {
            'status': 'error',
            'message': f'Ollama error: {str(e)}'
        }
    
    return Response(health_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root endpoint - список всех доступных API endpoints
    """
    return Response({
        'message': 'AI PC Configurator API',
        'version': '1.0',
        'endpoints': {
            'accounts': request.build_absolute_uri('/api/accounts/'),
            'computers': request.build_absolute_uri('/api/computers/'),
            'peripherals': request.build_absolute_uri('/api/peripherals/'),
            'recommendations': request.build_absolute_uri('/api/recommendations/'),
            'health': request.build_absolute_uri('/api/health/'),
            'documentation': request.build_absolute_uri('/api/docs/'),
            'schema': request.build_absolute_uri('/api/schema/'),
        },
        'auth': {
            'login': request.build_absolute_uri('/api/accounts/login/'),
            'register': request.build_absolute_uri('/api/accounts/register/'),
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health check endpoint
    path('api/health/', health_check, name='health-check'),
    
    # API root
    path('api/', api_root, name='api-root'),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/computers/', include('computers.urls')),
    path('api/peripherals/', include('peripherals.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    
    # SSE events for real-time updates
    path('api/events/', include('django_eventstream.urls'), {'channels': ['tasks']}),
    
    # API authentication
    path('api-auth/', include('rest_framework.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve React app for all non-API routes (must be last!)
# This catches all routes that don't match API or static files
urlpatterns += [
    re_path(r'^(?!api|admin|static|media).*$', serve_react_app, name='react-app'),
]
