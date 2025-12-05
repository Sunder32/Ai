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
