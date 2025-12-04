from django.contrib import admin
from .models import (
    Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair,
    Speakers, Mousepad, MonitorArm, USBHub, DeskLighting, StreamDeck,
    CaptureCard, Gamepad, Headphonestand
)


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


@admin.register(Speakers)
class SpeakersAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'speaker_type', 'total_power', 'bluetooth', 'price']
    list_filter = ['manufacturer', 'speaker_type', 'bluetooth', 'rgb']
    search_fields = ['name', 'manufacturer']


@admin.register(Mousepad)
class MousepadAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'size', 'width', 'height', 'rgb', 'price']
    list_filter = ['manufacturer', 'size', 'rgb']
    search_fields = ['name', 'manufacturer']


@admin.register(MonitorArm)
class MonitorArmAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'mount_type', 'max_screen_size', 'gas_spring', 'price']
    list_filter = ['manufacturer', 'mount_type', 'gas_spring']
    search_fields = ['name', 'manufacturer']


@admin.register(USBHub)
class USBHubAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'usb3_ports', 'usbc_ports', 'hdmi_port', 'price']
    list_filter = ['manufacturer', 'card_reader', 'hdmi_port', 'ethernet_port']
    search_fields = ['name', 'manufacturer']


@admin.register(DeskLighting)
class DeskLightingAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'lighting_type', 'rgb', 'smart_control', 'price']
    list_filter = ['manufacturer', 'lighting_type', 'rgb', 'smart_control']
    search_fields = ['name', 'manufacturer']


@admin.register(StreamDeck)
class StreamDeckAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'keys_count', 'lcd_keys', 'dials', 'price']
    list_filter = ['manufacturer', 'lcd_keys', 'touchscreen']
    search_fields = ['name', 'manufacturer']


@admin.register(CaptureCard)
class CaptureCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'max_resolution', 'max_fps', 'internal', 'price']
    list_filter = ['manufacturer', 'internal', 'passthrough']
    search_fields = ['name', 'manufacturer']


@admin.register(Gamepad)
class GamepadAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'platform', 'wireless', 'vibration', 'price']
    list_filter = ['manufacturer', 'platform', 'wireless', 'rgb']
    search_fields = ['name', 'manufacturer']


@admin.register(Headphonestand)
class HeadphonestandAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'usb_hub', 'usb_ports', 'rgb', 'price']
    list_filter = ['manufacturer', 'usb_hub', 'rgb', 'wireless_charging']
    search_fields = ['name', 'manufacturer']
