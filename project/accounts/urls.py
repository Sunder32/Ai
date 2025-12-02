from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet, login_view, register_view, logout_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]
