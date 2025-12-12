from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair,
    Speakers, Mousepad, MonitorArm, USBHub, DeskLighting, StreamDeck,
    CaptureCard, Gamepad, Headphonestand
)
from .serializers import (
    MonitorSerializer, KeyboardSerializer, MouseSerializer, HeadsetSerializer,
    WebcamSerializer, MicrophoneSerializer, DeskSerializer, ChairSerializer,
    SpeakersSerializer, MousepadSerializer, MonitorArmSerializer, USBHubSerializer,
    DeskLightingSerializer, StreamDeckSerializer, CaptureCardSerializer,
    GamepadSerializer, HeadphonestandSerializer
)


class ReadOnlyOrAdminPermission(IsAuthenticatedOrReadOnly):

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class PeripheralViewSet(viewsets.ModelViewSet):

    pagination_class = None


class MonitorViewSet(PeripheralViewSet):
    
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'screen_size', 'resolution', 'refresh_rate', 'panel_type']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'screen_size', 'refresh_rate']


class KeyboardViewSet(PeripheralViewSet):
    
    queryset = Keyboard.objects.all()
    serializer_class = KeyboardSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'switch_type', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class MouseViewSet(PeripheralViewSet):
    
    queryset = Mouse.objects.all()
    serializer_class = MouseSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'sensor_type', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'dpi']


class HeadsetViewSet(PeripheralViewSet):
    
    queryset = Headset.objects.all()
    serializer_class = HeadsetSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'wireless', 'microphone', 'surround', 'noise_cancelling']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class WebcamViewSet(PeripheralViewSet):
    
    queryset = Webcam.objects.all()
    serializer_class = WebcamSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'resolution', 'fps', 'autofocus']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class MicrophoneViewSet(PeripheralViewSet):
    
    queryset = Microphone.objects.all()
    serializer_class = MicrophoneSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'microphone_type', 'connection']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class DeskViewSet(PeripheralViewSet):
    
    queryset = Desk.objects.all()
    serializer_class = DeskSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'adjustable_height']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'width', 'depth']


class ChairViewSet(PeripheralViewSet):
    
    queryset = Chair.objects.all()
    serializer_class = ChairSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'ergonomic', 'adjustable_armrests', 'lumbar_support']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class SpeakersViewSet(PeripheralViewSet):
    
    queryset = Speakers.objects.all()
    serializer_class = SpeakersSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'speaker_type', 'bluetooth', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'total_power']


class MousepadViewSet(PeripheralViewSet):
    
    queryset = Mousepad.objects.all()
    serializer_class = MousepadSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'size', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'width', 'height']


class MonitorArmViewSet(PeripheralViewSet):
   
    queryset = MonitorArm.objects.all()
    serializer_class = MonitorArmSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'mount_type', 'gas_spring']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'max_screen_size']


class USBHubViewSet(PeripheralViewSet):
    
    queryset = USBHub.objects.all()
    serializer_class = USBHubSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'card_reader', 'hdmi_port', 'ethernet_port']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class DeskLightingViewSet(PeripheralViewSet):
    
    queryset = DeskLighting.objects.all()
    serializer_class = DeskLightingSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'lighting_type', 'rgb', 'smart_control']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class StreamDeckViewSet(PeripheralViewSet):
    
    queryset = StreamDeck.objects.all()
    serializer_class = StreamDeckSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'keys_count', 'lcd_keys', 'touchscreen']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'keys_count']


class CaptureCardViewSet(PeripheralViewSet):
    
    queryset = CaptureCard.objects.all()
    serializer_class = CaptureCardSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'max_resolution', 'internal', 'passthrough']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price', 'max_fps']


class GamepadViewSet(PeripheralViewSet):
    
    queryset = Gamepad.objects.all()
    serializer_class = GamepadSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'platform', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']


class HeadphonestandViewSet(PeripheralViewSet):
    
    queryset = Headphonestand.objects.all()
    serializer_class = HeadphonestandSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'usb_hub', 'rgb', 'wireless_charging']
    search_fields = ['name', 'manufacturer']
    ordering_fields = ['price']
