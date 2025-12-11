from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
from .serializers import (
    CPUSerializer, GPUSerializer, MotherboardSerializer, RAMSerializer,
    StorageSerializer, PSUSerializer, CaseSerializer, CoolingSerializer
)

# Время кэширования для компонентов (15 минут)
CACHE_TTL = 60 * 15


class ReadOnlyOrAdminPermission(IsAuthenticatedOrReadOnly):
    """Разрешает чтение всем авторизованным, создание/изменение только админам"""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class CachedModelViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet с кэшированием для списка и деталей"""
    # Отключаем пагинацию для компонентов - нужно показывать все сразу
    pagination_class = None
    
    @method_decorator(cache_page(CACHE_TTL))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(CACHE_TTL))
    @method_decorator(vary_on_headers('Authorization'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CPUViewSet(CachedModelViewSet):
    """ViewSet для процессоров. Чтение - авторизованным, изменение - только админам"""
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'socket', 'cores']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'performance_score', 'cores']


class GPUViewSet(CachedModelViewSet):
    """ViewSet для видеокарт. Чтение - авторизованным, изменение - только админам"""
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'memory']
    search_fields = ['name', 'manufacturer', 'chipset']
    ordering_fields = ['price', 'performance_score', 'memory']


class MotherboardViewSet(CachedModelViewSet):
    """ViewSet для материнских плат. Чтение - авторизованным, изменение - только админам"""
    queryset = Motherboard.objects.all()
    serializer_class = MotherboardSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'socket', 'form_factor', 'chipset']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class RAMViewSet(CachedModelViewSet):
    """ViewSet для оперативной памяти. Чтение - авторизованным, изменение - только админам"""
    queryset = RAM.objects.all()
    serializer_class = RAMSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'memory_type', 'capacity', 'speed']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'capacity', 'speed']


class StorageViewSet(CachedModelViewSet):
    """ViewSet для накопителей. Чтение - авторизованным, изменение - только админам"""
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'storage_type', 'capacity']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'capacity']


class PSUViewSet(CachedModelViewSet):
    """ViewSet для блоков питания. Чтение - авторизованным, изменение - только админам"""
    queryset = PSU.objects.all()
    serializer_class = PSUSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'wattage', 'efficiency_rating', 'modular']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'wattage']


class CaseViewSet(CachedModelViewSet):
    """ViewSet для корпусов. Чтение - авторизованным, изменение - только админам"""
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'form_factor', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class CoolingViewSet(CachedModelViewSet):
    """ViewSet для систем охлаждения. Чтение - авторизованным, изменение - только админам"""
    queryset = Cooling.objects.all()
    serializer_class = CoolingSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'cooling_type', 'max_tdp']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'max_tdp', 'noise_level']
