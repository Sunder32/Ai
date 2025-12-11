from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PCConfigurationViewSet, WorkspaceSetupViewSet, RecommendationViewSet, 
    WishlistViewSet, AIChatViewSet, PriceParserViewSet, 
    PersonalizationViewSet, AIAnalyticsViewSet
)

router = DefaultRouter()
router.register(r'configurations', PCConfigurationViewSet, basename='configuration')
router.register(r'workspace-setups', WorkspaceSetupViewSet, basename='workspace-setup')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# AI Chat & Personalization
router.register(r'chat', AIChatViewSet, basename='ai-chat')
router.register(r'prices', PriceParserViewSet, basename='price-parser')
router.register(r'personalization', PersonalizationViewSet, basename='personalization')
router.register(r'ai-analytics', AIAnalyticsViewSet, basename='ai-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
