
from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
from peripherals.models import Monitor, Keyboard, Mouse, Headset


print("Добавление процессоров...")
CPU.objects.get_or_create(
    name="Ryzen 5 5600X",
    defaults={
        'manufacturer': 'AMD',
        'socket': 'AM4',
        'cores': 6,
        'threads': 12,
        'base_clock': 3.7,
        'boost_clock': 4.6,
        'tdp': 65,
        'price': 15990,
        'performance_score': 3500
    }
)

CPU.objects.get_or_create(
    name="Ryzen 7 5800X3D",
    defaults={
        'manufacturer': 'AMD',
        'socket': 'AM4',
        'cores': 8,
        'threads': 16,
        'base_clock': 3.4,
        'boost_clock': 4.5,
        'tdp': 105,
        'price': 32990,
        'performance_score': 4200
    }
)

CPU.objects.get_or_create(
    name="Core i5-13600K",
    defaults={
        'manufacturer': 'Intel',
        'socket': 'LGA1700',
        'cores': 14,
        'threads': 20,
        'base_clock': 3.5,
        'boost_clock': 5.1,
        'tdp': 125,
        'price': 28990,
        'performance_score': 4500
    }
)

print("Добавление видеокарт...")
GPU.objects.get_or_create(
    name="RTX 4060",
    defaults={
        'manufacturer': 'NVIDIA',
        'chipset': 'GeForce RTX 4060',
        'memory': 8,
        'memory_type': 'GDDR6',
        'core_clock': 1830,
        'boost_clock': 2460,
        'tdp': 115,
        'recommended_psu': 550,
        'price': 32990,
        'performance_score': 6500
    }
)

GPU.objects.get_or_create(
    name="RTX 4070",
    defaults={
        'manufacturer': 'NVIDIA',
        'chipset': 'GeForce RTX 4070',
        'memory': 12,
        'memory_type': 'GDDR6X',
        'core_clock': 1920,
        'boost_clock': 2475,
        'tdp': 200,
        'recommended_psu': 650,
        'price': 54990,
        'performance_score': 8500
    }
)

GPU.objects.get_or_create(
    name="RX 7800 XT",
    defaults={
        'manufacturer': 'AMD',
        'chipset': 'Radeon RX 7800 XT',
        'memory': 16,
        'memory_type': 'GDDR6',
        'core_clock': 2124,
        'boost_clock': 2430,
        'tdp': 263,
        'recommended_psu': 700,
        'price': 49990,
        'performance_score': 8200
    }
)


print("Добавление материнских плат...")
Motherboard.objects.get_or_create(
    name="B550 AORUS ELITE",
    defaults={
        'manufacturer': 'Gigabyte',
        'socket': 'AM4',
        'chipset': 'B550',
        'form_factor': 'ATX',
        'memory_slots': 4,
        'max_memory': 128,
        'memory_type': 'DDR4',
        'pcie_slots': 3,
        'm2_slots': 2,
        'price': 12990
    }
)

Motherboard.objects.get_or_create(
    name="Z690 GAMING X",
    defaults={
        'manufacturer': 'Gigabyte',
        'socket': 'LGA1700',
        'chipset': 'Z690',
        'form_factor': 'ATX',
        'memory_slots': 4,
        'max_memory': 128,
        'memory_type': 'DDR5',
        'pcie_slots': 3,
        'm2_slots': 4,
        'price': 24990
    }
)


print("Добавление оперативной памяти...")
RAM.objects.get_or_create(
    name="Vengeance RGB 16GB",
    defaults={
        'manufacturer': 'Corsair',
        'memory_type': 'DDR4',
        'capacity': 16,
        'speed': 3200,
        'modules': 2,
        'cas_latency': 'CL16',
        'price': 5990
    }
)

RAM.objects.get_or_create(
    name="Vengeance RGB 32GB",
    defaults={
        'manufacturer': 'Corsair',
        'memory_type': 'DDR4',
        'capacity': 32,
        'speed': 3600,
        'modules': 2,
        'cas_latency': 'CL18',
        'price': 10990
    }
)


print("Добавление накопителей...")
Storage.objects.get_or_create(
    name="970 EVO Plus",
    defaults={
        'manufacturer': 'Samsung',
        'storage_type': 'ssd_nvme',
        'capacity': 1000,
        'read_speed': 3500,
        'write_speed': 3300,
        'price': 8990
    }
)

Storage.objects.get_or_create(
    name="KC3000",
    defaults={
        'manufacturer': 'Kingston',
        'storage_type': 'ssd_nvme',
        'capacity': 2000,
        'read_speed': 7000,
        'write_speed': 7000,
        'price': 15990
    }
)


print("Добавление блоков питания...")
PSU.objects.get_or_create(
    name="RM750x",
    defaults={
        'manufacturer': 'Corsair',
        'wattage': 750,
        'efficiency_rating': '80+ Gold',
        'modular': True,
        'price': 9990
    }
)

PSU.objects.get_or_create(
    name="ROG STRIX 850W",
    defaults={
        'manufacturer': 'ASUS',
        'wattage': 850,
        'efficiency_rating': '80+ Gold',
        'modular': True,
        'price': 13990
    }
)


print("Добавление корпусов...")
Case.objects.get_or_create(
    name="4000D Airflow",
    defaults={
        'manufacturer': 'Corsair',
        'form_factor': 'ATX',
        'max_gpu_length': 360,
        'fan_slots': 6,
        'rgb': False,
        'price': 7990
    }
)

Case.objects.get_or_create(
    name="H510 Flow",
    defaults={
        'manufacturer': 'NZXT',
        'form_factor': 'ATX',
        'max_gpu_length': 381,
        'fan_slots': 7,
        'rgb': True,
        'price': 9990
    }
)


print("Добавление систем охлаждения...")
Cooling.objects.get_or_create(
    name="NH-D15",
    defaults={
        'manufacturer': 'Noctua',
        'cooling_type': 'air',
        'socket_compatibility': 'AM4, LGA1700, LGA1200',
        'max_tdp': 220,
        'noise_level': 24,
        'price': 8990
    }
)

Cooling.objects.get_or_create(
    name="Kraken X63",
    defaults={
        'manufacturer': 'NZXT',
        'cooling_type': 'aio',
        'socket_compatibility': 'AM4, LGA1700, LGA1200',
        'max_tdp': 250,
        'noise_level': 28,
        'price': 14990
    }
)


print("Добавление мониторов...")
Monitor.objects.get_or_create(
    name="27GL850",
    defaults={
        'manufacturer': 'LG',
        'screen_size': 27.0,
        'resolution': '2560x1440',
        'refresh_rate': 144,
        'panel_type': 'IPS',
        'response_time': 1,
        'hdr': True,
        'curved': False,
        'price': 32990
    }
)

Monitor.objects.get_or_create(
    name="VG27AQ",
    defaults={
        'manufacturer': 'ASUS',
        'screen_size': 27.0,
        'resolution': '2560x1440',
        'refresh_rate': 165,
        'panel_type': 'IPS',
        'response_time': 1,
        'hdr': True,
        'curved': False,
        'price': 29990
    }
)


print("Добавление клавиатур...")
Keyboard.objects.get_or_create(
    name="K70 RGB",
    defaults={
        'manufacturer': 'Corsair',
        'switch_type': 'mechanical',
        'switch_model': 'Cherry MX Red',
        'rgb': True,
        'wireless': False,
        'form_factor': 'Full Size',
        'price': 12990
    }
)


print("Добавление мышей...")
Mouse.objects.get_or_create(
    name="G Pro Wireless",
    defaults={
        'manufacturer': 'Logitech',
        'sensor_type': 'optical',
        'dpi': 25600,
        'buttons': 8,
        'wireless': True,
        'rgb': True,
        'weight': 80,
        'price': 9990
    }
)


print("Добавление наушников...")
Headset.objects.get_or_create(
    name="Cloud II",
    defaults={
        'manufacturer': 'HyperX',
        'connection_type': 'USB/3.5mm',
        'wireless': False,
        'microphone': True,
        'surround': True,
        'noise_cancelling': False,
        'price': 7990
    }
)

print("✓ Тестовые данные добавлены успешно!")
