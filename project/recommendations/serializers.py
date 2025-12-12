from rest_framework import serializers
from .models import PCConfiguration, WorkspaceSetup, Recommendation
from computers.serializers import (
    CPUSerializer, GPUSerializer, MotherboardSerializer, RAMSerializer,
    StorageSerializer, PSUSerializer, CaseSerializer, CoolingSerializer
)
from peripherals.serializers import (
    MonitorSerializer, KeyboardSerializer, MouseSerializer, HeadsetSerializer,
    WebcamSerializer, MicrophoneSerializer, DeskSerializer, ChairSerializer,
    SpeakersSerializer, MousepadSerializer, MonitorArmSerializer, USBHubSerializer,
    DeskLightingSerializer, StreamDeckSerializer, CaptureCardSerializer,
    GamepadSerializer, HeadphonestandSerializer
)


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


class WorkspaceSetupDetailSerializer(serializers.ModelSerializer):

    monitor_primary_detail = MonitorSerializer(source='monitor_primary', read_only=True)
    monitor_secondary_detail = MonitorSerializer(source='monitor_secondary', read_only=True)
    keyboard_detail = KeyboardSerializer(source='keyboard', read_only=True)
    mouse_detail = MouseSerializer(source='mouse', read_only=True)
    headset_detail = HeadsetSerializer(source='headset', read_only=True)
    webcam_detail = WebcamSerializer(source='webcam', read_only=True)
    microphone_detail = MicrophoneSerializer(source='microphone', read_only=True)
    desk_detail = DeskSerializer(source='desk', read_only=True)
    chair_detail = ChairSerializer(source='chair', read_only=True)
    speakers_detail = SpeakersSerializer(source='speakers', read_only=True)
    mousepad_detail = MousepadSerializer(source='mousepad', read_only=True)
    
    class Meta:
        model = WorkspaceSetup
        fields = [
            'id', 'name', 'total_price',
            'monitor_primary', 'monitor_primary_detail',
            'monitor_secondary', 'monitor_secondary_detail',
            'keyboard', 'keyboard_detail',
            'mouse', 'mouse_detail',
            'headset', 'headset_detail',
            'webcam', 'webcam_detail',
            'microphone', 'microphone_detail',
            'desk', 'desk_detail',
            'chair', 'chair_detail',
            'speakers', 'speakers_detail',
            'mousepad', 'mousepad_detail',
            'lighting_recommendation',
            'created_at', 'updated_at',
        ]


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
    

    workspace = serializers.SerializerMethodField()
    
    class Meta:
        model = PCConfiguration
        fields = '__all__'
        read_only_fields = ['total_price', 'created_at', 'updated_at']
    
    def get_workspace(self, obj):

        workspace = obj.workspace_setups.first()
        if workspace:
            return WorkspaceSetupDetailSerializer(workspace).data
        return None
    
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
    

    speakers_detail = SpeakersSerializer(source='speakers', read_only=True)
    mousepad_detail = MousepadSerializer(source='mousepad', read_only=True)
    monitor_arm_detail = MonitorArmSerializer(source='monitor_arm', read_only=True)
    usb_hub_detail = USBHubSerializer(source='usb_hub', read_only=True)
    lighting_detail = DeskLightingSerializer(source='lighting', read_only=True)
    stream_deck_detail = StreamDeckSerializer(source='stream_deck', read_only=True)
    capture_card_detail = CaptureCardSerializer(source='capture_card', read_only=True)
    gamepad_detail = GamepadSerializer(source='gamepad', read_only=True)
    headphone_stand_detail = HeadphonestandSerializer(source='headphone_stand', read_only=True)
    
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

    user_type = serializers.ChoiceField(choices=[
        ('designer', 'Дизайнер'),
        ('programmer', 'Программист'),
        ('gamer', 'Геймер'),
        ('office', 'Офисный работник'),
        ('student', 'Студент'),
        ('content_creator', 'Контент-криэйтор'),
    ])
    min_budget = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=10000)
    max_budget = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=10000, max_value=10000000)
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
    existing_components_description = serializers.CharField(required=False, allow_blank=True, max_length=2000)
    

    include_workspace = serializers.BooleanField(default=False)
    use_ai = serializers.BooleanField(default=False)
    ai_generation_mode = serializers.ChoiceField(
        choices=[
            ('database', 'Выбор из базы данных'),
            ('generative', 'Генерация компонентов AI'),
            ('full_ai', 'Полная AI генерация'),
        ],
        default='database',
        required=False
    )
    peripheral_budget_percent = serializers.IntegerField(default=30, min_value=10, max_value=50)
    
    def validate(self, attrs):

        min_budget = attrs.get('min_budget')
        max_budget = attrs.get('max_budget')
        

        if min_budget and max_budget and min_budget > max_budget:
            raise serializers.ValidationError({
                'min_budget': 'Минимальный бюджет не может быть больше максимального'
            })
        
        if min_budget and max_budget and (max_budget - min_budget) < 5000:
            raise serializers.ValidationError({
                'max_budget': 'Разница между минимальным и максимальным бюджетом должна быть не менее 5000₽'
            })
        
        return attrs
    
    def validate_min_cpu_cores(self, value):

        if value and (value < 2 or value > 64):
            raise serializers.ValidationError('Количество ядер должно быть от 2 до 64')
        return value
    
    def validate_min_gpu_vram(self, value):

        if value and (value < 2 or value > 48):
            raise serializers.ValidationError('Объем видеопамяти должен быть от 2 до 48 ГБ')
        return value
    
    def validate_min_ram_capacity(self, value):

        if value and (value < 4 or value > 256):
            raise serializers.ValidationError('Объем ОЗУ должен быть от 4 до 256 ГБ')
        return value
    
    def validate_min_storage_capacity(self, value):

        if value and (value < 128 or value > 8192):
            raise serializers.ValidationError('Объем накопителя должен быть от 128 до 8192 ГБ')
        return value
    

    preferred_cpu_manufacturer = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('Intel', 'Intel'), ('intel', 'Intel'), ('AMD', 'AMD'), ('amd', 'AMD')],
        default='any',
        required=False
    )
    preferred_gpu_manufacturer = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('NVIDIA', 'NVIDIA'), ('nvidia', 'NVIDIA'), ('AMD', 'AMD'), ('amd', 'AMD')],
        default='any',
        required=False
    )
    min_cpu_cores = serializers.IntegerField(default=4, required=False)
    min_gpu_vram = serializers.IntegerField(default=4, required=False)
    min_ram_capacity = serializers.IntegerField(default=16, required=False)
    storage_type_preference = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('nvme', 'SSD NVMe'), ('ssd_nvme', 'SSD NVMe'), ('sata', 'SSD SATA'), ('ssd_sata', 'SSD SATA'), ('hdd', 'HDD')],
        default='any',
        required=False
    )
    min_storage_capacity = serializers.IntegerField(default=512, required=False)
    cooling_preference = serializers.ChoiceField(
        choices=[('any', 'Любое'), ('air', 'Воздушное'), ('liquid', 'Жидкостное'), ('aio', 'AIO'), ('custom', 'Кастомное')],
        default='any',
        required=False
    )
    rgb_preference = serializers.BooleanField(default=False, required=False)
    case_size_preference = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('mini', 'Mini'), ('mid', 'Mid Tower'), ('full', 'Full Tower')],
        default='any',
        required=False
    )
    overclocking_support = serializers.BooleanField(default=False, required=False)
    

    need_monitor = serializers.BooleanField(default=True)
    need_keyboard = serializers.BooleanField(default=True)
    need_mouse = serializers.BooleanField(default=True)
    need_headset = serializers.BooleanField(default=True)
    need_webcam = serializers.BooleanField(default=False)
    need_microphone = serializers.BooleanField(default=False)
    need_desk = serializers.BooleanField(default=True)
    need_chair = serializers.BooleanField(default=True)
    

    monitor_min_refresh_rate = serializers.IntegerField(default=60, required=False)
    monitor_min_resolution = serializers.CharField(default='1080p', required=False)
    monitor_size_preference = serializers.IntegerField(default=24, required=False)
    monitor_panel_type = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('IPS', 'IPS'), ('ips', 'IPS'), ('VA', 'VA'), ('va', 'VA'), ('TN', 'TN'), ('tn', 'TN'), ('OLED', 'OLED'), ('oled', 'OLED')],
        default='any',
        required=False
    )
    

    keyboard_type_preference = serializers.ChoiceField(
        choices=[('any', 'Любая'), ('mechanical', 'Механическая'), ('membrane', 'Мембранная')],
        default='any',
        required=False
    )
    keyboard_switch_type = serializers.ChoiceField(
        choices=[('any', 'Любые'), ('red', 'Red'), ('linear', 'Linear'), ('blue', 'Blue'), ('clicky', 'Clicky'), ('brown', 'Brown'), ('tactile', 'Tactile')],
        default='any',
        required=False
    )
    keyboard_rgb = serializers.BooleanField(default=False, required=False)
    

    mouse_min_dpi = serializers.IntegerField(default=1000, required=False)
    mouse_sensor_type = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('optical', 'Оптический'), ('laser', 'Лазерный')],
        default='any',
        required=False
    )
    mouse_wireless = serializers.BooleanField(default=False, required=False)
    

    headset_wireless = serializers.BooleanField(default=False, required=False)
    headset_noise_cancellation = serializers.BooleanField(default=False, required=False)
    

    webcam_min_resolution = serializers.ChoiceField(
        choices=[('any', 'Любое'), ('720p', '720p'), ('1080p', '1080p'), ('4k', '4K')],
        default='any',
        required=False
    )
    microphone_type = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('usb', 'USB'), ('xlr', 'XLR'), ('condenser', 'Конденсаторный'), ('dynamic', 'Динамический')],
        default='any',
        required=False
    )
    

    desk_min_width = serializers.IntegerField(default=120, required=False)
    desk_min_depth = serializers.IntegerField(default=60, required=False)
    desk_height_adjustable = serializers.BooleanField(default=False, required=False)
    desk_material_preference = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('wood', 'Дерево'), ('metal', 'Металл'), ('glass', 'Стекло')],
        default='any',
        required=False
    )
    desk_cable_management = serializers.BooleanField(default=True, required=False)
    

    chair_ergonomic = serializers.BooleanField(default=True, required=False)
    chair_lumbar_support = serializers.BooleanField(default=True, required=False)
    chair_armrests_adjustable = serializers.BooleanField(default=False, required=False)
    chair_max_weight = serializers.IntegerField(default=120, required=False)
    chair_material_preference = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('leather', 'Кожа'), ('fabric', 'Ткань'), ('mesh', 'Сетка')],
        default='any',
        required=False
    )
    

    workspace_rgb_lighting = serializers.BooleanField(default=False, required=False)
    workspace_lighting_type = serializers.ChoiceField(
        choices=[('any', 'Любой'), ('warm', 'Теплый'), ('neutral', 'Нейтральный'), ('cold', 'Холодный'), ('adjustable', 'Регулируемый')],
        default='any',
        required=False
    )
    workspace_sound_dampening = serializers.BooleanField(default=False, required=False)
    monitor_arm = serializers.BooleanField(default=False, required=False)
    cable_management_accessories = serializers.BooleanField(default=True, required=False)


class BuilderConfigurationSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    

    cpu = serializers.IntegerField(required=False, allow_null=True)
    gpu = serializers.IntegerField(required=False, allow_null=True)
    motherboard = serializers.IntegerField(required=False, allow_null=True)
    ram = serializers.IntegerField(required=False, allow_null=True)
    storage_primary = serializers.IntegerField(required=False, allow_null=True)
    storage_secondary = serializers.IntegerField(required=False, allow_null=True)
    psu = serializers.IntegerField(required=False, allow_null=True)
    case = serializers.IntegerField(required=False, allow_null=True)
    cooling = serializers.IntegerField(required=False, allow_null=True)
    

    monitor_primary = serializers.IntegerField(required=False, allow_null=True)
    monitor_secondary = serializers.IntegerField(required=False, allow_null=True)
    keyboard = serializers.IntegerField(required=False, allow_null=True)
    mouse = serializers.IntegerField(required=False, allow_null=True)
    headset = serializers.IntegerField(required=False, allow_null=True)
    webcam = serializers.IntegerField(required=False, allow_null=True)
    microphone = serializers.IntegerField(required=False, allow_null=True)
    desk = serializers.IntegerField(required=False, allow_null=True)
    chair = serializers.IntegerField(required=False, allow_null=True)
    

    speakers = serializers.IntegerField(required=False, allow_null=True)
    mousepad = serializers.IntegerField(required=False, allow_null=True)
    monitor_arm = serializers.IntegerField(required=False, allow_null=True)
    usb_hub = serializers.IntegerField(required=False, allow_null=True)
    lighting = serializers.IntegerField(required=False, allow_null=True)
    stream_deck = serializers.IntegerField(required=False, allow_null=True)
    capture_card = serializers.IntegerField(required=False, allow_null=True)
    gamepad = serializers.IntegerField(required=False, allow_null=True)
    headphone_stand = serializers.IntegerField(required=False, allow_null=True)
    

    is_public = serializers.BooleanField(default=False)


class PublicConfigurationSerializer(serializers.ModelSerializer):

    cpu_detail = CPUSerializer(source='cpu', read_only=True)
    gpu_detail = GPUSerializer(source='gpu', read_only=True)
    motherboard_detail = MotherboardSerializer(source='motherboard', read_only=True)
    ram_detail = RAMSerializer(source='ram', read_only=True)
    storage_primary_detail = StorageSerializer(source='storage_primary', read_only=True)
    storage_secondary_detail = StorageSerializer(source='storage_secondary', read_only=True)
    psu_detail = PSUSerializer(source='psu', read_only=True)
    case_detail = CaseSerializer(source='case', read_only=True)
    cooling_detail = CoolingSerializer(source='cooling', read_only=True)
    workspace = serializers.SerializerMethodField()
    
    class Meta:
        model = PCConfiguration
        fields = [
            'id', 'name', 'total_price', 'compatibility_check', 'compatibility_notes',
            'created_at', 'cpu_detail', 'gpu_detail', 'motherboard_detail', 'ram_detail',
            'storage_primary_detail', 'storage_secondary_detail', 'psu_detail', 
            'case_detail', 'cooling_detail', 'workspace'
        ]
    
    def get_workspace(self, obj):
        try:
            workspace = WorkspaceSetup.objects.filter(configuration=obj).first()
            if workspace:
                return WorkspaceSetupSerializer(workspace).data
        except:
            pass
        return None
