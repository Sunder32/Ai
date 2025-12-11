"""
Сервис чата с AI для уточнения требований и объяснения выбора компонентов.
"""
import logging
import requests
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)

# Конфигурация AI сервера
AI_SERVER_URL = os.environ.get('AI_SERVER_URL', 'http://localhost:5050')
OLLAMA_API_URL = os.environ.get('OLLAMA_API_URL', 'http://localhost:11434/api/generate')


class ChatSession(models.Model):
    """Сессия чата с AI"""
    
    user_id = models.IntegerField(db_index=True)
    session_id = models.CharField(max_length=64, unique=True)
    
    # Контекст сессии
    configuration_id = models.IntegerField(null=True)
    context_data = models.JSONField(default=dict)
    
    # История сообщений хранится в ChatMessage
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'recommendations'
        verbose_name = 'Сессия чата'
        verbose_name_plural = 'Сессии чата'
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    """Сообщение в чате"""
    
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'AI Ассистент'),
        ('system', 'Системное'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # Метаданные
    tokens_used = models.IntegerField(null=True)
    response_time_ms = models.IntegerField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'recommendations'
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'
        ordering = ['created_at']


class AIChatService:
    """
    Сервис чата с AI для:
    - Уточнения требований пользователя
    - Объяснения выбора компонентов
    - Помощь в оптимизации бюджета
    """
    
    # Системный промпт для чата
    SYSTEM_PROMPT = """Ты - эксперт по сборке компьютеров и периферии. 
Твоя задача - помочь пользователю подобрать оптимальную конфигурацию ПК.

Правила:
1. Отвечай кратко и по делу
2. Если спрашивают "почему выбрал X" - объясни преимущества и альтернативы
3. Если просят "дешевле" - предложи конкретные варианты экономии
4. Всегда учитывай совместимость компонентов
5. Называй конкретные модели и цены если знаешь
6. Отвечай на русском языке

Текущий контекст пользователя:
{context}
"""
    
    def __init__(self, user=None):
        self.user = user
        self.session = None
    
    def create_session(self, configuration_id: int = None) -> str:
        """Создать новую сессию чата"""
        import secrets
        
        session_id = secrets.token_urlsafe(32)
        
        context = {}
        if configuration_id:
            context['configuration_id'] = configuration_id
            # Загружаем данные конфигурации
            context['configuration'] = self._load_configuration_context(configuration_id)
        
        self.session = ChatSession.objects.create(
            user_id=self.user.id if self.user else 0,
            session_id=session_id,
            configuration_id=configuration_id,
            context_data=context
        )
        
        return session_id
    
    def _load_configuration_context(self, config_id: int) -> Dict:
        """Загрузить контекст конфигурации"""
        from .models import PCConfiguration
        
        try:
            config = PCConfiguration.objects.select_related(
                'cpu', 'gpu', 'motherboard', 'ram', 'storage_primary', 'psu', 'case', 'cooling'
            ).get(id=config_id)
            
            return {
                'name': config.name,
                'total_price': float(config.total_price) if config.total_price else 0,
                'components': {
                    'cpu': str(config.cpu) if config.cpu else None,
                    'gpu': str(config.gpu) if config.gpu else None,
                    'motherboard': str(config.motherboard) if config.motherboard else None,
                    'ram': str(config.ram) if config.ram else None,
                    'storage': str(config.storage_primary) if config.storage_primary else None,
                    'psu': str(config.psu) if config.psu else None,
                    'case': str(config.case) if config.case else None,
                    'cooling': str(config.cooling) if config.cooling else None,
                }
            }
        except PCConfiguration.DoesNotExist:
            return {}
    
    def get_or_create_session(self, session_id: str = None) -> ChatSession:
        """Получить или создать сессию"""
        if session_id:
            try:
                self.session = ChatSession.objects.get(
                    session_id=session_id,
                    user_id=self.user.id if self.user else 0
                )
                return self.session
            except ChatSession.DoesNotExist:
                pass
        
        self.create_session()
        return self.session
    
    def send_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """
        Отправить сообщение в чат и получить ответ AI.
        """
        import time
        
        # Получаем сессию
        session = self.get_or_create_session(session_id)
        
        # Сохраняем сообщение пользователя
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=message
        )
        
        # Формируем контекст
        context = self._build_context(session)
        
        # Формируем промпт
        system_prompt = self.SYSTEM_PROMPT.format(context=json.dumps(context, ensure_ascii=False, indent=2))
        
        # Получаем историю сообщений
        history = self._get_chat_history(session)
        
        # Отправляем запрос к AI
        start_time = time.time()
        
        try:
            response_text = self._call_ai(system_prompt, history, message)
            response_time = int((time.time() - start_time) * 1000)
            
            # Сохраняем ответ
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=response_text,
                response_time_ms=response_time
            )
            
            session.save()  # Обновляем updated_at
            
            return {
                'session_id': session.session_id,
                'response': response_text,
                'response_time_ms': response_time
            }
            
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            
            # Fallback ответ
            fallback = self._get_fallback_response(message)
            
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=fallback
            )
            
            return {
                'session_id': session.session_id,
                'response': fallback,
                'error': str(e)
            }
    
    def _build_context(self, session: ChatSession) -> Dict:
        """Построить контекст для AI"""
        context = session.context_data.copy()
        
        # Добавляем информацию о пользователе
        if self.user:
            context['user'] = {
                'username': self.user.username,
                'user_type': getattr(self.user, 'user_type', 'student')
            }
        
        return context
    
    def _get_chat_history(self, session: ChatSession, limit: int = 10) -> List[Dict]:
        """Получить историю чата"""
        messages = session.messages.order_by('-created_at')[:limit]
        return [
            {'role': m.role, 'content': m.content}
            for m in reversed(messages)
        ]
    
    def _call_ai(self, system_prompt: str, history: List[Dict], user_message: str) -> str:
        """Вызов AI сервера"""
        
        # Формируем полный промпт с историей
        full_prompt = f"{system_prompt}\n\n"
        
        for msg in history[-6:]:  # Последние 6 сообщений
            role = "Пользователь" if msg['role'] == 'user' else "Ассистент"
            full_prompt += f"{role}: {msg['content']}\n"
        
        full_prompt += f"\nПользователь: {user_message}\nАссистент:"
        
        # Пробуем FastAPI сервер
        try:
            response = requests.post(
                f"{AI_SERVER_URL}/api/chat",
                json={
                    "prompt": full_prompt,
                    "use_learning": True
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', 'Извините, не удалось получить ответ.')
        except requests.exceptions.RequestException:
            pass
        
        # Fallback на прямой Ollama
        try:
            response = requests.post(
                OLLAMA_API_URL,
                json={
                    "model": "deepseek-project-model:latest",
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', 'Извините, не удалось получить ответ.')
        except requests.exceptions.RequestException as e:
            raise Exception(f"AI service unavailable: {e}")
        
        raise Exception("All AI services unavailable")
    
    def _get_fallback_response(self, message: str) -> str:
        """Fallback ответ если AI недоступен"""
        message_lower = message.lower()
        
        if 'почему' in message_lower and ('gpu' in message_lower or 'видеокарт' in message_lower):
            return """При выборе видеокарты я учитывал:
1. Ваш бюджет и приоритеты
2. Соотношение цена/производительность
3. Совместимость с другими компонентами
4. Энергопотребление и требования к БП

Хотите узнать об альтернативных вариантах?"""
        
        if 'почему' in message_lower and ('cpu' in message_lower or 'процессор' in message_lower):
            return """При выборе процессора я учитывал:
1. Совместимость с материнской платой (сокет)
2. Количество ядер/потоков для ваших задач
3. Баланс производительности и цены
4. TDP и требования к охлаждению

Нужны альтернативы или детали?"""
        
        if 'дешевле' in message_lower or 'экономи' in message_lower or 'бюджет' in message_lower:
            return """Для экономии бюджета можно:
1. Выбрать процессор предыдущего поколения
2. Взять видеокарту с меньшим объёмом памяти
3. Уменьшить объём SSD и добавить HDD
4. Выбрать корпус попроще

Какой компонент хотите оптимизировать?"""
        
        if 'совместим' in message_lower:
            return """Я проверяю совместимость по следующим критериям:
1. Сокет CPU и материнской платы
2. Тип памяти (DDR4/DDR5)
3. Форм-фактор корпуса и платы
4. Мощность блока питания
5. Размеры видеокарты и корпуса

Есть конкретные опасения?"""
        
        return """Я готов помочь с вашим вопросом о сборке ПК.
Вы можете спросить:
- "Почему ты выбрал эту видеокарту?"
- "Можно ли сделать дешевле?"
- "Совместимы ли эти компоненты?"
- "Какие альтернативы есть?"

Чем могу помочь?"""
    
    def explain_component_choice(self, component_type: str, component_id: int, configuration_id: int = None) -> str:
        """
        Объяснить выбор конкретного компонента.
        """
        from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
        
        model_map = {
            'cpu': CPU, 'gpu': GPU, 'motherboard': Motherboard,
            'ram': RAM, 'storage': Storage, 'psu': PSU,
            'case': Case, 'cooling': Cooling
        }
        
        model = model_map.get(component_type)
        if not model:
            return "Неизвестный тип компонента"
        
        try:
            component = model.objects.get(id=component_id)
        except model.DoesNotExist:
            return "Компонент не найден"
        
        # Формируем объяснение
        prompt = f"""Объясни почему {component_type} "{component}" - хороший выбор для сборки ПК.
Укажи:
1. Основные преимущества
2. Для каких задач подходит
3. Возможные альтернативы в этой ценовой категории

Ответ на русском, кратко (3-4 предложения)."""
        
        try:
            response = requests.post(
                f"{AI_SERVER_URL}/api/chat",
                json={"prompt": prompt, "use_learning": True},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', self._get_component_fallback(component_type, component))
        except:
            pass
        
        return self._get_component_fallback(component_type, component)
    
    def _get_component_fallback(self, component_type: str, component) -> str:
        """Fallback объяснение для компонента"""
        explanations = {
            'cpu': f"{component} - отличный процессор с {component.cores} ядрами и частотой до {component.boost_clock}ГГц. Подходит для {component.cores >= 8 and 'многозадачности и тяжёлых приложений' or 'повседневных задач и игр'}.",
            'gpu': f"{component} с {component.memory}ГБ видеопамяти {component.memory_type}. {component.performance_score > 15000 and 'Топовый выбор для 4K гейминга' or 'Хороший баланс цены и производительности'}.",
            'ram': f"{component} - {component.capacity}ГБ памяти {component.memory_type} на частоте {component.speed}МГц. {component.capacity >= 32 and 'Идеально для продакшена и стриминга' or 'Достаточно для большинства задач'}.",
        }
        
        return explanations.get(component_type, f"{component} - качественный выбор в своей категории.")
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Получить историю чата"""
        try:
            session = ChatSession.objects.get(
                session_id=session_id,
                user_id=self.user.id if self.user else 0
            )
            
            messages = session.messages.all()
            return [
                {
                    'role': m.role,
                    'content': m.content,
                    'created_at': m.created_at.isoformat()
                }
                for m in messages
            ]
        except ChatSession.DoesNotExist:
            return []
