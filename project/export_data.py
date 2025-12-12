
import os
import sys
import json


os.environ['PYTHONIOENCODING'] = 'utf-8'


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core import serializers
from django.apps import apps

def export_data():

    exclude_models = [
        'auth.permission',
        'contenttypes.contenttype',
    ]
    
    all_objects = []
    
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            model_label = f"{model._meta.app_label}.{model._meta.model_name}"
            if model_label in exclude_models:
                continue
            
            try:
                objects = model.objects.all()
                if objects.exists():
                    data = serializers.serialize('python', objects)
                    all_objects.extend(data)
                    print(f"Exported {model_label}: {len(data)} objects")
            except Exception as e:
                print(f"Error exporting {model_label}: {e}")
    
    
    output_file = 'data_backup_clean.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_objects, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nExported {len(all_objects)} total objects to {output_file}")

if __name__ == '__main__':
    export_data()
