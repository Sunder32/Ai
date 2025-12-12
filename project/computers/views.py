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


CACHE_TTL = 60 * 15


class ReadOnlyOrAdminPermission(IsAuthenticatedOrReadOnly):
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class CachedModelViewSet(viewsets.ModelViewSet):
    
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
    
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'socket', 'cores']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'performance_score', 'cores']


class GPUViewSet(CachedModelViewSet):
    
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'memory']
    search_fields = ['name', 'manufacturer', 'chipset']
    ordering_fields = ['price', 'performance_score', 'memory']


class MotherboardViewSet(CachedModelViewSet):
    
    queryset = Motherboard.objects.all()
    serializer_class = MotherboardSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'socket', 'form_factor', 'chipset']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class RAMViewSet(CachedModelViewSet):
    
    queryset = RAM.objects.all()
    serializer_class = RAMSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'memory_type', 'capacity', 'speed']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'capacity', 'speed']


class StorageViewSet(CachedModelViewSet):
    
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'storage_type', 'capacity']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'capacity']


class PSUViewSet(CachedModelViewSet):
    
    queryset = PSU.objects.all()
    serializer_class = PSUSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'wattage', 'efficiency_rating', 'modular']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'wattage']


class CaseViewSet(CachedModelViewSet):
    
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'form_factor', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class CoolingViewSet(CachedModelViewSet):
    
    queryset = Cooling.objects.all()
    serializer_class = CoolingSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'cooling_type', 'max_tdp']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'max_tdp', 'noise_level']
