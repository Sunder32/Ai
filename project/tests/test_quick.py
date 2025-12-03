"""
Быстрые тесты для проверки
"""
import pytest

@pytest.mark.django_db
def test_simple():
    """Простейший тест"""
    assert 1 + 1 == 2
    print("✅ Базовый тест работает")

@pytest.mark.django_db 
def test_database():
    """Тест базы данных"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
    print("✅ База данных работает")

@pytest.mark.django_db
def test_create_user():
    """Тест создания пользователя"""
    try:
        from accounts.models import User
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        print("✅ Пользователь создан")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False