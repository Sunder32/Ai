from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PCConfigurationViewSet, WorkspaceSetupViewSet, RecommendationViewSet

router = DefaultRouter()
router.register(r'configurations', PCConfigurationViewSet, basename='configuration')
router.register(r'workspace-setups', WorkspaceSetupViewSet, basename='workspace-setup')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
]
