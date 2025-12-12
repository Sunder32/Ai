import pytest
import time
import psutil
import os
from django.test import TestCase
from concurrent.futures import ThreadPoolExecutor

class PerformanceTests(TestCase):
    def setUp(self):
        from django.test import Client
        self.client = Client()
    
    def test_memory_usage(self):

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024
        

        for _ in range(20):
            self.client.get('/api/computers/cpu/')
        
        mem_after = process.memory_info().rss / 1024 / 1024
        increase = mem_after - mem_before
        
        print(f"🧠 Память: было {mem_before:.1f}MB, стало {mem_after:.1f}MB (+{increase:.1f}MB)")
        self.assertLess(increase, 50)
    
    def test_concurrent_requests(self):

        def make_request():
            from django.test import Client
            client = Client()
            return client.get('/api/computers/cpu/')
        
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        total_time = time.time() - start
        success = sum(1 for r in results if r.status_code in [200, 401, 403])
        
        print(f"⚡ 10 конкурентных запросов: {success}/10 успешно, {total_time:.2f} сек")
        self.assertGreaterEqual(success, 8)