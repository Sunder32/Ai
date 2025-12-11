"""
Сервис валидации ответов AI и логирования.
Включает:
- Валидацию компонентов на совместимость
- Fallback на алгоритмический подбор
- Логирование AI-ответов для анализа
"""
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from decimal import Decimal
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class AIResponseLog(models.Model):
    """Логирование ответов AI для анализа и улучшения"""
    
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('validation_failed', 'Ошибка валидации'),
        ('fallback_used', 'Использован fallback'),
        ('error', 'Ошибка AI'),
    ]
    
    user_id = models.IntegerField(null=True, verbose_name='ID пользователя')
    
    # Входные данные
    request_type = models.CharField(max_length=50, verbose_name='Тип запроса')
    user_type = models.CharField(max_length=50, verbose_name='Тип пользователя')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    requirements = models.JSONField(default=dict, verbose_name='Требования')
    
    # Промпт и ответ
    prompt_sent = models.TextField(verbose_name='Отправленный промпт')
    raw_response = models.TextField(verbose_name='Сырой ответ AI')
    parsed_response = models.JSONField(null=True, verbose_name='Распарсенный ответ')
    
    # Результат
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    validation_errors = models.JSONField(default=list, verbose_name='Ошибки валидации')
    fallback_reason = models.TextField(blank=True, verbose_name='Причина fallback')
    
    # Метаданные
    model_used = models.CharField(max_length=100, verbose_name='Модель AI')
    response_time_ms = models.IntegerField(null=True, verbose_name='Время ответа (мс)')
    tokens_used = models.IntegerField(null=True, verbose_name='Использовано токенов')
    
    # Результирующая конфигурация
    configuration_id = models.IntegerField(null=True, verbose_name='ID созданной конфигурации')
    configuration_valid = models.BooleanField(default=False, verbose_name='Конфигурация валидна')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'recommendations'
        verbose_name = 'Лог AI ответа'
        verbose_name_plural = 'Логи AI ответов'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['user_id', '-created_at']),
        ]


class AIResponseValidator:
    """Валидатор ответов AI"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_configuration(self, ai_response: Dict, available_components: Dict) -> Tuple[bool, List[str]]:
        """
        Валидировать конфигурацию от AI.
        
        Args:
            ai_response: Ответ AI с выбранными компонентами
            available_components: Доступные компоненты из БД
        
        Returns:
            (is_valid, errors)
        """
        self.errors = []
        self.warnings = []
        
        # Проверка наличия обязательных компонентов
        required = ['cpu', 'motherboard', 'ram', 'storage_primary', 'psu', 'case']
        for comp in required:
            if not ai_response.get(comp):
                self.errors.append(f'Отсутствует обязательный компонент: {comp}')
        
        if self.errors:
            return False, self.errors
        
        # Проверка существования компонентов в БД
        for comp_type, comp_data in ai_response.items():
            if comp_data and comp_type in available_components:
                comp_id = comp_data.get('id') if isinstance(comp_data, dict) else comp_data
                if comp_id not in [c['id'] for c in available_components.get(comp_type, [])]:
                    self.errors.append(f'Компонент {comp_type} с ID {comp_id} не найден в БД')
        
        # Проверка совместимости сокетов
        cpu_data = ai_response.get('cpu', {})
        mb_data = ai_response.get('motherboard', {})
        
        if cpu_data and mb_data:
            cpu_socket = cpu_data.get('socket') if isinstance(cpu_data, dict) else None
            mb_socket = mb_data.get('socket') if isinstance(mb_data, dict) else None
            
            if cpu_socket and mb_socket and cpu_socket != mb_socket:
                self.errors.append(f'Несовместимость сокетов: CPU ({cpu_socket}) ≠ MB ({mb_socket})')
        
        # Проверка типа памяти
        ram_data = ai_response.get('ram', {})
        if ram_data and mb_data:
            ram_type = ram_data.get('memory_type') if isinstance(ram_data, dict) else None
            mb_ram_type = mb_data.get('memory_type') if isinstance(mb_data, dict) else None
            
            if ram_type and mb_ram_type and ram_type != mb_ram_type:
                self.errors.append(f'Несовместимость памяти: RAM ({ram_type}) ≠ MB ({mb_ram_type})')
        
        # Проверка бюджета
        total_price = sum(
            comp.get('price', 0) if isinstance(comp, dict) else 0
            for comp in ai_response.values()
            if comp
        )
        
        budget_max = ai_response.get('_budget_max', float('inf'))
        if total_price > budget_max * 1.1:  # Допускаем 10% превышение
            self.warnings.append(f'Превышен бюджет: {total_price} > {budget_max}')
        
        return len(self.errors) == 0, self.errors
    
    def validate_component_exists(self, component_type: str, component_id: int) -> bool:
        """Проверить существование компонента в БД"""
        from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
        
        model_map = {
            'cpu': CPU, 'gpu': GPU, 'motherboard': Motherboard,
            'ram': RAM, 'storage': Storage, 'psu': PSU,
            'case': Case, 'cooling': Cooling
        }
        
        model = model_map.get(component_type)
        if not model:
            return False
        
        return model.objects.filter(id=component_id).exists()


class AlgorithmicFallback:
    """
    Алгоритмический подбор компонентов как fallback при ошибке AI.
    """
    
    def __init__(self, user_type: str, min_budget: float, max_budget: float, priority: str = 'balanced'):
        self.user_type = user_type
        self.min_budget = Decimal(str(min_budget))
        self.max_budget = Decimal(str(max_budget))
        self.priority = priority
        
        # Распределение бюджета по типу пользователя
        self.budget_allocation = self._get_budget_allocation()
    
    def _get_budget_allocation(self) -> Dict[str, float]:
        """Получить распределение бюджета по компонентам"""
        allocations = {
            'gamer': {
                'cpu': 0.20, 'gpu': 0.40, 'motherboard': 0.10,
                'ram': 0.08, 'storage': 0.08, 'psu': 0.06,
                'case': 0.05, 'cooling': 0.03
            },
            'designer': {
                'cpu': 0.30, 'gpu': 0.30, 'motherboard': 0.10,
                'ram': 0.12, 'storage': 0.08, 'psu': 0.05,
                'case': 0.03, 'cooling': 0.02
            },
            'programmer': {
                'cpu': 0.30, 'gpu': 0.15, 'motherboard': 0.12,
                'ram': 0.18, 'storage': 0.12, 'psu': 0.05,
                'case': 0.05, 'cooling': 0.03
            },
            'office': {
                'cpu': 0.25, 'gpu': 0.10, 'motherboard': 0.15,
                'ram': 0.15, 'storage': 0.15, 'psu': 0.10,
                'case': 0.07, 'cooling': 0.03
            },
            'student': {
                'cpu': 0.25, 'gpu': 0.25, 'motherboard': 0.12,
                'ram': 0.12, 'storage': 0.12, 'psu': 0.06,
                'case': 0.05, 'cooling': 0.03
            }
        }
        return allocations.get(self.user_type, allocations['student'])
    
    def select_components(self) -> Dict[str, Any]:
        """
        Алгоритмический подбор компонентов.
        """
        from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
        
        result = {}
        remaining_budget = self.max_budget
        
        # 1. Выбираем CPU
        cpu_budget = self.max_budget * Decimal(str(self.budget_allocation['cpu']))
        cpu = self._select_best_component(CPU, cpu_budget, 'performance_score')
        if cpu:
            result['cpu'] = cpu
            remaining_budget -= cpu.price
        
        # 2. Выбираем материнскую плату (совместимую с CPU)
        if cpu:
            mb_budget = self.max_budget * Decimal(str(self.budget_allocation['motherboard']))
            mb = Motherboard.objects.filter(
                socket=cpu.socket,
                price__lte=mb_budget
            ).order_by('-price').first()
            if mb:
                result['motherboard'] = mb
                remaining_budget -= mb.price
        
        # 3. Выбираем GPU
        gpu_budget = self.max_budget * Decimal(str(self.budget_allocation['gpu']))
        gpu = self._select_best_component(GPU, gpu_budget, 'performance_score')
        if gpu:
            result['gpu'] = gpu
            remaining_budget -= gpu.price
        
        # 4. Выбираем RAM (совместимую с материнкой)
        if result.get('motherboard'):
            ram_budget = self.max_budget * Decimal(str(self.budget_allocation['ram']))
            ram = RAM.objects.filter(
                memory_type=result['motherboard'].memory_type,
                price__lte=ram_budget
            ).order_by('-capacity', '-speed').first()
            if ram:
                result['ram'] = ram
                remaining_budget -= ram.price
        
        # 5. Выбираем накопитель
        storage_budget = self.max_budget * Decimal(str(self.budget_allocation['storage']))
        storage = self._select_best_component(Storage, storage_budget, 'capacity', order_desc=True)
        if storage:
            result['storage_primary'] = storage
            remaining_budget -= storage.price
        
        # 6. Выбираем БП (с учётом TDP)
        required_wattage = 500  # Базовое значение
        if result.get('cpu'):
            required_wattage += result['cpu'].tdp
        if result.get('gpu'):
            required_wattage += result['gpu'].tdp
        required_wattage = int(required_wattage * 1.3)  # +30% запас
        
        psu_budget = self.max_budget * Decimal(str(self.budget_allocation['psu']))
        psu = PSU.objects.filter(
            wattage__gte=required_wattage,
            price__lte=psu_budget
        ).order_by('price').first()
        if not psu:
            psu = PSU.objects.filter(wattage__gte=required_wattage).order_by('price').first()
        if psu:
            result['psu'] = psu
            remaining_budget -= psu.price
        
        # 7. Выбираем корпус
        case_budget = self.max_budget * Decimal(str(self.budget_allocation['case']))
        case = self._select_best_component(Case, case_budget)
        if case:
            result['case'] = case
            remaining_budget -= case.price
        
        # 8. Выбираем охлаждение
        if result.get('cpu'):
            cooling_budget = self.max_budget * Decimal(str(self.budget_allocation['cooling']))
            cooling = Cooling.objects.filter(
                max_tdp__gte=result['cpu'].tdp,
                price__lte=cooling_budget
            ).order_by('-max_tdp').first()
            if cooling:
                result['cooling'] = cooling
                remaining_budget -= cooling.price
        
        return result
    
    def _select_best_component(self, model, budget: Decimal, score_field: str = None, order_desc: bool = True):
        """Выбрать лучший компонент в рамках бюджета"""
        queryset = model.objects.filter(price__lte=budget)
        
        if score_field:
            order = f'-{score_field}' if order_desc else score_field
            queryset = queryset.order_by(order)
        else:
            queryset = queryset.order_by('-price')  # Берём самый дорогой в бюджете
        
        return queryset.first()


class AILogger:
    """Логгер для AI запросов"""
    
    @staticmethod
    def log_request(
        user_id: int,
        request_type: str,
        user_type: str,
        budget_min: float,
        budget_max: float,
        requirements: Dict,
        prompt: str,
        response: str,
        parsed_response: Dict = None,
        status: str = 'success',
        validation_errors: List = None,
        fallback_reason: str = '',
        model_used: str = 'deepseek',
        response_time_ms: int = None,
        configuration_id: int = None,
        configuration_valid: bool = False
    ) -> AIResponseLog:
        """Записать лог AI запроса"""
        try:
            log = AIResponseLog.objects.create(
                user_id=user_id,
                request_type=request_type,
                user_type=user_type,
                budget_min=Decimal(str(budget_min)) if budget_min else None,
                budget_max=Decimal(str(budget_max)) if budget_max else None,
                requirements=requirements or {},
                prompt_sent=prompt[:10000],  # Ограничиваем размер
                raw_response=response[:50000],
                parsed_response=parsed_response,
                status=status,
                validation_errors=validation_errors or [],
                fallback_reason=fallback_reason,
                model_used=model_used,
                response_time_ms=response_time_ms,
                configuration_id=configuration_id,
                configuration_valid=configuration_valid
            )
            return log
        except Exception as e:
            logger.error(f"Failed to log AI request: {e}")
            return None
    
    @staticmethod
    def get_statistics(days: int = 7) -> Dict:
        """Получить статистику AI запросов"""
        from django.db.models import Count, Avg
        from datetime import timedelta
        from django.utils import timezone
        
        since = timezone.now() - timedelta(days=days)
        
        logs = AIResponseLog.objects.filter(created_at__gte=since)
        
        stats = {
            'total_requests': logs.count(),
            'by_status': dict(logs.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'avg_response_time_ms': logs.aggregate(Avg('response_time_ms'))['response_time_ms__avg'],
            'success_rate': 0,
            'fallback_rate': 0,
            'by_user_type': dict(logs.values('user_type').annotate(count=Count('id')).values_list('user_type', 'count')),
        }
        
        if stats['total_requests'] > 0:
            success_count = logs.filter(status='success').count()
            fallback_count = logs.filter(status='fallback_used').count()
            stats['success_rate'] = round(success_count / stats['total_requests'] * 100, 2)
            stats['fallback_rate'] = round(fallback_count / stats['total_requests'] * 100, 2)
        
        return stats
