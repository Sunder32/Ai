from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair
from .serializers import (
    MonitorSerializer, KeyboardSerializer, MouseSerializer, HeadsetSerializer,
    WebcamSerializer, MicrophoneSerializer, DeskSerializer, ChairSerializer
)


class MonitorViewSet(viewsets.ModelViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'screen_size', 'resolution', 'refresh_rate', 'panel_type']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'screen_size', 'refresh_rate']


class KeyboardViewSet(viewsets.ModelViewSet):
    queryset = Keyboard.objects.all()
    serializer_class = KeyboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'switch_type', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class MouseViewSet(viewsets.ModelViewSet):
    queryset = Mouse.objects.all()
    serializer_class = MouseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'sensor_type', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'dpi']


class HeadsetViewSet(viewsets.ModelViewSet):
    queryset = Headset.objects.all()
    serializer_class = HeadsetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'wireless', 'microphone', 'surround', 'noise_cancelling']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class WebcamViewSet(viewsets.ModelViewSet):
    queryset = Webcam.objects.all()
    serializer_class = WebcamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'resolution', 'fps', 'autofocus']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class MicrophoneViewSet(viewsets.ModelViewSet):
    queryset = Microphone.objects.all()
    serializer_class = MicrophoneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'microphone_type', 'connection']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class DeskViewSet(viewsets.ModelViewSet):
    queryset = Desk.objects.all()
    serializer_class = DeskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'adjustable_height']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'width', 'depth']


class ChairViewSet(viewsets.ModelViewSet):
    queryset = Chair.objects.all()
    serializer_class = ChairSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'ergonomic', 'adjustable_armrests', 'lumbar_support']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']
