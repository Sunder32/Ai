from django.contrib import admin
from .models import Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'screen_size', 'resolution', 'refresh_rate', 'price']
    list_filter = ['manufacturer', 'screen_size', 'refresh_rate', 'panel_type']
    search_fields = ['name', 'manufacturer']


@admin.register(Keyboard)
class KeyboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'switch_type', 'wireless', 'rgb', 'price']
    list_filter = ['manufacturer', 'switch_type', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']


@admin.register(Mouse)
class MouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'dpi', 'wireless', 'rgb', 'price']
    list_filter = ['manufacturer', 'sensor_type', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']


@admin.register(Headset)
class HeadsetAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'wireless', 'microphone', 'price']
    list_filter = ['manufacturer', 'wireless', 'microphone', 'surround']
    search_fields = ['name', 'manufacturer']


@admin.register(Webcam)
class WebcamAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'resolution', 'fps', 'price']
    list_filter = ['manufacturer', 'autofocus']
    search_fields = ['name', 'manufacturer']


@admin.register(Microphone)
class MicrophoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'microphone_type', 'price']
    list_filter = ['manufacturer', 'microphone_type']
    search_fields = ['name', 'manufacturer']


@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'width', 'depth', 'adjustable_height', 'price']
    list_filter = ['manufacturer', 'adjustable_height']
    search_fields = ['name', 'manufacturer']


@admin.register(Chair)
class ChairAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'ergonomic', 'lumbar_support', 'price']
    list_filter = ['manufacturer', 'ergonomic', 'lumbar_support']
    search_fields = ['name', 'manufacturer']
