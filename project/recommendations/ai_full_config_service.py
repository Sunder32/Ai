"""
AI Full Configuration Service
Сервис для генерации полных сборок ПК + периферия + рабочее место
используя обученную модель DeepSeek
"""
import json
import logging
import re
import requests
from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple

from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-project-model"


class AIFullConfigService:
    """
    Сервис для полной генерации конфигурации с использованием обученной AI модели.
    Генерирует: ПК компоненты + периферию + рабочее место
    """
    
    # Ценовые диапазоны для всех типов компонентов
    PRICE_RANGES = {
        # ПК компоненты
        'cpu': (5000, 150000),
        'gpu': (10000, 350000),
        'motherboard': (5000, 80000),
        'ram': (3000, 50000),
        'storage': (2000, 50000),
        'psu': (3000, 40000),
        'case': (2000, 50000),
        'cooling': (1000, 30000),
        # Периферия
        'monitor': (8000, 250000),
        'keyboard': (1000, 30000),
        'mouse': (500, 25000),
        'headset': (1000, 50000),
        'mousepad': (300, 10000),
        'speakers': (2000, 50000),
        'webcam': (1500, 30000),
        'microphone': (2000, 40000),
        # Рабочее место
        'desk': (5000, 80000),
        'chair': (5000, 100000),
    }
    
    # Профили использования с рекомендуемыми характеристиками
    USER_PROFILES = {
        'gaming': {
            'pc_budget_ratio': 0.6,
            'peripherals_budget_ratio': 0.3,
            'workspace_budget_ratio': 0.1,
            'min_monitor_hz': 144,
            'gpu_priority': 'high',
            'keyboard_type': 'mechanical',
            'mouse_wireless': False,
            'rgb_preference': True,
        },
        'office': {
            'pc_budget_ratio': 0.5,
            'peripherals_budget_ratio': 0.3,
            'workspace_budget_ratio': 0.2,
            'min_monitor_hz': 60,
            'gpu_priority': 'low',
            'keyboard_type': 'any',
            'mouse_wireless': True,
            'rgb_preference': False,
        },
        'content_creator': {
            'pc_budget_ratio': 0.55,
            'peripherals_budget_ratio': 0.25,
            'workspace_budget_ratio': 0.2,
            'min_monitor_hz': 60,
            'gpu_priority': 'high',
            'keyboard_type': 'mechanical',
            'mouse_wireless': True,
            'rgb_preference': False,
        },
        'developer': {
            'pc_budget_ratio': 0.5,
            'peripherals_budget_ratio': 0.3,
            'workspace_budget_ratio': 0.2,
            'min_monitor_hz': 60,
            'gpu_priority': 'medium',
            'keyboard_type': 'mechanical',
            'mouse_wireless': True,
            'rgb_preference': False,
        },
        'streamer': {
            'pc_budget_ratio': 0.5,
            'peripherals_budget_ratio': 0.35,
            'workspace_budget_ratio': 0.15,
            'min_monitor_hz': 144,
            'gpu_priority': 'high',
            'keyboard_type': 'mechanical',
            'mouse_wireless': False,
            'rgb_preference': True,
            'need_webcam': True,
            'need_microphone': True,
        },
        'student': {
            'pc_budget_ratio': 0.55,
            'peripherals_budget_ratio': 0.3,
            'workspace_budget_ratio': 0.15,
            'min_monitor_hz': 60,
            'gpu_priority': 'low',
            'keyboard_type': 'any',
            'mouse_wireless': True,
            'rgb_preference': False,
        },
    }
    
    def __init__(
        self,
        user_type: str = 'gaming',
        min_budget: float = 50000,
        max_budget: float = 150000,
        priority: str = 'balanced',
        requirements: Dict = None,
        pc_preferences: Dict = None,
        peripherals_preferences: Dict = None,
        workspace_preferences: Dict = None,
        include_peripherals: bool = True,
        include_workspace: bool = True,
    ):
        self.user_type = user_type
        self.min_budget = min_budget
        self.max_budget = max_budget
        self.priority = priority
        self.requirements = requirements or {}
        self.pc_preferences = pc_preferences or self._get_default_pc_preferences()
        self.peripherals_preferences = peripherals_preferences or {}
        self.workspace_preferences = workspace_preferences or {}
        self.include_peripherals = include_peripherals
        self.include_workspace = include_workspace
        
        # Получаем профиль пользователя
        self.profile = self.USER_PROFILES.get(user_type, self.USER_PROFILES['gaming'])
        
        # Рассчитываем бюджеты на каждую категорию
        self._calculate_budgets()
        
    def _calculate_budgets(self):
        """Рассчитать бюджеты для каждой категории"""
        total = self.max_budget
        
        if self.include_peripherals and self.include_workspace:
            self.pc_budget = total * self.profile['pc_budget_ratio']
            self.peripherals_budget = total * self.profile['peripherals_budget_ratio']
            self.workspace_budget = total * self.profile['workspace_budget_ratio']
        elif self.include_peripherals:
            self.pc_budget = total * 0.7
            self.peripherals_budget = total * 0.3
            self.workspace_budget = 0
        else:
            self.pc_budget = total
            self.peripherals_budget = 0
            self.workspace_budget = 0
            
        logger.info(f"Budget allocation: PC={self.pc_budget:.0f}, Peripherals={self.peripherals_budget:.0f}, Workspace={self.workspace_budget:.0f}")
    
    def _get_default_pc_preferences(self) -> Dict:
        """Дефолтные настройки для ПК"""
        return {
            'preferred_cpu_manufacturer': 'any',
            'preferred_gpu_manufacturer': 'any',
            'min_cpu_cores': 6,
            'min_gpu_vram': 6,
            'min_ram_capacity': 16,
            'storage_type_preference': 'ssd_nvme',
            'min_storage_capacity': 500,
            'cooling_preference': 'air',
            'rgb_preference': self.profile.get('rgb_preference', False),
        }
    
    def _build_full_prompt(self) -> str:
        """Создать промпт для полной генерации конфигурации"""
        
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
            requirements_list.append("работа с 4K")
        if self.requirements.get('vr_support'):
            requirements_list.append("VR")
        if self.requirements.get('programming'):
            requirements_list.append("программирование")
        if self.requirements.get('office_work'):
            requirements_list.append("офисная работа")
            
        requirements_text = ", ".join(requirements_list) if requirements_list else "универсальное использование"
        
        pref = self.pc_preferences
        
        # Формируем секции в зависимости от настроек
        peripherals_section = ""
        workspace_section = ""
        
        if self.include_peripherals:
            peripherals_section = f"""
ПЕРИФЕРИЯ (бюджет ~{self.peripherals_budget:.0f} руб):
  "monitor": {{"name": "модель", "manufacturer": "бренд", "screen_size": дюймы, "resolution": "разрешение", "refresh_rate": Гц, "panel_type": "IPS/VA/TN", "response_time": мс, "hdr": true/false, "curved": true/false, "price": рублей}},
  "keyboard": {{"name": "модель", "manufacturer": "бренд", "switch_type": "mechanical/membrane", "switch_model": "модель свитчей", "rgb": true/false, "wireless": true/false, "form_factor": "Full-size/TKL/60%", "price": рублей}},
  "mouse": {{"name": "модель", "manufacturer": "бренд", "sensor_type": "optical/laser", "dpi": число, "buttons": число, "wireless": true/false, "rgb": true/false, "weight": грамм, "price": рублей}},
  "headset": {{"name": "модель", "manufacturer": "бренд", "connection_type": "USB/3.5mm/Wireless", "wireless": true/false, "microphone": true/false, "surround": true/false, "price": рублей}},
  "mousepad": {{"name": "модель", "manufacturer": "бренд", "size": "small/medium/large/xl", "width": мм, "height": мм, "rgb": true/false, "price": рублей}},"""
            
            if self.profile.get('need_webcam') or self.requirements.get('streaming'):
                peripherals_section += """
  "webcam": {{"name": "модель", "manufacturer": "бренд", "resolution": "1080p/4K", "fps": число, "autofocus": true/false, "price": рублей}},"""
                
            if self.profile.get('need_microphone') or self.requirements.get('streaming'):
                peripherals_section += """
  "microphone": {{"name": "модель", "manufacturer": "бренд", "microphone_type": "condenser/dynamic/usb", "connection": "USB/XLR", "price": рублей}},"""
        
        if self.include_workspace:
            workspace_section = f"""
РАБОЧЕЕ МЕСТО (бюджет ~{self.workspace_budget:.0f} руб):
  "desk": {{"name": "модель", "manufacturer": "бренд", "width": см, "depth": см, "adjustable_height": true/false, "price": рублей}},
  "chair": {{"name": "модель", "manufacturer": "бренд", "ergonomic": true/false, "adjustable_armrests": true/false, "lumbar_support": true/false, "max_weight": кг, "price": рублей}},"""
        
        prompt = f"""Ты эксперт по сборке компьютеров и организации рабочего места. У тебя есть обширная база знаний о компонентах ПК, периферии и мебели.

ЗАДАЧА: Собери ПОЛНУЮ сборку для {self.user_type}.
Общий бюджет: {self.min_budget:.0f}-{self.max_budget:.0f} рублей
Задачи: {requirements_text}
Приоритет: {self.priority}

ТРЕБОВАНИЯ К ПК (бюджет ~{self.pc_budget:.0f} руб):
- CPU: {pref['preferred_cpu_manufacturer']}, минимум {pref['min_cpu_cores']} ядер
- GPU: {pref['preferred_gpu_manufacturer']}, минимум {pref['min_gpu_vram']}GB VRAM
- RAM: минимум {pref['min_ram_capacity']}GB
- Накопитель: {pref['storage_type_preference']}, {pref['min_storage_capacity']}GB+
- Охлаждение: {pref['cooling_preference']}
- RGB: {'да' if pref['rgb_preference'] else 'нет'}

Ответь ТОЛЬКО JSON без лишнего текста:
{{
ПК КОМПОНЕНТЫ:
  "cpu": {{"name": "модель", "manufacturer": "Intel/AMD", "socket": "сокет", "cores": ядра, "threads": потоки, "base_clock": ГГц, "boost_clock": ГГц, "tdp": Вт, "price": рублей, "performance_score": 1-100}},
  "gpu": {{"name": "модель", "manufacturer": "NVIDIA/AMD", "chipset": "чип", "memory": ГБ, "memory_type": "GDDR6/GDDR6X", "core_clock": МГц, "boost_clock": МГц, "tdp": Вт, "recommended_psu": Вт, "price": рублей, "performance_score": 1-100}},
  "motherboard": {{"name": "модель", "manufacturer": "бренд", "socket": "как у CPU", "chipset": "чипсет", "form_factor": "ATX/mATX", "memory_slots": 4, "max_memory": ГБ, "memory_type": "DDR4/DDR5", "pcie_slots": 2, "m2_slots": 2, "price": рублей}},
  "ram": {{"name": "модель", "manufacturer": "бренд", "memory_type": "как у MB", "capacity": ГБ, "speed": МГц, "modules": планок, "cas_latency": "CL", "price": рублей}},
  "storage": {{"name": "модель", "manufacturer": "бренд", "storage_type": "ssd_nvme/ssd_sata/hdd", "capacity": ГБ, "read_speed": МБс, "write_speed": МБс, "price": рублей}},
  "psu": {{"name": "модель", "manufacturer": "бренд", "wattage": Вт, "efficiency_rating": "80+ Bronze/Gold/Platinum", "modular": true/false, "price": рублей}},
  "case": {{"name": "модель", "manufacturer": "бренд", "form_factor": "Mid-Tower/Full-Tower", "max_gpu_length": мм, "fan_slots": штук, "rgb": true/false, "price": рублей}},
  "cooling": {{"name": "модель", "manufacturer": "бренд", "cooling_type": "air/aio", "socket_compatibility": "сокеты", "max_tdp": Вт, "noise_level": дБ, "price": рублей}},
{peripherals_section}
{workspace_section}
  "reasoning": {{
    "cpu": "почему выбран этот процессор",
    "gpu": "почему выбрана эта видеокарта",
    "motherboard": "почему выбрана эта материнка",
    "monitor": "почему выбран этот монитор",
    "keyboard": "почему выбрана эта клавиатура",
    "overall": "общее обоснование сборки"
  }},
  "total_price": общая_сумма,
  "pc_price": сумма_пк,
  "peripherals_price": сумма_периферии,
  "workspace_price": сумма_рабочего_места,
  "confidence": 0.9
}}

КРИТИЧЕСКИ ВАЖНО:
1. socket CPU = socket материнской платы
2. memory_type RAM = memory_type материнской платы
3. wattage PSU >= recommended_psu видеокарты + 150Вт
4. max_tdp охлаждения >= tdp процессора
5. Общая цена <= {self.max_budget} рублей
6. Используй реальные модели компонентов из своей базы знаний
7. Все цены должны быть реалистичными (в рублях, декабрь 2024)"""

        return prompt
    
    def _call_ai_model(self, prompt: str) -> Optional[str]:
        """Вызвать AI модель"""
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.4,  # Немного снижаем для более предсказуемых результатов
                    "top_p": 0.9,
                    "num_predict": 8192,  # Увеличиваем для более длинных ответов
                }
            }
            
            logger.info(f"Calling AI model: {MODEL_NAME}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=600)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                logger.info(f"AI responded with {len(ai_response)} characters")
                return ai_response
            else:
                logger.error(f"AI model error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running?")
            return None
        except requests.exceptions.Timeout:
            logger.error("AI request timed out (600s)")
            return None
        except Exception as e:
            logger.error(f"Error calling AI model: {e}")
            return None
    
    def _parse_ai_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Распарсить ответ AI"""
        try:
            # Ищем JSON в ответе
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                
                # Пробуем очистить JSON от комментариев
                json_str = re.sub(r'//.*?\n', '\n', json_str)
                json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                
                parsed = json.loads(json_str)
                
                # Логируем найденные компоненты
                pc_components = [k for k in ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case', 'cooling'] if k in parsed]
                peripheral_components = [k for k in ['monitor', 'keyboard', 'mouse', 'headset', 'mousepad', 'webcam', 'microphone', 'speakers'] if k in parsed]
                workspace_components = [k for k in ['desk', 'chair'] if k in parsed]
                
                logger.info(f"Parsed components - PC: {pc_components}, Peripherals: {peripheral_components}, Workspace: {workspace_components}")
                
                return parsed
            
            logger.error("No JSON found in AI response")
            logger.debug(f"Full response: {response[:2000]}...")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Response was: {response[:1000]}...")
            return None
    
    def _validate_component_spec(self, component_type: str, spec: dict) -> Tuple[bool, List[str]]:
        """Валидировать спецификацию компонента"""
        issues = []
        
        # Проверяем обязательные поля
        if 'name' not in spec or not spec['name']:
            issues.append(f"Missing required field: name")
            
        if 'price' not in spec:
            issues.append(f"Missing required field: price")
        else:
            price = float(spec.get('price', 0))
            min_price, max_price = self.PRICE_RANGES.get(component_type, (100, 500000))
            
            if price < min_price:
                issues.append(f"Price {price} too low (min: {min_price})")
            elif price > max_price:
                issues.append(f"Price {price} too high (max: {max_price})")
        
        is_valid = len(issues) == 0 or all("too low" in i or "too high" in i for i in issues)
        return is_valid, issues
    
    def _check_compatibility(self, parsed: Dict) -> Tuple[bool, List[str]]:
        """Проверить совместимость компонентов"""
        issues = []
        
        # Проверяем совместимость сокета CPU и материнской платы
        cpu = parsed.get('cpu', {})
        mb = parsed.get('motherboard', {})
        
        if cpu and mb:
            cpu_socket = str(cpu.get('socket', '')).upper()
            mb_socket = str(mb.get('socket', '')).upper()
            
            if cpu_socket and mb_socket and cpu_socket != mb_socket:
                issues.append(f"[ERROR] CPU socket ({cpu_socket}) != MB socket ({mb_socket})")
        
        # Проверяем тип памяти
        ram = parsed.get('ram', {})
        
        if ram and mb:
            ram_type = str(ram.get('memory_type', '')).upper()
            mb_mem_type = str(mb.get('memory_type', '')).upper()
            
            if ram_type and mb_mem_type and ram_type != mb_mem_type:
                issues.append(f"[ERROR] RAM type ({ram_type}) != MB memory type ({mb_mem_type})")
        
        # Проверяем мощность БП
        gpu = parsed.get('gpu', {})
        psu = parsed.get('psu', {})
        
        if gpu and psu:
            recommended_psu = int(gpu.get('recommended_psu', 0))
            cpu_tdp = int(cpu.get('tdp', 0)) if cpu else 0
            psu_wattage = int(psu.get('wattage', 0))
            
            min_wattage = recommended_psu + cpu_tdp + 100  # Запас 100Вт
            if psu_wattage < min_wattage:
                issues.append(f"[WARN] PSU wattage ({psu_wattage}W) may be insufficient (recommended: {min_wattage}W)")
        
        # Проверяем охлаждение
        cooling = parsed.get('cooling', {})
        
        if cpu and cooling:
            cpu_tdp = int(cpu.get('tdp', 0))
            max_tdp = int(cooling.get('max_tdp', 0))
            
            if max_tdp and cpu_tdp > max_tdp:
                issues.append(f"[WARN] CPU TDP ({cpu_tdp}W) exceeds cooling capacity ({max_tdp}W)")
        
        # Проверяем общий бюджет
        total = self._calculate_total_price(parsed)
        if total > float(self.max_budget) * 1.1:  # Допускаем 10% превышения
            issues.append(f"[WARN] Total price ({total:.0f} RUB) exceeds budget ({self.max_budget:.0f} RUB)")
        
        is_compatible = not any("[ERROR]" in issue for issue in issues)
        return is_compatible, issues
    
    def _calculate_total_price(self, parsed: Dict) -> float:
        """Рассчитать общую стоимость"""
        total = 0
        
        for key in ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case', 'cooling',
                    'monitor', 'keyboard', 'mouse', 'headset', 'mousepad', 'webcam', 'microphone', 'speakers',
                    'desk', 'chair']:
            if key in parsed and parsed[key]:
                total += float(parsed[key].get('price', 0))
        
        return total
    
    def _normalize_price(self, value) -> int:
        """Нормализовать цену в целое число"""
        if isinstance(value, str):
            value = ''.join(c for c in value if c.isdigit() or c == '.')
            return int(float(value)) if value else 0
        return int(float(value)) if value else 0
    
    def _get_model_fields(self, model_class) -> set:
        """Получить список допустимых полей модели"""
        return {field.name for field in model_class._meta.get_fields() 
                if hasattr(field, 'column') and field.column is not None}
    
    def _create_component_from_spec(self, model_class, spec: dict, ai_confidence: float):
        """Создать компонент в БД из спецификации AI"""
        try:
            valid_fields = self._get_model_fields(model_class)
            filtered_spec = {k: v for k, v in spec.items() if k in valid_fields}
            
            # Добавляем AI метаданные если поля есть в модели
            if 'is_ai_generated' in valid_fields:
                filtered_spec['is_ai_generated'] = True
            if 'ai_generation_date' in valid_fields:
                filtered_spec['ai_generation_date'] = timezone.now()
            if 'ai_confidence' in valid_fields:
                filtered_spec['ai_confidence'] = ai_confidence
            
            # Преобразуем price в Decimal
            if 'price' in filtered_spec:
                filtered_spec['price'] = Decimal(str(self._normalize_price(filtered_spec['price'])))
            
            component = model_class.objects.create(**filtered_spec)
            logger.info(f"[OK] Created {model_class.__name__}: {component.name} (price: {component.price})")
            return component
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to create {model_class.__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def generate_full_configuration(self, user) -> Tuple[Optional[Any], Optional[Any], Dict]:
        """
        Генерация полной конфигурации: ПК + периферия + рабочее место
        
        Returns:
            tuple: (PCConfiguration или None, WorkspaceSetup или None, dict с info)
        """
        from recommendations.models import PCConfiguration, Recommendation, WorkspaceSetup
        from peripherals.models import Monitor, Keyboard, Mouse, Headset, Mousepad, Webcam, Microphone, Speakers, Desk, Chair
        from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
        
        logger.info(f"Starting FULL AI configuration for user: {user.username}")
        logger.info(f"Profile: {self.user_type}, Budget: {self.min_budget}-{self.max_budget}")
        logger.info(f"Include peripherals: {self.include_peripherals}, Include workspace: {self.include_workspace}")
        
        # Генерируем промпт и вызываем AI
        prompt = self._build_full_prompt()
        ai_response = self._call_ai_model(prompt)
        
        if not ai_response:
            return None, None, {"error": "AI модель недоступна или не ответила"}
        
        # Парсим ответ
        parsed = self._parse_ai_response(ai_response)
        if not parsed:
            return None, None, {"error": "Не удалось распарсить ответ AI"}
        
        confidence = parsed.get('confidence', 0.8)
        
        # Проверяем совместимость
        is_compatible, compat_issues = self._check_compatibility(parsed)
        if not is_compatible:
            logger.warning(f"Compatibility issues: {compat_issues}")
        
        try:
            # 1. Создаем ПК компоненты
            pc_components = {}
            pc_mapping = [
                ('cpu', CPU, 'cpu'),
                ('gpu', GPU, 'gpu'),
                ('motherboard', Motherboard, 'motherboard'),
                ('ram', RAM, 'ram'),
                ('storage', Storage, 'storage_primary'),
                ('psu', PSU, 'psu'),
                ('case', Case, 'case'),
                ('cooling', Cooling, 'cooling'),
            ]
            
            for spec_key, model_class, component_key in pc_mapping:
                if spec_key in parsed and parsed[spec_key]:
                    spec = parsed[spec_key].copy()
                    is_valid, _ = self._validate_component_spec(spec_key, spec)
                    if is_valid:
                        component = self._create_component_from_spec(model_class, spec, confidence)
                        if component:
                            pc_components[component_key] = component
            
            # Проверяем обязательные компоненты
            required = ['cpu', 'motherboard', 'ram', 'storage_primary']
            missing = [c for c in required if c not in pc_components]
            if missing:
                return None, None, {"error": f"Не удалось создать компоненты: {', '.join(missing)}"}
            
            # Создаем PCConfiguration
            config = PCConfiguration.objects.create(
                user=user,
                name=f"AI-сборка для {self.user_type}",
                **pc_components
            )
            config.calculate_total_price()
            config.compatibility_check = is_compatible
            config.compatibility_notes = "\n".join(compat_issues) if compat_issues else "[OK] Все компоненты совместимы"
            config.save()
            
            # Сохраняем обоснования
            reasoning = parsed.get('reasoning', {})
            for component_type, reason in reasoning.items():
                if component_type in pc_components:
                    component = pc_components[component_type]
                    Recommendation.objects.create(
                        configuration=config,
                        component_type=component_type,
                        component_id=component.id,
                        reason=str(reason)
                    )
            
            # 2. Создаем периферию
            peripherals = {}
            workspace_setup = None
            
            if self.include_peripherals:
                peripherals_mapping = [
                    ('monitor', Monitor),
                    ('keyboard', Keyboard),
                    ('mouse', Mouse),
                    ('headset', Headset),
                    ('mousepad', Mousepad),
                    ('webcam', Webcam),
                    ('microphone', Microphone),
                    ('speakers', Speakers),
                ]
                
                for spec_key, model_class in peripherals_mapping:
                    if spec_key in parsed and parsed[spec_key]:
                        spec = parsed[spec_key].copy()
                        is_valid, _ = self._validate_component_spec(spec_key, spec)
                        if is_valid:
                            component = self._create_component_from_spec(model_class, spec, confidence)
                            if component:
                                peripherals[spec_key] = component
            
            # 3. Создаем рабочее место
            workspace_components = {}
            if self.include_workspace:
                workspace_mapping = [
                    ('desk', Desk),
                    ('chair', Chair),
                ]
                
                for spec_key, model_class in workspace_mapping:
                    if spec_key in parsed and parsed[spec_key]:
                        spec = parsed[spec_key].copy()
                        is_valid, _ = self._validate_component_spec(spec_key, spec)
                        if is_valid:
                            component = self._create_component_from_spec(model_class, spec, confidence)
                            if component:
                                workspace_components[spec_key] = component
            
            # 4. Создаем WorkspaceSetup если есть периферия или рабочее место
            if peripherals or workspace_components:
                workspace_data = {
                    'user': user,
                    'name': f"Рабочее место для {self.user_type}",
                    'configuration': config,
                }
                
                # Добавляем периферию
                if 'monitor' in peripherals:
                    workspace_data['monitor_primary'] = peripherals['monitor']
                if 'keyboard' in peripherals:
                    workspace_data['keyboard'] = peripherals['keyboard']
                if 'mouse' in peripherals:
                    workspace_data['mouse'] = peripherals['mouse']
                if 'headset' in peripherals:
                    workspace_data['headset'] = peripherals['headset']
                if 'mousepad' in peripherals:
                    workspace_data['mousepad'] = peripherals['mousepad']
                if 'webcam' in peripherals:
                    workspace_data['webcam'] = peripherals['webcam']
                if 'microphone' in peripherals:
                    workspace_data['microphone'] = peripherals['microphone']
                if 'speakers' in peripherals:
                    workspace_data['speakers'] = peripherals['speakers']
                
                # Добавляем рабочее место
                if 'desk' in workspace_components:
                    workspace_data['desk'] = workspace_components['desk']
                if 'chair' in workspace_components:
                    workspace_data['chair'] = workspace_components['chair']
                
                workspace_setup = WorkspaceSetup.objects.create(**workspace_data)
                workspace_setup.calculate_total_price()
                logger.info(f"[OK] Created WorkspaceSetup: {workspace_setup.name}")
            
            # Рассчитываем итоговые цены
            pc_price = float(config.total_price)
            peripherals_price = sum(float(p.price) for p in peripherals.values())
            workspace_price = sum(float(w.price) for w in workspace_components.values())
            total_price = pc_price + peripherals_price + workspace_price
            
            logger.info(f"[OK] Full AI configuration created!")
            logger.info(f"PC: {pc_price:.0f}₽, Peripherals: {peripherals_price:.0f}₽, Workspace: {workspace_price:.0f}₽")
            logger.info(f"Total: {total_price:.0f}₽")
            
            return config, workspace_setup, {
                "ai_used": True,
                "generation_mode": "full_ai_generation",
                "confidence": confidence,
                "is_compatible": is_compatible,
                "compatibility_issues": compat_issues,
                "reasoning": reasoning,
                "prices": {
                    "pc": pc_price,
                    "peripherals": peripherals_price,
                    "workspace": workspace_price,
                    "total": total_price,
                },
                "components": {
                    "pc": list(pc_components.keys()),
                    "peripherals": list(peripherals.keys()),
                    "workspace": list(workspace_components.keys()),
                },
                "summary": f"Полная сборка сгенерирована AI с {int(confidence * 100)}% уверенностью"
            }
            
        except Exception as e:
            import traceback
            logger.error(f"Error creating full configuration: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None, None, {"error": f"Ошибка создания конфигурации: {str(e)}"}
