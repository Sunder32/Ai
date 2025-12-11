"""
Celery configuration for PC Configurator project.

Handles:
- Async AI generation tasks
- Scheduled price updates
- Email notifications
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('pckonfai')

# Load config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Update prices every 6 hours
    'update-component-prices': {
        'task': 'recommendations.tasks.update_all_prices',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'options': {'queue': 'prices'}
    },
    
    # Check price alerts and send notifications every hour
    'check-price-alerts': {
        'task': 'recommendations.tasks.check_price_alerts',
        'schedule': crontab(minute=0),  # Every hour at minute 0
        'options': {'queue': 'notifications'}
    },
    
    # Clean up old AI logs weekly
    'cleanup-old-ai-logs': {
        'task': 'recommendations.tasks.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3:00 AM
        'options': {'queue': 'maintenance'}
    },
    
    # Generate AI analytics report daily
    'daily-ai-analytics': {
        'task': 'recommendations.tasks.generate_ai_analytics_report',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6:00 AM
        'options': {'queue': 'analytics'}
    },
}

# Task routing
app.conf.task_routes = {
    'recommendations.tasks.generate_ai_configuration': {'queue': 'ai'},
    'recommendations.tasks.update_all_prices': {'queue': 'prices'},
    'recommendations.tasks.update_component_price': {'queue': 'prices'},
    'recommendations.tasks.check_price_alerts': {'queue': 'notifications'},
    'recommendations.tasks.send_price_alert_email': {'queue': 'notifications'},
    'recommendations.tasks.cleanup_old_logs': {'queue': 'maintenance'},
    'recommendations.tasks.generate_ai_analytics_report': {'queue': 'analytics'},
}

# Task settings
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'Europe/Moscow'
app.conf.enable_utc = True

# Result backend settings
app.conf.result_expires = 3600  # Results expire after 1 hour

# Worker settings
app.conf.worker_prefetch_multiplier = 1  # Prevent long tasks from blocking
app.conf.task_acks_late = True  # Acknowledge after task completion

# AI task specific settings
app.conf.task_time_limit = 300  # 5 minutes max for any task
app.conf.task_soft_time_limit = 240  # Soft limit 4 minutes


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
