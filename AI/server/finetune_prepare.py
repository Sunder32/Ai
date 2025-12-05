"""
Fine-tuning Data Preparation
Подготовка данных для fine-tuning модели
"""

import os
import json
import re
from typing import List, Dict, Optional, Union


def prepare_chat_format(data: Union[List[Dict], str], output_path: str) -> str:
    """
    Конвертировать данные в формат для fine-tuning (chat format)
    Поддерживает форматы: Alpaca, ShareGPT, OpenAI, Product Catalog, TXT
    """
    
    # Если это строка (текст из txt файла)
    if isinstance(data, str):
        return _prepare_text_data(data, output_path)
    
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
    
    # Если это каталог продуктов (category, model, price и т.п.)
    elif "category" in sample and ("model" in sample or "name" in sample):
        return _prepare_product_catalog_data(data, output_path)
    
    # Если есть поля description/specs - пробуем как продуктовые данные
    elif "description" in sample or "specs" in sample:
        return _prepare_product_catalog_data(data, output_path)
    
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


def _prepare_product_catalog_data(data: List[Dict], output_path: str) -> str:
    """Подготовка данных каталога продуктов для fine-tuning"""
    
    formatted = []
    
    # Группируем по категориям для более разнообразных вопросов
    from collections import defaultdict
    by_category = defaultdict(list)
    for item in data:
        category = item.get("category", "Товар")
        by_category[category].append(item)
    
    for item in data:
        category = item.get("category", "Товар")
        manufacturer = item.get("manufacturer", item.get("brand", ""))
        model = item.get("model", item.get("name", ""))
        price = item.get("price_rub", item.get("price", ""))
        specs = item.get("specs", item.get("specifications", ""))
        description = item.get("description", "")
        
        # Создаём несколько вариантов вопросов-ответов
        product_name = f"{manufacturer} {model}".strip()
        
        # Вопрос о характеристиках
        if specs:
            formatted.append({
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Какие характеристики у {product_name}?"
                    },
                    {
                        "role": "assistant", 
                        "content": f"{product_name} ({category}): {specs}. {description}"
                    }
                ]
            })
        
        # Вопрос о цене
        if price:
            formatted.append({
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Сколько стоит {product_name}?"
                    },
                    {
                        "role": "assistant", 
                        "content": f"{product_name} стоит {price} рублей. {description}"
                    }
                ]
            })
        
        # Общий вопрос о продукте
        full_info = f"{product_name}"
        if category:
            full_info = f"{category}: {full_info}"
        if price:
            full_info += f", цена: {price} руб."
        if specs:
            full_info += f" Характеристики: {specs}."
        if description:
            full_info += f" {description}"
            
        formatted.append({
            "messages": [
                {
                    "role": "user", 
                    "content": f"Расскажи про {product_name}"
                },
                {
                    "role": "assistant", 
                    "content": full_info
                }
            ]
        })
    
    # Добавляем вопросы по категориям
    for category, items in by_category.items():
        if len(items) >= 2:
            items_list = ", ".join([
                f"{item.get('manufacturer', '')} {item.get('model', item.get('name', ''))}".strip()
                for item in items[:10]
            ])
            formatted.append({
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Какие {category} есть в наличии?"
                    },
                    {
                        "role": "assistant", 
                        "content": f"В категории {category} доступны: {items_list}."
                    }
                ]
            })
    
    jsonl_path = output_path.replace(".json", "_finetune.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in formatted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    # Также создаем Alpaca format
    alpaca_data = []
    for item in data:
        product_name = f"{item.get('manufacturer', '')} {item.get('model', item.get('name', ''))}".strip()
        full_info = f"Категория: {item.get('category', 'Товар')}"
        if item.get('price_rub') or item.get('price'):
            full_info += f", Цена: {item.get('price_rub', item.get('price'))} руб."
        if item.get('specs'):
            full_info += f", Характеристики: {item.get('specs')}"
        if item.get('description'):
            full_info += f", {item.get('description')}"
            
        alpaca_data.append({
            "instruction": f"Предоставь информацию о товаре {product_name}",
            "input": "",
            "output": full_info
        })
    
    alpaca_path = output_path.replace(".json", "_alpaca.json")
    with open(alpaca_path, "w", encoding="utf-8") as f:
        json.dump(alpaca_data, f, ensure_ascii=False, indent=2)
    
    print(f"[FINETUNE] Обработано {len(data)} товаров, создано {len(formatted)} примеров")
    
    return jsonl_path


def _prepare_text_data(text: str, output_path: str) -> str:
    """Подготовка текстовых данных из TXT файла для fine-tuning"""
    
    formatted = []
    
    # Разбиваем текст на строки и обрабатываем
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    # Пробуем парсить как список товаров (формат: "Название — описание цена")
    product_pattern = re.compile(r'^(.+?)\s*[—–-]\s*(.+?)\s+([\d.,]+)\s*р\.?$', re.IGNORECASE)
    
    products = []
    other_lines = []
    
    for line in lines:
        match = product_pattern.match(line)
        if match:
            name, description, price = match.groups()
            products.append({
                "name": name.strip(),
                "description": description.strip(),
                "price": price.replace(',', '').replace('.', '')
            })
        else:
            other_lines.append(line)
    
    # Если нашли товары - создаём Q&A по ним
    if products:
        for product in products:
            # Вопрос о цене
            formatted.append({
                "messages": [
                    {"role": "user", "content": f"Сколько стоит {product['name']}?"},
                    {"role": "assistant", "content": f"{product['name']} стоит {product['price']} рублей. {product['description']}"}
                ]
            })
            
            # Вопрос о характеристиках
            formatted.append({
                "messages": [
                    {"role": "user", "content": f"Расскажи про {product['name']}"},
                    {"role": "assistant", "content": f"{product['name']} — {product['description']}. Цена: {product['price']} руб."}
                ]
            })
    
    # Если есть другие строки - обрабатываем как обычный текст
    if other_lines and not products:
        # Разбиваем на чанки для обучения
        chunk_size = 500
        full_text = "\n".join(other_lines)
        
        for i in range(0, len(full_text), chunk_size):
            chunk = full_text[i:i+chunk_size]
            if len(chunk) > 50:  # Минимальная длина
                formatted.append({
                    "messages": [
                        {"role": "system", "content": "Используй эту информацию для ответов на вопросы."},
                        {"role": "user", "content": "Что ты знаешь об этом?"},
                        {"role": "assistant", "content": chunk}
                    ]
                })
    
    # Сохраняем результат
    jsonl_path = output_path.replace(".txt", "_finetune.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in formatted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"[FINETUNE] Обработан TXT файл: {len(products)} товаров, {len(formatted)} примеров")
    
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
        file_ext = os.path.splitext(dataset_path)[1].lower()
        
        if file_ext == '.txt':
            # Обработка текстового файла
            with open(dataset_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Парсим как товары
            lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
            product_pattern = re.compile(r'^(.+?)\s*[—–-]\s*(.+?)\s+([\d.,]+)\s*р\.?$', re.IGNORECASE)
            
            for line in lines[:15]:  # Максимум 15 примеров
                match = product_pattern.match(line)
                if match:
                    name, description, price = match.groups()
                    examples.append(f"Товар: {name.strip()}\nОписание: {description.strip()}\nЦена: {price} руб.")
                else:
                    examples.append(line)
        
        elif file_ext == '.json':
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, list) and data:
                sample = data[0]
                
                # Если это классификация
                if "text" in sample and "label" in sample:
                    from collections import defaultdict
                    by_label = defaultdict(list)
                    for item in data:
                        label = item.get("label", "unknown")
                        if len(by_label[label]) < 5:
                            by_label[label].append(item)
                    
                    for label, items in by_label.items():
                        for item in items:
                            examples.append(f"Текст: {item['text']}\nКатегория: {label}")
                
                # Если это каталог продуктов
                elif "category" in sample or "model" in sample or "manufacturer" in sample:
                    for item in data[:15]:
                        product_name = f"{item.get('manufacturer', '')} {item.get('model', item.get('name', ''))}".strip()
                        info = f"Товар: {product_name}"
                        if item.get('category'):
                            info += f"\nКатегория: {item['category']}"
                        if item.get('price_rub') or item.get('price'):
                            info += f"\nЦена: {item.get('price_rub', item.get('price'))} руб."
                        if item.get('specs'):
                            info += f"\nХарактеристики: {item['specs']}"
                        if item.get('description'):
                            info += f"\nОписание: {item['description']}"
                        examples.append(info)
    
    examples_text = "\n\n".join(examples[:15])  # Максимум 15 примеров
    
    # Определяем тип контента для system prompt
    if examples and ("Товар:" in examples[0] or "Категория:" in examples[0]):
        system_prompt = """Ты эксперт-консультант по компьютерной технике и периферии.

Ты знаешь следующие товары:

""" + examples_text + """

Отвечай на вопросы о товарах, ценах, характеристиках. Рекомендуй подходящие товары."""
    else:
        system_prompt = """Ты эксперт по классификации текстов на русском языке.

Твоя задача - классифицировать отзывы в категории: positive, negative, neutral.

Вот примеры правильной классификации:

""" + examples_text + """

Отвечай ТОЛЬКО названием категории: positive, negative или neutral."""
    
    modelfile_content = f'''FROM {base_model}
PARAMETER temperature 0.3
PARAMETER top_p 0.9

SYSTEM """{system_prompt}"""
'''
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(modelfile_content)
    
    return output_path


def get_dataset_info(file_path: str) -> dict:
    """Получить информацию о датасете (JSON или TXT)"""
    
    if not os.path.exists(file_path):
        return {"error": "Файл не найден"}
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Обработка TXT файлов
    if file_ext == '.txt':
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        # Пробуем парсить как товары
        product_pattern = re.compile(r'^(.+?)\s*[—–-]\s*(.+?)\s+([\d.,]+)\s*р\.?$', re.IGNORECASE)
        products = []
        for line in lines:
            match = product_pattern.match(line)
            if match:
                name, description, price = match.groups()
                products.append({
                    "name": name.strip(),
                    "description": description.strip(),
                    "price": price
                })
        
        if products:
            return {
                "total_samples": len(products),
                "fields": ["name", "description", "price"],
                "format": "products_txt",
                "labels_distribution": {},
                "sample": products[0] if products else None
            }
        else:
            return {
                "total_samples": len(lines),
                "fields": ["text"],
                "format": "text",
                "labels_distribution": {},
                "sample": {"text": lines[0][:100] + "..." if lines else ""}
            }
    
    # Обработка JSON файлов
    elif file_ext == '.json':
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not data:
            return {"error": "Пустой датасет"}
        
        if not isinstance(data, list):
            return {"error": "Датасет должен быть списком"}
        
        sample = data[0]
        
        # Определяем формат
        if "text" in sample and "label" in sample:
            format_type = "classification"
        elif "category" in sample or ("model" in sample and "manufacturer" in sample):
            format_type = "product_catalog"
        elif "instruction" in sample or "question" in sample:
            format_type = "qa"
        elif "messages" in sample or "conversations" in sample:
            format_type = "conversation"
        else:
            format_type = "unknown"
        
        # Статистика по лейблам
        labels = {}
        if "label" in sample:
            for item in data:
                label = item.get("label", "unknown")
                labels[label] = labels.get(label, 0) + 1
        
        # Статистика по категориям для продуктов
        if "category" in sample:
            for item in data:
                cat = item.get("category", "unknown")
                labels[cat] = labels.get(cat, 0) + 1
        
        return {
            "total_samples": len(data),
            "fields": list(sample.keys()),
            "format": format_type,
            "labels_distribution": labels,
            "sample": sample
        }
    
    elif file_ext == '.jsonl':
        lines = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    lines.append(json.loads(line))
        
        if not lines:
            return {"error": "Пустой датасет"}
        
        sample = lines[0]
        return {
            "total_samples": len(lines),
            "fields": list(sample.keys()) if isinstance(sample, dict) else ["data"],
            "format": "jsonl",
            "labels_distribution": {},
            "sample": sample
        }
    
    else:
        return {"error": f"Неподдерживаемый формат файла: {file_ext}"}
