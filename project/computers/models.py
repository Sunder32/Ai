from django.db import models


class CPU(models.Model):
    """Процессор"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    socket = models.CharField(max_length=50, verbose_name='Сокет')
    cores = models.IntegerField(verbose_name='Количество ядер')
    threads = models.IntegerField(verbose_name='Количество потоков')
    base_clock = models.FloatField(verbose_name='Базовая частота (ГГц)')
    boost_clock = models.FloatField(verbose_name='Турбо частота (ГГц)', null=True, blank=True)
    tdp = models.IntegerField(verbose_name='TDP (Вт)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    performance_score = models.IntegerField(verbose_name='Оценка производительности', default=0)
    
    # AI Generation fields
    is_ai_generated = models.BooleanField(default=False, verbose_name='Сгенерировано AI')
    ai_generation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата генерации AI')
    ai_confidence = models.FloatField(null=True, blank=True, verbose_name='Уверенность AI (0-1)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Процессор'
        verbose_name_plural = 'Процессоры'
        ordering = ['-performance_score']
        indexes = [
            models.Index(fields=['price', 'performance_score']),
            models.Index(fields=['manufacturer', 'socket']),
            models.Index(fields=['-performance_score', 'price']),
            models.Index(fields=['socket', 'price']),
        ]
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class GPU(models.Model):
    """Видеокарта"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    chipset = models.CharField(max_length=100, verbose_name='Чипсет')
    memory = models.IntegerField(verbose_name='Объем памяти (ГБ)')
    memory_type = models.CharField(max_length=50, verbose_name='Тип памяти')
    core_clock = models.IntegerField(verbose_name='Частота ядра (МГц)')
    boost_clock = models.IntegerField(verbose_name='Boost частота (МГц)', null=True, blank=True)
    tdp = models.IntegerField(verbose_name='TDP (Вт)')
    recommended_psu = models.IntegerField(verbose_name='Рекомендуемый БП (Вт)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    performance_score = models.IntegerField(verbose_name='Оценка производительности', default=0)
    
    # AI Generation fields
    is_ai_generated = models.BooleanField(default=False, verbose_name='Сгенерировано AI')
    ai_generation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата генерации AI')
    ai_confidence = models.FloatField(null=True, blank=True, verbose_name='Уверенность AI (0-1)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Видеокарта'
        verbose_name_plural = 'Видеокарты'
        ordering = ['-performance_score']
        indexes = [
            models.Index(fields=['price', 'performance_score']),
            models.Index(fields=['manufacturer', 'memory']),
            models.Index(fields=['-performance_score', 'price']),
            models.Index(fields=['memory', 'price']),
        ]
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Motherboard(models.Model):
    """Материнская плата"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    socket = models.CharField(max_length=50, verbose_name='Сокет')
    chipset = models.CharField(max_length=100, verbose_name='Чипсет')
    form_factor = models.CharField(max_length=50, verbose_name='Форм-фактор')
    memory_slots = models.IntegerField(verbose_name='Количество слотов памяти')
    max_memory = models.IntegerField(verbose_name='Максимальный объем памяти (ГБ)')
    memory_type = models.CharField(max_length=50, verbose_name='Тип памяти')
    pcie_slots = models.IntegerField(verbose_name='Количество PCIe слотов')
    m2_slots = models.IntegerField(verbose_name='Количество M.2 слотов', default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    
    # AI Generation fields
    is_ai_generated = models.BooleanField(default=False, verbose_name='Сгенерировано AI')
    ai_generation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата генерации AI')
    ai_confidence = models.FloatField(null=True, blank=True, verbose_name='Уверенность AI (0-1)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Материнская плата'
        verbose_name_plural = 'Материнские платы'
        indexes = [
            models.Index(fields=['socket', 'price']),
            models.Index(fields=['manufacturer', 'form_factor']),
        ]
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class RAM(models.Model):
    """Оперативная память"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    memory_type = models.CharField(max_length=50, verbose_name='Тип памяти')
    capacity = models.IntegerField(verbose_name='Объем (ГБ)')
    speed = models.IntegerField(verbose_name='Частота (МГц)')
    modules = models.IntegerField(verbose_name='Количество модулей', default=1)
    cas_latency = models.CharField(max_length=50, verbose_name='CAS латентность', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    
    # AI Generation fields
    is_ai_generated = models.BooleanField(default=False, verbose_name='Сгенерировано AI')
    ai_generation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата генерации AI')
    ai_confidence = models.FloatField(null=True, blank=True, verbose_name='Уверенность AI (0-1)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Оперативная память'
        verbose_name_plural = 'Оперативная память'
        indexes = [
            models.Index(fields=['capacity', 'price']),
            models.Index(fields=['memory_type', 'speed']),
        ]
    
    def __str__(self):
        return f'{self.manufacturer} {self.name} {self.capacity}GB'


class Storage(models.Model):
    """Накопитель"""
    STORAGE_TYPE_CHOICES = [
        ('ssd_nvme', 'SSD NVMe'),
        ('ssd_sata', 'SSD SATA'),
        ('hdd', 'HDD'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPE_CHOICES, verbose_name='Тип')
    capacity = models.IntegerField(verbose_name='Объем (ГБ)')
    read_speed = models.IntegerField(verbose_name='Скорость чтения (МБ/с)', null=True, blank=True)
    write_speed = models.IntegerField(verbose_name='Скорость записи (МБ/с)', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    
    # AI Generation fields
    is_ai_generated = models.BooleanField(default=False, verbose_name='Сгенерировано AI')
    ai_generation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата генерации AI')
    ai_confidence = models.FloatField(null=True, blank=True, verbose_name='Уверенность AI (0-1)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Накопитель'
        verbose_name_plural = 'Накопители'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name} {self.capacity}GB'


class PSU(models.Model):
    """Блок питания"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    wattage = models.IntegerField(verbose_name='Мощность (Вт)')
    efficiency_rating = models.CharField(max_length=50, verbose_name='Сертификат 80 PLUS')
    modular = models.BooleanField(default=False, verbose_name='Модульный')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    
    # AI Generation fields
    is_ai_generated = models.BooleanField(default=False, verbose_name='Сгенерировано AI')
    ai_generation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата генерации AI')
    ai_confidence = models.FloatField(null=True, blank=True, verbose_name='Уверенность AI (0-1)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Блок питания'
        verbose_name_plural = 'Блоки питания'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name} {self.wattage}W'


class Case(models.Model):
    """Корпус"""
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    form_factor = models.CharField(max_length=50, verbose_name='Форм-фактор')
    max_gpu_length = models.IntegerField(verbose_name='Макс. длина видеокарты (мм)', null=True, blank=True)
    fan_slots = models.IntegerField(verbose_name='Слоты для вентиляторов', default=0)
    rgb = models.BooleanField(default=False, verbose_name='RGB подсветка')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    
    # AI Generation fields
    is_ai_generated = models.BooleanField(default=False, verbose_name='Сгенерировано AI')
    ai_generation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата генерации AI')
    ai_confidence = models.FloatField(null=True, blank=True, verbose_name='Уверенность AI (0-1)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Корпус'
        verbose_name_plural = 'Корпуса'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'


class Cooling(models.Model):
    """Система охлаждения"""
    COOLING_TYPE_CHOICES = [
        ('air', 'Воздушное'),
        ('aio', 'Водяное (AIO)'),
        ('custom', 'Кастомное водяное'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    cooling_type = models.CharField(max_length=20, choices=COOLING_TYPE_CHOICES, verbose_name='Тип')
    socket_compatibility = models.TextField(verbose_name='Совместимые сокеты')
    max_tdp = models.IntegerField(verbose_name='Макс. TDP (Вт)')
    noise_level = models.IntegerField(verbose_name='Уровень шума (дБ)', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    
    # AI Generation fields
    is_ai_generated = models.BooleanField(default=False, verbose_name='Сгенерировано AI')
    ai_generation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата генерации AI')
    ai_confidence = models.FloatField(null=True, blank=True, verbose_name='Уверенность AI (0-1)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Система охлаждения'
        verbose_name_plural = 'Системы охлаждения'
    
    def __str__(self):
        return f'{self.manufacturer} {self.name}'
