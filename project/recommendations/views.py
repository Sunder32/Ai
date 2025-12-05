import logging
import secrets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .models import PCConfiguration, WorkspaceSetup, Recommendation
from .serializers import (
    PCConfigurationSerializer, WorkspaceSetupSerializer, 
    RecommendationSerializer, ConfigurationRequestSerializer,
    BuilderConfigurationSerializer, PublicConfigurationSerializer
)
from .services import ConfigurationService
from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
from peripherals.models import (
    Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair,
    Speakers, Mousepad, MonitorArm, USBHub, DeskLighting, StreamDeck,
    CaptureCard, Gamepad, Headphonestand
)


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

try:
    from .ai_full_config_service import AIFullConfigService
except ImportError:
    AIFullConfigService = None
    logger.warning("AIFullConfigService not available")


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
        Генерация конфигурации с помощью AI
        Rate limit: 3 запроса в минуту на пользователя
        
        AI создаёт полную конфигурацию: ПК + периферия + рабочее место
        на основе актуальных данных о комплектующих.
        """
        serializer = ConfigurationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем параметры
        data = serializer.validated_data
        include_workspace = data.get('include_workspace', True)
        
        logger.info(f"AI Configuration generation request: user_type={data.get('user_type')}, budget={data.get('min_budget')}-{data.get('max_budget')}, include_workspace={include_workspace}")
        
        try:
            # Всегда используем AI генерацию
            if not AIFullConfigService:
                return Response(
                    {'error': 'AI сервис недоступен'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            logger.info("Using AI generation mode (PC + Peripherals + Workspace)")
            
            # Создаем сервис AI генерации
            full_ai_service = AIFullConfigService(
                user_type=data.get('user_type', 'gaming'),
                min_budget=float(data.get('min_budget', 50000)),
                max_budget=float(data.get('max_budget', 150000)),
                priority=data.get('priority', 'balanced'),
                requirements={
                    'gaming': data.get('gaming', False),
                    'streaming': data.get('streaming', False),
                    'video_editing': data.get('video_editing', False),
                    'multitasking': data.get('multitasking', False),
                    'work_with_4k': data.get('work_with_4k', False),
                    'vr_support': data.get('vr_support', False),
                    'programming': data.get('programming', False),
                    'office_work': data.get('office_work', False),
                },
                pc_preferences={
                    'preferred_cpu_manufacturer': data.get('preferred_cpu_manufacturer', 'any'),
                    'preferred_gpu_manufacturer': data.get('preferred_gpu_manufacturer', 'any'),
                    'min_cpu_cores': data.get('min_cpu_cores', 4),
                    'min_gpu_vram': data.get('min_gpu_vram', 4),
                    'min_ram_capacity': data.get('min_ram_capacity', 16),
                    'storage_type_preference': data.get('storage_type_preference', 'nvme'),
                    'min_storage_capacity': data.get('min_storage_capacity', 512),
                    'cooling_preference': data.get('cooling_preference', 'any'),
                    'rgb_preference': data.get('rgb_preference', False),
                    'case_size_preference': data.get('case_size_preference', 'any'),
                },
                peripherals_preferences={
                    'need_monitor': data.get('need_monitor', True),
                    'need_keyboard': data.get('need_keyboard', True),
                    'need_mouse': data.get('need_mouse', True),
                    'need_headset': data.get('need_headset', True),
                    'monitor_min_refresh_rate': data.get('monitor_min_refresh_rate', 60),
                    'monitor_min_resolution': data.get('monitor_min_resolution', '1080p'),
                    'keyboard_type_preference': data.get('keyboard_type_preference', 'any'),
                    'mouse_wireless': data.get('mouse_wireless', False),
                },
                workspace_preferences={
                    'need_desk': data.get('need_desk', True),
                    'need_chair': data.get('need_chair', True),
                    'chair_ergonomic': data.get('chair_ergonomic', True),
                },
                include_peripherals=True,  # Всегда включаем периферию
                include_workspace=include_workspace,
            )
            
            # Генерируем полную конфигурацию
            configuration, workspace, ai_info = full_ai_service.generate_full_configuration(request.user)
            
            if not configuration:
                return Response(
                    {'error': ai_info.get('error', 'AI не смог сгенерировать конфигурацию')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Формируем ответ
            result_serializer = PCConfigurationSerializer(configuration)
            response_data = result_serializer.data
            response_data['ai_info'] = ai_info
            
            if workspace:
                workspace_serializer = WorkspaceSetupSerializer(workspace)
                response_data['workspace'] = workspace_serializer.data
                logger.info(f"Workspace included: {workspace.total_price} RUB")
            
            logger.info(f"AI configuration created ID: {response_data.get('id')}, total: {ai_info.get('prices', {}).get('total', 0)} RUB")
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
    
    @action(detail=False, methods=['post'])
    def save_build(self, request):
        """Сохранение сборки из Build Yourself"""
        serializer = BuilderConfigurationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # Получаем компоненты по ID
            config_data = {
                'user': request.user,
                'name': data.get('name', 'Моя сборка'),
                'is_saved': True,
                'is_public': data.get('is_public', False),
            }
            
            # PC компоненты
            if data.get('cpu'):
                config_data['cpu'] = CPU.objects.get(id=data['cpu'])
            if data.get('gpu'):
                config_data['gpu'] = GPU.objects.get(id=data['gpu'])
            if data.get('motherboard'):
                config_data['motherboard'] = Motherboard.objects.get(id=data['motherboard'])
            if data.get('ram'):
                config_data['ram'] = RAM.objects.get(id=data['ram'])
            if data.get('storage_primary'):
                config_data['storage_primary'] = Storage.objects.get(id=data['storage_primary'])
            if data.get('storage_secondary'):
                config_data['storage_secondary'] = Storage.objects.get(id=data['storage_secondary'])
            if data.get('psu'):
                config_data['psu'] = PSU.objects.get(id=data['psu'])
            if data.get('case'):
                config_data['case'] = Case.objects.get(id=data['case'])
            if data.get('cooling'):
                config_data['cooling'] = Cooling.objects.get(id=data['cooling'])
            
            # Создаем конфигурацию
            configuration = PCConfiguration.objects.create(**config_data)
            configuration.calculate_total_price()
            
            # Генерируем share_code если публичная
            if data.get('is_public'):
                configuration.share_code = secrets.token_urlsafe(16)
            
            configuration.save()
            
            # Создаем workspace setup если есть периферия
            has_peripherals = any([
                data.get('monitor_primary'), data.get('monitor_secondary'),
                data.get('keyboard'), data.get('mouse'), data.get('headset'),
                data.get('webcam'), data.get('microphone'), data.get('desk'),
                data.get('chair'), data.get('speakers'), data.get('mousepad'),
                data.get('monitor_arm'), data.get('usb_hub'), data.get('lighting'),
                data.get('stream_deck'), data.get('capture_card'), data.get('gamepad'),
                data.get('headphone_stand')
            ])
            
            workspace = None
            if has_peripherals:
                workspace_data = {
                    'user': request.user,
                    'configuration': configuration,
                    'name': f"Рабочее место: {data.get('name', 'Моя сборка')}",
                }
                
                # Базовая периферия
                if data.get('monitor_primary'):
                    workspace_data['monitor_primary'] = Monitor.objects.get(id=data['monitor_primary'])
                if data.get('monitor_secondary'):
                    workspace_data['monitor_secondary'] = Monitor.objects.get(id=data['monitor_secondary'])
                if data.get('keyboard'):
                    workspace_data['keyboard'] = Keyboard.objects.get(id=data['keyboard'])
                if data.get('mouse'):
                    workspace_data['mouse'] = Mouse.objects.get(id=data['mouse'])
                if data.get('headset'):
                    workspace_data['headset'] = Headset.objects.get(id=data['headset'])
                if data.get('webcam'):
                    workspace_data['webcam'] = Webcam.objects.get(id=data['webcam'])
                if data.get('microphone'):
                    workspace_data['microphone'] = Microphone.objects.get(id=data['microphone'])
                if data.get('desk'):
                    workspace_data['desk'] = Desk.objects.get(id=data['desk'])
                if data.get('chair'):
                    workspace_data['chair'] = Chair.objects.get(id=data['chair'])
                
                # Дополнительная периферия
                if data.get('speakers'):
                    workspace_data['speakers'] = Speakers.objects.get(id=data['speakers'])
                if data.get('mousepad'):
                    workspace_data['mousepad'] = Mousepad.objects.get(id=data['mousepad'])
                if data.get('monitor_arm'):
                    workspace_data['monitor_arm'] = MonitorArm.objects.get(id=data['monitor_arm'])
                if data.get('usb_hub'):
                    workspace_data['usb_hub'] = USBHub.objects.get(id=data['usb_hub'])
                if data.get('lighting'):
                    workspace_data['lighting'] = DeskLighting.objects.get(id=data['lighting'])
                if data.get('stream_deck'):
                    workspace_data['stream_deck'] = StreamDeck.objects.get(id=data['stream_deck'])
                if data.get('capture_card'):
                    workspace_data['capture_card'] = CaptureCard.objects.get(id=data['capture_card'])
                if data.get('gamepad'):
                    workspace_data['gamepad'] = Gamepad.objects.get(id=data['gamepad'])
                if data.get('headphone_stand'):
                    workspace_data['headphone_stand'] = Headphonestand.objects.get(id=data['headphone_stand'])
                
                workspace = WorkspaceSetup.objects.create(**workspace_data)
                workspace.calculate_total_price()
                workspace.save()
            
            # Формируем ответ
            result = PCConfigurationSerializer(configuration).data
            if workspace:
                result['workspace'] = WorkspaceSetupSerializer(workspace).data
            
            result['share_url'] = f"/build/{configuration.share_code}" if configuration.share_code else None
            
            return Response(result, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception(f"Error saving build: {str(e)}")
            return Response(
                {'error': f'Ошибка при сохранении сборки: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='public/(?P<share_code>[^/.]+)', permission_classes=[AllowAny])
    def public_build(self, request, share_code=None):
        """Получение публичной сборки по share_code"""
        try:
            configuration = PCConfiguration.objects.select_related(
                'cpu', 'gpu', 'motherboard', 'ram', 'storage_primary',
                'storage_secondary', 'psu', 'case', 'cooling'
            ).get(share_code=share_code, is_public=True)
            
            return Response(PublicConfigurationSerializer(configuration).data)
            
        except PCConfiguration.DoesNotExist:
            return Response(
                {'error': 'Сборка не найдена или недоступна'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def my_builds(self, request):
        """Получение всех сохраненных сборок пользователя"""
        configurations = PCConfiguration.objects.filter(
            user=request.user, is_saved=True
        ).select_related(
            'cpu', 'gpu', 'motherboard', 'ram', 'storage_primary',
            'storage_secondary', 'psu', 'case', 'cooling'
        ).order_by('-created_at')
        
        return Response(PCConfigurationSerializer(configurations, many=True).data)
    
    @action(detail=False, methods=['get'])
    def compare(self, request):
        """Сравнение нескольких сборок"""
        ids = request.query_params.getlist('ids')
        
        if not ids or len(ids) < 2:
            return Response(
                {'error': 'Укажите минимум 2 ID для сравнения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            configurations = PCConfiguration.objects.filter(
                id__in=ids
            ).select_related(
                'cpu', 'gpu', 'motherboard', 'ram', 'storage_primary',
                'storage_secondary', 'psu', 'case', 'cooling'
            )
            
            # Проверяем доступ
            for config in configurations:
                if config.user != request.user and not config.is_public:
                    return Response(
                        {'error': f'Нет доступа к сборке {config.id}'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            return Response(PCConfigurationSerializer(configurations, many=True).data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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
