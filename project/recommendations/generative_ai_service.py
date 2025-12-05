"""
Generative AI Service - создает компоненты с нуля используя AI
"""
import logging
import requests
import json
import re
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from typing import Optional, Dict, Any, List, Tuple
from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-project-model:latest"

# Валидационные константы
VALID_CPU_SOCKETS = ['LGA1700', 'LGA1200', 'LGA1151', 'AM5', 'AM4', 'sTRX4', 'TR4']
VALID_MEMORY_TYPES = ['DDR5', 'DDR4', 'DDR3']
VALID_GPU_MANUFACTURERS = ['NVIDIA', 'AMD', 'Intel']
VALID_CPU_MANUFACTURERS = ['Intel', 'AMD']

# Ценовые диапазоны для валидации (декабрь 2025, Россия)
PRICE_RANGES = {
    'cpu': (5000, 150000),
    'gpu': (10000, 350000),
    'motherboard': (5000, 80000),
    'ram': (3000, 50000),
    'storage': (2000, 50000),
    'psu': (3000, 40000),
    'case': (2000, 50000),
    'cooling': (1000, 30000),
}


class GenerativeAIService:
    """Сервис для генерации компонентов ПК с использованием AI"""
    
    def __init__(self, user_profile_data: dict):
        # Сохраняем все данные от пользователя
        self.user_data = user_profile_data
        
        # Базовые параметры
        self.user_type = user_profile_data.get('user_type', 'gamer')
        self.min_budget = Decimal(str(user_profile_data.get('min_budget', 50000)))
        self.max_budget = Decimal(str(user_profile_data.get('max_budget', 100000)))
        self.priority = user_profile_data.get('priority', 'performance')
        
        # Требования к использованию
        self.requirements = {
            'multitasking': user_profile_data.get('multitasking', False),
            'work_with_4k': user_profile_data.get('work_with_4k', False),
            'vr_support': user_profile_data.get('vr_support', False),
            'video_editing': user_profile_data.get('video_editing', False),
            'gaming': user_profile_data.get('gaming', False),
            'streaming': user_profile_data.get('streaming', False),
        }
        
        # Расширенные параметры PC
        self.pc_preferences = {
            'preferred_cpu_manufacturer': user_profile_data.get('preferred_cpu_manufacturer', 'any'),
            'preferred_gpu_manufacturer': user_profile_data.get('preferred_gpu_manufacturer', 'any'),
            'min_cpu_cores': user_profile_data.get('min_cpu_cores', 4),
            'min_gpu_vram': user_profile_data.get('min_gpu_vram', 4),
            'min_ram_capacity': user_profile_data.get('min_ram_capacity', 16),
            'storage_type_preference': user_profile_data.get('storage_type_preference', 'any'),
            'min_storage_capacity': user_profile_data.get('min_storage_capacity', 512),
            'cooling_preference': user_profile_data.get('cooling_preference', 'any'),
            'rgb_preference': user_profile_data.get('rgb_preference', False),
            'case_size_preference': user_profile_data.get('case_size_preference', 'any'),
            'overclocking_support': user_profile_data.get('overclocking_support', False),
        }
        
        # Существующие компоненты пользователя
        self.has_existing_components = user_profile_data.get('has_existing_components', False)
        self.existing_components_description = user_profile_data.get('existing_components_description', '')
        
        self.validation_warnings = []
    
    def _validate_component_spec(self, component_type: str, spec: dict) -> Tuple[bool, List[str]]:
        """
        Валидация спецификации компонента от AI
        Returns: (is_valid, list of warnings/errors)
        """
        errors = []
        warnings = []
        
        if not spec or not isinstance(spec, dict):
            return False, ["Пустая или некорректная спецификация"]
        
        # Проверка обязательных полей
        required_fields = {
            'cpu': ['name', 'manufacturer', 'socket', 'cores', 'threads', 'tdp', 'price'],
            'gpu': ['name', 'manufacturer', 'memory', 'tdp', 'price'],
            'motherboard': ['name', 'manufacturer', 'socket', 'memory_type', 'price'],
            'ram': ['name', 'manufacturer', 'memory_type', 'capacity', 'speed', 'price'],
            'storage': ['name', 'manufacturer', 'storage_type', 'capacity', 'price'],
            'psu': ['name', 'manufacturer', 'wattage', 'price'],
            'case': ['name', 'manufacturer', 'form_factor', 'price'],
            'cooling': ['name', 'manufacturer', 'cooling_type', 'max_tdp', 'price'],
        }
        
        for field in required_fields.get(component_type, []):
            if field not in spec or spec[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Валидация цены
        price = spec.get('price', 0)
        min_price, max_price = PRICE_RANGES.get(component_type, (1000, 500000))
        if price < min_price:
            warnings.append(f"Price too low ({price} RUB), minimum {min_price} RUB")
            spec['price'] = min_price
        elif price > max_price:
            warnings.append(f"Price too high ({price} RUB), maximum {max_price} RUB")
            spec['price'] = max_price
        
        # Специфичная валидация
        if component_type == 'cpu':
            if spec.get('manufacturer') not in VALID_CPU_MANUFACTURERS:
                warnings.append(f"Unknown CPU manufacturer: {spec.get('manufacturer')}")
            if spec.get('socket') not in VALID_CPU_SOCKETS:
                warnings.append(f"Unknown socket: {spec.get('socket')}")
            if spec.get('cores', 0) < 2 or spec.get('cores', 0) > 128:
                errors.append(f"Invalid core count: {spec.get('cores')}")
        
        elif component_type == 'gpu':
            if spec.get('manufacturer') not in VALID_GPU_MANUFACTURERS:
                warnings.append(f"Unknown GPU manufacturer: {spec.get('manufacturer')}")
            if spec.get('memory', 0) < 2 or spec.get('memory', 0) > 48:
                warnings.append(f"Suspicious GPU memory: {spec.get('memory')}GB")
        
        elif component_type == 'motherboard':
            if spec.get('socket') not in VALID_CPU_SOCKETS:
                warnings.append(f"Unknown motherboard socket: {spec.get('socket')}")
            if spec.get('memory_type') not in VALID_MEMORY_TYPES:
                warnings.append(f"Unknown memory type: {spec.get('memory_type')}")
        
        elif component_type == 'ram':
            if spec.get('memory_type') not in VALID_MEMORY_TYPES:
                warnings.append(f"Unknown memory type: {spec.get('memory_type')}")
            if spec.get('capacity', 0) not in [4, 8, 16, 32, 64, 128, 256]:
                warnings.append(f"Non-standard RAM capacity: {spec.get('capacity')}GB")
        
        elif component_type == 'psu':
            wattage = spec.get('wattage', 0)
            if wattage < 300 or wattage > 2000:
                warnings.append(f"Suspicious PSU wattage: {wattage}W")
        
        is_valid = len(errors) == 0
        all_issues = errors + warnings
        
        return is_valid, all_issues
    
    def _check_compatibility(self, parsed: dict) -> Tuple[bool, List[str]]:
        """
        Проверка совместимости сгенерированных компонентов
        """
        issues = []
        
        cpu = parsed.get('cpu', {})
        motherboard = parsed.get('motherboard', {})
        ram = parsed.get('ram', {})
        
        # 1. CPU socket == Motherboard socket
        cpu_socket = cpu.get('socket')
        mb_socket = motherboard.get('socket')
        if cpu_socket and mb_socket and cpu_socket != mb_socket:
            issues.append(f"[ERROR] Incompatible sockets: CPU ({cpu_socket}) != MB ({mb_socket})")
        
        # 2. RAM type == Motherboard memory_type
        ram_type = ram.get('memory_type')
        mb_memory_type = motherboard.get('memory_type')
        if ram_type and mb_memory_type and ram_type != mb_memory_type:
            issues.append(f"[ERROR] Incompatible memory: RAM ({ram_type}) != MB ({mb_memory_type})")
        
        # 3. Проверка мощности БП
        cpu_tdp = cpu.get('tdp', 0)
        gpu = parsed.get('gpu', {})
        gpu_tdp = gpu.get('tdp', 0) if gpu else 0
        psu = parsed.get('psu', {})
        psu_wattage = psu.get('wattage', 0)
        
        total_tdp = cpu_tdp + gpu_tdp
        recommended_psu = int(total_tdp * 1.5)
        
        if psu_wattage > 0 and psu_wattage < total_tdp:
            issues.append(f"[WARN] PSU power insufficient: {psu_wattage}W < {total_tdp}W (CPU+GPU)")
        elif psu_wattage > 0 and psu_wattage < recommended_psu:
            issues.append(f"[WARN] Recommended PSU {recommended_psu}W+ (current {psu_wattage}W)")
        
        # 4. Проверка охлаждения
        cooling = parsed.get('cooling', {})
        cooling_max_tdp = cooling.get('max_tdp', 0)
        if cooling_max_tdp > 0 and cpu_tdp > 0 and cooling_max_tdp < cpu_tdp:
            issues.append(f"[WARN] Cooling insufficient: {cooling_max_tdp}W < CPU TDP {cpu_tdp}W")
        
        # 5. Проверка общей цены
        total = sum([
            parsed.get('cpu', {}).get('price', 0),
            parsed.get('gpu', {}).get('price', 0) if parsed.get('gpu') else 0,
            parsed.get('motherboard', {}).get('price', 0),
            parsed.get('ram', {}).get('price', 0),
            parsed.get('storage', {}).get('price', 0),
            parsed.get('psu', {}).get('price', 0),
            parsed.get('case', {}).get('price', 0),
            parsed.get('cooling', {}).get('price', 0),
        ])
        
        if total > float(self.max_budget):
            issues.append(f"[WARN] Total price ({total} RUB) exceeds budget ({self.max_budget} RUB)")
        
        is_compatible = not any("[ERROR]" in issue for issue in issues)
        return is_compatible, issues
    
    def _build_generative_prompt(self) -> str:
        """Создать промпт для генерации полных спецификаций компонентов"""
        
        # Собираем требования
        requirements_list = []
        if self.requirements.get('gaming'):
            requirements_list.append("игры")
        if self.requirements.get('streaming'):
            requirements_list.append("стриминг")
        if self.requirements.get('video_editing'):
            requirements_list.append("видеомонтаж")
        if self.requirements.get('multitasking'):
            requirements_list.append("многозадачность")
        if self.requirements.get('work_with_4k'):
            requirements_list.append("4K")
        if self.requirements.get('vr_support'):
            requirements_list.append("VR")
        
        requirements_text = ", ".join(requirements_list) if requirements_list else "универсальное использование"
        
        pref = self.pc_preferences
        
        # Существующие компоненты
        existing_info = ""
        if self.has_existing_components and self.existing_components_description:
            existing_info = f"Учти что у пользователя уже есть: {self.existing_components_description}"
        
        prompt = f"""Собери компьютер для {self.user_type}.
Бюджет: {self.min_budget}-{self.max_budget} рублей.
Задачи: {requirements_text}.
Приоритет: {self.priority}.
{existing_info}

Требования:
- CPU: {pref['preferred_cpu_manufacturer']}, минимум {pref['min_cpu_cores']} ядер
- GPU: {pref['preferred_gpu_manufacturer']}, минимум {pref['min_gpu_vram']}GB
- RAM: минимум {pref['min_ram_capacity']}GB
- Накопитель: {pref['storage_type_preference']}, {pref['min_storage_capacity']}GB+
- Охлаждение: {pref['cooling_preference']}
- RGB: {'да' if pref['rgb_preference'] else 'нет'}

Ответь ТОЛЬКО JSON:
{{
  "cpu": {{"name": "модель", "manufacturer": "Intel/AMD", "socket": "сокет", "cores": ядра, "threads": потоки, "base_clock": ГГц, "boost_clock": ГГц, "tdp": Вт, "price": рублей, "performance_score": оценка}},
  "gpu": {{"name": "модель", "manufacturer": "NVIDIA/AMD", "chipset": "чип", "memory": ГБ, "memory_type": "GDDR6", "core_clock": МГц, "boost_clock": МГц, "tdp": Вт, "recommended_psu": Вт, "price": рублей, "performance_score": оценка}},
  "motherboard": {{"name": "модель", "manufacturer": "бренд", "socket": "как у CPU", "chipset": "чипсет", "form_factor": "ATX", "memory_slots": 4, "max_memory": ГБ, "memory_type": "DDR4/DDR5", "pcie_slots": 2, "m2_slots": 2, "price": рублей}},
  "ram": {{"name": "модель", "manufacturer": "бренд", "memory_type": "как у MB", "capacity": ГБ, "speed": МГц, "modules": планок, "cas_latency": "CL", "price": рублей}},
  "storage": {{"name": "модель", "manufacturer": "бренд", "storage_type": "ssd_nvme", "capacity": ГБ, "read_speed": МБс, "write_speed": МБс, "price": рублей}},
  "psu": {{"name": "модель", "manufacturer": "бренд", "wattage": Вт, "efficiency_rating": "80+ Gold", "modular": true, "price": рублей}},
  "case": {{"name": "модель", "manufacturer": "бренд", "form_factor": "Mid-Tower", "max_gpu_length": мм, "fan_slots": штук, "rgb": true/false, "price": рублей}},
  "cooling": {{"name": "модель", "manufacturer": "бренд", "cooling_type": "air/aio", "socket_compatibility": "сокеты", "max_tdp": Вт, "noise_level": дБ, "price": рублей}},
  "reasoning": {{"cpu": "причина", "gpu": "причина", "motherboard": "причина", "ram": "причина", "storage": "причина", "psu": "причина", "case": "причина", "cooling": "причина"}},
  "total_price": сумма,
  "confidence": 0.9
}}

ВАЖНО: socket CPU = socket MB, тип RAM = тип MB, цена <= {self.max_budget} руб."""
        
        return prompt
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Вызвать Ollama API"""
        try:
            # Добавляем инструкции прямо в промпт (system не работает в /api/generate)
            full_prompt = f"""[ИНСТРУКЦИЯ] Ты эксперт по сборке компьютеров. Отвечай ТОЛЬКО JSON без текста.

{prompt}"""
            
            payload = {
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "num_predict": 4096
                }
            }
            
            logger.info("Sending generative request to Ollama...")
            logger.info(f"Prompt length: {len(full_prompt)} characters")
            
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                logger.info(f"Ollama responded with {len(ai_response)} characters")
                
                # Если ответ пустой, логируем полный response для отладки
                if not ai_response:
                    logger.warning(f"Empty response from Ollama. Full data: {data}")
                    # Попробуем использовать thinking если есть
                    if data.get("thinking"):
                        logger.info("Model returned thinking instead of response")
                
                return ai_response
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running?")
            return None
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out (300s)")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    def _parse_ai_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Распарсить ответ AI"""
        try:
            # Логируем длину ответа для отладки
            logger.info(f"AI response length: {len(response)} characters")
            
            # Ищем JSON в ответе
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Логируем какие компоненты нашли
                found_components = [k for k in ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case', 'cooling'] if k in parsed]
                logger.info(f"Parsed AI response. Found components: {found_components}")
                
                return parsed
            
            logger.error("No JSON found in AI response")
            logger.debug(f"Full response: {response[:1000]}...")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Response was: {response[:500]}...")
            return None
    
    def _get_model_fields(self, model_class) -> set:
        """Получить список допустимых полей модели"""
        return {field.name for field in model_class._meta.get_fields() 
                if hasattr(field, 'column') and field.column is not None}
    
    def _normalize_ai_spec(self, component_type: str, spec: dict) -> dict:
        """Нормализовать спецификацию от AI в формат нашей БД"""
        normalized = spec.copy()
        
        # Нормализация общих полей
        # Преобразуем price если это строка или число
        if 'price' in normalized:
            price_val = normalized['price']
            if isinstance(price_val, str):
                # Убираем все нечисловые символы кроме точки
                price_val = ''.join(c for c in price_val if c.isdigit() or c == '.')
            normalized['price'] = int(float(price_val)) if price_val else 0
        
        # Нормализация по типу компонента
        if component_type == 'gpu':
            # memory может прийти как "8GB GDDR6" - нужно только число
            if 'memory' in normalized and isinstance(normalized['memory'], str):
                mem_str = normalized['memory']
                mem_match = re.search(r'(\d+)', mem_str)
                normalized['memory'] = int(mem_match.group(1)) if mem_match else 8
            
            # Извлекаем memory_type если он в строке memory
            if 'memory' in spec and isinstance(spec['memory'], str) and 'memory_type' not in normalized:
                if 'GDDR6X' in spec['memory']:
                    normalized['memory_type'] = 'GDDR6X'
                elif 'GDDR6' in spec['memory']:
                    normalized['memory_type'] = 'GDDR6'
                elif 'GDDR5' in spec['memory']:
                    normalized['memory_type'] = 'GDDR5'
            
            # core_clock и boost_clock в МГц
            for field in ['core_clock', 'boost_clock']:
                if field in normalized:
                    val = normalized[field]
                    if isinstance(val, float) and val < 100:  # Скорее всего в ГГц
                        normalized[field] = int(val * 1000)
                    elif isinstance(val, (int, float)):
                        normalized[field] = int(val)
        
        elif component_type == 'ram':
            # capacity может быть числом или строкой
            if 'capacity' in normalized:
                cap_val = normalized['capacity']
                if isinstance(cap_val, str):
                    cap_match = re.search(r'(\d+)', cap_val)
                    normalized['capacity'] = int(cap_match.group(1)) if cap_match else 16
                elif isinstance(cap_val, int) and cap_val > 1000:  # Возможно в МБ
                    normalized['capacity'] = cap_val // 1024
        
        elif component_type == 'storage':
            # capacity может быть в ГБ или ТБ
            if 'capacity' in normalized:
                cap_val = normalized['capacity']
                if isinstance(cap_val, str):
                    if 'TB' in cap_val.upper() or 'ТБ' in cap_val.upper():
                        cap_match = re.search(r'(\d+)', cap_val)
                        normalized['capacity'] = int(cap_match.group(1)) * 1000 if cap_match else 1000
                    else:
                        cap_match = re.search(r'(\d+)', cap_val)
                        normalized['capacity'] = int(cap_match.group(1)) if cap_match else 512
            
            # Нормализуем storage_type
            if 'type' in normalized and 'storage_type' not in normalized:
                type_val = normalized['type'].lower()
                if 'nvme' in type_val or 'm.2' in type_val:
                    normalized['storage_type'] = 'ssd_nvme'
                elif 'ssd' in type_val:
                    normalized['storage_type'] = 'ssd_sata'
                elif 'hdd' in type_val:
                    normalized['storage_type'] = 'hdd'
                else:
                    normalized['storage_type'] = 'ssd_nvme'
        
        elif component_type == 'psu':
            # wattage/power
            if 'power' in normalized and 'wattage' not in normalized:
                normalized['wattage'] = int(normalized['power'])
            if 'wattage' in normalized:
                val = normalized['wattage']
                if isinstance(val, str):
                    watt_match = re.search(r'(\d+)', val)
                    normalized['wattage'] = int(watt_match.group(1)) if watt_match else 500
        
        elif component_type == 'cooling':
            # max_tdp
            if 'max_tdp' not in normalized:
                normalized['max_tdp'] = 150  # Дефолтное значение
            
            # cooling_type
            if 'type' in normalized and 'cooling_type' not in normalized:
                type_val = str(normalized['type']).lower()
                if 'water' in type_val or 'liquid' in type_val or 'aio' in type_val:
                    normalized['cooling_type'] = 'aio'
                else:
                    normalized['cooling_type'] = 'air'
        
        return normalized

    def _create_component_from_spec(self, model_class, spec: dict, ai_confidence: float):
        """Создать компонент в БД из спецификации AI"""
        try:
            # Получаем допустимые поля модели
            valid_fields = self._get_model_fields(model_class)
            logger.debug(f"{model_class.__name__} valid fields: {valid_fields}")
            
            # Фильтруем spec, оставляя только допустимые поля
            filtered_spec = {k: v for k, v in spec.items() if k in valid_fields}
            
            # Логируем если были отфильтрованы поля
            removed_fields = set(spec.keys()) - set(filtered_spec.keys())
            if removed_fields:
                logger.info(f"Filtered out unknown fields for {model_class.__name__}: {removed_fields}")
            
            # Добавляем AI метаданные
            filtered_spec['is_ai_generated'] = True
            filtered_spec['ai_generation_date'] = timezone.now()
            filtered_spec['ai_confidence'] = ai_confidence
            
            # Преобразуем price в Decimal если это число
            if 'price' in filtered_spec and not isinstance(filtered_spec['price'], Decimal):
                filtered_spec['price'] = Decimal(str(filtered_spec['price']))
            
            logger.info(f"Creating {model_class.__name__} with fields: {list(filtered_spec.keys())}")
            
            # Создаем компонент
            component = model_class.objects.create(**filtered_spec)
            logger.info(f"[OK] Created AI-generated {model_class.__name__}: {component.name} (price: {component.price})")
            return component
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to create {model_class.__name__}: {e}")
            logger.error(f"Spec was: {spec}")
            logger.error(f"Filtered spec was: {filtered_spec if 'filtered_spec' in dir() else 'N/A'}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def generate_configuration(self, user) -> tuple:
        """
        Генерация конфигурации с полностью AI-созданными компонентами
        
        Returns:
            tuple: (PCConfiguration или None, dict с info/error)
        """
        from recommendations.models import PCConfiguration, Recommendation
        
        logger.info(f"Starting generative configuration for user: {user.username}")
        logger.info(f"User profile: type={self.user_type}, budget={self.min_budget}-{self.max_budget}, priority={self.priority}")
        logger.info(f"PC preferences: {self.pc_preferences}")
        
        # Генерируем промпт и вызываем AI
        prompt = self._build_generative_prompt()
        logger.debug(f"Generated prompt length: {len(prompt)} characters")
        
        ai_response = self._call_ollama(prompt)
        
        if not ai_response:
            logger.error("AI did not respond or is unavailable")
            return None, {"error": "AI is unavailable or did not respond"}
        
        # Парсим ответ
        parsed = self._parse_ai_response(ai_response)
        if not parsed:
            logger.error("Failed to parse AI response")
            return None, {"error": "Failed to parse AI response"}
        
        # Получаем confidence score
        confidence = parsed.get('confidence', 0.8)
        logger.info(f"AI confidence: {confidence}")
        
        # Проверяем совместимость компонентов
        is_compatible, compat_issues = self._check_compatibility(parsed)
        if not is_compatible:
            logger.warning(f"AI generated incompatible components: {compat_issues}")
        else:
            logger.info("All components are compatible")
        
        try:
            # Создаем компоненты из спецификаций AI с валидацией
            components = {}
            validation_warnings = []
            creation_errors = []
            
            component_mapping = [
                ('cpu', CPU, 'cpu'),
                ('gpu', GPU, 'gpu'),
                ('motherboard', Motherboard, 'motherboard'),
                ('ram', RAM, 'ram'),
                ('storage', Storage, 'storage_primary'),
                ('psu', PSU, 'psu'),
                ('case', Case, 'case'),
                ('cooling', Cooling, 'cooling'),
            ]
            
            for spec_key, model_class, component_key in component_mapping:
                if spec_key in parsed and parsed[spec_key]:
                    spec = parsed[spec_key].copy()
                    logger.info(f"Processing {spec_key}: {spec.get('name', 'unknown')}")
                    
                    # Нормализуем спецификацию от AI
                    spec = self._normalize_ai_spec(spec_key, spec)
                    logger.debug(f"Normalized {spec_key}: {spec}")
                    
                    # Валидируем спецификацию
                    is_valid, issues = self._validate_component_spec(spec_key, spec)
                    if issues:
                        validation_warnings.extend([f"{spec_key}: {issue}" for issue in issues])
                        logger.warning(f"Validation issues for {spec_key}: {issues}")
                    
                    if is_valid:
                        component = self._create_component_from_spec(model_class, spec, confidence)
                        if component:
                            components[component_key] = component
                        else:
                            creation_errors.append(f"Failed to create {spec_key}")
                            logger.error(f"Failed to create {spec_key} from spec")
                    else:
                        creation_errors.append(f"Invalid {spec_key}: {issues}")
                        logger.error(f"Invalid {spec_key} specification: {issues}")
                else:
                    logger.warning(f"No spec found for {spec_key}")
            
            # Логируем результаты создания компонентов
            logger.info(f"Created components: {list(components.keys())}")
            if creation_errors:
                logger.error(f"Creation errors: {creation_errors}")
            
            # Проверяем что обязательные компоненты созданы
            required_components = ['cpu', 'motherboard', 'ram', 'storage_primary']
            missing = [c for c in required_components if c not in components or not components[c]]
            if missing:
                error_msg = f"Failed to create required components: {', '.join(missing)}"
                logger.error(error_msg)
                if creation_errors:
                    error_msg += f". Details: {'; '.join(creation_errors)}"
                return None, {"error": error_msg}
            
            # Создаем конфигурацию
            logger.info("Creating PCConfiguration...")
            config = PCConfiguration.objects.create(
                user=user,
                name=f"AI-build for {self.user_type}",
                **components
            )
            
            config.calculate_total_price()
            
            # Сохраняем информацию о совместимости
            config.compatibility_check = is_compatible
            config.compatibility_notes = "\n".join(compat_issues) if compat_issues else "[OK] All components are compatible"
            config.save()
            
            # Сохраняем обоснования от AI
            reasoning = parsed.get('reasoning', {})
            for component_type, reason in reasoning.items():
                component = components.get(component_type)
                if component:
                    Recommendation.objects.create(
                        configuration=config,
                        component_type=component_type,
                        component_id=component.id,
                        reason=reason
                    )
            
            logger.info(f"[OK] AI-generated configuration created: {config.name} (total: {config.total_price} RUB)")
            
            return config, {
                "ai_used": True,
                "generation_mode": "fully_generative",
                "reasoning": reasoning,
                "total_price": float(config.total_price),
                "confidence": confidence,
                "is_ai_generated": True,
                "compatibility_check": is_compatible,
                "compatibility_issues": compat_issues,
                "validation_warnings": validation_warnings,
                "components_created": list(components.keys()),
                "summary": f"Configuration generated by AI with {int(confidence * 100)}% confidence"
            }
            
        except Exception as e:
            import traceback
            logger.error(f"Error creating AI-generated configuration: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None, {"error": f"Error creating configuration: {str(e)}"}
