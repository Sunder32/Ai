from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MonitorViewSet, KeyboardViewSet, MouseViewSet, HeadsetViewSet,
    WebcamViewSet, MicrophoneViewSet, DeskViewSet, ChairViewSet,
    SpeakersViewSet, MousepadViewSet, MonitorArmViewSet, USBHubViewSet,
    DeskLightingViewSet, StreamDeckViewSet, CaptureCardViewSet,
    GamepadViewSet, HeadphonestandViewSet
)

router = DefaultRouter()
router.register(r'monitors', MonitorViewSet, basename='monitor')
router.register(r'keyboards', KeyboardViewSet, basename='keyboard')
router.register(r'mice', MouseViewSet, basename='mouse')
router.register(r'headsets', HeadsetViewSet, basename='headset')
router.register(r'webcams', WebcamViewSet, basename='webcam')
router.register(r'microphones', MicrophoneViewSet, basename='microphone')
router.register(r'desks', DeskViewSet, basename='desk')
router.register(r'chairs', ChairViewSet, basename='chair')
router.register(r'speakers', SpeakersViewSet, basename='speakers')
router.register(r'mousepads', MousepadViewSet, basename='mousepad')
router.register(r'monitor-arms', MonitorArmViewSet, basename='monitor-arm')
router.register(r'usb-hubs', USBHubViewSet, basename='usb-hub')
router.register(r'lighting', DeskLightingViewSet, basename='lighting')
router.register(r'stream-decks', StreamDeckViewSet, basename='stream-deck')
router.register(r'capture-cards', CaptureCardViewSet, basename='capture-card')
router.register(r'gamepads', GamepadViewSet, basename='gamepad')
router.register(r'headphone-stands', HeadphonestandViewSet, basename='headphone-stand')

urlpatterns = [
    path('', include(router.urls)),
]
