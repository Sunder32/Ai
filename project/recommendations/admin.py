from django.contrib import admin
from .models import PCConfiguration, WorkspaceSetup, Recommendation


class RecommendationInline(admin.TabularInline):
    model = Recommendation
    extra = 0
    readonly_fields = ['component_type', 'component_id', 'reason']


@admin.register(PCConfiguration)
class PCConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'total_price', 'compatibility_check', 'is_saved', 'created_at']
    list_filter = ['compatibility_check', 'is_saved', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    inlines = [RecommendationInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'is_saved')
        }),
        ('Компоненты', {
            'fields': ('cpu', 'gpu', 'motherboard', 'ram', 'storage_primary', 
                      'storage_secondary', 'psu', 'case', 'cooling')
        }),
        ('Совместимость и цена', {
            'fields': ('total_price', 'compatibility_check', 'compatibility_notes')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WorkspaceSetup)
class WorkspaceSetupAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'configuration', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['total_price', 'created_at', 'updated_at']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['configuration', 'component_type', 'component_id', 'created_at']
    list_filter = ['component_type', 'created_at']
    search_fields = ['configuration__name', 'reason']
