from django.contrib import admin
from .models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling


@admin.register(CPU)
class CPUAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'cores', 'threads', 'price', 'performance_score']
    list_filter = ['manufacturer', 'socket']
    search_fields = ['name', 'manufacturer']


@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'memory', 'price', 'performance_score']
    list_filter = ['manufacturer', 'memory']
    search_fields = ['name', 'manufacturer', 'chipset']


@admin.register(Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'socket', 'chipset', 'form_factor', 'price']
    list_filter = ['manufacturer', 'socket', 'form_factor']
    search_fields = ['name', 'manufacturer']


@admin.register(RAM)
class RAMAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'capacity', 'speed', 'price']
    list_filter = ['manufacturer', 'memory_type', 'capacity']
    search_fields = ['name', 'manufacturer']


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'storage_type', 'capacity', 'price']
    list_filter = ['manufacturer', 'storage_type']
    search_fields = ['name', 'manufacturer']


@admin.register(PSU)
class PSUAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'wattage', 'efficiency_rating', 'modular', 'price']
    list_filter = ['manufacturer', 'efficiency_rating', 'modular']
    search_fields = ['name', 'manufacturer']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'form_factor', 'rgb', 'price']
    list_filter = ['manufacturer', 'form_factor', 'rgb']
    search_fields = ['name', 'manufacturer']


@admin.register(Cooling)
class CoolingAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'cooling_type', 'max_tdp', 'price']
    list_filter = ['manufacturer', 'cooling_type']
    search_fields = ['name', 'manufacturer']
