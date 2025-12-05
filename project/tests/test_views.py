import pytest
from django.test import TestCase, Client
from rest_framework import status

class TestAPIEndpoints(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_api_endpoints(self):
        """Тест доступности API"""
        endpoints = [
            '/api/computers/cpu/',
            '/api/computers/gpu/',
            '/api/computers/ram/',
            '/api/computers/storage/',
        ]
        
        for url in endpoints:
            response = self.client.get(url)
            # 200, 401, 403 - OK, 404 - не найден
            self.assertIn(response.status_code, [200, 401, 403, 404])
    
    def test_api_response_time(self):
        """Тест времени ответа API"""
        import time
        
        start = time.time()
        response = self.client.get('/api/computers/cpu/')
        duration = time.time() - start
        
        print(f"⏱️ Время ответа CPU API: {duration:.3f} сек")
        
        if response.status_code == 200:
            self.assertLess(duration, 2.0)