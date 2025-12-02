from rest_framework import serializers
from .models import PCConfiguration, WorkspaceSetup, Recommendation
from computers.serializers import (
    CPUSerializer, GPUSerializer, MotherboardSerializer, RAMSerializer,
    StorageSerializer, PSUSerializer, CaseSerializer, CoolingSerializer
)
from peripherals.serializers import (
    MonitorSerializer, KeyboardSerializer, MouseSerializer, HeadsetSerializer,
    WebcamSerializer, MicrophoneSerializer, DeskSerializer, ChairSerializer
)


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


class PCConfigurationSerializer(serializers.ModelSerializer):
    cpu_detail = CPUSerializer(source='cpu', read_only=True)
    gpu_detail = GPUSerializer(source='gpu', read_only=True)
    motherboard_detail = MotherboardSerializer(source='motherboard', read_only=True)
    ram_detail = RAMSerializer(source='ram', read_only=True)
    storage_primary_detail = StorageSerializer(source='storage_primary', read_only=True)
    storage_secondary_detail = StorageSerializer(source='storage_secondary', read_only=True)
    psu_detail = PSUSerializer(source='psu', read_only=True)
    case_detail = CaseSerializer(source='case', read_only=True)
    cooling_detail = CoolingSerializer(source='cooling', read_only=True)
    recommendations = RecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = PCConfiguration
        fields = '__all__'
        read_only_fields = ['total_price', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        configuration = super().create(validated_data)
        configuration.calculate_total_price()
        configuration.save()
        return configuration
    
    def update(self, instance, validated_data):
        configuration = super().update(instance, validated_data)
        configuration.calculate_total_price()
        configuration.save()
        return configuration


class WorkspaceSetupSerializer(serializers.ModelSerializer):
    configuration_detail = PCConfigurationSerializer(source='configuration', read_only=True)
    monitor_primary_detail = MonitorSerializer(source='monitor_primary', read_only=True)
    monitor_secondary_detail = MonitorSerializer(source='monitor_secondary', read_only=True)
    keyboard_detail = KeyboardSerializer(source='keyboard', read_only=True)
    mouse_detail = MouseSerializer(source='mouse', read_only=True)
    headset_detail = HeadsetSerializer(source='headset', read_only=True)
    webcam_detail = WebcamSerializer(source='webcam', read_only=True)
    microphone_detail = MicrophoneSerializer(source='microphone', read_only=True)
    desk_detail = DeskSerializer(source='desk', read_only=True)
    chair_detail = ChairSerializer(source='chair', read_only=True)
    
    class Meta:
        model = WorkspaceSetup
        fields = '__all__'
        read_only_fields = ['total_price', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        workspace = super().create(validated_data)
        workspace.calculate_total_price()
        workspace.save()
        return workspace
    
    def update(self, instance, validated_data):
        workspace = super().update(instance, validated_data)
        workspace.calculate_total_price()
        workspace.save()
        return workspace


class ConfigurationRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса на подбор конфигурации"""
    user_type = serializers.ChoiceField(choices=[
        ('designer', 'Дизайнер'),
        ('programmer', 'Программист'),
        ('gamer', 'Геймер'),
        ('office', 'Офисный работник'),
        ('student', 'Студент'),
        ('content_creator', 'Контент-криэйтор'),
    ])
    min_budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    priority = serializers.ChoiceField(choices=[
        ('performance', 'Производительность'),
        ('silence', 'Тишина работы'),
        ('compactness', 'Компактность'),
        ('aesthetics', 'Эстетика'),
    ])
    multitasking = serializers.BooleanField(default=False)
    work_with_4k = serializers.BooleanField(default=False)
    vr_support = serializers.BooleanField(default=False)
    video_editing = serializers.BooleanField(default=False)
    gaming = serializers.BooleanField(default=False)
    streaming = serializers.BooleanField(default=False)
    has_existing_components = serializers.BooleanField(default=False)
    existing_components_description = serializers.CharField(required=False, allow_blank=True)
