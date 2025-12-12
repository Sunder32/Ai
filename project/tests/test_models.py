import pytest
import time
from django.test import TestCase
from accounts.models import User  

class TestBasicModels(TestCase):
    def test_user_creation(self):

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        print("✅ Пользователь создан успешно")
    
    def test_database_connection(self):

        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)
        print("✅ Подключение к базе данных работает")
    
    def test_bulk_create_performance(self):

        start = time.time()
        
        users = []
        for i in range(50):
            users.append(User(
                username=f'user{i}',
                email=f'user{i}@example.com'
            ))
        
        User.objects.bulk_create(users, ignore_conflicts=True)
        duration = time.time() - start
        
        print(f"⏱️ Создано 50 пользователей за {duration:.2f} секунд")
        self.assertLess(duration, 5.0)
        print(f"📊 Всего пользователей в базе: {User.objects.count()}")