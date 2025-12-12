

import asyncio
import aiohttp
import hashlib
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, quote_plus
from dataclasses import dataclass, asdict
from enum import Enum

from django.conf import settings
from django.core.cache import cache
from django.db import models

logger = logging.getLogger(__name__)


class Store(Enum):
    DNS = "dns"
    CITILINK = "citilink"
    REGARD = "regard"
    MVIDEO = "mvideo"
    ELDORADO = "eldorado"


@dataclass
class StoreProduct:
 
    store: str
    product_id: str
    name: str
    price: float
    original_price: Optional[float]  
    url: str
    affiliate_url: str
    in_stock: bool
    stock_quantity: Optional[int]
    delivery_days: Optional[int]
    rating: Optional[float]
    reviews_count: Optional[int]
    image_url: Optional[str]
    last_updated: datetime
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['last_updated'] = self.last_updated.isoformat()
        return result


@dataclass
class PriceHistoryPoint:
    
    date: datetime
    price: float
    store: str
    in_stock: bool
    
    def to_dict(self) -> Dict:
        return {
            'date': self.date.isoformat(),
            'price': self.price,
            'store': self.store,
            'in_stock': self.in_stock
        }


class StoreIntegrationService:

    AFFILIATE_CONFIG = {
        Store.DNS: {
            'base_url': 'https://www.dns-shop.ru',
            'search_url': 'https://www.dns-shop.ru/search/',
            'affiliate_param': 'utm_source=pckonfai&utm_medium=affiliate',
            'api_key': getattr(settings, 'DNS_API_KEY', None),
        },
        Store.CITILINK: {
            'base_url': 'https://www.citilink.ru',
            'search_url': 'https://www.citilink.ru/search/',
            'affiliate_param': 'utm_source=pckonfai&utm_medium=affiliate',
            'api_key': getattr(settings, 'CITILINK_API_KEY', None),
        },
        Store.REGARD: {
            'base_url': 'https://www.regard.ru',
            'search_url': 'https://www.regard.ru/catalog/?search=',
            'affiliate_param': 'utm_source=pckonfai',
            'api_key': None,
        },
        Store.MVIDEO: {
            'base_url': 'https://www.mvideo.ru',
            'search_url': 'https://www.mvideo.ru/product-list-page?q=',
            'affiliate_param': 'utm_source=pckonfai',
            'api_key': None,
        },
    }
    

    CATEGORY_MAPPING = {
        'cpu': {
            Store.DNS: 'processors',
            Store.CITILINK: 'processory',
        },
        'gpu': {
            Store.DNS: 'videokarty',
            Store.CITILINK: 'videokarty',
        },
        'motherboard': {
            Store.DNS: 'materinskie-platy',
            Store.CITILINK: 'materinskie-platy',
        },
        'ram': {
            Store.DNS: 'operativnaya-pamyat',
            Store.CITILINK: 'moduli-pamyati',
        },
        'storage': {
            Store.DNS: 'ssd-nakopiteli',
            Store.CITILINK: 'ssd-nakopiteli',
        },
        'psu': {
            Store.DNS: 'bloki-pitaniya',
            Store.CITILINK: 'bloki-pitaniya',
        },
        'case': {
            Store.DNS: 'korpusa',
            Store.CITILINK: 'korpusa',
        },
        'cooling': {
            Store.DNS: 'kulery',
            Store.CITILINK: 'kulery-dlya-processorov',
        },
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json, text/html',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                }
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    def generate_affiliate_url(self, store: Store, product_url: str) -> str:

        config = self.AFFILIATE_CONFIG.get(store, {})
        affiliate_param = config.get('affiliate_param', '')
        
        separator = '&' if '?' in product_url else '?'
        return f"{product_url}{separator}{affiliate_param}"
    
    def generate_search_url(self, store: Store, query: str, category: Optional[str] = None) -> str:

        config = self.AFFILIATE_CONFIG.get(store, {})
        search_url = config.get('search_url', '')
        affiliate_param = config.get('affiliate_param', '')
        
        encoded_query = quote_plus(query)
        
        if store == Store.DNS:
            url = f"{search_url}?q={encoded_query}"
        elif store == Store.CITILINK:
            url = f"{search_url}?text={encoded_query}"
        elif store == Store.REGARD:
            url = f"{search_url}{encoded_query}"
        else:
            url = f"{search_url}{encoded_query}"
        
        return f"{url}&{affiliate_param}" if affiliate_param else url
    
    async def search_product(
        self, 
        query: str, 
        stores: Optional[List[Store]] = None,
        category: Optional[str] = None
    ) -> Dict[str, List[StoreProduct]]:

        if stores is None:
            stores = [Store.DNS, Store.CITILINK, Store.REGARD]
        

        cache_key = f"store_search_{hashlib.md5(f'{query}_{stores}'.encode()).hexdigest()}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        results = {}
        tasks = []
        
        for store in stores:
            tasks.append(self._search_in_store(store, query, category))
        
        store_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for store, result in zip(stores, store_results):
            if isinstance(result, Exception):
                logger.error(f"Error searching in {store.value}: {result}")
                results[store.value] = []
            else:
                results[store.value] = result
        

        cache.set(cache_key, results, 900)
        
        return results
    
    async def _search_in_store(
        self, 
        store: Store, 
        query: str, 
        category: Optional[str]
    ) -> List[StoreProduct]:

        
        search_url = self.generate_search_url(store, query, category)
        

        products = []
        

        demo_product = StoreProduct(
            store=store.value,
            product_id=f"{store.value}_{hashlib.md5(query.encode()).hexdigest()[:8]}",
            name=query,
            price=self._estimate_price(query, store),
            original_price=None,
            url=search_url,
            affiliate_url=self.generate_affiliate_url(store, search_url),
            in_stock=True,
            stock_quantity=None,
            delivery_days=self._estimate_delivery(store),
            rating=None,
            reviews_count=None,
            image_url=None,
            last_updated=datetime.now()
        )
        products.append(demo_product)
        
        return products
    
    def _estimate_price(self, query: str, store: Store) -> float:
        """Оценка цены (для демо)"""

        base_prices = {
            'rtx 4090': 180000,
            'rtx 4080': 120000,
            'rtx 4070': 70000,
            'rtx 4060': 40000,
            'ryzen 9 7950x': 55000,
            'ryzen 7 7800x3d': 40000,
            'ryzen 5 7600x': 20000,
            'core i9-14900k': 60000,
            'core i7-14700k': 40000,
            'core i5-14600k': 28000,
        }
        
        query_lower = query.lower()
        for key, price in base_prices.items():
            if key in query_lower:

                multiplier = 1 + (hash(store.value) % 10 - 5) / 100
                return round(price * multiplier, -2)
        
        return 10000  
    
    def _estimate_delivery(self, store: Store) -> int:

        delivery_days = {
            Store.DNS: 1,
            Store.CITILINK: 1,
            Store.REGARD: 2,
            Store.MVIDEO: 2,
        }
        return delivery_days.get(store, 3)
    
    async def check_availability(
        self, 
        product_name: str,
        stores: Optional[List[Store]] = None
    ) -> Dict[str, Dict]:

        if stores is None:
            stores = list(Store)
        
        results = {}
        
        for store in stores:
            config = self.AFFILIATE_CONFIG.get(store, {})
            search_url = self.generate_search_url(store, product_name)
            
            results[store.value] = {
                'store_name': store.value.upper(),
                'search_url': search_url,
                'affiliate_url': self.generate_affiliate_url(store, search_url),
                'estimated_available': True,  # В реальности - проверка через API
                'last_checked': datetime.now().isoformat(),
            }
        
        return results
    
    def get_component_store_links(self, component: Any) -> Dict[str, str]:

        if not component or not hasattr(component, 'name'):
            return {}
        
        links = {}
        for store in [Store.DNS, Store.CITILINK, Store.REGARD, Store.MVIDEO]:
            search_url = self.generate_search_url(store, component.name)
            links[store.value] = self.generate_affiliate_url(store, search_url)
        
        return links
    
    def get_configuration_store_links(self, configuration) -> Dict[str, Dict[str, str]]:

        components = {
            'cpu': getattr(configuration, 'cpu', None),
            'gpu': getattr(configuration, 'gpu', None),
            'motherboard': getattr(configuration, 'motherboard', None),
            'ram': getattr(configuration, 'ram', None),
            'storage_primary': getattr(configuration, 'storage_primary', None),
            'psu': getattr(configuration, 'psu', None),
            'case': getattr(configuration, 'case', None),
            'cooling': getattr(configuration, 'cooling', None),
        }
        
        result = {}
        for comp_type, component in components.items():
            if component:
                result[comp_type] = {
                    'name': component.name,
                    'stores': self.get_component_store_links(component)
                }
        
        return result


class PriceHistoryService:

    
    def __init__(self):
        self.store_service = StoreIntegrationService()
    
    def get_price_history(
        self, 
        component_name: str,
        days: int = 30
    ) -> List[PriceHistoryPoint]:

        from datetime import date
        import random
        
        history = []
        base_price = self.store_service._estimate_price(component_name, Store.DNS)
        
        for i in range(days, -1, -1):
            point_date = datetime.now() - timedelta(days=i)
            
            variation = random.uniform(-0.1, 0.1)
            price = base_price * (1 + variation)
            

            price *= (1 - i * 0.001)
            
            history.append(PriceHistoryPoint(
                date=point_date,
                price=round(price, -2),
                store=Store.DNS.value,
                in_stock=random.random() > 0.1  
            ))
        
        return history
    
    def get_price_chart_data(
        self, 
        component_name: str,
        days: int = 30
    ) -> Dict:

        history = self.get_price_history(component_name, days)
        
        if not history:
            return {'data': [], 'stats': {}}
        
        prices = [p.price for p in history]
        
        return {
            'data': [p.to_dict() for p in history],
            'stats': {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': sum(prices) / len(prices),
                'current_price': prices[-1] if prices else 0,
                'price_change_30d': ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] > 0 else 0,
                'best_time_to_buy': min(prices) == prices[-1],
            }
        }
    
    def get_price_alerts(
        self,
        component_name: str,
        target_price: float
    ) -> Dict:

        history = self.get_price_history(component_name, 7)
        current_price = history[-1].price if history else 0
        
        return {
            'component': component_name,
            'target_price': target_price,
            'current_price': current_price,
            'target_reached': current_price <= target_price,
            'difference': current_price - target_price,
            'difference_percent': ((current_price - target_price) / target_price * 100) if target_price > 0 else 0,
        }



def get_store_links_for_component(component) -> Dict[str, str]:

    service = StoreIntegrationService()
    return service.get_component_store_links(component)


def get_store_links_for_configuration(configuration) -> Dict:
    
    service = StoreIntegrationService()
    return service.get_configuration_store_links(configuration)


def get_price_history_data(component_name: str, days: int = 30) -> Dict:

    service = PriceHistoryService()
    return service.get_price_chart_data(component_name, days)
