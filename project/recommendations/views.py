import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .models import PCConfiguration, WorkspaceSetup, Recommendation
from .serializers import (
    PCConfigurationSerializer, WorkspaceSetupSerializer, 
    RecommendationSerializer, ConfigurationRequestSerializer
)
from .services import ConfigurationService


logger = logging.getLogger(__name__)

try:
    from .ai_service import AIConfigurationService
except ImportError:
    AIConfigurationService = None
    logger.warning("AIConfigurationService not available")

try:
    from .generative_ai_service import GenerativeAIService
except ImportError:
    GenerativeAIService = None
    logger.warning("GenerativeAIService not available")


class PCConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления конфигурациями ПК"""
    queryset = PCConfiguration.objects.all()
    serializer_class = PCConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Пользователи видят только свои конфигурации"""
        base_queryset = PCConfiguration.objects.select_related(
            'user',
            'cpu',
            'gpu',
            'motherboard',
            'ram',
            'storage_primary',
            'storage_secondary',
            'psu',
            'case',
            'cooling'
        ).prefetch_related('recommendations')
        
        if self.request.user.is_staff:
            return base_queryset
        return base_queryset.filter(user=self.request.user)
    
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
    
    @method_decorator(ratelimit(key='user', rate='3/m', method='POST'))
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Генерация конфигурации на основе профиля пользователя
        Rate limit: 3 запроса в минуту на пользователя
        
        Параметры:
        - include_workspace: bool - включить ли подбор периферии и рабочего места (по умолчанию False)
        - use_ai: bool - использовать ли AI для подбора (по умолчанию False)
        """
        serializer = ConfigurationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем дополнительные параметры
        include_workspace = serializer.validated_data.get('include_workspace', False)
        use_ai = serializer.validated_data.get('use_ai', False)
        ai_generation_mode = serializer.validated_data.get('ai_generation_mode', 'database')
        peripheral_budget_percent = serializer.validated_data.get('peripheral_budget_percent', 30)
        
        logger.info(f"Configuration generation request: include_workspace={include_workspace}, use_ai={use_ai}, ai_generation_mode={ai_generation_mode}, peripheral_budget={peripheral_budget_percent}%")
        
        try:
            # Выбор режима генерации
            if use_ai and ai_generation_mode == 'generative' and GenerativeAIService:
                # Полностью генеративный режим - AI создает компоненты
                logger.info("Using fully generative AI mode")
                generative_service = GenerativeAIService(serializer.validated_data)
                configuration, ai_info = generative_service.generate_configuration(request.user)
                
                if not configuration:
                    return Response(
                        {'error': ai_info.get('error', 'AI не смог сгенерировать конфигурацию')},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Проверяем совместимость сгенерированных компонентов
                compat_service = ConfigurationService({
                    'user_type': 'student',
                    'min_budget': 0,
                    'max_budget': 0
                })
                compat_service.check_compatibility(configuration)
                
                # Формируем ответ
                result_serializer = PCConfigurationSerializer(configuration)
                response_data = result_serializer.data
                response_data['ai_info'] = ai_info
                
                logger.info(f"Returning generative AI configuration ID: {response_data.get('id')} with total: {response_data.get('total_price')}")
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            else:
                # Режим выбора из БД (с опциональным AI-анализом)
                logger.info(f"Using database selection mode (AI analysis: {use_ai})")
                service = ConfigurationService(serializer.validated_data, use_ai=use_ai)
                configuration, workspace = service.generate_configuration(
                    request.user, 
                    include_workspace=include_workspace
                )
                service.check_compatibility(configuration)
                
                # Формируем ответ
                result_serializer = PCConfigurationSerializer(configuration)
                response_data = result_serializer.data
                
                if workspace:
                    workspace_serializer = WorkspaceSetupSerializer(workspace)
                    response_data['workspace'] = workspace_serializer.data
                    logger.info(f"Workspace included in response: ${workspace.total_price}")
                
                response_data['ai_info'] = {
                    "ai_used": use_ai and service.ai_service is not None,
                    "generation_mode": "database",
                    "summary": "Конфигурация подобрана с использованием AI" if (use_ai and service.ai_service) else "Конфигурация подобрана алгоритмически"
                }
                
                logger.info(f"Returning configuration ID: {response_data.get('id')} with total: {response_data.get('total_price')}")
                return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.exception(f"Configuration generation error: {str(e)}")
            return Response(
                {'error': f'Ошибка при генерации конфигурации: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @method_decorator(ratelimit(key='ip', rate='10/m', method='GET'))
    @action(detail=False, methods=['get'])
    def ai_status(self, request):
        """Проверить статус ИИ сервиса. Rate limit: 10 запросов/мин на IP"""
        ai_service = AIConfigurationService({})
        available = ai_service.check_ollama_available()
        return Response({
            'ai_available': available,
            'model': 'deepseek-r1:8b' if available else None
        })


class WorkspaceSetupViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рабочими местами"""
    queryset = WorkspaceSetup.objects.all()
    serializer_class = WorkspaceSetupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Пользователи видят только свои рабочие места"""
        base_queryset = WorkspaceSetup.objects.select_related(
            'user',
            'configuration',
            'monitor_primary',
            'monitor_secondary',
            'keyboard',
            'mouse',
            'headset',
            'webcam',
            'microphone',
            'desk',
            'chair'
        )
        
        if self.request.user.is_staff:
            return base_queryset
        return base_queryset.filter(user=self.request.user)
    
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
