"""
Сервис персонализации и рекомендаций на основе истории пользователя.
"""
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import models
from django.db.models import Count, Avg, F

logger = logging.getLogger(__name__)


class UserBuildHistory(models.Model):
    """История сборок пользователя для анализа предпочтений"""
    
    user_id = models.IntegerField(db_index=True)
    configuration_id = models.IntegerField()
    
    # Статистика
    user_type = models.CharField(max_length=50)
    budget_used = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Предпочтения по производителям
    cpu_manufacturer = models.CharField(max_length=50, blank=True)
    gpu_manufacturer = models.CharField(max_length=50, blank=True)
    
    # Приоритеты
    priority = models.CharField(max_length=50)  # performance, balanced, budget
    
    # Оценка пользователя
    user_rating = models.IntegerField(null=True)  # 1-5
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'recommendations'
        verbose_name = 'История сборки'
        verbose_name_plural = 'История сборок'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
        ]


class PersonalizationService:
    """Сервис персонализации рекомендаций"""
    
    def __init__(self, user):
        self.user = user
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Анализ предпочтений пользователя на основе истории.
        """
        from .models import PCConfiguration
        
        # Получаем все сборки пользователя
        configurations = PCConfiguration.objects.filter(
            user=self.user
        ).select_related('cpu', 'gpu', 'motherboard', 'ram')
        
        if not configurations.exists():
            return {
                'has_history': False,
                'preferences': None,
                'recommendation': 'Создайте первую сборку для получения персональных рекомендаций'
            }
        
        preferences = {
            'has_history': True,
            'total_builds': configurations.count(),
            'avg_budget': 0,
            'preferred_cpu_manufacturer': None,
            'preferred_gpu_manufacturer': None,
            'typical_use_cases': [],
            'budget_range': {'min': 0, 'max': 0}
        }
        
        # Анализ бюджета
        budgets = [float(c.total_price) for c in configurations if c.total_price]
        if budgets:
            preferences['avg_budget'] = sum(budgets) / len(budgets)
            preferences['budget_range'] = {
                'min': min(budgets),
                'max': max(budgets)
            }
        
        # Анализ производителей CPU
        cpu_manufacturers = {}
        for config in configurations:
            if config.cpu:
                mfr = config.cpu.manufacturer
                cpu_manufacturers[mfr] = cpu_manufacturers.get(mfr, 0) + 1
        
        if cpu_manufacturers:
            preferences['preferred_cpu_manufacturer'] = max(cpu_manufacturers, key=cpu_manufacturers.get)
        
        # Анализ производителей GPU
        gpu_manufacturers = {}
        for config in configurations:
            if config.gpu:
                mfr = config.gpu.manufacturer
                gpu_manufacturers[mfr] = gpu_manufacturers.get(mfr, 0) + 1
        
        if gpu_manufacturers:
            preferences['preferred_gpu_manufacturer'] = max(gpu_manufacturers, key=gpu_manufacturers.get)
        
        return preferences
    
    def get_upgrade_recommendations(self, current_config_id: int) -> Dict[str, Any]:
        """
        Рекомендации по апгрейду существующей системы.
        """
        from .models import PCConfiguration
        from computers.models import CPU, GPU, RAM, Storage
        
        try:
            config = PCConfiguration.objects.select_related(
                'cpu', 'gpu', 'motherboard', 'ram', 'storage_primary'
            ).get(id=current_config_id, user=self.user)
        except PCConfiguration.DoesNotExist:
            return {'error': 'Configuration not found'}
        
        upgrades = []
        
        # Рекомендации по CPU
        if config.cpu and config.motherboard:
            better_cpus = CPU.objects.filter(
                socket=config.motherboard.socket,
                performance_score__gt=config.cpu.performance_score,
                price__gt=config.cpu.price
            ).order_by('-performance_score')[:3]
            
            if better_cpus:
                upgrades.append({
                    'component': 'cpu',
                    'current': str(config.cpu),
                    'current_score': config.cpu.performance_score,
                    'recommendations': [
                        {
                            'name': cpu.name,
                            'score': cpu.performance_score,
                            'price': float(cpu.price),
                            'improvement': f"+{cpu.performance_score - config.cpu.performance_score} очков"
                        }
                        for cpu in better_cpus
                    ]
                })
        
        # Рекомендации по GPU
        if config.gpu:
            better_gpus = GPU.objects.filter(
                performance_score__gt=config.gpu.performance_score,
                price__lte=config.gpu.price * 2  # Не более чем в 2 раза дороже
            ).order_by('-performance_score')[:3]
            
            if better_gpus:
                upgrades.append({
                    'component': 'gpu',
                    'current': str(config.gpu),
                    'current_score': config.gpu.performance_score,
                    'recommendations': [
                        {
                            'name': gpu.name,
                            'score': gpu.performance_score,
                            'memory': gpu.memory,
                            'price': float(gpu.price),
                            'improvement': f"+{gpu.performance_score - config.gpu.performance_score} очков"
                        }
                        for gpu in better_gpus
                    ]
                })
        
        # Рекомендации по RAM
        if config.ram and config.motherboard:
            # Можно добавить больше RAM или быстрее
            more_ram = RAM.objects.filter(
                memory_type=config.motherboard.memory_type,
                capacity__gt=config.ram.capacity
            ).order_by('capacity')[:3]
            
            if more_ram:
                upgrades.append({
                    'component': 'ram',
                    'current': f"{config.ram.capacity}GB",
                    'recommendations': [
                        {
                            'name': ram.name,
                            'capacity': ram.capacity,
                            'speed': ram.speed,
                            'price': float(ram.price)
                        }
                        for ram in more_ram
                    ]
                })
        
        # Рекомендации по накопителю
        if config.storage_primary:
            faster_storage = Storage.objects.filter(
                storage_type='ssd_nvme',
                capacity__gte=config.storage_primary.capacity
            ).exclude(id=config.storage_primary.id).order_by('-read_speed')[:3]
            
            if faster_storage:
                upgrades.append({
                    'component': 'storage',
                    'current': str(config.storage_primary),
                    'recommendations': [
                        {
                            'name': st.name,
                            'capacity': st.capacity,
                            'type': st.storage_type,
                            'read_speed': st.read_speed,
                            'price': float(st.price)
                        }
                        for st in faster_storage
                    ]
                })
        
        return {
            'configuration_id': current_config_id,
            'configuration_name': config.name,
            'current_total': float(config.total_price) if config.total_price else 0,
            'upgrades': upgrades,
            'total_upgrade_options': len(upgrades)
        }
    
    def get_similar_builds(self, config_id: int = None, budget: float = None, user_type: str = None) -> List[Dict]:
        """
        Получить похожие сборки других пользователей.
        """
        from .models import PCConfiguration
        
        # Базовый запрос - только публичные сборки
        queryset = PCConfiguration.objects.filter(
            is_public=True
        ).exclude(user=self.user).select_related(
            'cpu', 'gpu', 'motherboard', 'ram'
        )
        
        # Если указан ID конфигурации - ищем похожие
        if config_id:
            try:
                reference = PCConfiguration.objects.get(id=config_id)
                budget = float(reference.total_price) if reference.total_price else 100000
            except PCConfiguration.DoesNotExist:
                pass
        
        # Фильтр по бюджету (±30%)
        if budget:
            min_budget = Decimal(str(budget * 0.7))
            max_budget = Decimal(str(budget * 1.3))
            queryset = queryset.filter(
                total_price__gte=min_budget,
                total_price__lte=max_budget
            )
        
        # Ограничиваем выборку
        similar = queryset.order_by('-created_at')[:10]
        
        return [
            {
                'id': config.id,
                'name': config.name,
                'total_price': float(config.total_price) if config.total_price else 0,
                'cpu': str(config.cpu) if config.cpu else None,
                'gpu': str(config.gpu) if config.gpu else None,
                'ram': f"{config.ram.capacity}GB" if config.ram else None,
                'share_code': config.share_code,
                'created_at': config.created_at.isoformat()
            }
            for config in similar
        ]
