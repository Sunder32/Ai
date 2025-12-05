from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CPUViewSet, GPUViewSet, MotherboardViewSet, RAMViewSet,
    StorageViewSet, PSUViewSet, CaseViewSet, CoolingViewSet
)

router = DefaultRouter()
router.register(r'cpu', CPUViewSet, basename='cpu')
router.register(r'gpu', GPUViewSet, basename='gpu')
router.register(r'motherboard', MotherboardViewSet, basename='motherboard')
router.register(r'ram', RAMViewSet, basename='ram')
router.register(r'storage', StorageViewSet, basename='storage')
router.register(r'psu', PSUViewSet, basename='psu')
router.register(r'case', CaseViewSet, basename='case')
router.register(r'cooling', CoolingViewSet, basename='cooling')

urlpatterns = [
    path('', include(router.urls)),
]
