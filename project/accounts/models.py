from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    
    USER_TYPE_CHOICES = [
        ('designer', 'Дизайнер'),
        ('programmer', 'Программист'),
        ('gamer', 'Геймер'),
        ('office', 'Офисный работник'),
        ('student', 'Студент'),
        ('content_creator', 'Контент-криэйтор'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Тип пользователя'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.username


class UserProfile(models.Model):

    
    PRIORITY_CHOICES = [
        ('performance', 'Производительность'),
        ('silence', 'Тишина работы'),
        ('compactness', 'Компактность'),
        ('aesthetics', 'Эстетика'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    

    min_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Минимальный бюджет'
    )
    max_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Максимальный бюджет'
    )
    

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='performance',
        verbose_name='Приоритет'
    )
    

    multitasking = models.BooleanField(default=False, verbose_name='Многозадачность')
    work_with_4k = models.BooleanField(default=False, verbose_name='Работа с 4K')
    vr_support = models.BooleanField(default=False, verbose_name='Поддержка VR')
    video_editing = models.BooleanField(default=False, verbose_name='Видеомонтаж')
    gaming = models.BooleanField(default=False, verbose_name='Гейминг')
    streaming = models.BooleanField(default=False, verbose_name='Стриминг')
    

    has_existing_components = models.BooleanField(
        default=False,
        verbose_name='Есть существующие компоненты'
    )
    existing_components_description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание существующих компонентов'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f'Профиль {self.user.username}'
