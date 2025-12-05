"""
Learning Engine - Самообучение на основе обратной связи пользователей
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

LEARNING_DIR = os.path.join(os.path.dirname(__file__), "..", "learning_data")
CORRECTIONS_FILE = os.path.join(LEARNING_DIR, "corrections.jsonl")
GOOD_RESPONSES_FILE = os.path.join(LEARNING_DIR, "good_responses.jsonl")
LEARNING_CONTEXT_FILE = os.path.join(LEARNING_DIR, "learning_context.json")

os.makedirs(LEARNING_DIR, exist_ok=True)


class LearningEngine:
    """Движок самообучения на основе обратной связи"""
    
    def __init__(self):
        self.corrections: List[Dict] = []
        self.good_responses: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        """Загрузить данные обучения"""
        # Загружаем исправления
        if os.path.exists(CORRECTIONS_FILE):
            try:
                with open(CORRECTIONS_FILE, 'r', encoding='utf-8') as f:
                    self.corrections = [json.loads(line) for line in f if line.strip()]
            except:
                self.corrections = []
        
        # Загружаем хорошие ответы
        if os.path.exists(GOOD_RESPONSES_FILE):
            try:
                with open(GOOD_RESPONSES_FILE, 'r', encoding='utf-8') as f:
                    self.good_responses = [json.loads(line) for line in f if line.strip()]
            except:
                self.good_responses = []
    
    def add_correction(self, prompt: str, original_response: str, corrected_response: str, 
                       feedback: str = "") -> dict:
        """
        Добавить исправление от пользователя
        Это учит ИИ не повторять ошибки
        """
        correction = {
            "id": f"corr_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "original_response": original_response,
            "corrected_response": corrected_response,
            "feedback": feedback
        }
        
        self.corrections.append(correction)
        
        # Сохраняем
        with open(CORRECTIONS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(correction, ensure_ascii=False) + "\n")
        
        # Обновляем контекст обучения
        self._update_learning_context()
        
        return correction
    
    def add_good_response(self, prompt: str, response: str) -> dict:
        """
        Пометить ответ как хороший (лайк)
        Это усиливает подобные ответы
        """
        good = {
            "id": f"good_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response
        }
        
        self.good_responses.append(good)
        
        with open(GOOD_RESPONSES_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(good, ensure_ascii=False) + "\n")
        
        self._update_learning_context()
        
        return good
    
    def get_learning_context(self, max_examples: int = 10) -> str:
        """
        Получить контекст обучения для добавления в промпт
        Включает примеры исправлений и хороших ответов
        """
        context_parts = []
        
        # Добавляем последние исправления
        if self.corrections:
            context_parts.append("=== ВАЖНО: Учти эти исправления от пользователя ===")
            for corr in self.corrections[-max_examples:]:
                context_parts.append(f"""
Вопрос: {corr['prompt'][:200]}
❌ Неправильный ответ: {corr['original_response'][:300]}
✅ Правильный ответ: {corr['corrected_response'][:300]}
{f"Комментарий: {corr['feedback']}" if corr.get('feedback') else ""}
""")
        
        # Добавляем примеры хороших ответов
        if self.good_responses:
            context_parts.append("\n=== Примеры хороших ответов (делай так же) ===")
            for good in self.good_responses[-max_examples//2:]:
                context_parts.append(f"""
Вопрос: {good['prompt'][:200]}
Хороший ответ: {good['response'][:400]}
""")
        
        return "\n".join(context_parts)
    
    def _update_learning_context(self):
        """Обновить файл контекста обучения"""
        context = {
            "last_updated": datetime.now().isoformat(),
            "total_corrections": len(self.corrections),
            "total_good_responses": len(self.good_responses),
            "learning_context": self.get_learning_context()
        }
        
        with open(LEARNING_CONTEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
    
    def get_stats(self) -> dict:
        """Статистика обучения"""
        return {
            "corrections_count": len(self.corrections),
            "good_responses_count": len(self.good_responses),
            "total_examples": len(self.corrections) + len(self.good_responses),
            "last_correction": self.corrections[-1] if self.corrections else None,
            "last_good": self.good_responses[-1] if self.good_responses else None
        }
    
    def export_training_data(self) -> str:
        """
        Экспортировать данные для fine-tuning
        Формат: JSONL с исправлениями
        """
        export_file = os.path.join(LEARNING_DIR, "training_export.jsonl")
        
        with open(export_file, 'w', encoding='utf-8') as f:
            # Экспортируем исправления как обучающие примеры
            for corr in self.corrections:
                item = {
                    "messages": [
                        {"role": "user", "content": corr['prompt']},
                        {"role": "assistant", "content": corr['corrected_response']}
                    ]
                }
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
            # Экспортируем хорошие ответы
            for good in self.good_responses:
                item = {
                    "messages": [
                        {"role": "user", "content": good['prompt']},
                        {"role": "assistant", "content": good['response']}
                    ]
                }
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        return export_file


# Singleton
_learning_engine = None

def get_learning_engine() -> LearningEngine:
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine()
    return _learning_engine
