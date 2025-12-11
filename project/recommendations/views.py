import logging
import secrets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.core.cache import cache, caches
from django.http import HttpResponse
from django.db import models as db_models
from .models import PCConfiguration, WorkspaceSetup, Recommendation, Wishlist, AILog
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

# Import export services
try:
    from .export_service import ConfigurationExportService, PowerCalculatorService, CompatibilityChecker
    EXPORT_SERVICE_AVAILABLE = True
except ImportError:
    EXPORT_SERVICE_AVAILABLE = False

# Import AI enhancement services
try:
    from .price_service import PriceParserService
    PRICE_SERVICE_AVAILABLE = True
except ImportError:
    PRICE_SERVICE_AVAILABLE = False

try:
    from .ai_validator import AIValidator, AlgorithmicFallback, AILogger
    AI_VALIDATOR_AVAILABLE = True
except ImportError:
    AI_VALIDATOR_AVAILABLE = False

try:
    from .personalization_service import PersonalizationService
    PERSONALIZATION_AVAILABLE = True
except ImportError:
    PERSONALIZATION_AVAILABLE = False

try:
    from .chat_service import AIChatService
    CHAT_SERVICE_AVAILABLE = True
except ImportError:
    CHAT_SERVICE_AVAILABLE = False



try:
    from .store_integration import (
        StoreIntegrationService, PriceHistoryService,
        get_store_links_for_configuration, get_price_history_data
    )
    STORE_SERVICE_AVAILABLE = True
except ImportError:
    STORE_SERVICE_AVAILABLE = False

try:
    from .benchmark_service import (
        BenchmarkService, FPSPredictionService, ConfigurationPerformanceAnalyzer,
        get_benchmarks_for_cpu, get_benchmarks_for_gpu, predict_game_fps,
        get_available_games, analyze_configuration_performance
    )
    BENCHMARK_SERVICE_AVAILABLE = True
except ImportError:
    BENCHMARK_SERVICE_AVAILABLE = False


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
    
    @method_decorator(ratelimit(key='user', rate='5/m', method='POST'))
    @action(detail=False, methods=['post'])
    def generate_async(self, request):
        """
        Асинхронная генерация конфигурации с помощью Celery.
        Возвращает task_id для отслеживания прогресса.
        
        Используйте для длительных AI запросов.
        Статус можно проверить через /api/recommendations/configurations/task_status/?task_id=XXX
        """
        serializer = ConfigurationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Prepare config params for Celery task
        config_params = {
            'user_type': data.get('user_type', 'gaming'),
            'min_budget': float(data.get('min_budget', 50000)),
            'max_budget': float(data.get('max_budget', 150000)),
            'priority': data.get('priority', 'balanced'),
            'requirements': {
                'gaming': data.get('gaming', False),
                'streaming': data.get('streaming', False),
                'video_editing': data.get('video_editing', False),
                'multitasking': data.get('multitasking', False),
                'work_with_4k': data.get('work_with_4k', False),
                'vr_support': data.get('vr_support', False),
                'programming': data.get('programming', False),
                'office_work': data.get('office_work', False),
            },
            'pc_preferences': {
                'preferred_cpu_manufacturer': data.get('preferred_cpu_manufacturer', 'any'),
                'preferred_gpu_manufacturer': data.get('preferred_gpu_manufacturer', 'any'),
                'min_cpu_cores': data.get('min_cpu_cores', 4),
                'min_gpu_vram': data.get('min_gpu_vram', 4),
                'min_ram_capacity': data.get('min_ram_capacity', 16),
            },
            'peripherals_preferences': {
                'need_monitor': data.get('need_monitor', True),
                'need_keyboard': data.get('need_keyboard', True),
                'need_mouse': data.get('need_mouse', True),
                'need_headset': data.get('need_headset', True),
            },
            'workspace_preferences': {
                'need_desk': data.get('need_desk', True),
                'need_chair': data.get('need_chair', True),
            },
            'include_peripherals': True,
            'include_workspace': data.get('include_workspace', True),
        }
        
        try:
            from .tasks import generate_ai_configuration
            
            # Start async task
            task = generate_ai_configuration.delay(request.user.id, config_params)
            
            logger.info(f"Started async AI generation task: {task.id}")
            
            return Response({
                'task_id': task.id,
                'status': 'pending',
                'message': 'AI generation started. Check status with task_id.',
                'check_url': f'/api/recommendations/configurations/task_status/?task_id={task.id}'
            }, status=status.HTTP_202_ACCEPTED)
            
        except ImportError:
            # Fallback to sync if Celery not available
            logger.warning("Celery not available, falling back to sync generation")
            return self.generate(request)
        except Exception as e:
            logger.exception(f"Async task creation error: {e}")
            return Response(
                {'error': f'Failed to start async task: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def task_status(self, request):
        """
        Проверить статус асинхронной задачи генерации.
        
        Query params:
        - task_id: ID задачи Celery
        """
        task_id = request.query_params.get('task_id')
        
        if not task_id:
            return Response(
                {'error': 'Укажите task_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from celery.result import AsyncResult
            
            result = AsyncResult(task_id)
            
            response_data = {
                'task_id': task_id,
                'status': result.status,
                'ready': result.ready(),
            }
            
            if result.ready():
                if result.successful():
                    response_data['result'] = result.result
                else:
                    response_data['error'] = str(result.result)
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Task status check error: {e}")
            return Response(
                {'error': f'Failed to check task status: {str(e)}'},
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
    
    @action(detail=True, methods=['get'], url_path='store-links')
    def store_links(self, request, pk=None):
        """
        Получение ссылок на магазины для всех компонентов конфигурации.
        Возвращает ссылки на DNS, Citilink, М.Видео и др.
        """
        configuration = self.get_object()
        
        if not STORE_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис магазинов недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            links = get_store_links_for_configuration(configuration)
            return Response({
                'configuration_id': configuration.id,
                'components': links
            })
        except Exception as e:
            logger.exception(f"Error getting store links: {e}")
            return Response(
                {'error': f'Ошибка получения ссылок на магазины: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='performance-analysis')
    def performance_analysis(self, request, pk=None):
        """
        Анализ производительности конфигурации.
        Включает бенчмарки, предсказание FPS в играх, анализ bottleneck.
        """
        configuration = self.get_object()
        
        if not BENCHMARK_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис анализа производительности недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            analysis = analyze_configuration_performance(configuration)
            return Response({
                'configuration_id': configuration.id,
                'analysis': analysis
            })
        except Exception as e:
            logger.exception(f"Error analyzing performance: {e}")
            return Response(
                {'error': f'Ошибка анализа производительности: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='benchmarks')
    def benchmarks(self, request, pk=None):
        """
        Получение бенчмарков для CPU и GPU конфигурации.
        """
        configuration = self.get_object()
        
        if not BENCHMARK_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис бенчмарков недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            result = {
                'cpu_name': None,
                'gpu_name': None,
                'cpu_benchmarks': {},
                'gpu_benchmarks': {},
            }
            
            if configuration.cpu:
                result['cpu_name'] = configuration.cpu.name
                result['cpu_benchmarks'] = get_benchmarks_for_cpu(configuration.cpu.name)
            
            if configuration.gpu:
                result['gpu_name'] = configuration.gpu.name
                result['gpu_benchmarks'] = get_benchmarks_for_gpu(configuration.gpu.name)
            
            return Response(result)
        except Exception as e:
            logger.exception(f"Error getting benchmarks: {e}")
            return Response(
                {'error': f'Ошибка получения бенчмарков: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='fps-prediction')
    def fps_prediction(self, request, pk=None):
        """
        Предсказание FPS в играх для конфигурации.
        
        Query params:
        - resolution: разрешение экрана (1080p, 1440p, 4k). По умолчанию 1080p.
        """
        configuration = self.get_object()
        resolution = request.query_params.get('resolution', '1080p')
        
        if not BENCHMARK_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис предсказания FPS недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            # Получаем список игр
            games = get_available_games()
            predictions = []
            
            gpu_name = configuration.gpu.name if configuration.gpu else None
            cpu_name = configuration.cpu.name if configuration.cpu else None
            
            if not gpu_name or not cpu_name:
                return Response(
                    {'error': 'Для предсказания FPS нужны CPU и GPU'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            for game in games:
                fps_data = predict_game_fps(gpu_name, cpu_name, game, resolution)
                if fps_data:
                    predictions.append(fps_data)
            
            return Response({
                'configuration_id': configuration.id,
                'resolution': resolution,
                'predictions': predictions
            })
        except Exception as e:
            logger.exception(f"Error predicting FPS: {e}")
            return Response(
                {'error': f'Ошибка предсказания FPS: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def compare(self, request):
        """
        Детальное сравнение нескольких сборок ПК.
        Показывает разницу в характеристиках и ценах.
        
        Параметры: ?ids=1,2,3 или ?ids=1&ids=2&ids=3
        """
        ids = request.query_params.getlist('ids')
        
        # Поддержка формата ids=1,2,3
        if len(ids) == 1 and ',' in ids[0]:
            ids = ids[0].split(',')
        
        if not ids or len(ids) < 2:
            return Response(
                {'error': 'Укажите минимум 2 ID для сравнения (параметр ids)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(ids) > 5:
            return Response(
                {'error': 'Максимум 5 сборок для сравнения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем кэш
        cache_key = f"compare_{'_'.join(sorted(ids))}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        try:
            configurations = PCConfiguration.objects.filter(
                id__in=ids
            ).select_related(
                'cpu', 'gpu', 'motherboard', 'ram', 'storage_primary',
                'storage_secondary', 'psu', 'case', 'cooling'
            )
            
            # Проверяем доступ
            for config in configurations:
                if config.user != request.user and not config.is_public and not request.user.is_staff:
                    return Response(
                        {'error': f'Нет доступа к сборке {config.id}'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Формируем детальное сравнение
            builds = []
            for config in configurations:
                build_data = {
                    'id': config.id,
                    'name': config.name,
                    'total_price': float(config.total_price) if config.total_price else 0,
                    'performance_score': float(config.performance_score) if hasattr(config, 'performance_score') and config.performance_score else 0,
                    'components': {
                        'cpu': {
                            'name': config.cpu.name if config.cpu else None,
                            'cores': config.cpu.cores if config.cpu else None,
                            'threads': config.cpu.threads if config.cpu else None,
                            'base_clock': float(config.cpu.base_clock) if config.cpu and config.cpu.base_clock else None,
                            'boost_clock': float(config.cpu.boost_clock) if config.cpu and config.cpu.boost_clock else None,
                            'price': float(config.cpu.price) if config.cpu else None,
                            'performance_score': float(config.cpu.performance_score) if config.cpu and config.cpu.performance_score else None,
                        } if config.cpu else None,
                        'gpu': {
                            'name': config.gpu.name if config.gpu else None,
                            'memory': config.gpu.memory if config.gpu else None,
                            'memory_type': config.gpu.memory_type if config.gpu else None,
                            'price': float(config.gpu.price) if config.gpu else None,
                            'performance_score': float(config.gpu.performance_score) if config.gpu and config.gpu.performance_score else None,
                        } if config.gpu else None,
                        'ram': {
                            'name': config.ram.name if config.ram else None,
                            'capacity': config.ram.capacity if config.ram else None,
                            'speed': config.ram.speed if config.ram else None,
                            'price': float(config.ram.price) if config.ram else None,
                        } if config.ram else None,
                        'storage_primary': {
                            'name': config.storage_primary.name if config.storage_primary else None,
                            'capacity': config.storage_primary.capacity if config.storage_primary else None,
                            'storage_type': config.storage_primary.storage_type if config.storage_primary else None,
                            'price': float(config.storage_primary.price) if config.storage_primary else None,
                        } if config.storage_primary else None,
                    }
                }
                builds.append(build_data)
            
            # Вычисляем сравнительные метрики
            comparison = {
                'builds': builds,
                'summary': {
                    'cheapest': min(builds, key=lambda x: x['total_price'])['name'] if builds else None,
                    'most_expensive': max(builds, key=lambda x: x['total_price'])['name'] if builds else None,
                    'price_difference': max(b['total_price'] for b in builds) - min(b['total_price'] for b in builds) if builds else 0,
                    'best_cpu_performance': max(
                        (b for b in builds if b['components']['cpu'] and b['components']['cpu'].get('performance_score')),
                        key=lambda x: x['components']['cpu']['performance_score'],
                        default=None
                    ),
                    'best_gpu_performance': max(
                        (b for b in builds if b['components']['gpu'] and b['components']['gpu'].get('performance_score')),
                        key=lambda x: x['components']['gpu']['performance_score'],
                        default=None
                    ),
                },
                'criteria': {
                    'cpu_cores': {b['name']: b['components']['cpu']['cores'] if b['components']['cpu'] else None for b in builds},
                    'gpu_memory': {b['name']: b['components']['gpu']['memory'] if b['components']['gpu'] else None for b in builds},
                    'ram_capacity': {b['name']: b['components']['ram']['capacity'] if b['components']['ram'] else None for b in builds},
                    'storage_capacity': {b['name']: b['components']['storage_primary']['capacity'] if b['components']['storage_primary'] else None for b in builds},
                    'total_price': {b['name']: b['total_price'] for b in builds},
                }
            }
            
            return Response(comparison)
            
        except Exception as e:
            logger.exception(f"Error comparing configurations: {e}")
            return Response(
                {'error': f'Ошибка при сравнении сборок: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            # Кэшируем результат на 5 минут
            cache.set(cache_key, comparison, 300)
            
            return Response(comparison)
            
        except Exception as e:
            logger.exception(f"Compare error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'], url_path='export/(?P<export_format>csv|excel|pdf)')
    def export(self, request, pk=None, export_format='csv'):
        """
        Экспорт конфигурации в различные форматы.
        Форматы: csv, excel, pdf
        """
        if not EXPORT_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис экспорта недоступен. Установите openpyxl и reportlab.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        configuration = self.get_object()
        export_service = ConfigurationExportService(configuration)
        
        if export_format == 'csv':
            output = export_service.export_to_csv()
            response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="config_{configuration.id}.csv"'
            return response
        
        elif export_format == 'excel':
            output = export_service.export_to_excel()
            if not output:
                return Response(
                    {'error': 'Экспорт в Excel недоступен. Установите openpyxl.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="config_{configuration.id}.xlsx"'
            return response
        
        elif export_format == 'pdf':
            output = export_service.export_to_pdf()
            if not output:
                return Response(
                    {'error': 'Экспорт в PDF недоступен. Установите reportlab.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            response = HttpResponse(output.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="config_{configuration.id}.pdf"'
            return response
        
        return Response({'error': 'Неподдерживаемый формат'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def shop_links(self, request, pk=None):
        """Получить ссылки на магазины для всех компонентов конфигурации"""
        if not EXPORT_SERVICE_AVAILABLE:
            return Response({'error': 'Сервис недоступен'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        configuration = self.get_object()
        export_service = ConfigurationExportService(configuration)
        
        components = export_service.get_components_list()
        peripherals = export_service.get_peripherals_list()
        
        result = []
        for item in components + peripherals:
            result.append({
                'type': item['type'],
                'name': item['name'],
                'price': item['price'],
                'links': export_service.generate_shop_links(item['search_query'])
            })
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def power_calculator(self, request, pk=None):
        """
        Калькулятор энергопотребления для конфигурации.
        Параметры: hours_per_day (int), load_percent (float 0-1)
        """
        if not EXPORT_SERVICE_AVAILABLE:
            return Response({'error': 'Сервис недоступен'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        configuration = self.get_object()
        calculator = PowerCalculatorService(configuration)
        
        hours = int(request.query_params.get('hours_per_day', 8))
        load = float(request.query_params.get('load_percent', 0.7))
        
        return Response({
            'system_tdp': calculator.calculate_system_tdp(),
            'psu_recommendation': calculator.recommend_psu(),
            'electricity_cost': calculator.calculate_electricity_cost(hours, load)
        })
    
    @action(detail=True, methods=['get'])
    def compatibility_check(self, request, pk=None):
        """Расширенная проверка совместимости компонентов"""
        if not EXPORT_SERVICE_AVAILABLE:
            # Fallback to basic check
            configuration = self.get_object()
            service = ConfigurationService({
                'user_type': request.user.user_type if hasattr(request.user, 'user_type') else 'student',
                'min_budget': 0,
                'max_budget': 0,
                'priority': 'performance'
            })
            is_compatible, issues = service.check_compatibility(configuration)
            return Response({
                'compatible': is_compatible,
                'issues': [{'message': issue} for issue in issues],
                'warnings': [],
                'checks_passed': 1 if is_compatible else 0
            })
        
        configuration = self.get_object()
        checker = CompatibilityChecker(configuration)
        return Response(checker.check_all())


class WishlistViewSet(viewsets.ModelViewSet):
    """ViewSet для управления избранными компонентами"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class WishlistSerializer(serializers.ModelSerializer):
            component_name = serializers.SerializerMethodField()
            current_price = serializers.SerializerMethodField()
            price_change = serializers.SerializerMethodField()
            
            class Meta:
                model = Wishlist
                fields = [
                    'id', 'component_type', 'component_id', 'component_name',
                    'price_at_add', 'current_price', 'price_change',
                    'price_alert_threshold', 'notify_on_price_drop',
                    'notes', 'created_at'
                ]
                read_only_fields = ['id', 'created_at', 'component_name', 'current_price', 'price_change']
            
            def get_component_name(self, obj):
                component = obj.get_component()
                return str(component) if component else None
            
            def get_current_price(self, obj):
                component = obj.get_component()
                return float(component.price) if component and hasattr(component, 'price') else None
            
            def get_price_change(self, obj):
                return obj.check_price_change()
        
        return WishlistSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def add_component(self, request):
        """Добавить компонент в избранное"""
        component_type = request.data.get('component_type')
        component_id = request.data.get('component_id')
        
        if not component_type or not component_id:
            return Response(
                {'error': 'Укажите component_type и component_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем текущую цену компонента
        model_map = {
            'cpu': CPU, 'gpu': GPU, 'motherboard': Motherboard,
            'ram': RAM, 'storage': Storage, 'psu': PSU,
            'case': Case, 'cooling': Cooling,
            'monitor': Monitor, 'keyboard': Keyboard,
            'mouse': Mouse, 'headset': Headset,
        }
        
        model = model_map.get(component_type)
        if not model:
            return Response({'error': 'Неверный тип компонента'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            component = model.objects.get(id=component_id)
        except model.DoesNotExist:
            return Response({'error': 'Компонент не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        # Создаём или обновляем запись
        wishlist_item, created = Wishlist.objects.update_or_create(
            user=request.user,
            component_type=component_type,
            component_id=component_id,
            defaults={
                'price_at_add': component.price,
                'notify_on_price_drop': request.data.get('notify_on_price_drop', True),
                'price_alert_threshold': request.data.get('price_alert_threshold'),
                'notes': request.data.get('notes', ''),
            }
        )
        
        return Response({
            'id': wishlist_item.id,
            'created': created,
            'component': str(component),
            'price': float(component.price)
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'])
    def remove_component(self, request):
        """Удалить компонент из избранного"""
        component_type = request.data.get('component_type')
        component_id = request.data.get('component_id')
        
        deleted, _ = Wishlist.objects.filter(
            user=request.user,
            component_type=component_type,
            component_id=component_id
        ).delete()
        
        if deleted:
            return Response({'message': 'Удалено из избранного'})
        return Response({'error': 'Не найдено в избранном'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def price_alerts(self, request):
        """Получить список компонентов с изменившейся ценой"""
        wishlist = self.get_queryset().filter(notify_on_price_drop=True)
        
        alerts = []
        for item in wishlist:
            price_info = item.check_price_change()
            if price_info and (price_info['price_dropped'] or price_info['below_threshold']):
                alerts.append({
                    'id': item.id,
                    'component_type': item.component_type,
                    'component_id': item.component_id,
                    'component_name': str(item.get_component()),
                    'price_info': price_info
                })
        
        return Response(alerts)
    
    @action(detail=False, methods=['post'])
    def add_to_build(self, request):
        """Добавить компоненты из избранного в сборку"""
        wishlist_ids = request.data.get('wishlist_ids', [])
        build_id = request.data.get('build_id')
        
        if not wishlist_ids:
            return Response({'error': 'Укажите wishlist_ids'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем или создаём сборку
        if build_id:
            try:
                configuration = PCConfiguration.objects.get(id=build_id, user=request.user)
            except PCConfiguration.DoesNotExist:
                return Response({'error': 'Сборка не найдена'}, status=status.HTTP_404_NOT_FOUND)
        else:
            configuration = PCConfiguration.objects.create(
                user=request.user,
                name='Сборка из избранного',
                is_saved=True
            )
        
        # Добавляем компоненты
        added = []
        for item in Wishlist.objects.filter(id__in=wishlist_ids, user=request.user):
            component = item.get_component()
            if component:
                field_map = {
                    'cpu': 'cpu', 'gpu': 'gpu', 'motherboard': 'motherboard',
                    'ram': 'ram', 'storage': 'storage_primary',
                    'psu': 'psu', 'case': 'case', 'cooling': 'cooling'
                }
                field = field_map.get(item.component_type)
                if field:
                    setattr(configuration, field, component)
                    added.append(item.component_type)
        
        configuration.calculate_total_price()
        configuration.save()
        
        return Response({
            'build_id': configuration.id,
            'added_components': added,
            'total_price': float(configuration.total_price)
        })



    # ==================== Store Integration ====================
    
    @action(detail=True, methods=['get'], url_path='store-links')
    def store_links(self, request, pk=None):
        """
        Получение ссылок на магазины для всех компонентов конфигурации
        """
        if not STORE_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис магазинов недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            config = self.get_queryset().get(pk=pk)
        except PCConfiguration.DoesNotExist:
            return Response(
                {'error': 'Конфигурация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        links = get_store_links_for_configuration(config)
        
        return Response({
            'configuration_id': config.id,
            'configuration_name': config.name,
            'components': links,
            'stores': ['dns', 'citilink', 'regard', 'mvideo'],
        })
    
    @action(detail=True, methods=['get'], url_path='price-history')
    def price_history(self, request, pk=None):
        """
        История цен компонентов конфигурации
        
        Query params:
            days: количество дней (default: 30)
            component: конкретный компонент (cpu, gpu, etc.)
        """
        if not STORE_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            config = self.get_queryset().get(pk=pk)
        except PCConfiguration.DoesNotExist:
            return Response(
                {'error': 'Конфигурация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        days = int(request.query_params.get('days', 30))
        component_filter = request.query_params.get('component')
        
        result = {}
        components = {
            'cpu': config.cpu,
            'gpu': config.gpu,
            'motherboard': config.motherboard,
            'ram': config.ram,
            'storage_primary': config.storage_primary,
            'psu': config.psu,
            'case': config.case,
            'cooling': config.cooling,
        }
        
        for comp_type, comp in components.items():
            if comp and (not component_filter or component_filter == comp_type):
                result[comp_type] = {
                    'name': comp.name,
                    'current_price': float(comp.price) if comp.price else 0,
                    'history': get_price_history_data(comp.name, days),
                }
        
        return Response({
            'configuration_id': config.id,
            'days': days,
            'price_history': result,
        })

    # ==================== Benchmarks & Performance ====================
    
    @action(detail=True, methods=['get'], url_path='benchmarks')
    def benchmarks(self, request, pk=None):
        """
        Получение бенчмарков для компонентов конфигурации
        """
        if not BENCHMARK_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис бенчмарков недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            config = self.get_queryset().get(pk=pk)
        except PCConfiguration.DoesNotExist:
            return Response(
                {'error': 'Конфигурация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        result = {
            'cpu_benchmarks': {},
            'gpu_benchmarks': {},
        }
        
        if config.cpu:
            result['cpu_benchmarks'] = get_benchmarks_for_cpu(config.cpu.name)
            result['cpu_name'] = config.cpu.name
        
        if config.gpu:
            result['gpu_benchmarks'] = get_benchmarks_for_gpu(config.gpu.name)
            result['gpu_name'] = config.gpu.name
        
        return Response(result)
    
    @action(detail=True, methods=['get'], url_path='fps-prediction')
    def fps_prediction(self, request, pk=None):
        """
        Предсказание FPS в играх для конфигурации
        
        Query params:
            game: название игры (optional)
            resolution: 1080p, 1440p, 4k (default: 1080p)
            ray_tracing: true/false (default: false)
        """
        if not BENCHMARK_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            config = self.get_queryset().get(pk=pk)
        except PCConfiguration.DoesNotExist:
            return Response(
                {'error': 'Конфигурация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not config.cpu or not config.gpu:
            return Response(
                {'error': 'Для предсказания FPS нужны CPU и GPU'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        game = request.query_params.get('game')
        resolution = request.query_params.get('resolution', '1080p')
        ray_tracing = request.query_params.get('ray_tracing', 'false').lower() == 'true'
        
        fps_service = FPSPredictionService()
        
        if game:
            # Предсказание для конкретной игры
            prediction = predict_game_fps(
                config.gpu.name,
                config.cpu.name,
                game,
                resolution
            )
            
            if not prediction:
                return Response(
                    {'error': f'Игра "{game}" не найдена в базе'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'game': game,
                'resolution': resolution,
                'prediction': prediction,
            })
        else:
            # Предсказание для всех игр
            predictions = fps_service.predict_all_games(
                config.gpu.name,
                config.cpu.name,
                resolution
            )
            
            return Response({
                'cpu': config.cpu.name,
                'gpu': config.gpu.name,
                'resolution': resolution,
                'predictions': [p.to_dict() for p in predictions],
                'available_games': fps_service.get_game_list(),
            })
    
    @action(detail=True, methods=['get'], url_path='performance-analysis')
    def performance_analysis(self, request, pk=None):
        """
        Полный анализ производительности конфигурации
        """
        if not BENCHMARK_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            config = self.get_queryset().get(pk=pk)
        except PCConfiguration.DoesNotExist:
            return Response(
                {'error': 'Конфигурация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        analysis = analyze_configuration_performance(config)
        
        return Response({
            'configuration_id': config.id,
            'configuration_name': config.name,
            'analysis': analysis,
        })
    
    @action(detail=False, methods=['get'], url_path='available-games')
    def available_games(self, request):
        """Список доступных игр для FPS предсказания"""
        if not BENCHMARK_SERVICE_AVAILABLE:
            return Response({'games': []})
        
        return Response({
            'games': get_available_games(),
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


# ============================================================================
# AI CHAT VIEWSET
# ============================================================================

class AIChatViewSet(viewsets.ViewSet):
    """
    ViewSet для чата с AI ассистентом.
    Позволяет уточнять требования и получать объяснения по выбору компонентов.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """
        Отправить сообщение в чат с AI.
        
        Request body:
        - message: текст сообщения
        - session_id: ID сессии (опционально)
        - configuration_id: ID конфигурации для контекста (опционально)
        """
        if not CHAT_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис чата недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        message = request.data.get('message')
        if not message:
            return Response(
                {'error': 'Укажите сообщение'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session_id = request.data.get('session_id')
        configuration_id = request.data.get('configuration_id')
        
        chat_service = AIChatService(user=request.user)
        
        # Создаём сессию с контекстом конфигурации если указана
        if not session_id and configuration_id:
            session_id = chat_service.create_session(configuration_id=configuration_id)
        
        result = chat_service.send_message(message, session_id=session_id)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Получить историю чата"""
        if not CHAT_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис чата недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {'error': 'Укажите session_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chat_service = AIChatService(user=request.user)
        history = chat_service.get_chat_history(session_id)
        
        return Response({'history': history})
    
    @action(detail=False, methods=['post'])
    def explain(self, request):
        """
        Объяснить выбор конкретного компонента.
        
        Request body:
        - component_type: тип компонента (cpu, gpu, etc.)
        - component_id: ID компонента
        - configuration_id: ID конфигурации (опционально)
        """
        if not CHAT_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис чата недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        component_type = request.data.get('component_type')
        component_id = request.data.get('component_id')
        
        if not component_type or not component_id:
            return Response(
                {'error': 'Укажите component_type и component_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chat_service = AIChatService(user=request.user)
        explanation = chat_service.explain_component_choice(
            component_type=component_type,
            component_id=component_id,
            configuration_id=request.data.get('configuration_id')
        )
        
        return Response({'explanation': explanation})


# ============================================================================
# PRICE PARSER VIEWSET
# ============================================================================

class PriceParserViewSet(viewsets.ViewSet):
    """
    ViewSet для получения актуальных цен с магазинов (DNS, Citilink, Regard).
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def component_prices(self, request):
        """
        Получить цены на компонент из разных магазинов.
        
        Query params:
        - component_type: тип компонента (cpu, gpu, etc.)
        - component_id: ID компонента
        """
        if not PRICE_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис парсинга цен недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        component_type = request.query_params.get('component_type')
        component_id = request.query_params.get('component_id')
        
        if not component_type or not component_id:
            return Response(
                {'error': 'Укажите component_type и component_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = PriceParserService()
        prices = service.get_component_prices(component_type, int(component_id))
        
        return Response(prices)
    
    @action(detail=False, methods=['post'])
    def update_prices(self, request):
        """
        Обновить цены для списка компонентов.
        
        Request body:
        - components: список {component_type, component_id}
        """
        if not PRICE_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис парсинга цен недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        components = request.data.get('components', [])
        if not components:
            return Response(
                {'error': 'Укажите список компонентов'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = PriceParserService()
        results = []
        
        for comp in components:  # Обрабатываем все компоненты
            updated = service.update_component_price(
                comp.get('component_type'),
                comp.get('component_id')
            )
            results.append({
                'component_type': comp.get('component_type'),
                'component_id': comp.get('component_id'),
                'updated': updated
            })
        
        return Response({'results': results})
    
    @action(detail=False, methods=['get'])
    def compare_prices(self, request):
        """
        Сравнить цены на все компоненты конфигурации.
        
        Query params:
        - configuration_id: ID конфигурации
        """
        if not PRICE_SERVICE_AVAILABLE:
            return Response(
                {'error': 'Сервис парсинга цен недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        config_id = request.query_params.get('configuration_id')
        if not config_id:
            return Response(
                {'error': 'Укажите configuration_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            configuration = PCConfiguration.objects.get(
                id=config_id,
                user=request.user
            )
        except PCConfiguration.DoesNotExist:
            return Response(
                {'error': 'Конфигурация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        service = PriceParserService()
        comparison = service.compare_prices(configuration)
        
        return Response(comparison)


# ============================================================================
# PERSONALIZATION VIEWSET
# ============================================================================

class PersonalizationViewSet(viewsets.ViewSet):
    """
    ViewSet для персонализированных рекомендаций на основе истории пользователя.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def preferences(self, request):
        """Получить проанализированные предпочтения пользователя"""
        if not PERSONALIZATION_AVAILABLE:
            return Response(
                {'error': 'Сервис персонализации недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        service = PersonalizationService(request.user)
        preferences = service.analyze_user_preferences()
        
        return Response(preferences)
    
    @action(detail=False, methods=['get'])
    def suggested_upgrades(self, request):
        """
        Получить рекомендуемые апгрейды для существующей конфигурации.
        
        Query params:
        - configuration_id: ID конфигурации
        """
        if not PERSONALIZATION_AVAILABLE:
            return Response(
                {'error': 'Сервис персонализации недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        config_id = request.query_params.get('configuration_id')
        if not config_id:
            return Response(
                {'error': 'Укажите configuration_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            configuration = PCConfiguration.objects.get(
                id=config_id,
                user=request.user
            )
        except PCConfiguration.DoesNotExist:
            return Response(
                {'error': 'Конфигурация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        service = PersonalizationService(request.user)
        upgrades = service.suggest_upgrades(configuration)
        
        return Response(upgrades)
    
    @action(detail=False, methods=['get'])
    def similar_builds(self, request):
        """Найти похожие сборки от других пользователей"""
        if not PERSONALIZATION_AVAILABLE:
            return Response(
                {'error': 'Сервис персонализации недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        service = PersonalizationService(request.user)
        similar = service.find_similar_users_builds()
        
        return Response({'similar_builds': similar})
    
    @action(detail=False, methods=['get'])
    def personalized_recommendations(self, request):
        """Получить персонализированные рекомендации компонентов"""
        if not PERSONALIZATION_AVAILABLE:
            return Response(
                {'error': 'Сервис персонализации недоступен'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        component_type = request.query_params.get('component_type')
        limit = int(request.query_params.get('limit', 5))
        
        if not component_type:
            return Response(
                {'error': 'Укажите component_type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = PersonalizationService(request.user)
        recommendations = service.get_personalized_recommendations(
            component_type=component_type,
            limit=limit
        )
        
        return Response({'recommendations': recommendations})


# ============================================================================
# AI ANALYTICS VIEWSET
# ============================================================================

class AIAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet для аналитики AI ответов (только для staff).
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получить статистику AI ответов"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Доступ запрещён'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 7))
        
        success_rate = AILog.get_success_rate(days=days)
        common_errors = AILog.get_common_errors(days=days)
        
        # Общая статистика
        from datetime import timedelta
        from django.utils import timezone
        
        since = timezone.now() - timedelta(days=days)
        logs = AILog.objects.filter(created_at__gte=since)
        
        return Response({
            'period_days': days,
            'success_rate': success_rate,
            'total_requests': logs.count(),
            'by_status': {
                'success': logs.filter(status='success').count(),
                'validation_failed': logs.filter(status='validation_failed').count(),
                'fallback_used': logs.filter(status='fallback_used').count(),
                'error': logs.filter(status='error').count(),
            },
            'common_errors': common_errors,
            'avg_response_time_ms': logs.aggregate(
                avg=db_models.Avg('response_time_ms')
            )['avg']
        })
    
    @action(detail=False, methods=['get'])
    def recent_logs(self, request):
        """Получить последние логи AI"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Доступ запрещён'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        limit = int(request.query_params.get('limit', 50))
        status_filter = request.query_params.get('status')
        
        logs = AILog.objects.all()
        if status_filter:
            logs = logs.filter(status=status_filter)
        
        logs = logs[:limit]
        
        return Response({
            'logs': [
                {
                    'id': log.id,
                    'status': log.status,
                    'user': log.user.username if log.user else None,
                    'response_time_ms': log.response_time_ms,
                    'validation_errors': log.validation_errors,
                    'fallback_reason': log.fallback_reason,
                    'created_at': log.created_at.isoformat()
                }
                for log in logs
            ]
        })
