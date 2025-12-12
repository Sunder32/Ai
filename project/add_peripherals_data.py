
import os
import sys
import django


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from peripherals.models import (
    Speakers, Mousepad, MonitorArm, USBHub, DeskLighting,
    StreamDeck, CaptureCard, Gamepad, Headphonestand,
    Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair
)

def add_sample_data():
    print("Добавление периферийных устройств...")
    

    speakers_data = [
        {'name': 'Pebble V3', 'manufacturer': 'Logitech', 'speaker_type': '2.0', 'total_power': 8, 'bluetooth': True, 'rgb': False, 'price': 4990},
        {'name': 'Z333', 'manufacturer': 'Logitech', 'speaker_type': '2.1', 'total_power': 40, 'bluetooth': False, 'rgb': False, 'price': 7990},
        {'name': 'Arena 7', 'manufacturer': 'SteelSeries', 'speaker_type': '2.0', 'total_power': 100, 'bluetooth': True, 'rgb': True, 'price': 29990},
        {'name': 'Arena 9', 'manufacturer': 'SteelSeries', 'speaker_type': '5.1', 'total_power': 130, 'bluetooth': True, 'rgb': True, 'price': 44990},
        {'name': 'Razer Nommo Chroma', 'manufacturer': 'Razer', 'speaker_type': '2.0', 'total_power': 24, 'bluetooth': False, 'rgb': True, 'price': 14990},
        {'name': 'Creative Pebble Plus', 'manufacturer': 'Creative', 'speaker_type': '2.1', 'total_power': 8, 'bluetooth': False, 'rgb': False, 'price': 2990},
        {'name': 'Edifier R1280T', 'manufacturer': 'Edifier', 'speaker_type': '2.0', 'total_power': 42, 'bluetooth': False, 'rgb': False, 'price': 8990},
        {'name': 'Edifier R1280DBs', 'manufacturer': 'Edifier', 'speaker_type': '2.0', 'total_power': 42, 'bluetooth': True, 'rgb': False, 'price': 11990},
    ]
    
    for data in speakers_data:
        Speakers.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено колонок: {len(speakers_data)}")
    

    mousepad_data = [
        {'name': 'QcK Large', 'manufacturer': 'SteelSeries', 'size': 'large', 'width': 450, 'height': 400, 'thickness': 2, 'rgb': False, 'material': 'Ткань', 'price': 1990},
        {'name': 'QcK Prism XL', 'manufacturer': 'SteelSeries', 'size': 'xl', 'width': 900, 'height': 300, 'thickness': 4, 'rgb': True, 'material': 'Ткань', 'price': 5990},
        {'name': 'Goliathus Extended Chroma', 'manufacturer': 'Razer', 'size': 'xl', 'width': 920, 'height': 294, 'thickness': 3, 'rgb': True, 'material': 'Ткань', 'price': 6990},
        {'name': 'Firefly V2', 'manufacturer': 'Razer', 'size': 'medium', 'width': 355, 'height': 255, 'thickness': 3, 'rgb': True, 'material': 'Пластик', 'price': 5490},
        {'name': 'Powerplay', 'manufacturer': 'Logitech', 'size': 'medium', 'width': 344, 'height': 321, 'thickness': 4, 'rgb': True, 'material': 'Ткань/Пластик', 'price': 12990},
        {'name': 'G640', 'manufacturer': 'Logitech', 'size': 'large', 'width': 460, 'height': 400, 'thickness': 3, 'rgb': False, 'material': 'Ткань', 'price': 3990},
        {'name': 'MM700', 'manufacturer': 'Corsair', 'size': 'xl', 'width': 930, 'height': 400, 'thickness': 4, 'rgb': True, 'material': 'Ткань', 'price': 6990},
        {'name': 'AMP500', 'manufacturer': 'HyperX', 'size': 'large', 'width': 450, 'height': 400, 'thickness': 4, 'rgb': False, 'material': 'Ткань/Силикон', 'price': 3490},
    ]
    
    for data in mousepad_data:
        Mousepad.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено ковриков: {len(mousepad_data)}")
    

    monitor_arm_data = [
        {'name': 'LX Desk Mount', 'manufacturer': 'Ergotron', 'mount_type': 'single', 'max_screen_size': 34, 'max_weight': 11.3, 'vesa_pattern': '75x75, 100x100', 'gas_spring': True, 'cable_management': True, 'price': 16990},
        {'name': 'LX Dual Side-by-Side', 'manufacturer': 'Ergotron', 'mount_type': 'dual', 'max_screen_size': 27, 'max_weight': 9.1, 'vesa_pattern': '75x75, 100x100', 'gas_spring': True, 'cable_management': True, 'price': 24990},
        {'name': 'Arctic Z1 Pro', 'manufacturer': 'Arctic', 'mount_type': 'single', 'max_screen_size': 43, 'max_weight': 15.0, 'vesa_pattern': '75x75, 100x100', 'gas_spring': True, 'cable_management': True, 'price': 6990},
        {'name': 'Arctic Z2-3D', 'manufacturer': 'Arctic', 'mount_type': 'dual', 'max_screen_size': 32, 'max_weight': 15.0, 'vesa_pattern': '75x75, 100x100', 'gas_spring': True, 'cable_management': True, 'price': 8990},
        {'name': 'HX Desk Mount', 'manufacturer': 'Ergotron', 'mount_type': 'single', 'max_screen_size': 49, 'max_weight': 19.1, 'vesa_pattern': '75x75, 100x100, 200x100, 200x200', 'gas_spring': True, 'cable_management': True, 'price': 29990},
        {'name': 'DS200', 'manufacturer': 'Brateck', 'mount_type': 'single', 'max_screen_size': 32, 'max_weight': 9.0, 'vesa_pattern': '75x75, 100x100', 'gas_spring': True, 'cable_management': True, 'price': 3990},
    ]
    
    for data in monitor_arm_data:
        MonitorArm.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено кронштейнов: {len(monitor_arm_data)}")
    

    usb_hub_data = [
        {'name': 'UH-700', 'manufacturer': 'Anker', 'usb3_ports': 7, 'usbc_ports': 0, 'usb2_ports': 0, 'card_reader': False, 'hdmi_port': False, 'ethernet_port': False, 'power_delivery': None, 'price': 4990},
        {'name': 'USB-C Hub 8-in-1', 'manufacturer': 'Ugreen', 'usb3_ports': 3, 'usbc_ports': 1, 'usb2_ports': 0, 'card_reader': True, 'hdmi_port': True, 'ethernet_port': True, 'power_delivery': 100, 'price': 6990},
        {'name': 'PowerExpand+ 7-in-1', 'manufacturer': 'Anker', 'usb3_ports': 2, 'usbc_ports': 1, 'usb2_ports': 0, 'card_reader': True, 'hdmi_port': True, 'ethernet_port': False, 'power_delivery': 85, 'price': 5490},
        {'name': 'CalDigit TS4', 'manufacturer': 'CalDigit', 'usb3_ports': 5, 'usbc_ports': 3, 'usb2_ports': 0, 'card_reader': True, 'hdmi_port': False, 'ethernet_port': True, 'power_delivery': 98, 'price': 39990},
        {'name': 'Thunderbolt 4 Dock', 'manufacturer': 'Belkin', 'usb3_ports': 4, 'usbc_ports': 2, 'usb2_ports': 0, 'card_reader': True, 'hdmi_port': True, 'ethernet_port': True, 'power_delivery': 90, 'price': 29990},
        {'name': 'USB 3.0 Hub 4-port', 'manufacturer': 'TP-Link', 'usb3_ports': 4, 'usbc_ports': 0, 'usb2_ports': 0, 'card_reader': False, 'hdmi_port': False, 'ethernet_port': False, 'power_delivery': None, 'price': 1990},
    ]
    
    for data in usb_hub_data:
        USBHub.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено USB-хабов: {len(usb_hub_data)}")
    
  
    lighting_data = [
        {'name': 'ScreenBar Halo', 'manufacturer': 'BenQ', 'lighting_type': 'monitor_bar', 'rgb': False, 'dimmable': True, 'color_temperature': '2700K-6500K', 'smart_control': True, 'price': 12990},
        {'name': 'ScreenBar Plus', 'manufacturer': 'BenQ', 'lighting_type': 'monitor_bar', 'rgb': False, 'dimmable': True, 'color_temperature': '2700K-6500K', 'smart_control': False, 'price': 9990},
        {'name': 'Light Bar Pro', 'manufacturer': 'Xiaomi', 'lighting_type': 'monitor_bar', 'rgb': False, 'dimmable': True, 'color_temperature': '2700K-6500K', 'smart_control': True, 'price': 4990},
        {'name': 'Lightstrip Plus', 'manufacturer': 'Philips Hue', 'lighting_type': 'led_strip', 'rgb': True, 'dimmable': True, 'color_temperature': '2000K-6500K', 'smart_control': True, 'price': 7990},
        {'name': 'Gradient Lightstrip', 'manufacturer': 'Philips Hue', 'lighting_type': 'ambient', 'rgb': True, 'dimmable': True, 'color_temperature': '2000K-6500K', 'smart_control': True, 'price': 14990},
        {'name': 'Nanoleaf Shapes', 'manufacturer': 'Nanoleaf', 'lighting_type': 'ambient', 'rgb': True, 'dimmable': True, 'color_temperature': '1200K-6500K', 'smart_control': True, 'price': 15990},
        {'name': 'Ring Light 18"', 'manufacturer': 'Neewer', 'lighting_type': 'ring_light', 'rgb': False, 'dimmable': True, 'color_temperature': '3200K-5600K', 'smart_control': False, 'price': 5990},
        {'name': 'Key Light', 'manufacturer': 'Elgato', 'lighting_type': 'desk_lamp', 'rgb': False, 'dimmable': True, 'color_temperature': '2900K-7000K', 'smart_control': True, 'price': 19990},
    ]
    
    for data in lighting_data:
        DeskLighting.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено освещения: {len(lighting_data)}")
    

    stream_deck_data = [
        {'name': 'Stream Deck MK.2', 'manufacturer': 'Elgato', 'keys_count': 15, 'lcd_keys': True, 'dials': 0, 'touchscreen': False, 'price': 14990},
        {'name': 'Stream Deck XL', 'manufacturer': 'Elgato', 'keys_count': 32, 'lcd_keys': True, 'dials': 0, 'touchscreen': False, 'price': 24990},
        {'name': 'Stream Deck +', 'manufacturer': 'Elgato', 'keys_count': 8, 'lcd_keys': True, 'dials': 4, 'touchscreen': True, 'price': 19990},
        {'name': 'Stream Deck Mini', 'manufacturer': 'Elgato', 'keys_count': 6, 'lcd_keys': True, 'dials': 0, 'touchscreen': False, 'price': 8990},
        {'name': 'Stream Deck Neo', 'manufacturer': 'Elgato', 'keys_count': 8, 'lcd_keys': True, 'dials': 2, 'touchscreen': False, 'price': 9990},
        {'name': 'Loupedeck CT', 'manufacturer': 'Loupedeck', 'keys_count': 12, 'lcd_keys': True, 'dials': 6, 'touchscreen': True, 'price': 54990},
    ]
    
    for data in stream_deck_data:
        StreamDeck.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено стрим-пультов: {len(stream_deck_data)}")
    

    capture_card_data = [
        {'name': 'HD60 S+', 'manufacturer': 'Elgato', 'max_resolution': '4K60', 'max_fps': 60, 'connection': 'USB 3.0', 'passthrough': True, 'internal': False, 'price': 17990},
        {'name': '4K60 Pro MK.2', 'manufacturer': 'Elgato', 'max_resolution': '4K60', 'max_fps': 60, 'connection': 'PCIe x4', 'passthrough': True, 'internal': True, 'price': 24990},
        {'name': 'Cam Link 4K', 'manufacturer': 'Elgato', 'max_resolution': '4K30', 'max_fps': 30, 'connection': 'USB 3.0', 'passthrough': False, 'internal': False, 'price': 12990},
        {'name': 'Live Gamer Ultra', 'manufacturer': 'AVerMedia', 'max_resolution': '4K60', 'max_fps': 60, 'connection': 'USB 3.1', 'passthrough': True, 'internal': False, 'price': 22990},
        {'name': 'Live Gamer 4K', 'manufacturer': 'AVerMedia', 'max_resolution': '4K60', 'max_fps': 60, 'connection': 'PCIe x4', 'passthrough': True, 'internal': True, 'price': 29990},
        {'name': 'Ripsaw HD', 'manufacturer': 'Razer', 'max_resolution': '4K60', 'max_fps': 60, 'connection': 'USB 3.0', 'passthrough': True, 'internal': False, 'price': 16990},
    ]
    
    for data in capture_card_data:
        CaptureCard.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено карт захвата: {len(capture_card_data)}")
    

    gamepad_data = [
        {'name': 'Xbox Wireless Controller', 'manufacturer': 'Microsoft', 'platform': 'universal', 'wireless': True, 'vibration': True, 'rgb': False, 'extra_buttons': 0, 'price': 5990},
        {'name': 'Xbox Elite Series 2', 'manufacturer': 'Microsoft', 'platform': 'universal', 'wireless': True, 'vibration': True, 'rgb': False, 'extra_buttons': 4, 'price': 16990},
        {'name': 'DualSense', 'manufacturer': 'Sony', 'platform': 'playstation', 'wireless': True, 'vibration': True, 'rgb': True, 'extra_buttons': 0, 'price': 6990},
        {'name': 'DualSense Edge', 'manufacturer': 'Sony', 'platform': 'playstation', 'wireless': True, 'vibration': True, 'rgb': True, 'extra_buttons': 4, 'price': 19990},
        {'name': 'Wolverine V2 Chroma', 'manufacturer': 'Razer', 'platform': 'xbox', 'wireless': False, 'vibration': True, 'rgb': True, 'extra_buttons': 6, 'price': 14990},
        {'name': 'F710', 'manufacturer': 'Logitech', 'platform': 'pc', 'wireless': True, 'vibration': True, 'rgb': False, 'extra_buttons': 0, 'price': 3990},
        {'name': '8BitDo Pro 2', 'manufacturer': '8BitDo', 'platform': 'universal', 'wireless': True, 'vibration': True, 'rgb': False, 'extra_buttons': 2, 'price': 4990},
        {'name': 'Thrustmaster eSwap X Pro', 'manufacturer': 'Thrustmaster', 'platform': 'xbox', 'wireless': False, 'vibration': True, 'rgb': True, 'extra_buttons': 4, 'price': 16990},
    ]
    
    for data in gamepad_data:
        Gamepad.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено геймпадов: {len(gamepad_data)}")
    
 
    headphone_stand_data = [
        {'name': 'Base Station V2 Chroma', 'manufacturer': 'Razer', 'usb_hub': True, 'usb_ports': 2, 'rgb': True, 'wireless_charging': False, 'price': 7990},
        {'name': 'ST100 RGB', 'manufacturer': 'Corsair', 'usb_hub': True, 'usb_ports': 2, 'rgb': True, 'wireless_charging': False, 'price': 5990},
        {'name': 'HS1', 'manufacturer': 'SteelSeries', 'usb_hub': False, 'usb_ports': 0, 'rgb': False, 'wireless_charging': False, 'price': 2990},
        {'name': 'G502 Stand', 'manufacturer': 'Logitech', 'usb_hub': True, 'usb_ports': 2, 'rgb': True, 'wireless_charging': True, 'price': 9990},
        {'name': 'ROG Throne', 'manufacturer': 'ASUS', 'usb_hub': True, 'usb_ports': 2, 'rgb': True, 'wireless_charging': True, 'price': 11990},
        {'name': 'HyperX Headset Stand', 'manufacturer': 'HyperX', 'usb_hub': False, 'usb_ports': 0, 'rgb': False, 'wireless_charging': False, 'price': 1990},
    ]
    
    for data in headphone_stand_data:
        Headphonestand.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено подставок для наушников: {len(headphone_stand_data)}")
    
 
    monitor_data = [
        {'name': 'PG27AQDM', 'manufacturer': 'ASUS ROG Swift', 'screen_size': 27, 'resolution': '2560x1440', 'refresh_rate': 240, 'panel_type': 'OLED', 'response_time': 0.03, 'hdr': True, 'curved': False, 'price': 109990},
        {'name': 'Odyssey G9', 'manufacturer': 'Samsung', 'screen_size': 49, 'resolution': '5120x1440', 'refresh_rate': 240, 'panel_type': 'VA', 'response_time': 1, 'hdr': True, 'curved': True, 'price': 129990},
        {'name': 'XG27AQM', 'manufacturer': 'ASUS ROG Strix', 'screen_size': 27, 'resolution': '2560x1440', 'refresh_rate': 270, 'panel_type': 'IPS', 'response_time': 1, 'hdr': True, 'curved': False, 'price': 54990},
        {'name': 'Dell UltraSharp U2723QE', 'manufacturer': 'Dell', 'screen_size': 27, 'resolution': '3840x2160', 'refresh_rate': 60, 'panel_type': 'IPS', 'response_time': 5, 'hdr': True, 'curved': False, 'price': 69990},
        {'name': 'LG 27GP950-B', 'manufacturer': 'LG', 'screen_size': 27, 'resolution': '3840x2160', 'refresh_rate': 160, 'panel_type': 'IPS', 'response_time': 1, 'hdr': True, 'curved': False, 'price': 79990},
    ]
    
    for data in monitor_data:
        Monitor.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено мониторов: {len(monitor_data)}")
    
  
    keyboard_data = [
        {'name': 'Huntsman V3 Pro', 'manufacturer': 'Razer', 'switch_type': 'optical', 'switch_model': 'Razer Analog Optical', 'rgb': True, 'wireless': False, 'form_factor': 'Full-size', 'price': 24990},
        {'name': 'G915 TKL', 'manufacturer': 'Logitech', 'switch_type': 'mechanical', 'switch_model': 'GL Low Profile', 'rgb': True, 'wireless': True, 'form_factor': 'TKL', 'price': 22990},
        {'name': 'Apex Pro TKL', 'manufacturer': 'SteelSeries', 'switch_type': 'mechanical', 'switch_model': 'OmniPoint 2.0', 'rgb': True, 'wireless': False, 'form_factor': 'TKL', 'price': 19990},
        {'name': 'K100 RGB', 'manufacturer': 'Corsair', 'switch_type': 'optical', 'switch_model': 'OPX', 'rgb': True, 'wireless': False, 'form_factor': 'Full-size', 'price': 21990},
        {'name': 'Wooting 60HE', 'manufacturer': 'Wooting', 'switch_type': 'mechanical', 'switch_model': 'Lekker', 'rgb': True, 'wireless': False, 'form_factor': '60%', 'price': 17990},
    ]
    
    for data in keyboard_data:
        Keyboard.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено клавиатур: {len(keyboard_data)}")
    

    mouse_data = [
        {'name': 'DeathAdder V3 Pro', 'manufacturer': 'Razer', 'sensor_type': 'optical', 'dpi': 30000, 'buttons': 5, 'wireless': True, 'rgb': False, 'weight': 63, 'price': 14990},
        {'name': 'G Pro X Superlight 2', 'manufacturer': 'Logitech', 'sensor_type': 'optical', 'dpi': 32000, 'buttons': 5, 'wireless': True, 'rgb': False, 'weight': 60, 'price': 15990},
        {'name': 'Viper V3 Pro', 'manufacturer': 'Razer', 'sensor_type': 'optical', 'dpi': 35000, 'buttons': 5, 'wireless': True, 'rgb': False, 'weight': 54, 'price': 14990},
        {'name': 'Pulsar X2', 'manufacturer': 'Pulsar', 'sensor_type': 'optical', 'dpi': 26000, 'buttons': 5, 'wireless': True, 'rgb': False, 'weight': 52, 'price': 11990},
        {'name': 'Finalmouse UltralightX', 'manufacturer': 'Finalmouse', 'sensor_type': 'optical', 'dpi': 26000, 'buttons': 5, 'wireless': True, 'rgb': False, 'weight': 45, 'price': 24990},
    ]
    
    for data in mouse_data:
        Mouse.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено мышей: {len(mouse_data)}")
    

    headset_data = [
        {'name': 'BlackShark V2 Pro', 'manufacturer': 'Razer', 'connection_type': 'USB-C / 2.4GHz', 'wireless': True, 'microphone': True, 'surround': True, 'noise_cancelling': True, 'price': 17990},
        {'name': 'Arctis Nova Pro', 'manufacturer': 'SteelSeries', 'connection_type': 'USB-C / 2.4GHz / Bluetooth', 'wireless': True, 'microphone': True, 'surround': True, 'noise_cancelling': True, 'price': 34990},
        {'name': 'Cloud III Wireless', 'manufacturer': 'HyperX', 'connection_type': '2.4GHz', 'wireless': True, 'microphone': True, 'surround': True, 'noise_cancelling': False, 'price': 14990},
        {'name': 'Virtuoso RGB Wireless XT', 'manufacturer': 'Corsair', 'connection_type': 'USB / 2.4GHz / Bluetooth', 'wireless': True, 'microphone': True, 'surround': True, 'noise_cancelling': False, 'price': 24990},
        {'name': 'Astro A50', 'manufacturer': 'Logitech', 'connection_type': '2.4GHz', 'wireless': True, 'microphone': True, 'surround': True, 'noise_cancelling': False, 'price': 29990},
    ]
    
    for data in headset_data:
        Headset.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено наушников: {len(headset_data)}")
    

    webcam_data = [
        {'name': 'Facecam Pro', 'manufacturer': 'Elgato', 'resolution': '4K', 'fps': 60, 'autofocus': True, 'price': 34990},
        {'name': 'Brio 500', 'manufacturer': 'Logitech', 'resolution': '4K', 'fps': 30, 'autofocus': True, 'price': 14990},
        {'name': 'Kiyo Pro Ultra', 'manufacturer': 'Razer', 'resolution': '4K', 'fps': 30, 'autofocus': True, 'price': 29990},
        {'name': 'StreamCam', 'manufacturer': 'Logitech', 'resolution': '1080p', 'fps': 60, 'autofocus': True, 'price': 14990},
        {'name': 'C920 HD Pro', 'manufacturer': 'Logitech', 'resolution': '1080p', 'fps': 30, 'autofocus': True, 'price': 7990},
    ]
    
    for data in webcam_data:
        Webcam.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено веб-камер: {len(webcam_data)}")
    

    microphone_data = [
        {'name': 'Wave:3', 'manufacturer': 'Elgato', 'microphone_type': 'condenser', 'connection': 'USB-C', 'polar_pattern': 'Кардиоида', 'price': 14990},
        {'name': 'Blue Yeti X', 'manufacturer': 'Logitech', 'microphone_type': 'condenser', 'connection': 'USB', 'polar_pattern': 'Многорежимный', 'price': 16990},
        {'name': 'Seiren V3 Chroma', 'manufacturer': 'Razer', 'microphone_type': 'condenser', 'connection': 'USB', 'polar_pattern': 'Суперкардиоида', 'price': 14990},
        {'name': 'Shure MV7', 'manufacturer': 'Shure', 'microphone_type': 'dynamic', 'connection': 'USB/XLR', 'polar_pattern': 'Кардиоида', 'price': 24990},
        {'name': 'Rode NT-USB+', 'manufacturer': 'Rode', 'microphone_type': 'condenser', 'connection': 'USB-C', 'polar_pattern': 'Кардиоида', 'price': 19990},
    ]
    
    for data in microphone_data:
        Microphone.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено микрофонов: {len(microphone_data)}")
    

    desk_data = [
        {'name': 'UPPSPEL', 'manufacturer': 'IKEA', 'width': 180, 'depth': 80, 'adjustable_height': True, 'price': 39990},
        {'name': 'BEKANT', 'manufacturer': 'IKEA', 'width': 160, 'depth': 80, 'adjustable_height': True, 'price': 34990},
        {'name': 'E7 Pro', 'manufacturer': 'FlexiSpot', 'width': 180, 'depth': 80, 'adjustable_height': True, 'price': 49990},
        {'name': 'Arozzi Arena', 'manufacturer': 'Arozzi', 'width': 160, 'depth': 80, 'adjustable_height': False, 'price': 29990},
        {'name': 'Gaming Desk', 'manufacturer': 'Secretlab', 'width': 150, 'depth': 75, 'adjustable_height': True, 'price': 54990},
    ]
    
    for data in desk_data:
        Desk.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено столов: {len(desk_data)}")
    

    chair_data = [
        {'name': 'TITAN Evo 2022', 'manufacturer': 'Secretlab', 'ergonomic': True, 'adjustable_armrests': True, 'lumbar_support': True, 'max_weight': 130, 'price': 49990},
        {'name': 'Embody', 'manufacturer': 'Herman Miller', 'ergonomic': True, 'adjustable_armrests': True, 'lumbar_support': True, 'max_weight': 136, 'price': 169990},
        {'name': 'Aeron', 'manufacturer': 'Herman Miller', 'ergonomic': True, 'adjustable_armrests': True, 'lumbar_support': True, 'max_weight': 159, 'price': 149990},
        {'name': 'Vernazza', 'manufacturer': 'Arozzi', 'ergonomic': True, 'adjustable_armrests': True, 'lumbar_support': True, 'max_weight': 145, 'price': 34990},
        {'name': 'JÄRVFJÄLLET', 'manufacturer': 'IKEA', 'ergonomic': True, 'adjustable_armrests': True, 'lumbar_support': True, 'max_weight': 110, 'price': 24990},
    ]
    
    for data in chair_data:
        Chair.objects.get_or_create(name=data['name'], manufacturer=data['manufacturer'], defaults=data)
    print(f"  Добавлено кресел: {len(chair_data)}")
    
    print("\n✅ Все периферийные устройства успешно добавлены!")

if __name__ == '__main__':
    add_sample_data()
