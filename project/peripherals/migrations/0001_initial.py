

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('ergonomic', models.BooleanField(default=False, verbose_name='Эргономичное')),
                ('adjustable_armrests', models.BooleanField(default=False, verbose_name='Регулируемые подлокотники')),
                ('lumbar_support', models.BooleanField(default=False, verbose_name='Поддержка поясницы')),
                ('max_weight', models.IntegerField(blank=True, null=True, verbose_name='Макс. вес (кг)')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Кресло',
                'verbose_name_plural': 'Кресла',
            },
        ),
        migrations.CreateModel(
            name='Desk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('width', models.IntegerField(verbose_name='Ширина (см)')),
                ('depth', models.IntegerField(verbose_name='Глубина (см)')),
                ('adjustable_height', models.BooleanField(default=False, verbose_name='Регулируемая высота')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Стол',
                'verbose_name_plural': 'Столы',
            },
        ),
        migrations.CreateModel(
            name='Headset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('connection_type', models.CharField(max_length=50, verbose_name='Тип подключения')),
                ('wireless', models.BooleanField(default=False, verbose_name='Беспроводные')),
                ('microphone', models.BooleanField(default=False, verbose_name='С микрофоном')),
                ('surround', models.BooleanField(default=False, verbose_name='Объемный звук')),
                ('noise_cancelling', models.BooleanField(default=False, verbose_name='Шумоподавление')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Наушники',
                'verbose_name_plural': 'Наушники',
            },
        ),
        migrations.CreateModel(
            name='Keyboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('switch_type', models.CharField(choices=[('mechanical', 'Механическая'), ('membrane', 'Мембранная'), ('optical', 'Оптическая')], max_length=20, verbose_name='Тип переключателей')),
                ('switch_model', models.CharField(blank=True, max_length=100, verbose_name='Модель переключателей')),
                ('rgb', models.BooleanField(default=False, verbose_name='RGB подсветка')),
                ('wireless', models.BooleanField(default=False, verbose_name='Беспроводная')),
                ('form_factor', models.CharField(blank=True, max_length=50, verbose_name='Форм-фактор')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Клавиатура',
                'verbose_name_plural': 'Клавиатуры',
            },
        ),
        migrations.CreateModel(
            name='Microphone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('microphone_type', models.CharField(choices=[('condenser', 'Конденсаторный'), ('dynamic', 'Динамический'), ('usb', 'USB')], max_length=20, verbose_name='Тип')),
                ('connection', models.CharField(max_length=50, verbose_name='Тип подключения')),
                ('polar_pattern', models.CharField(blank=True, max_length=100, verbose_name='Диаграмма направленности')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Микрофон',
                'verbose_name_plural': 'Микрофоны',
            },
        ),
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('screen_size', models.FloatField(verbose_name='Диагональ (дюймы)')),
                ('resolution', models.CharField(max_length=50, verbose_name='Разрешение')),
                ('refresh_rate', models.IntegerField(verbose_name='Частота обновления (Гц)')),
                ('panel_type', models.CharField(max_length=50, verbose_name='Тип матрицы')),
                ('response_time', models.IntegerField(verbose_name='Время отклика (мс)')),
                ('hdr', models.BooleanField(default=False, verbose_name='HDR')),
                ('curved', models.BooleanField(default=False, verbose_name='Изогнутый')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Монитор',
                'verbose_name_plural': 'Мониторы',
            },
        ),
        migrations.CreateModel(
            name='Mouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('sensor_type', models.CharField(choices=[('optical', 'Оптический'), ('laser', 'Лазерный')], max_length=20, verbose_name='Тип сенсора')),
                ('dpi', models.IntegerField(verbose_name='Максимальный DPI')),
                ('buttons', models.IntegerField(verbose_name='Количество кнопок')),
                ('wireless', models.BooleanField(default=False, verbose_name='Беспроводная')),
                ('rgb', models.BooleanField(default=False, verbose_name='RGB подсветка')),
                ('weight', models.IntegerField(blank=True, null=True, verbose_name='Вес (г)')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Мышь',
                'verbose_name_plural': 'Мыши',
            },
        ),
        migrations.CreateModel(
            name='Webcam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Производитель')),
                ('resolution', models.CharField(max_length=50, verbose_name='Разрешение')),
                ('fps', models.IntegerField(verbose_name='Кадров в секунду')),
                ('autofocus', models.BooleanField(default=False, verbose_name='Автофокус')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Веб-камера',
                'verbose_name_plural': 'Веб-камеры',
            },
        ),
    ]
