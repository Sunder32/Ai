from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PCConfiguration, WorkspaceSetup, Recommendation
from .serializers import (
    PCConfigurationSerializer, WorkspaceSetupSerializer, 
    RecommendationSerializer, ConfigurationRequestSerializer
)
from .services import ConfigurationService


class PCConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления конфигурациями ПК"""
    queryset = PCConfiguration.objects.all()
    serializer_class = PCConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Пользователи видят только свои конфигурации"""
        if self.request.user.is_staff:
            return PCConfiguration.objects.all()
        return PCConfiguration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Автоматически привязываем конфигурацию к текущему пользователю"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def check_compatibility(self, request, pk=None):
        """Проверка совместимости компонентов конфигурации"""
        configuration = self.get_object()
        service = ConfigurationService({
            'user_type': request.user.user_type or 'student',
            'min_budget': 0,
            'max_budget': 0,
            'priority': 'performance'
        })
        
        is_compatible, issues = service.check_compatibility(configuration)
        
        return Response({
            'compatible': is_compatible,
            'issues': issues,
            'notes': configuration.compatibility_notes
        })
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Генерация конфигурации на основе профиля пользователя"""
        serializer = ConfigurationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Создание сервиса подбора конфигурации
        service = ConfigurationService(serializer.validated_data)
        
        try:
            configuration = service.generate_configuration(request.user)
            service.check_compatibility(configuration)
            
            result_serializer = PCConfigurationSerializer(configuration)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Ошибка при генерации конфигурации: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkspaceSetupViewSet(viewsets.ModelViewSet):
    """ViewSet для управления настройками рабочего места"""
    queryset = WorkspaceSetup.objects.all()
    serializer_class = WorkspaceSetupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Пользователи видят только свои настройки"""
        if self.request.user.is_staff:
            return WorkspaceSetup.objects.all()
        return WorkspaceSetup.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Автоматически привязываем настройку к текущему пользователю"""
        serializer.save(user=self.request.user)


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра рекомендаций"""
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Пользователи видят только свои рекомендации"""
        if self.request.user.is_staff:
            return Recommendation.objects.all()
        return Recommendation.objects.filter(configuration__user=self.request.user)
