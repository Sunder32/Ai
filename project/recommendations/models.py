from django.db import models
from accounts.models import User
from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
from peripherals.models import (
    Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair,
    Speakers, Mousepad, MonitorArm, USBHub, DeskLighting, StreamDeck,
    CaptureCard, Gamepad, Headphonestand
)


class PCConfiguration(models.Model):
    """Конфигурация ПК"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='configurations',
        verbose_name='Пользователь'
    )
    
    name = models.CharField(max_length=255, verbose_name='Название конфигурации')
    
    # Компоненты
    cpu = models.ForeignKey(CPU, on_delete=models.SET_NULL, null=True, verbose_name='Процессор')
    gpu = models.ForeignKey(GPU, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Видеокарта')
    motherboard = models.ForeignKey(Motherboard, on_delete=models.SET_NULL, null=True, verbose_name='Материнская плата')
    ram = models.ForeignKey(RAM, on_delete=models.SET_NULL, null=True, verbose_name='Оперативная память')
    storage_primary = models.ForeignKey(
        Storage,
        on_delete=models.SET_NULL,
        null=True,
        related_name='primary_storage',
        verbose_name='Основной накопитель'
    )
    storage_secondary = models.ForeignKey(
        Storage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secondary_storage',
        verbose_name='Дополнительный накопитель'
    )
    psu = models.ForeignKey(PSU, on_delete=models.SET_NULL, null=True, verbose_name='Блок питания')
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, verbose_name='Корпус')
    cooling = models.ForeignKey(Cooling, on_delete=models.SET_NULL, null=True, verbose_name='Охлаждение')
    
    # Общая информация
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Общая стоимость'
    )
    
    compatibility_check = models.BooleanField(default=True, verbose_name='Проверка совместимости')
    compatibility_notes = models.TextField(blank=True, verbose_name='Примечания по совместимости')
    
    is_saved = models.BooleanField(default=False, verbose_name='Сохранена')
    is_public = models.BooleanField(default=False, verbose_name='Публичная сборка')
    share_code = models.CharField(max_length=32, blank=True, null=True, unique=True, verbose_name='Код для шаринга')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Конфигурация ПК'
        verbose_name_plural = 'Конфигурации ПК'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - {self.user.username}'
    
    def calculate_total_price(self):
        """Рассчитать общую стоимость конфигурации"""
        total = 0
        if self.cpu:
            total += self.cpu.price
        if self.gpu:
            total += self.gpu.price
        if self.motherboard:
            total += self.motherboard.price
        if self.ram:
            total += self.ram.price
        if self.storage_primary:
            total += self.storage_primary.price
        if self.storage_secondary:
            total += self.storage_secondary.price
        if self.psu:
            total += self.psu.price
        if self.case:
            total += self.case.price
        if self.cooling:
            total += self.cooling.price
        
        self.total_price = total
        return total


class WorkspaceSetup(models.Model):
    """Настройка рабочего места"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workspace_setups',
        verbose_name='Пользователь'
    )
    
    configuration = models.ForeignKey(
        PCConfiguration,
        on_delete=models.CASCADE,
        related_name='workspace_setups',
        verbose_name='Конфигурация ПК'
    )
    
    name = models.CharField(max_length=255, verbose_name='Название')
    
    # Периферия
    monitor_primary = models.ForeignKey(
        Monitor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_monitor',
        verbose_name='Основной монитор'
    )
    monitor_secondary = models.ForeignKey(
        Monitor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secondary_monitor',
        verbose_name='Дополнительный монитор'
    )
    keyboard = models.ForeignKey(Keyboard, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Клавиатура')
    mouse = models.ForeignKey(Mouse, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Мышь')
    headset = models.ForeignKey(Headset, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Наушники')
    webcam = models.ForeignKey(Webcam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Веб-камера')
    microphone = models.ForeignKey(Microphone, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Микрофон')
    desk = models.ForeignKey(Desk, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Стол')
    chair = models.ForeignKey(Chair, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Кресло')
    
    # Дополнительная периферия
    speakers = models.ForeignKey(Speakers, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Колонки')
    mousepad = models.ForeignKey(Mousepad, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Коврик')
    monitor_arm = models.ForeignKey(MonitorArm, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Кронштейн')
    usb_hub = models.ForeignKey(USBHub, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='USB-хаб')
    lighting = models.ForeignKey(DeskLighting, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Освещение')
    stream_deck = models.ForeignKey(StreamDeck, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Стрим-пульт')
    capture_card = models.ForeignKey(CaptureCard, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Карта захвата')
    gamepad = models.ForeignKey(Gamepad, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Геймпад')
    headphone_stand = models.ForeignKey(Headphonestand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Подставка для наушников')
    
    # Рекомендации
    lighting_recommendation = models.TextField(blank=True, verbose_name='Рекомендации по освещению')
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Общая стоимость'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Настройка рабочего места'
        verbose_name_plural = 'Настройки рабочих мест'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - {self.user.username}'
    
    def calculate_total_price(self):
        """Рассчитать общую стоимость рабочего места"""
        total = self.configuration.total_price if self.configuration else 0
        
        peripherals = [
            self.monitor_primary, self.monitor_secondary, self.keyboard, self.mouse,
            self.headset, self.webcam, self.microphone, self.desk, self.chair,
            self.speakers, self.mousepad, self.monitor_arm, self.usb_hub,
            self.lighting, self.stream_deck, self.capture_card, self.gamepad,
            self.headphone_stand
        ]
        
        for peripheral in peripherals:
            if peripheral and hasattr(peripheral, 'price'):
                total += peripheral.price
        
        self.total_price = total
        return total


class Recommendation(models.Model):
    """Рекомендация с обоснованием"""
    configuration = models.ForeignKey(
        PCConfiguration,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='Конфигурация'
    )
    
    component_type = models.CharField(max_length=50, verbose_name='Тип компонента')
    component_id = models.IntegerField(verbose_name='ID компонента')
    reason = models.TextField(verbose_name='Обоснование выбора')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'
    
    def __str__(self):
        return f'Рекомендация для {self.configuration.name} - {self.component_type}'


class Wishlist(models.Model):
    """Избранные компоненты пользователя"""
    COMPONENT_TYPES = [
        ('cpu', 'Процессор'),
        ('gpu', 'Видеокарта'),
        ('motherboard', 'Материнская плата'),
        ('ram', 'Оперативная память'),
        ('storage', 'Накопитель'),
        ('psu', 'Блок питания'),
        ('case', 'Корпус'),
        ('cooling', 'Охлаждение'),
        ('monitor', 'Монитор'),
        ('keyboard', 'Клавиатура'),
        ('mouse', 'Мышь'),
        ('headset', 'Наушники'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name='Пользователь'
    )
    
    component_type = models.CharField(
        max_length=50,
        choices=COMPONENT_TYPES,
        verbose_name='Тип компонента'
    )
    component_id = models.IntegerField(verbose_name='ID компонента')
    
    # Отслеживание цены
    price_at_add = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена при добавлении'
    )
    price_alert_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Порог уведомления о цене'
    )
    notify_on_price_drop = models.BooleanField(
        default=True,
        verbose_name='Уведомлять о снижении цены'
    )
    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name='Уведомления включены'
    )
    
    notes = models.TextField(blank=True, verbose_name='Заметки')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'component_type', 'component_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_component_type_display()} #{self.component_id}'
    
    def get_component(self):
        """Получить объект компонента"""
        from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
        from peripherals.models import Monitor, Keyboard, Mouse, Headset
        
        model_map = {
            'cpu': CPU,
            'gpu': GPU,
            'motherboard': Motherboard,
            'ram': RAM,
            'storage': Storage,
            'psu': PSU,
            'case': Case,
            'cooling': Cooling,
            'monitor': Monitor,
            'keyboard': Keyboard,
            'mouse': Mouse,
            'headset': Headset,
        }
        
        model = model_map.get(self.component_type)
        if model:
            try:
                return model.objects.get(id=self.component_id)
            except model.DoesNotExist:
                return None
        return None
    
    def check_price_change(self):
        """Проверить изменение цены компонента"""
        component = self.get_component()
        if component and hasattr(component, 'price'):
            current_price = component.price
            price_diff = float(current_price) - float(self.price_at_add)
            percent_change = (price_diff / float(self.price_at_add)) * 100 if self.price_at_add else 0
            
            return {
                'current_price': float(current_price),
                'price_at_add': float(self.price_at_add),
                'difference': price_diff,
                'percent_change': round(percent_change, 2),
                'price_dropped': current_price < self.price_at_add,
                'below_threshold': self.price_alert_threshold and current_price <= self.price_alert_threshold
            }
        return None


class AILog(models.Model):
    """Лог ответов AI для анализа и улучшения"""
    
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('validation_failed', 'Ошибка валидации'),
        ('fallback_used', 'Использован fallback'),
        ('error', 'Ошибка'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    
    # Входные данные
    prompt = models.TextField(verbose_name='Промпт')
    user_requirements = models.JSONField(default=dict, verbose_name='Требования пользователя')
    
    # Ответ AI
    raw_response = models.TextField(blank=True, verbose_name='Сырой ответ AI')
    parsed_response = models.JSONField(default=dict, verbose_name='Распарсенный ответ')
    
    # Валидация
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='success', verbose_name='Статус')
    validation_errors = models.JSONField(default=list, verbose_name='Ошибки валидации')
    fallback_reason = models.TextField(blank=True, verbose_name='Причина fallback')
    
    # Результат
    configuration_id = models.IntegerField(null=True, verbose_name='ID созданной конфигурации')
    
    # Метрики
    response_time_ms = models.IntegerField(null=True, verbose_name='Время ответа (мс)')
    tokens_used = models.IntegerField(null=True, verbose_name='Использовано токенов')
    
    # Обратная связь
    user_approved = models.BooleanField(null=True, verbose_name='Одобрено пользователем')
    user_feedback = models.TextField(blank=True, verbose_name='Отзыв пользователя')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Лог AI'
        verbose_name_plural = 'Логи AI'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"AI Log #{self.id} - {self.status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def log_response(cls, user, prompt, raw_response, parsed_response, 
                     status='success', validation_errors=None, response_time_ms=None,
                     configuration_id=None, fallback_reason=''):
        """Создать запись лога"""
        return cls.objects.create(
            user=user,
            prompt=prompt,
            raw_response=raw_response,
            parsed_response=parsed_response,
            status=status,
            validation_errors=validation_errors or [],
            response_time_ms=response_time_ms,
            configuration_id=configuration_id,
            fallback_reason=fallback_reason
        )
    
    @classmethod
    def get_success_rate(cls, days=7):
        """Получить процент успешных ответов за период"""
        from datetime import timedelta
        from django.utils import timezone
        
        since = timezone.now() - timedelta(days=days)
        total = cls.objects.filter(created_at__gte=since).count()
        if total == 0:
            return 100.0
        
        success = cls.objects.filter(created_at__gte=since, status='success').count()
        return round((success / total) * 100, 2)
    
    @classmethod
    def get_common_errors(cls, days=7, limit=10):
        """Получить самые частые ошибки валидации"""
        from datetime import timedelta
        from django.utils import timezone
        from collections import Counter
        
        since = timezone.now() - timedelta(days=days)
        logs = cls.objects.filter(
            created_at__gte=since,
            status__in=['validation_failed', 'fallback_used']
        )
        
        errors = []
        for log in logs:
            errors.extend(log.validation_errors)
        
        counter = Counter(errors)
        return counter.most_common(limit)
