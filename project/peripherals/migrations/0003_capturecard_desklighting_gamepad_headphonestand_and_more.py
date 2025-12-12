

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peripherals', '0002_keyboard_peripherals_price_bf4cbc_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaptureCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('max_resolution', models.CharField(max_length=50, verbose_name='Макс. разрешение')),
                ('max_fps', models.IntegerField(verbose_name='Макс. FPS')),
                ('connection', models.CharField(max_length=50, verbose_name='Подключение')),
                ('passthrough', models.BooleanField(default=True, verbose_name='Passthrough')),
                ('internal', models.BooleanField(default=False, verbose_name='Внутренняя')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Карта захвата',
                'verbose_name_plural': 'Карты захвата',
            },
        ),
        migrations.CreateModel(
            name='DeskLighting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('lighting_type', models.CharField(choices=[('led_strip', 'LED лента'), ('desk_lamp', 'Настольная лампа'), ('monitor_bar', 'Лампа на монитор'), ('ambient', 'Ambient подсветка'), ('ring_light', 'Кольцевая лампа')], max_length=20, verbose_name='Тип освещения')),
                ('rgb', models.BooleanField(default=False, verbose_name='RGB')),
                ('dimmable', models.BooleanField(default=True, verbose_name='Регулировка яркости')),
                ('color_temperature', models.CharField(blank=True, max_length=50, verbose_name='Цветовая температура')),
                ('smart_control', models.BooleanField(default=False, verbose_name='Умное управление')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Освещение',
                'verbose_name_plural': 'Освещение',
            },
        ),
        migrations.CreateModel(
            name='Gamepad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('platform', models.CharField(choices=[('pc', 'PC'), ('xbox', 'Xbox'), ('playstation', 'PlayStation'), ('universal', 'Универсальный')], max_length=20, verbose_name='Платформа')),
                ('wireless', models.BooleanField(default=False, verbose_name='Беспроводной')),
                ('vibration', models.BooleanField(default=True, verbose_name='Вибрация')),
                ('rgb', models.BooleanField(default=False, verbose_name='RGB подсветка')),
                ('extra_buttons', models.IntegerField(default=0, verbose_name='Доп. кнопки')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Геймпад',
                'verbose_name_plural': 'Геймпады',
            },
        ),
        migrations.CreateModel(
            name='Headphonestand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('usb_hub', models.BooleanField(default=False, verbose_name='Встроенный USB-хаб')),
                ('usb_ports', models.IntegerField(default=0, verbose_name='USB портов')),
                ('rgb', models.BooleanField(default=False, verbose_name='RGB подсветка')),
                ('wireless_charging', models.BooleanField(default=False, verbose_name='Беспроводная зарядка')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Подставка для наушников',
                'verbose_name_plural': 'Подставки для наушников',
            },
        ),
        migrations.CreateModel(
            name='MonitorArm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('mount_type', models.CharField(choices=[('single', 'Для одного монитора'), ('dual', 'Для двух мониторов'), ('triple', 'Для трёх мониторов'), ('quad', 'Для четырёх мониторов')], max_length=20, verbose_name='Тип крепления')),
                ('max_screen_size', models.IntegerField(verbose_name='Макс. диагональ (дюймы)')),
                ('max_weight', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Макс. вес (кг)')),
                ('vesa_pattern', models.CharField(default='75x75, 100x100', max_length=50, verbose_name='VESA паттерн')),
                ('gas_spring', models.BooleanField(default=False, verbose_name='Газлифт')),
                ('cable_management', models.BooleanField(default=True, verbose_name='Кабель-менеджмент')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Кронштейн для монитора',
                'verbose_name_plural': 'Кронштейны для мониторов',
            },
        ),
        migrations.CreateModel(
            name='Mousepad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('size', models.CharField(choices=[('small', 'Маленький (до 30 см)'), ('medium', 'Средний (30-45 см)'), ('large', 'Большой (45-80 см)'), ('xl', 'XL (80+ см)'), ('desk', 'На весь стол')], max_length=20, verbose_name='Размер')),
                ('width', models.IntegerField(verbose_name='Ширина (мм)')),
                ('height', models.IntegerField(verbose_name='Высота (мм)')),
                ('thickness', models.IntegerField(default=3, verbose_name='Толщина (мм)')),
                ('rgb', models.BooleanField(default=False, verbose_name='RGB подсветка')),
                ('material', models.CharField(default='Ткань', max_length=100, verbose_name='Материал')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Коврик для мыши',
                'verbose_name_plural': 'Коврики для мыши',
            },
        ),
        migrations.CreateModel(
            name='Speakers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('speaker_type', models.CharField(choices=[('2.0', '2.0 Стерео'), ('2.1', '2.1 с сабвуфером'), ('5.1', '5.1 Surround'), ('soundbar', 'Саундбар')], max_length=20, verbose_name='Тип')),
                ('total_power', models.IntegerField(verbose_name='Мощность (Вт)')),
                ('frequency_response', models.CharField(blank=True, max_length=50, verbose_name='Частотный диапазон')),
                ('bluetooth', models.BooleanField(default=False, verbose_name='Bluetooth')),
                ('rgb', models.BooleanField(default=False, verbose_name='RGB подсветка')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Колонки',
                'verbose_name_plural': 'Колонки',
            },
        ),
        migrations.CreateModel(
            name='StreamDeck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('keys_count', models.IntegerField(verbose_name='Количество клавиш')),
                ('lcd_keys', models.BooleanField(default=True, verbose_name='LCD клавиши')),
                ('dials', models.IntegerField(default=0, verbose_name='Количество крутилок')),
                ('touchscreen', models.BooleanField(default=False, verbose_name='Сенсорный экран')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Стрим-пульт',
                'verbose_name_plural': 'Стрим-пульты',
            },
        ),
        migrations.CreateModel(
            name='USBHub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('usb3_ports', models.IntegerField(default=0, verbose_name='USB 3.0 портов')),
                ('usbc_ports', models.IntegerField(default=0, verbose_name='USB-C портов')),
                ('usb2_ports', models.IntegerField(default=0, verbose_name='USB 2.0 портов')),
                ('card_reader', models.BooleanField(default=False, verbose_name='Картридер')),
                ('hdmi_port', models.BooleanField(default=False, verbose_name='HDMI выход')),
                ('ethernet_port', models.BooleanField(default=False, verbose_name='Ethernet порт')),
                ('power_delivery', models.IntegerField(blank=True, null=True, verbose_name='Power Delivery (Вт)')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'USB-хаб',
                'verbose_name_plural': 'USB-хабы',
            },
        ),
    ]
