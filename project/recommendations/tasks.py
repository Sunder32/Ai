
import logging
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import models as db_models
from datetime import timedelta

logger = logging.getLogger(__name__)




@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_ai_configuration(self, user_id: int, config_params: dict):

    from accounts.models import User
    from .models import PCConfiguration, AILog
    from .ai_full_config_service import AIFullConfigService
    
    logger.info(f"[CELERY] Starting AI generation for user {user_id}")
    
    try:
        user = User.objects.get(id=user_id)
        

        ai_service = AIFullConfigService(
            user_type=config_params.get('user_type', 'gaming'),
            min_budget=float(config_params.get('min_budget', 50000)),
            max_budget=float(config_params.get('max_budget', 150000)),
            priority=config_params.get('priority', 'balanced'),
            requirements=config_params.get('requirements', {}),
            pc_preferences=config_params.get('pc_preferences', {}),
            peripherals_preferences=config_params.get('peripherals_preferences', {}),
            workspace_preferences=config_params.get('workspace_preferences', {}),
            include_peripherals=config_params.get('include_peripherals', True),
            include_workspace=config_params.get('include_workspace', True),
        )
        

        import time
        start_time = time.time()
        
        configuration, workspace, ai_info = ai_service.generate_full_configuration(user)
        
        response_time = int((time.time() - start_time) * 1000)
        
        if configuration:

            AILog.log_response(
                user=user,
                prompt=str(config_params),
                raw_response=str(ai_info),
                parsed_response={'configuration_id': configuration.id},
                status='success',
                response_time_ms=response_time,
                configuration_id=configuration.id
            )
            
            logger.info(f"[CELERY] AI generation complete: config #{configuration.id}")
            
            return {
                'status': 'success',
                'configuration_id': configuration.id,
                'workspace_id': workspace.id if workspace else None,
                'total_price': float(configuration.total_price),
                'response_time_ms': response_time
            }
        else:

            AILog.log_response(
                user=user,
                prompt=str(config_params),
                raw_response='',
                parsed_response={},
                status='error',
                response_time_ms=response_time,
                fallback_reason=ai_info.get('error', 'Unknown error')
            )
            
            return {
                'status': 'error',
                'error': ai_info.get('error', 'AI generation failed')
            }
            
    except SoftTimeLimitExceeded:
        logger.error(f"[CELERY] AI generation timeout for user {user_id}")
        return {
            'status': 'timeout',
            'error': 'AI generation timed out after 4 minutes'
        }
        
    except Exception as e:
        logger.exception(f"[CELERY] AI generation error: {e}")
        

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            'status': 'error',
            'error': str(e)
        }



@shared_task(bind=True)
def update_all_prices(self):

    from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
    from .price_service import PriceParserService
    
    logger.info("[CELERY] Starting scheduled price update")
    
    service = PriceParserService()
    updated_count = 0
    error_count = 0
    

    component_models = [
        ('cpu', CPU),
        ('gpu', GPU),
        ('motherboard', Motherboard),
        ('ram', RAM),
        ('storage', Storage),
        ('psu', PSU),
        ('case', Case),
        ('cooling', Cooling),
    ]
    
    for component_type, model in component_models:
        components = model.objects.all()[:50]  
        
        for component in components:
            try:
                updated = service.update_component_price(component_type, component.id)
                if updated:
                    updated_count += 1
            except Exception as e:
                logger.warning(f"[CELERY] Price update failed for {component_type} #{component.id}: {e}")
                error_count += 1
    
    logger.info(f"[CELERY] Price update complete: {updated_count} updated, {error_count} errors")
    
    return {
        'status': 'complete',
        'updated': updated_count,
        'errors': error_count
    }


@shared_task
def update_component_price(component_type: str, component_id: int):

    from .price_service import PriceParserService
    
    service = PriceParserService()
    updated = service.update_component_price(component_type, component_id)
    
    return {
        'component_type': component_type,
        'component_id': component_id,
        'updated': updated
    }



@shared_task
def check_price_alerts():

    from .models import Wishlist
    from accounts.models import User
    
    logger.info("[CELERY] Checking price alerts")
    
    alerts_sent = 0
    

    wishlists = Wishlist.objects.filter(
        price_alert_threshold__isnull=False,
        notifications_enabled=True
    ).select_related('user')
    
    for wishlist_item in wishlists:
        price_info = wishlist_item.check_price_change()
        
        if price_info and price_info.get('below_threshold'):
            
            send_price_alert_email.delay(
                user_id=wishlist_item.user.id,
                component_type=wishlist_item.component_type,
                component_id=wishlist_item.component_id,
                current_price=price_info['current_price'],
                threshold_price=float(wishlist_item.price_alert_threshold),
                original_price=price_info['price_at_add']
            )
            alerts_sent += 1
    
    logger.info(f"[CELERY] Price alerts sent: {alerts_sent}")
    
    return {'alerts_sent': alerts_sent}


@shared_task
def send_price_alert_email(user_id: int, component_type: str, component_id: int,
                            current_price: float, threshold_price: float, original_price: float):
    
    from accounts.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            logger.warning(f"[CELERY] User {user_id} has no email")
            return {'status': 'skipped', 'reason': 'no email'}
        
        
        component_name = f"{component_type.upper()} #{component_id}"
        
        subject = f"🔔 Цена снизилась! {component_name}"
        message = f"""
Привет, {user.username}!

Отличные новости! Цена на компонент из вашего списка желаний снизилась:

📦 {component_name}
💰 Текущая цена: {current_price:,.0f} ₽
🎯 Ваш порог: {threshold_price:,.0f} ₽
📉 Было: {original_price:,.0f} ₽

Скидка: {((original_price - current_price) / original_price * 100):.1f}%

Поспешите - цены могут измениться!

---
PC Configurator
https://pckonfai.ru
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
        
        logger.info(f"[CELERY] Price alert sent to {user.email}")
        return {'status': 'sent', 'email': user.email}
        
    except User.DoesNotExist:
        logger.error(f"[CELERY] User {user_id} not found")
        return {'status': 'error', 'reason': 'user not found'}
    except Exception as e:
        logger.exception(f"[CELERY] Email send error: {e}")
        return {'status': 'error', 'reason': str(e)}




@shared_task
def cleanup_old_logs(days: int = 30):

    from .models import AILog
    
    cutoff_date = timezone.now() - timedelta(days=days)
    

    deleted_count, _ = AILog.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['error', 'validation_failed']
    ).delete()
    
    logger.info(f"[CELERY] Cleaned up {deleted_count} old AI logs")
    
    return {'deleted': deleted_count}


@shared_task
def generate_ai_analytics_report():

    from .models import AILog
    

    yesterday = timezone.now() - timedelta(days=1)
    today_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    logs = AILog.objects.filter(
        created_at__gte=today_start,
        created_at__lt=today_end
    )
    
    total = logs.count()
    success = logs.filter(status='success').count()
    errors = logs.filter(status='error').count()
    fallbacks = logs.filter(status='fallback_used').count()
    
    avg_time = logs.exclude(response_time_ms__isnull=True).aggregate(
        avg=db_models.Avg('response_time_ms')
    )['avg'] or 0
    
    report = {
        'date': today_start.date().isoformat(),
        'total_requests': total,
        'success_count': success,
        'error_count': errors,
        'fallback_count': fallbacks,
        'success_rate': round(success / total * 100, 2) if total > 0 else 0,
        'avg_response_time_ms': round(avg_time, 2)
    }
    
    logger.info(f"[CELERY] Daily AI report: {report}")
    
    return report



@shared_task
def send_configuration_ready_notification(user_id: int, configuration_id: int):

    from django_eventstream import send_event
    
    try:
        send_event(
            f'user-{user_id}',
            'configuration-ready',
            {
                'configuration_id': configuration_id,
                'message': 'Your AI configuration is ready!'
            }
        )
        return {'status': 'sent'}
    except Exception as e:
        logger.error(f"[CELERY] SSE notification error: {e}")
        return {'status': 'error', 'reason': str(e)}
