from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_staff', 'created_at']
    list_filter = ['user_type', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('user_type', 'phone')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'min_budget', 'max_budget', 'priority', 'created_at']
    list_filter = ['priority', 'multitasking', 'gaming', 'streaming']
    search_fields = ['user__username', 'user__email']
