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
        indexes = [
            models.Index(fields=['price', 'refresh_rate']),
            models.Index(fields=['screen_size', 'resolution']),
        ]
    
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
        indexes = [
            models.Index(fields=['price', 'switch_type']),
        ]
    
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
        indexes = [
            models.Index(fields=['price', 'dpi']),
        ]
    
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


class Speakers(models.Model):
    """Колонки"""
    SPEAKER_TYPE_CHOICES = [
        ('2.0', '2.0 Стерео'),
        ('2.1', '2.1 с сабвуфером'),
        ('5.1', '5.1 Surround'),
        ('soundbar', 'Саундбар'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    speaker_type = models.CharField(max_length=20, choices=SPEAKER_TYPE_CHOICES, verbose_name='Тип')
    total_power = models.IntegerField(verbose_name='Мощность (Вт)')
    frequency_response = models.CharField(max_length=50, verbose_name='Частотный диапазон', blank=True)
    bluetooth = models.BooleanField(default=False, verbose_name='Bluetooth')
    rgb = models.BooleanField(default=False, verbose_name='RGB подсветка')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Колонки'
        verbose_name_plural = 'Колонки'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Mousepad(models.Model):
    """Коврик для мыши"""
    SIZE_CHOICES = [
        ('small', 'Маленький (до 30 см)'),
        ('medium', 'Средний (30-45 см)'),
        ('large', 'Большой (45-80 см)'),
        ('xl', 'XL (80+ см)'),
        ('desk', 'На весь стол'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, verbose_name='Размер')
    width = models.IntegerField(verbose_name='Ширина (мм)')
    height = models.IntegerField(verbose_name='Высота (мм)')
    thickness = models.IntegerField(verbose_name='Толщина (мм)', default=3)
    rgb = models.BooleanField(default=False, verbose_name='RGB подсветка')
    material = models.CharField(max_length=100, verbose_name='Материал', default='Ткань')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Коврик для мыши'
        verbose_name_plural = 'Коврики для мыши'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class MonitorArm(models.Model):
    """Кронштейн для монитора"""
    MOUNT_TYPE_CHOICES = [
        ('single', 'Для одного монитора'),
        ('dual', 'Для двух мониторов'),
        ('triple', 'Для трёх мониторов'),
        ('quad', 'Для четырёх мониторов'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    mount_type = models.CharField(max_length=20, choices=MOUNT_TYPE_CHOICES, verbose_name='Тип крепления')
    max_screen_size = models.IntegerField(verbose_name='Макс. диагональ (дюймы)')
    max_weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Макс. вес (кг)')
    vesa_pattern = models.CharField(max_length=50, verbose_name='VESA паттерн', default='75x75, 100x100')
    gas_spring = models.BooleanField(default=False, verbose_name='Газлифт')
    cable_management = models.BooleanField(default=True, verbose_name='Кабель-менеджмент')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Кронштейн для монитора'
        verbose_name_plural = 'Кронштейны для мониторов'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class USBHub(models.Model):
    """USB-хаб"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    usb3_ports = models.IntegerField(verbose_name='USB 3.0 портов', default=0)
    usbc_ports = models.IntegerField(verbose_name='USB-C портов', default=0)
    usb2_ports = models.IntegerField(verbose_name='USB 2.0 портов', default=0)
    card_reader = models.BooleanField(default=False, verbose_name='Картридер')
    hdmi_port = models.BooleanField(default=False, verbose_name='HDMI выход')
    ethernet_port = models.BooleanField(default=False, verbose_name='Ethernet порт')
    power_delivery = models.IntegerField(verbose_name='Power Delivery (Вт)', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'USB-хаб'
        verbose_name_plural = 'USB-хабы'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class DeskLighting(models.Model):
    """Освещение рабочего места"""
    LIGHTING_TYPE_CHOICES = [
        ('led_strip', 'LED лента'),
        ('desk_lamp', 'Настольная лампа'),
        ('monitor_bar', 'Лампа на монитор'),
        ('ambient', 'Ambient подсветка'),
        ('ring_light', 'Кольцевая лампа'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    lighting_type = models.CharField(max_length=20, choices=LIGHTING_TYPE_CHOICES, verbose_name='Тип освещения')
    rgb = models.BooleanField(default=False, verbose_name='RGB')
    dimmable = models.BooleanField(default=True, verbose_name='Регулировка яркости')
    color_temperature = models.CharField(max_length=50, verbose_name='Цветовая температура', blank=True)
    smart_control = models.BooleanField(default=False, verbose_name='Умное управление')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Освещение'
        verbose_name_plural = 'Освещение'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class StreamDeck(models.Model):
    """Стрим-пульт"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    keys_count = models.IntegerField(verbose_name='Количество клавиш')
    lcd_keys = models.BooleanField(default=True, verbose_name='LCD клавиши')
    dials = models.IntegerField(verbose_name='Количество крутилок', default=0)
    touchscreen = models.BooleanField(default=False, verbose_name='Сенсорный экран')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Стрим-пульт'
        verbose_name_plural = 'Стрим-пульты'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class CaptureCard(models.Model):
    """Карта захвата видео"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    max_resolution = models.CharField(max_length=50, verbose_name='Макс. разрешение')
    max_fps = models.IntegerField(verbose_name='Макс. FPS')
    connection = models.CharField(max_length=50, verbose_name='Подключение')
    passthrough = models.BooleanField(default=True, verbose_name='Passthrough')
    internal = models.BooleanField(default=False, verbose_name='Внутренняя')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Карта захвата'
        verbose_name_plural = 'Карты захвата'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Gamepad(models.Model):
    """Геймпад"""
    PLATFORM_CHOICES = [
        ('pc', 'PC'),
        ('xbox', 'Xbox'),
        ('playstation', 'PlayStation'),
        ('universal', 'Универсальный'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name='Платформа')
    wireless = models.BooleanField(default=False, verbose_name='Беспроводной')
    vibration = models.BooleanField(default=True, verbose_name='Вибрация')
    rgb = models.BooleanField(default=False, verbose_name='RGB подсветка')
    extra_buttons = models.IntegerField(verbose_name='Доп. кнопки', default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Геймпад'
        verbose_name_plural = 'Геймпады'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Headphonestand(models.Model):
    """Подставка для наушников"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    usb_hub = models.BooleanField(default=False, verbose_name='Встроенный USB-хаб')
    usb_ports = models.IntegerField(verbose_name='USB портов', default=0)
    rgb = models.BooleanField(default=False, verbose_name='RGB подсветка')
    wireless_charging = models.BooleanField(default=False, verbose_name='Беспроводная зарядка')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Подставка для наушников'
        verbose_name_plural = 'Подставки для наушников'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'
