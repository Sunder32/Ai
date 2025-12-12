
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('pckonfai')


app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {

    'update-component-prices': {
        'task': 'recommendations.tasks.update_all_prices',
        'schedule': crontab(hour='*/6'),  
        'options': {'queue': 'prices'}
    },
    

    'check-price-alerts': {
        'task': 'recommendations.tasks.check_price_alerts',
        'schedule': crontab(minute=0),  
        'options': {'queue': 'notifications'}
    },
    

    'cleanup-old-ai-logs': {
        'task': 'recommendations.tasks.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  
        'options': {'queue': 'maintenance'}
    },
    

    'daily-ai-analytics': {
        'task': 'recommendations.tasks.generate_ai_analytics_report',
        'schedule': crontab(hour=6, minute=0),  
        'options': {'queue': 'analytics'}
    },
}


app.conf.task_routes = {
    'recommendations.tasks.generate_ai_configuration': {'queue': 'ai'},
    'recommendations.tasks.update_all_prices': {'queue': 'prices'},
    'recommendations.tasks.update_component_price': {'queue': 'prices'},
    'recommendations.tasks.check_price_alerts': {'queue': 'notifications'},
    'recommendations.tasks.send_price_alert_email': {'queue': 'notifications'},
    'recommendations.tasks.cleanup_old_logs': {'queue': 'maintenance'},
    'recommendations.tasks.generate_ai_analytics_report': {'queue': 'analytics'},
}


app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'Europe/Moscow'
app.conf.enable_utc = True


app.conf.result_expires = 3600 


app.conf.worker_prefetch_multiplier = 1  
app.conf.task_acks_late = True  


app.conf.task_time_limit = 300  
app.conf.task_soft_time_limit = 240  


@app.task(bind=True, ignore_result=True)
def debug_task(self):

    print(f'Request: {self.request!r}')
