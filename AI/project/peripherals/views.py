from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair
from .serializers import (
    MonitorSerializer, KeyboardSerializer, MouseSerializer, HeadsetSerializer,
    WebcamSerializer, MicrophoneSerializer, DeskSerializer, ChairSerializer
)


class ReadOnlyOrAdminPermission(IsAuthenticatedOrReadOnly):
    """Разрешает чтение всем авторизованным, создание/изменение только админам"""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class MonitorViewSet(viewsets.ModelViewSet):
    """ViewSet для мониторов. Чтение - авторизованным, изменение - только админам"""
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'screen_size', 'resolution', 'refresh_rate', 'panel_type']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'screen_size', 'refresh_rate']


class KeyboardViewSet(viewsets.ModelViewSet):
    """ViewSet для клавиатур. Чтение - авторизованным, изменение - только админам"""
    queryset = Keyboard.objects.all()
    serializer_class = KeyboardSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'switch_type', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class MouseViewSet(viewsets.ModelViewSet):
    """ViewSet для мышей. Чтение - авторизованным, изменение - только админам"""
    queryset = Mouse.objects.all()
    serializer_class = MouseSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'sensor_type', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'dpi']


class HeadsetViewSet(viewsets.ModelViewSet):
    """ViewSet для гарнитур. Чтение - авторизованным, изменение - только админам"""
    queryset = Headset.objects.all()
    serializer_class = HeadsetSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'wireless', 'microphone', 'surround', 'noise_cancelling']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class WebcamViewSet(viewsets.ModelViewSet):
    """ViewSet для веб-камер. Чтение - авторизованным, изменение - только админам"""
    queryset = Webcam.objects.all()
    serializer_class = WebcamSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'resolution', 'fps', 'autofocus']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class MicrophoneViewSet(viewsets.ModelViewSet):
    """ViewSet для микрофонов. Чтение - авторизованным, изменение - только админам"""
    queryset = Microphone.objects.all()
    serializer_class = MicrophoneSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'microphone_type', 'connection']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class DeskViewSet(viewsets.ModelViewSet):
    """ViewSet для столов. Чтение - авторизованным, изменение - только админам"""
    queryset = Desk.objects.all()
    serializer_class = DeskSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'adjustable_height']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'width', 'depth']


class ChairViewSet(viewsets.ModelViewSet):
    """ViewSet для кресел. Чтение - авторизованным, изменение - только админам"""
    queryset = Chair.objects.all()
    serializer_class = ChairSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'ergonomic', 'adjustable_armrests', 'lumbar_support']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']
