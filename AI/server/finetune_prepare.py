"""
Fine-tuning Data Preparation
Подготовка данных для fine-tuning модели
"""

import os
import json
from typing import List, Dict, Optional


def prepare_chat_format(data: List[Dict], output_path: str) -> str:
    """
    Конвертировать данные в формат для fine-tuning (chat format)
    Поддерживает форматы: Alpaca, ShareGPT, OpenAI
    """
    
    # Определяем тип данных
    if not data:
        raise ValueError("Пустой датасет")
    
    sample = data[0]
    
    # Если это классификация (text + label)
    if "text" in sample and "label" in sample:
        return _prepare_classification_data(data, output_path)
    
    # Если это Q&A (question + answer или input + output)
    elif ("question" in sample and "answer" in sample) or \
         ("input" in sample and "output" in sample) or \
         ("instruction" in sample):
        return _prepare_qa_data(data, output_path)
    
    # Если это диалоги (messages или conversations)
    elif "messages" in sample or "conversations" in sample:
        return _prepare_conversation_data(data, output_path)
    
    else:
        raise ValueError(f"Неизвестный формат данных. Ключи: {list(sample.keys())}")


def _prepare_classification_data(data: List[Dict], output_path: str) -> str:
    """Подготовка данных классификации для fine-tuning"""
    
    # Собираем уникальные лейблы
    labels = list(set(item.get("label", "") for item in data))
    labels_str = ", ".join(labels)
    
    # Конвертируем в chat format
    formatted = []
    for item in data:
        text = item.get("text", "")
        label = item.get("label", "")
        
        formatted.append({
            "messages": [
                {
                    "role": "system",
                    "content": f"Ты эксперт по классификации текстов. Классифицируй текст в одну из категорий: {labels_str}. Отвечай только названием категории."
                },
                {
                    "role": "user",
                    "content": f"Классифицируй этот текст:\n\n{text}"
                },
                {
                    "role": "assistant",
                    "content": label
                }
            ]
        })
    
    # Сохраняем в JSONL формате (стандарт для fine-tuning)
    jsonl_path = output_path.replace(".json", "_finetune.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in formatted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    # Также создаем Alpaca format (для LLaMA-Factory и подобных)
    alpaca_data = []
    for item in data:
        alpaca_data.append({
            "instruction": f"Классифицируй этот отзыв как {labels_str}",
            "input": item.get("text", ""),
            "output": item.get("label", "")
        })
    
    alpaca_path = output_path.replace(".json", "_alpaca.json")
    with open(alpaca_path, "w", encoding="utf-8") as f:
        json.dump(alpaca_data, f, ensure_ascii=False, indent=2)
    
    return jsonl_path


def _prepare_qa_data(data: List[Dict], output_path: str) -> str:
    """Подготовка Q&A данных для fine-tuning"""
    
    formatted = []
    for item in data:
        # Поддержка разных форматов
        instruction = item.get("instruction", item.get("question", ""))
        input_text = item.get("input", "")
        output_text = item.get("output", item.get("answer", ""))
        
        user_content = instruction
        if input_text:
            user_content += f"\n\n{input_text}"
        
        formatted.append({
            "messages": [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": output_text}
            ]
        })
    
    jsonl_path = output_path.replace(".json", "_finetune.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in formatted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    return jsonl_path


def _prepare_conversation_data(data: List[Dict], output_path: str) -> str:
    """Подготовка диалоговых данных"""
    
    formatted = []
    for item in data:
        messages = item.get("messages", item.get("conversations", []))
        
        # Нормализуем формат сообщений
        normalized = []
        for msg in messages:
            role = msg.get("role", msg.get("from", "user"))
            content = msg.get("content", msg.get("value", ""))
            
            # Приводим роли к стандарту
            if role in ["human", "user"]:
                role = "user"
            elif role in ["gpt", "assistant", "bot"]:
                role = "assistant"
            
            normalized.append({"role": role, "content": content})
        
        if normalized:
            formatted.append({"messages": normalized})
    
    jsonl_path = output_path.replace(".json", "_finetune.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in formatted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    return jsonl_path


def create_ollama_training_modelfile(
    base_model: str = "deepseek-r1:8b",
    dataset_path: str = None,
    output_path: str = "Modelfile.train"
) -> str:
    """
    Создать Modelfile с примерами из датасета (few-shot learning)
    Ollama не поддерживает настоящий fine-tuning, но можно добавить примеры в промпт
    """
    
    examples = []
    if dataset_path and os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Берём до 10 примеров каждого класса
        from collections import defaultdict
        by_label = defaultdict(list)
        for item in data:
            label = item.get("label", "unknown")
            if len(by_label[label]) < 5:
                by_label[label].append(item)
        
        for label, items in by_label.items():
            for item in items:
                examples.append(f"Текст: {item['text']}\nКатегория: {label}")
    
    examples_text = "\n\n".join(examples[:15])  # Максимум 15 примеров
    
    modelfile_content = f'''FROM {base_model}
PARAMETER temperature 0.3
PARAMETER top_p 0.9

SYSTEM """Ты эксперт по классификации текстов на русском языке.

Твоя задача - классифицировать отзывы в категории: positive, negative, neutral.

Вот примеры правильной классификации:

{examples_text}

Отвечай ТОЛЬКО названием категории: positive, negative или neutral."""
'''
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(modelfile_content)
    
    return output_path


def get_dataset_info(file_path: str) -> dict:
    """Получить информацию о датасете"""
    
    if not os.path.exists(file_path):
        return {"error": "Файл не найден"}
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not data:
        return {"error": "Пустой датасет"}
    
    sample = data[0]
    
    # Статистика по лейблам
    labels = {}
    if "label" in sample:
        for item in data:
            label = item.get("label", "unknown")
            labels[label] = labels.get(label, 0) + 1
    
    return {
        "total_samples": len(data),
        "fields": list(sample.keys()),
        "labels_distribution": labels,
        "sample": sample
    }
