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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


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
    
    # API root
    path('api/', api_root, name='api-root'),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/computers/', include('computers.urls')),
    path('api/peripherals/', include('peripherals.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    
    # API authentication
    path('api-auth/', include('rest_framework.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
