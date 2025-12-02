from django.db import models


class Monitor(models.Model):
    """Монитор"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    screen_size = models.FloatField(verbose_name='Диагональ (дюймы)')
    resolution = models.CharField(max_length=50, verbose_name='Разрешение')
    refresh_rate = models.IntegerField(verbose_name='Частота обновления (Гц)')
    panel_type = models.CharField(max_length=50, verbose_name='Тип матрицы')
    response_time = models.IntegerField(verbose_name='Время отклика (мс)')
    hdr = models.BooleanField(default=False, verbose_name='HDR')
    curved = models.BooleanField(default=False, verbose_name='Изогнутый')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Монитор'
        verbose_name_plural = 'Мониторы'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name} {self.screen_size}"'


class Keyboard(models.Model):
    """Клавиатура"""
    SWITCH_TYPE_CHOICES = [
        ('mechanical', 'Механическая'),
        ('membrane', 'Мембранная'),
        ('optical', 'Оптическая'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    switch_type = models.CharField(max_length=20, choices=SWITCH_TYPE_CHOICES, verbose_name='Тип переключателей')
    switch_model = models.CharField(max_length=100, verbose_name='Модель переключателей', blank=True)
    rgb = models.BooleanField(default=False, verbose_name='RGB подсветка')
    wireless = models.BooleanField(default=False, verbose_name='Беспроводная')
    form_factor = models.CharField(max_length=50, verbose_name='Форм-фактор', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Клавиатура'
        verbose_name_plural = 'Клавиатуры'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Mouse(models.Model):
    """Мышь"""
    SENSOR_TYPE_CHOICES = [
        ('optical', 'Оптический'),
        ('laser', 'Лазерный'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPE_CHOICES, verbose_name='Тип сенсора')
    dpi = models.IntegerField(verbose_name='Максимальный DPI')
    buttons = models.IntegerField(verbose_name='Количество кнопок')
    wireless = models.BooleanField(default=False, verbose_name='Беспроводная')
    rgb = models.BooleanField(default=False, verbose_name='RGB подсветка')
    weight = models.IntegerField(verbose_name='Вес (г)', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Мышь'
        verbose_name_plural = 'Мыши'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Headset(models.Model):
    """Наушники"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    connection_type = models.CharField(max_length=50, verbose_name='Тип подключения')
    wireless = models.BooleanField(default=False, verbose_name='Беспроводные')
    microphone = models.BooleanField(default=False, verbose_name='С микрофоном')
    surround = models.BooleanField(default=False, verbose_name='Объемный звук')
    noise_cancelling = models.BooleanField(default=False, verbose_name='Шумоподавление')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Наушники'
        verbose_name_plural = 'Наушники'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Webcam(models.Model):
    """Веб-камера"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    resolution = models.CharField(max_length=50, verbose_name='Разрешение')
    fps = models.IntegerField(verbose_name='Кадров в секунду')
    autofocus = models.BooleanField(default=False, verbose_name='Автофокус')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Веб-камера'
        verbose_name_plural = 'Веб-камеры'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Microphone(models.Model):
    """Микрофон"""
    MICROPHONE_TYPE_CHOICES = [
        ('condenser', 'Конденсаторный'),
        ('dynamic', 'Динамический'),
        ('usb', 'USB'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    microphone_type = models.CharField(max_length=20, choices=MICROPHONE_TYPE_CHOICES, verbose_name='Тип')
    connection = models.CharField(max_length=50, verbose_name='Тип подключения')
    polar_pattern = models.CharField(max_length=100, verbose_name='Диаграмма направленности', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Микрофон'
        verbose_name_plural = 'Микрофоны'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Desk(models.Model):
    """Стол"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    width = models.IntegerField(verbose_name='Ширина (см)')
    depth = models.IntegerField(verbose_name='Глубина (см)')
    adjustable_height = models.BooleanField(default=False, verbose_name='Регулируемая высота')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Стол'
        verbose_name_plural = 'Столы'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Chair(models.Model):
    """Кресло"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    ergonomic = models.BooleanField(default=False, verbose_name='Эргономичное')
    adjustable_armrests = models.BooleanField(default=False, verbose_name='Регулируемые подлокотники')
    lumbar_support = models.BooleanField(default=False, verbose_name='Поддержка поясницы')
    max_weight = models.IntegerField(verbose_name='Макс. вес (кг)', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Кресло'
        verbose_name_plural = 'Кресла'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'
