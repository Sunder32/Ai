from django.core.management.base import BaseCommand
from computers.models import CPU, GPU, RAM, Storage
from recommendations.models import PCConfiguration
from accounts.models import User
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('Начало заполнения базы данных...')

        # Удаляем существующие данные
        self.stdout.write('Удаление существующих данных...')
        PCConfiguration.objects.all().delete()
        CPU.objects.all().delete()
        GPU.objects.all().delete()
        RAM.objects.all().delete()
        Storage.objects.all().delete()

        # Создаем процессоры
        self.stdout.write('Создание процессоров...')
        cpus_data = [
            # Intel
            {
                'name': 'Intel Core i9-14900K',
                'manufacturer': 'Intel',
                'socket': 'LGA1700',
                'cores': 24,
                'threads': 32,
                'base_clock': 3.0,
                'boost_clock': 6.0,
                'tdp': 125,
                'price': Decimal('64999.00'),
                'performance_score': 98,
            },
            {
                'name': 'Intel Core i7-14700K',
                'manufacturer': 'Intel',
                'socket': 'LGA1700',
                'cores': 20,
                'threads': 28,
                'base_clock': 3.4,
                'boost_clock': 5.6,
                'tdp': 125,
                'price': Decimal('49999.00'),
                'performance_score': 92,
            },
            {
                'name': 'Intel Core i5-14600K',
                'manufacturer': 'Intel',
                'socket': 'LGA1700',
                'cores': 14,
                'threads': 20,
                'base_clock': 3.5,
                'boost_clock': 5.3,
                'tdp': 125,
                'price': Decimal('35999.00'),
                'performance_score': 85,
            },
            {
                'name': 'Intel Core i5-13400F',
                'manufacturer': 'Intel',
                'socket': 'LGA1700',
                'cores': 10,
                'threads': 16,
                'base_clock': 2.5,
                'boost_clock': 4.6,
                'tdp': 65,
                'price': Decimal('19999.00'),
                'performance_score': 75,
            },
            # AMD
            {
                'name': 'AMD Ryzen 9 7950X',
                'manufacturer': 'AMD',
                'socket': 'AM5',
                'cores': 16,
                'threads': 32,
                'base_clock': 4.5,
                'boost_clock': 5.7,
                'tdp': 170,
                'price': Decimal('59999.00'),
                'performance_score': 96,
            },
            {
                'name': 'AMD Ryzen 7 7800X3D',
                'manufacturer': 'AMD',
                'socket': 'AM5',
                'cores': 8,
                'threads': 16,
                'base_clock': 4.2,
                'boost_clock': 5.0,
                'tdp': 120,
                'price': Decimal('44999.00'),
                'performance_score': 94,
            },
            {
                'name': 'AMD Ryzen 5 7600X',
                'manufacturer': 'AMD',
                'socket': 'AM5',
                'cores': 6,
                'threads': 12,
                'base_clock': 4.7,
                'boost_clock': 5.3,
                'tdp': 105,
                'price': Decimal('29999.00'),
                'performance_score': 82,
            },
            {
                'name': 'AMD Ryzen 5 5600',
                'manufacturer': 'AMD',
                'socket': 'AM4',
                'cores': 6,
                'threads': 12,
                'base_clock': 3.5,
                'boost_clock': 4.4,
                'tdp': 65,
                'price': Decimal('14999.00'),
                'performance_score': 70,
            },
        ]

        cpus = []
        for cpu_data in cpus_data:
            cpu = CPU.objects.create(**cpu_data)
            cpus.append(cpu)
            self.stdout.write(f'  ✓ {cpu.name}')

        # Создаем видеокарты
        self.stdout.write('Создание видеокарт...')
        gpus_data = [
            # NVIDIA
            {
                'name': 'NVIDIA GeForce RTX 4090',
                'manufacturer': 'NVIDIA',
                'chipset': 'AD102',
                'memory': 24,
                'memory_type': 'GDDR6X',
                'core_clock': 2520,
                'tdp': 450,
                'recommended_psu': 850,
                'price': Decimal('179999.00'),
                'performance_score': 100,
            },
            {
                'name': 'NVIDIA GeForce RTX 4080',
                'manufacturer': 'NVIDIA',
                'chipset': 'AD103',
                'memory': 16,
                'memory_type': 'GDDR6X',
                'core_clock': 2505,
                'tdp': 320,
                'recommended_psu': 750,
                'price': Decimal('129999.00'),
                'performance_score': 92,
            },
            {
                'name': 'NVIDIA GeForce RTX 4070 Ti',
                'manufacturer': 'NVIDIA',
                'chipset': 'AD104',
                'memory': 12,
                'memory_type': 'GDDR6X',
                'core_clock': 2610,
                'tdp': 285,
                'recommended_psu': 700,
                'price': Decimal('94999.00'),
                'performance_score': 85,
            },
            {
                'name': 'NVIDIA GeForce RTX 4060 Ti',
                'manufacturer': 'NVIDIA',
                'chipset': 'AD106',
                'memory': 8,
                'memory_type': 'GDDR6',
                'core_clock': 2535,
                'tdp': 160,
                'recommended_psu': 550,
                'price': Decimal('49999.00'),
                'performance_score': 75,
            },
            {
                'name': 'NVIDIA GeForce RTX 3060',
                'manufacturer': 'NVIDIA',
                'chipset': 'GA106',
                'memory': 12,
                'memory_type': 'GDDR6',
                'core_clock': 1777,
                'tdp': 170,
                'recommended_psu': 550,
                'price': Decimal('34999.00'),
                'performance_score': 65,
            },
            # AMD
            {
                'name': 'AMD Radeon RX 7900 XTX',
                'manufacturer': 'AMD',
                'chipset': 'Navi 31',
                'memory': 24,
                'memory_type': 'GDDR6',
                'core_clock': 2500,
                'tdp': 355,
                'recommended_psu': 800,
                'price': Decimal('109999.00'),
                'performance_score': 90,
            },
            {
                'name': 'AMD Radeon RX 7800 XT',
                'manufacturer': 'AMD',
                'chipset': 'Navi 32',
                'memory': 16,
                'memory_type': 'GDDR6',
                'core_clock': 2430,
                'tdp': 263,
                'recommended_psu': 700,
                'price': Decimal('64999.00'),
                'performance_score': 80,
            },
            {
                'name': 'AMD Radeon RX 6700 XT',
                'manufacturer': 'AMD',
                'chipset': 'Navi 22',
                'memory': 12,
                'memory_type': 'GDDR6',
                'core_clock': 2581,
                'tdp': 230,
                'recommended_psu': 650,
                'price': Decimal('44999.00'),
                'performance_score': 72,
            },
        ]

        gpus = []
        for gpu_data in gpus_data:
            gpu = GPU.objects.create(**gpu_data)
            gpus.append(gpu)
            self.stdout.write(f'  ✓ {gpu.name}')

        # Создаем оперативную память
        self.stdout.write('Создание оперативной памяти...')
        ram_data = [
            {
                'name': 'Corsair Vengeance RGB DDR5',
                'manufacturer': 'Corsair',
                'memory_type': 'DDR5',
                'capacity': 32,
                'speed': 6000,
                'modules': 2,
                'cas_latency': 30,
                'price': Decimal('14999.00'),
            },
            {
                'name': 'G.Skill Trident Z5 RGB DDR5',
                'manufacturer': 'G.Skill',
                'memory_type': 'DDR5',
                'capacity': 32,
                'speed': 6400,
                'modules': 2,
                'cas_latency': 32,
                'price': Decimal('16999.00'),
            },
            {
                'name': 'Kingston FURY Beast DDR5',
                'manufacturer': 'Kingston',
                'memory_type': 'DDR5',
                'capacity': 16,
                'speed': 5200,
                'modules': 2,
                'cas_latency': 40,
                'price': Decimal('7999.00'),
            },
            {
                'name': 'Corsair Vengeance LPX DDR4',
                'manufacturer': 'Corsair',
                'memory_type': 'DDR4',
                'capacity': 32,
                'speed': 3200,
                'modules': 2,
                'cas_latency': 16,
                'price': Decimal('9999.00'),
            },
            {
                'name': 'G.Skill Ripjaws V DDR4',
                'manufacturer': 'G.Skill',
                'memory_type': 'DDR4',
                'capacity': 16,
                'speed': 3600,
                'modules': 2,
                'cas_latency': 16,
                'price': Decimal('5999.00'),
            },
            {
                'name': 'Kingston FURY Beast DDR4',
                'manufacturer': 'Kingston',
                'memory_type': 'DDR4',
                'capacity': 16,
                'speed': 3200,
                'modules': 2,
                'cas_latency': 16,
                'price': Decimal('4999.00'),
            },
        ]

        rams = []
        for ram_item in ram_data:
            ram = RAM.objects.create(**ram_item)
            rams.append(ram)
            self.stdout.write(f'  ✓ {ram.name}')

        # Создаем накопители
        self.stdout.write('Создание накопителей...')
        storage_data = [
            # NVMe SSD
            {
                'name': 'Samsung 990 Pro',
                'manufacturer': 'Samsung',
                'storage_type': 'nvme',
                'capacity': 2000,
                'read_speed': 7450,
                'write_speed': 6900,
                'price': Decimal('19999.00'),
            },
            {
                'name': 'WD Black SN850X',
                'manufacturer': 'Western Digital',
                'storage_type': 'nvme',
                'capacity': 2000,
                'read_speed': 7300,
                'write_speed': 6600,
                'price': Decimal('17999.00'),
            },
            {
                'name': 'Samsung 980 Pro',
                'manufacturer': 'Samsung',
                'storage_type': 'nvme',
                'capacity': 1000,
                'read_speed': 7000,
                'write_speed': 5100,
                'price': Decimal('11999.00'),
            },
            {
                'name': 'Kingston KC3000',
                'manufacturer': 'Kingston',
                'storage_type': 'nvme',
                'capacity': 1000,
                'read_speed': 7000,
                'write_speed': 6000,
                'price': Decimal('9999.00'),
            },
            # SATA SSD
            {
                'name': 'Samsung 870 EVO',
                'manufacturer': 'Samsung',
                'storage_type': 'ssd',
                'capacity': 1000,
                'read_speed': 560,
                'write_speed': 530,
                'price': Decimal('7999.00'),
            },
            {
                'name': 'Crucial MX500',
                'manufacturer': 'Crucial',
                'storage_type': 'ssd',
                'capacity': 1000,
                'read_speed': 560,
                'write_speed': 510,
                'price': Decimal('6999.00'),
            },
            # HDD
            {
                'name': 'Seagate BarraCuda',
                'manufacturer': 'Seagate',
                'storage_type': 'hdd',
                'capacity': 4000,
                'read_speed': None,
                'write_speed': None,
                'price': Decimal('8999.00'),
            },
            {
                'name': 'WD Blue',
                'manufacturer': 'Western Digital',
                'storage_type': 'hdd',
                'capacity': 2000,
                'read_speed': None,
                'write_speed': None,
                'price': Decimal('5999.00'),
            },
        ]

        storages = []
        for storage_item in storage_data:
            storage = Storage.objects.create(**storage_item)
            storages.append(storage)
            self.stdout.write(f'  ✓ {storage.name}')

        # Создаем тестового пользователя
        self.stdout.write('Создание тестового пользователя...')
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write('  ✓ testuser (пароль: testpass123)')
        else:
            self.stdout.write('  ℹ testuser уже существует')

        # Создаем примеры конфигураций
        self.stdout.write('Создание конфигураций...')
        
        configurations_data = [
            {
                'name': 'Игровая станция 4K',
                'user_type': 'gamer',
                'budget': Decimal('250000.00'),
                'components': {
                    'cpu': cpus[0],  # i9-14900K
                    'gpu': gpus[0],  # RTX 4090
                    'ram': rams[0],  # 32GB DDR5 6000MHz
                    'storage': storages[0],  # Samsung 990 Pro 2TB
                }
            },
            {
                'name': 'Профессиональная рабочая станция',
                'user_type': 'designer',
                'budget': Decimal('180000.00'),
                'components': {
                    'cpu': cpus[4],  # Ryzen 9 7950X
                    'gpu': gpus[5],  # RX 7900 XTX
                    'ram': rams[1],  # 32GB DDR5 6400MHz
                    'storage': storages[1],  # WD Black 2TB
                }
            },
            {
                'name': 'Сбалансированный ПК для работы',
                'user_type': 'programmer',
                'budget': Decimal('120000.00'),
                'components': {
                    'cpu': cpus[2],  # i5-14600K
                    'gpu': gpus[6],  # RX 7800 XT
                    'ram': rams[3],  # 32GB DDR4 3200MHz
                    'storage': storages[2],  # Samsung 980 Pro 1TB
                }
            },
            {
                'name': 'Бюджетный игровой ПК',
                'user_type': 'gamer',
                'budget': Decimal('70000.00'),
                'components': {
                    'cpu': cpus[7],  # Ryzen 5 5600
                    'gpu': gpus[4],  # RTX 3060
                    'ram': rams[5],  # 16GB DDR4 3200MHz
                    'storage': storages[5],  # Crucial MX500 1TB
                }
            },
            {
                'name': 'Офисный ПК',
                'user_type': 'office',
                'budget': Decimal('50000.00'),
                'components': {
                    'cpu': cpus[3],  # i5-13400F
                    'gpu': None,
                    'ram': rams[4],  # 16GB DDR4 3600MHz
                    'storage': storages[4],  # Samsung 870 EVO 1TB
                }
            },
        ]

        for config_data in configurations_data:
            components = config_data['components']
            
            config = PCConfiguration.objects.create(
                user=user,
                name=config_data['name'],
                cpu=components['cpu'],
                gpu=components['gpu'],
                ram=components['ram'],
                storage_primary=components['storage'],
                is_saved=True
            )

            # Рассчитываем общую стоимость
            config.calculate_total_price()
            config.save()

            self.stdout.write(f'  ✓ {config.name} (₽{config.total_price:,.0f})')

        self.stdout.write(self.style.SUCCESS('\n✅ База данных успешно заполнена!'))
        self.stdout.write(f'\nСтатистика:')
        self.stdout.write(f'  • Процессоров: {len(cpus)}')
        self.stdout.write(f'  • Видеокарт: {len(gpus)}')
        self.stdout.write(f'  • Модулей RAM: {len(rams)}')
        self.stdout.write(f'  • Накопителей: {len(storages)}')
        self.stdout.write(f'  • Конфигураций: {len(configurations_data)}')
        self.stdout.write(f'\nТестовый пользователь:')
        self.stdout.write(f'  Логин: testuser')
        self.stdout.write(f'  Пароль: testpass123')
