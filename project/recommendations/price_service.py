"""
Сервис получения актуальных цен на компоненты ПК.
Парсинг цен с популярных магазинов: DNS, Citilink, Regard.

ВАЖНО: Парсинг сайтов может нарушать их Terms of Service.
Рекомендуется использовать официальные API партнёров если они доступны.
"""
import logging
import requests
import re
import json
from typing import Optional, Dict, List, Any
from urllib.parse import quote
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import models

logger = logging.getLogger(__name__)


class PriceCache(models.Model):
    """Кэш цен компонентов"""
    component_type = models.CharField(max_length=50)
    component_id = models.IntegerField()
    shop = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    url = models.URLField(max_length=500, blank=True)
    in_stock = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'recommendations'
        unique_together = ['component_type', 'component_id', 'shop']
        indexes = [
            models.Index(fields=['component_type', 'component_id']),
        ]


class PriceParserService:
    """
    Сервис парсинга цен с магазинов.
    
    Использует поиск по названию товара и парсит результаты.
    Результаты кэшируются на 1 час.
    """
    
    # Базовые URL магазинов
    SHOPS = {
        'dns': {
            'name': 'DNS',
            'search_url': 'https://www.dns-shop.ru/search/',
            'api_search': 'https://restapi.dns-shop.ru/v1/search',  # Неофициальный API
        },
        'citilink': {
            'name': 'Citilink',
            'search_url': 'https://www.citilink.ru/search/',
        },
        'regard': {
            'name': 'Regard',
            'search_url': 'https://www.regard.ru/catalog',
        }
    }
    
    # User-Agent для запросов
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    CACHE_TTL = 3600  # 1 час
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def search_component_prices(self, component_name: str, component_type: str = None) -> Dict[str, Any]:
        """
        Поиск цен на компонент во всех магазинах.
        
        Args:
            component_name: Название компонента (например "Intel Core i5-13600K")
            component_type: Тип компонента для уточнения поиска
        
        Returns:
            Dict с ценами из разных магазинов
        """
        cache_key = f"prices_{quote(component_name)}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        results = {
            'component': component_name,
            'searched_at': datetime.now().isoformat(),
            'prices': {},
            'best_price': None,
            'best_shop': None
        }
        
        # Поиск в каждом магазине
        for shop_id, shop_info in self.SHOPS.items():
            try:
                price_data = self._search_in_shop(shop_id, component_name)
                if price_data:
                    results['prices'][shop_id] = price_data
                    
                    # Определяем лучшую цену
                    if price_data.get('price'):
                        if not results['best_price'] or price_data['price'] < results['best_price']:
                            results['best_price'] = price_data['price']
                            results['best_shop'] = shop_id
            except Exception as e:
                logger.warning(f"Error searching {shop_id}: {e}")
                results['prices'][shop_id] = {'error': str(e)}
        
        # Кэшируем результат
        cache.set(cache_key, results, self.CACHE_TTL)
        
        return results
    
    def _search_in_shop(self, shop_id: str, query: str) -> Optional[Dict]:
        """Поиск в конкретном магазине"""
        if shop_id == 'dns':
            return self._search_dns(query)
        elif shop_id == 'citilink':
            return self._search_citilink(query)
        elif shop_id == 'regard':
            return self._search_regard(query)
        return None
    
    def _search_dns(self, query: str) -> Optional[Dict]:
        """
        Поиск в DNS.
        DNS имеет защиту от парсинга, поэтому используем упрощённый подход.
        """
        try:
            url = f"https://www.dns-shop.ru/search/?q={quote(query)}"
            
            # DNS блокирует прямые запросы, возвращаем ссылку для ручного поиска
            return {
                'shop': 'DNS',
                'search_url': url,
                'price': None,
                'note': 'Автоматический парсинг DNS недоступен. Используйте ссылку для поиска.'
            }
        except Exception as e:
            logger.error(f"DNS search error: {e}")
            return None
    
    def _search_citilink(self, query: str) -> Optional[Dict]:
        """
        Поиск в Citilink.
        """
        try:
            url = f"https://www.citilink.ru/search/?text={quote(query)}"
            
            # Citilink также имеет защиту от парсинга
            return {
                'shop': 'Citilink',
                'search_url': url,
                'price': None,
                'note': 'Автоматический парсинг Citilink недоступен. Используйте ссылку для поиска.'
            }
        except Exception as e:
            logger.error(f"Citilink search error: {e}")
            return None
    
    def _search_regard(self, query: str) -> Optional[Dict]:
        """
        Поиск в Regard.
        """
        try:
            url = f"https://www.regard.ru/catalog?search={quote(query)}"
            
            return {
                'shop': 'Regard',
                'search_url': url,
                'price': None,
                'note': 'Автоматический парсинг Regard недоступен. Используйте ссылку для поиска.'
            }
        except Exception as e:
            logger.error(f"Regard search error: {e}")
            return None
    
    def get_component_links(self, component_name: str) -> Dict[str, str]:
        """
        Получить ссылки на поиск компонента во всех магазинах.
        """
        encoded_name = quote(component_name)
        return {
            'dns': f"https://www.dns-shop.ru/search/?q={encoded_name}",
            'citilink': f"https://www.citilink.ru/search/?text={encoded_name}",
            'regard': f"https://www.regard.ru/catalog?search={encoded_name}",
            'mvideo': f"https://www.mvideo.ru/product-list-page?q={encoded_name}",
            'ozon': f"https://www.ozon.ru/search/?text={encoded_name}&from_global=true",
            'yandex_market': f"https://market.yandex.ru/search?text={encoded_name}",
        }


class ComponentPriceUpdater:
    """
    Сервис обновления цен компонентов в базе данных.
    
    Использует данные из внешних источников для актуализации цен.
    """
    
    def __init__(self):
        self.parser = PriceParserService()
    
    def update_component_price(self, component_type: str, component_id: int) -> Dict:
        """
        Обновить цену конкретного компонента.
        """
        from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
        
        model_map = {
            'cpu': CPU,
            'gpu': GPU,
            'motherboard': Motherboard,
            'ram': RAM,
            'storage': Storage,
            'psu': PSU,
            'case': Case,
            'cooling': Cooling,
        }
        
        model = model_map.get(component_type)
        if not model:
            return {'error': 'Unknown component type'}
        
        try:
            component = model.objects.get(id=component_id)
        except model.DoesNotExist:
            return {'error': 'Component not found'}
        
        # Получаем ссылки на магазины
        links = self.parser.get_component_links(component.name)
        
        return {
            'component': str(component),
            'current_price': float(component.price),
            'shop_links': links,
            'note': 'Автоматическое обновление цен требует партнёрского API. Используйте ссылки для проверки актуальных цен.'
        }
    
    def bulk_update_prices(self, component_type: str = None) -> Dict:
        """
        Массовое обновление цен.
        
        Примечание: Для реального обновления цен необходим 
        партнёрский API магазина.
        """
        return {
            'status': 'not_implemented',
            'message': 'Массовое обновление цен требует партнёрского API магазинов (DNS, Citilink). '
                      'Для получения API обратитесь в партнёрские программы магазинов.',
            'partner_programs': {
                'dns': 'https://www.dns-shop.ru/affiliate/',
                'citilink': 'https://www.citilink.ru/partnership/',
            }
        }


class ExternalPriceAPI:
    """
    Интеграция с внешними API для получения цен.
    
    Поддерживаемые API:
    - Яндекс.Маркет API (требует регистрации)
    - Партнёрские API магазинов
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def search_yandex_market(self, query: str) -> Optional[Dict]:
        """
        Поиск на Яндекс.Маркет через API.
        
        Требует регистрации и получения API ключа:
        https://tech.yandex.ru/market/content-data/
        """
        if not self.api_key:
            return {
                'error': 'API key required',
                'register_url': 'https://partner.market.yandex.ru/',
                'search_link': f"https://market.yandex.ru/search?text={quote(query)}"
            }
        
        # Здесь была бы интеграция с Яндекс.Маркет API
        # API_URL = "https://api.partner.market.yandex.ru/v2/..."
        
        return None
    
    def get_all_prices(self, component_name: str) -> Dict[str, Any]:
        """
        Получить цены из всех доступных источников.
        """
        parser = PriceParserService()
        links = parser.get_component_links(component_name)
        
        return {
            'component': component_name,
            'auto_prices': None,  # Автопарсинг недоступен
            'manual_links': links,
            'recommendation': 'Используйте ссылки для ручной проверки цен. '
                            'Для автоматизации зарегистрируйтесь в партнёрских программах магазинов.'
        }
