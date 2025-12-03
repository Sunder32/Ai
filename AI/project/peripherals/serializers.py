from rest_framework import serializers
from .models import Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair


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
