from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MonitorViewSet, KeyboardViewSet, MouseViewSet, HeadsetViewSet,
    WebcamViewSet, MicrophoneViewSet, DeskViewSet, ChairViewSet
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

urlpatterns = [
    path('', include(router.urls)),
]
