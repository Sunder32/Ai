from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
from .serializers import (
    CPUSerializer, GPUSerializer, MotherboardSerializer, RAMSerializer,
    StorageSerializer, PSUSerializer, CaseSerializer, CoolingSerializer
)


class CPUViewSet(viewsets.ModelViewSet):
    queryset = CPU.objects.all()
    serializer_class = CPUSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'socket', 'cores']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'performance_score', 'cores']


class GPUViewSet(viewsets.ModelViewSet):
    queryset = GPU.objects.all()
    serializer_class = GPUSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'memory']
    search_fields = ['name', 'manufacturer', 'chipset']
    ordering_fields = ['price', 'performance_score', 'memory']


class MotherboardViewSet(viewsets.ModelViewSet):
    queryset = Motherboard.objects.all()
    serializer_class = MotherboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'socket', 'form_factor', 'chipset']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class RAMViewSet(viewsets.ModelViewSet):
    queryset = RAM.objects.all()
    serializer_class = RAMSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'memory_type', 'capacity', 'speed']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'capacity', 'speed']


class StorageViewSet(viewsets.ModelViewSet):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'storage_type', 'capacity']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'capacity']


class PSUViewSet(viewsets.ModelViewSet):
    queryset = PSU.objects.all()
    serializer_class = PSUSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'wattage', 'efficiency_rating', 'modular']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'wattage']


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'form_factor', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class CoolingViewSet(viewsets.ModelViewSet):
    queryset = Cooling.objects.all()
    serializer_class = CoolingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'cooling_type', 'max_tdp']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'max_tdp', 'noise_level']
