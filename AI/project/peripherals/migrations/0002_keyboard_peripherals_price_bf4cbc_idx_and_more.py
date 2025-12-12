
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peripherals', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='keyboard',
            index=models.Index(fields=['price', 'switch_type'], name='peripherals_price_bf4cbc_idx'),
        ),
        migrations.AddIndex(
            model_name='monitor',
            index=models.Index(fields=['price', 'refresh_rate'], name='peripherals_price_ff74a3_idx'),
        ),
        migrations.AddIndex(
            model_name='monitor',
            index=models.Index(fields=['screen_size', 'resolution'], name='peripherals_screen__f79aab_idx'),
        ),
        migrations.AddIndex(
            model_name='mouse',
            index=models.Index(fields=['price', 'dpi'], name='peripherals_price_0e74e2_idx'),
        ),
    ]
