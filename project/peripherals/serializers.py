from rest_framework import serializers
from .models import (
    Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair,
    Speakers, Mousepad, MonitorArm, USBHub, DeskLighting, StreamDeck,
    CaptureCard, Gamepad, Headphonestand
)


class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = '__all__'


class KeyboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyboard
        fields = '__all__'


class MouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mouse
        fields = '__all__'


class HeadsetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headset
        fields = '__all__'


class WebcamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webcam
        fields = '__all__'


class MicrophoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Microphone
        fields = '__all__'


class DeskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desk
        fields = '__all__'


class ChairSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chair
        fields = '__all__'


class SpeakersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speakers
        fields = '__all__'


class MousepadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mousepad
        fields = '__all__'


class MonitorArmSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitorArm
        fields = '__all__'


class USBHubSerializer(serializers.ModelSerializer):
    class Meta:
        model = USBHub
        fields = '__all__'


class DeskLightingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeskLighting
        fields = '__all__'


class StreamDeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamDeck
        fields = '__all__'


class CaptureCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaptureCard
        fields = '__all__'


class GamepadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamepad
        fields = '__all__'


class HeadphonestandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headphonestand
        fields = '__all__'
