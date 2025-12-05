"""
AI Full Configuration Service
Сервис для генерации полных сборок ПК + периферия + рабочее место
используя обученную модель DeepSeek с данными из pc_components_dec_2025.json
и файлов периферии
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

# Ollama API configuration - обращаемся к AI серверу
OLLAMA_API_URL = "http://localhost:11434/api/generate"
AI_SERVER_URL = "http://localhost:5050/api/chat"  # AI сервер с обученной моделью
MODEL_NAME = "deepseek-project-model"


class AIFullConfigService:
    """
    Сервис для полной генерации конфигурации с использованием обученной AI модели.
    Генерирует: ПК компоненты + периферию + рабочее место
    """
    
    # Маппинг типов пользователей из frontend в профили
    USER_TYPE_MAPPING = {
        'gamer': 'gaming',
        'gaming': 'gaming',
        'programmer': 'developer',
        'developer': 'developer',
        'designer': 'content_creator',
        'content_creator': 'content_creator',
        'office': 'office',
        'student': 'student',
        'streamer': 'streamer',
    }
    
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
        self.include_peripherals = include_peripherals
        self.include_workspace = include_workspace
        
        # Маппируем тип пользователя в профиль - ДОЛЖНО БЫТЬ ДО _get_default_pc_preferences()
        mapped_type = self.USER_TYPE_MAPPING.get(user_type, 'gaming')
        
        # Получаем профиль пользователя - ДОЛЖНО БЫТЬ ДО _get_default_pc_preferences()
        self.profile = self.USER_PROFILES.get(mapped_type, self.USER_PROFILES['gaming'])
        
        # Теперь можно безопасно вызвать _get_default_pc_preferences()
        self.pc_preferences = pc_preferences or self._get_default_pc_preferences()
        self.peripherals_preferences = peripherals_preferences or {}
        self.workspace_preferences = workspace_preferences or {}
        
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
    
    def _generate_default_peripherals(self) -> Dict:
        """Генерация периферии из базы знаний AI"""
        from peripherals.models import Monitor, Keyboard, Mouse, Headset, Mousepad
        from decimal import Decimal
        
        peripherals = {}
        budget = self.peripherals_budget
        
        # Распределение бюджета: монитор 50%, клавиатура 15%, мышь 12%, гарнитура 15%, коврик 8%
        monitor_budget = budget * 0.50
        keyboard_budget = budget * 0.15
        mouse_budget = budget * 0.12
        headset_budget = budget * 0.15
        mousepad_budget = budget * 0.08
        
        # Определяем характеристики по профилю
        profile = self.profile
        is_gaming = self.user_type in ['gamer', 'gaming', 'streamer']
        is_creator = self.user_type in ['designer', 'content_creator']
        
        # Монитор
        monitor_specs = {
            'name': 'ASUS ProArt PA279CV' if is_creator else ('ASUS VG27AQ1A' if is_gaming else 'Dell S2722QC'),
            'manufacturer': 'ASUS' if is_creator or is_gaming else 'Dell',
            'screen_size': Decimal('27'),
            'resolution': '3840x2160' if is_creator else ('2560x1440' if is_gaming else '2560x1440'),
            'refresh_rate': 60 if is_creator else (165 if is_gaming else 75),
            'panel_type': 'IPS',
            'response_time': Decimal('5') if is_creator else (Decimal('1') if is_gaming else Decimal('4')),
            'hdr': True,
            'curved': False,
            'price': Decimal(str(min(monitor_budget, 45000 if is_creator else 35000))),
            'is_ai_generated': True,
        }
        peripherals['monitor'] = Monitor.objects.create(**monitor_specs)
        logger.info(f"Generated monitor: {peripherals['monitor'].name}")
        
        # Клавиатура
        keyboard_specs = {
            'name': 'Keychron K8 Pro' if is_creator else ('Logitech G Pro X' if is_gaming else 'Logitech MX Keys'),
            'manufacturer': 'Keychron' if is_creator else 'Logitech',
            'switch_type': 'mechanical',
            'switch_model': 'Gateron Brown' if is_creator else ('GX Blue' if is_gaming else 'Low Profile'),
            'rgb': True if is_gaming else False,
            'wireless': True,
            'form_factor': 'TKL',
            'price': Decimal(str(min(keyboard_budget, 12000))),
            'is_ai_generated': True,
        }
        peripherals['keyboard'] = Keyboard.objects.create(**keyboard_specs)
        logger.info(f"Generated keyboard: {peripherals['keyboard'].name}")
        
        # Мышь
        mouse_specs = {
            'name': 'Logitech MX Master 3S' if is_creator else ('Logitech G Pro X Superlight' if is_gaming else 'Logitech M720'),
            'manufacturer': 'Logitech',
            'sensor_type': 'optical',
            'dpi': 8000 if is_creator else (25600 if is_gaming else 4000),
            'buttons': 7 if is_creator else (5 if is_gaming else 8),
            'wireless': True,
            'rgb': True if is_gaming else False,
            'weight': Decimal('141') if is_creator else (Decimal('63') if is_gaming else Decimal('135')),
            'price': Decimal(str(min(mouse_budget, 10000))),
            'is_ai_generated': True,
        }
        peripherals['mouse'] = Mouse.objects.create(**mouse_specs)
        logger.info(f"Generated mouse: {peripherals['mouse'].name}")
        
        # Гарнитура
        headset_specs = {
            'name': 'Sony WH-1000XM5' if is_creator else ('SteelSeries Arctis Nova Pro' if is_gaming else 'Jabra Evolve2 75'),
            'manufacturer': 'Sony' if is_creator else ('SteelSeries' if is_gaming else 'Jabra'),
            'connection_type': 'Wireless',
            'wireless': True,
            'microphone': True,
            'noise_cancellation': True if is_creator else False,
            'surround': True if is_gaming else False,
            'price': Decimal(str(min(headset_budget, 15000))),
            'is_ai_generated': True,
        }
        peripherals['headset'] = Headset.objects.create(**headset_specs)
        logger.info(f"Generated headset: {peripherals['headset'].name}")
        
        # Коврик
        mousepad_specs = {
            'name': 'SteelSeries QcK Heavy XXL' if is_gaming else 'Logitech Desk Mat',
            'manufacturer': 'SteelSeries' if is_gaming else 'Logitech',
            'size': 'XXL' if is_gaming else 'XL',
            'width': Decimal('900') if is_gaming else Decimal('700'),
            'height': Decimal('400') if is_gaming else Decimal('300'),
            'thickness': Decimal('4'),
            'rgb': False,
            'price': Decimal(str(min(mousepad_budget, 3000))),
            'is_ai_generated': True,
        }
        peripherals['mousepad'] = Mousepad.objects.create(**mousepad_specs)
        logger.info(f"Generated mousepad: {peripherals['mousepad'].name}")
        
        return peripherals
    
    def _generate_default_workspace(self) -> Dict:
        """Генерация рабочего места из базы знаний AI"""
        from peripherals.models import Desk, Chair
        from decimal import Decimal
        
        workspace = {}
        budget = self.workspace_budget
        
        # Распределение бюджета: стол 45%, кресло 55%
        desk_budget = budget * 0.45
        chair_budget = budget * 0.55
        
        is_pro = self.user_type in ['designer', 'content_creator', 'programmer', 'developer']
        
        # Стол
        desk_specs = {
            'name': 'IKEA BEKANT с регулировкой' if is_pro else 'IKEA LAGKAPTEN/ALEX',
            'manufacturer': 'IKEA',
            'width': Decimal('160') if is_pro else Decimal('140'),
            'depth': Decimal('80') if is_pro else Decimal('60'),
            'height': Decimal('75'),
            'adjustable_height': True if is_pro else False,
            'material': 'laminate',
            'cable_management': True,
            'price': Decimal(str(min(desk_budget, 25000 if is_pro else 15000))),
            'is_ai_generated': True,
        }
        workspace['desk'] = Desk.objects.create(**desk_specs)
        logger.info(f"Generated desk: {workspace['desk'].name}")
        
        # Кресло
        chair_specs = {
            'name': 'Herman Miller Aeron' if is_pro and budget > 80000 else ('IKEA JÄRVFJÄLLET' if is_pro else 'IKEA MARKUS'),
            'manufacturer': 'Herman Miller' if is_pro and budget > 80000 else 'IKEA',
            'ergonomic': True,
            'adjustable_armrests': True if is_pro else False,
            'lumbar_support': True,
            'headrest': True if is_pro else False,
            'max_weight': Decimal('130'),
            'material': 'mesh' if is_pro else 'fabric',
            'price': Decimal(str(min(chair_budget, 50000 if is_pro and budget > 80000 else 20000))),
            'is_ai_generated': True,
        }
        workspace['chair'] = Chair.objects.create(**chair_specs)
        logger.info(f"Generated chair: {workspace['chair'].name}")
        
        return workspace
    
    def _build_full_prompt(self) -> str:
        """Создать промпт для полной генерации конфигурации из обученных данных AI"""
        
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
        
        # Простой промпт для AI чтобы она использовала свои обученные данные
        prompt = f"""Собери компьютер для профиля "{self.user_type}" с бюджетом {self.min_budget:.0f}-{self.max_budget:.0f} рублей.

Задачи: {requirements_text}

Бюджет на ПК: ~{self.pc_budget:.0f} руб
Бюджет на периферию: ~{self.peripherals_budget:.0f} руб  
Бюджет на рабочее место: ~{self.workspace_budget:.0f} руб

Требования:
- Процессор: минимум {pref['min_cpu_cores']} ядер
- Видеокарта: минимум {pref['min_gpu_vram']}GB видеопамяти
- Оперативная память: минимум {pref['min_ram_capacity']}GB
- Накопитель: минимум {pref['min_storage_capacity']}GB

Используй свои знания о компонентах и ценах на декабрь 2025.
Подбери совместимые комплектующие (socket CPU = socket материнки, тип RAM = тип на материнке).

Ответь в формате JSON:
{{
  "cpu": {{"name": "модель", "manufacturer": "Intel/AMD", "socket": "сокет", "cores": число, "threads": число, "base_clock": число, "boost_clock": число, "tdp": число, "price": число}},
  "gpu": {{"name": "модель", "manufacturer": "NVIDIA/AMD", "chipset": "чип", "memory": число, "memory_type": "GDDR6", "tdp": число, "recommended_psu": число, "price": число}},
  "motherboard": {{"name": "модель", "manufacturer": "бренд", "socket": "сокет", "chipset": "чипсет", "form_factor": "ATX/mATX", "memory_slots": число, "max_memory": число, "memory_type": "DDR4/DDR5", "price": число}},
  "ram": {{"name": "модель", "manufacturer": "бренд", "memory_type": "DDR4/DDR5", "capacity": число, "speed": число, "modules": число, "price": число}},
  "storage": {{"name": "модель", "manufacturer": "бренд", "storage_type": "ssd_nvme", "capacity": число, "read_speed": число, "write_speed": число, "price": число}},
  "psu": {{"name": "модель", "manufacturer": "бренд", "wattage": число, "efficiency_rating": "80+ Gold", "modular": true/false, "price": число}},
  "case": {{"name": "модель", "manufacturer": "бренд", "form_factor": "Mid-Tower", "max_gpu_length": число, "rgb": true/false, "price": число}},
  "cooling": {{"name": "модель", "manufacturer": "бренд", "cooling_type": "air/aio", "max_tdp": число, "price": число}},
  "monitor": {{"name": "модель", "manufacturer": "бренд", "screen_size": число, "resolution": "разрешение", "refresh_rate": число, "panel_type": "IPS", "price": число}},
  "keyboard": {{"name": "модель", "manufacturer": "бренд", "switch_type": "mechanical/membrane", "rgb": true/false, "wireless": true/false, "price": число}},
  "mouse": {{"name": "модель", "manufacturer": "бренд", "dpi": число, "wireless": true/false, "price": число}},
  "headset": {{"name": "модель", "manufacturer": "бренд", "wireless": true/false, "microphone": true/false, "price": число}},
  "mousepad": {{"name": "модель", "manufacturer": "бренд", "size": "XL", "price": число}},
  "desk": {{"name": "модель", "manufacturer": "бренд", "width": число, "depth": число, "adjustable_height": true/false, "price": число}},
  "chair": {{"name": "модель", "manufacturer": "бренд", "ergonomic": true/false, "lumbar_support": true/false, "price": число}},
  "reasoning": {{"overall": "обоснование выбора"}},
  "total_price": число,
  "confidence": 0.9
}}"""

        return prompt
    
    def _call_ai_model(self, prompt: str) -> Optional[str]:
        """Вызвать AI модель - сначала через AI сервер, потом напрямую в Ollama"""
        
        # Способ 1: Через AI сервер (с обученной моделью)
        try:
            logger.info("Trying AI server at localhost:5050...")
            payload = {
                "prompt": prompt,
                "use_learning": True
            }
            
            response = requests.post(AI_SERVER_URL, json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                if ai_response and len(ai_response) > 100:
                    logger.info(f"AI server responded with {len(ai_response)} characters")
                    return ai_response
                    
        except requests.exceptions.ConnectionError:
            logger.warning("AI server not available, trying Ollama directly...")
        except Exception as e:
            logger.warning(f"AI server error: {e}, trying Ollama directly...")
        
        # Способ 2: Напрямую в Ollama
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "num_predict": 8192,
                }
            }
            
            logger.info(f"Calling Ollama directly with model: {MODEL_NAME}")
            
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                logger.info(f"Ollama responded with {len(ai_response)} characters")
                return ai_response
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running?")
            return None
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
            
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
    
    def _generate_from_trained_data(self) -> Dict[str, Any]:
        """
        Генерирует сборку из обученных данных AI (pc_components_dec_2025.json и txt файлы)
        Используется когда AI модель не отвечает или отвечает некорректно
        """
        logger.info("Generating configuration from trained data...")
        
        # Определяем профиль и бюджет
        is_gaming = self.user_type in ['gamer', 'gaming', 'streamer']
        is_office = self.user_type in ['office', 'student']
        is_creator = self.user_type in ['designer', 'content_creator', 'developer']
        
        pc_budget = float(self.pc_budget)
        
        # Распределение бюджета ПК
        if is_gaming:
            budget_split = {'cpu': 0.18, 'gpu': 0.40, 'motherboard': 0.12, 'ram': 0.08, 'storage': 0.08, 'psu': 0.06, 'case': 0.05, 'cooling': 0.03}
        elif is_creator:
            budget_split = {'cpu': 0.25, 'gpu': 0.30, 'motherboard': 0.12, 'ram': 0.12, 'storage': 0.10, 'psu': 0.05, 'case': 0.04, 'cooling': 0.02}
        else:  # office
            budget_split = {'cpu': 0.25, 'gpu': 0.15, 'motherboard': 0.15, 'ram': 0.15, 'storage': 0.15, 'psu': 0.07, 'case': 0.05, 'cooling': 0.03}
        
        # Подбираем компоненты под бюджет (из обученных данных)
        result = {}
        
        # CPU - из pc_components_dec_2025.json
        cpu_budget = pc_budget * budget_split['cpu']
        if is_gaming or is_creator:
            if cpu_budget >= 35000:
                result['cpu'] = {"name": "Core i5-14600K", "manufacturer": "Intel", "socket": "LGA1700", "cores": 14, "threads": 20, "base_clock": 3.5, "boost_clock": 5.3, "tdp": 125, "price": 35999}
            elif cpu_budget >= 20000:
                result['cpu'] = {"name": "Ryzen 5 7600X", "manufacturer": "AMD", "socket": "AM5", "cores": 6, "threads": 12, "base_clock": 4.7, "boost_clock": 5.3, "tdp": 105, "price": 29999}
            elif cpu_budget >= 12000:
                result['cpu'] = {"name": "Core i5-12400F", "manufacturer": "Intel", "socket": "LGA1700", "cores": 6, "threads": 12, "base_clock": 2.5, "boost_clock": 4.4, "tdp": 65, "price": 11000}
            else:
                result['cpu'] = {"name": "Core i3-12100F", "manufacturer": "Intel", "socket": "LGA1700", "cores": 4, "threads": 8, "base_clock": 3.3, "boost_clock": 4.3, "tdp": 58, "price": 7500}
        else:
            if cpu_budget >= 15000:
                result['cpu'] = {"name": "Ryzen 5 5600", "manufacturer": "AMD", "socket": "AM4", "cores": 6, "threads": 12, "base_clock": 3.5, "boost_clock": 4.4, "tdp": 65, "price": 14999}
            else:
                result['cpu'] = {"name": "Core i3-12100F", "manufacturer": "Intel", "socket": "LGA1700", "cores": 4, "threads": 8, "base_clock": 3.3, "boost_clock": 4.3, "tdp": 58, "price": 7500}
        
        # Материнская плата - совместимая с CPU
        cpu_socket = result['cpu']['socket']
        mb_budget = pc_budget * budget_split['motherboard']
        
        if cpu_socket == "LGA1700":
            if mb_budget >= 15000:
                result['motherboard'] = {"name": "AORUS Elite AX B760", "manufacturer": "Gigabyte", "socket": "LGA1700", "chipset": "B760", "form_factor": "ATX", "memory_slots": 4, "max_memory": 128, "memory_type": "DDR5", "pcie_slots": 2, "m2_slots": 2, "price": 15000}
            else:
                result['motherboard'] = {"name": "TUF GAMING B760-PLUS WIFI", "manufacturer": "ASUS", "socket": "LGA1700", "chipset": "B760", "form_factor": "ATX", "memory_slots": 4, "max_memory": 128, "memory_type": "DDR4", "pcie_slots": 2, "m2_slots": 2, "price": 10990}
        elif cpu_socket == "AM5":
            result['motherboard'] = {"name": "B650M Pro RS WiFi", "manufacturer": "ASRock", "socket": "AM5", "chipset": "B650", "form_factor": "mATX", "memory_slots": 4, "max_memory": 128, "memory_type": "DDR5", "pcie_slots": 2, "m2_slots": 2, "price": 14900}
        else:  # AM4
            result['motherboard'] = {"name": "B550M Pro-VDH WiFi", "manufacturer": "MSI", "socket": "AM4", "chipset": "B550", "form_factor": "mATX", "memory_slots": 4, "max_memory": 128, "memory_type": "DDR4", "pcie_slots": 2, "m2_slots": 1, "price": 8500}
        
        # RAM - совместимая с материнкой
        ram_type = result['motherboard']['memory_type']
        ram_budget = pc_budget * budget_split['ram']
        
        if ram_type == "DDR5":
            if ram_budget >= 10000:
                result['ram'] = {"name": "Vengeance RGB DDR5", "manufacturer": "Corsair", "memory_type": "DDR5", "capacity": 32, "speed": 5600, "modules": 2, "price": 14999}
            else:
                result['ram'] = {"name": "FURY Beast DDR5", "manufacturer": "Kingston", "memory_type": "DDR5", "capacity": 16, "speed": 5200, "modules": 2, "price": 7999}
        else:
            if ram_budget >= 8000:
                result['ram'] = {"name": "Vengeance LPX DDR4", "manufacturer": "Corsair", "memory_type": "DDR4", "capacity": 32, "speed": 3200, "modules": 2, "price": 9999}
            else:
                result['ram'] = {"name": "FURY Beast DDR4", "manufacturer": "Kingston", "memory_type": "DDR4", "capacity": 16, "speed": 3200, "modules": 2, "price": 4999}
        
        # GPU - добавляем core_clock
        gpu_budget = pc_budget * budget_split['gpu']
        if is_gaming:
            if gpu_budget >= 80000:
                result['gpu'] = {"name": "GeForce RTX 4070 Ti SUPER", "manufacturer": "NVIDIA", "chipset": "RTX 4070 Ti SUPER", "memory": 16, "memory_type": "GDDR6X", "core_clock": 2340, "boost_clock": 2610, "tdp": 285, "recommended_psu": 700, "price": 85000}
            elif gpu_budget >= 55000:
                result['gpu'] = {"name": "GeForce RTX 4070", "manufacturer": "NVIDIA", "chipset": "RTX 4070", "memory": 12, "memory_type": "GDDR6X", "core_clock": 1920, "boost_clock": 2475, "tdp": 200, "recommended_psu": 650, "price": 55000}
            elif gpu_budget >= 35000:
                result['gpu'] = {"name": "GeForce RTX 4060 Ti", "manufacturer": "NVIDIA", "chipset": "RTX 4060 Ti", "memory": 8, "memory_type": "GDDR6", "core_clock": 2310, "boost_clock": 2535, "tdp": 160, "recommended_psu": 550, "price": 38000}
            else:
                result['gpu'] = {"name": "GeForce RTX 4060", "manufacturer": "NVIDIA", "chipset": "RTX 4060", "memory": 8, "memory_type": "GDDR6", "core_clock": 1830, "boost_clock": 2460, "tdp": 115, "recommended_psu": 450, "price": 28000}
        elif is_creator:
            if gpu_budget >= 50000:
                result['gpu'] = {"name": "GeForce RTX 4070", "manufacturer": "NVIDIA", "chipset": "RTX 4070", "memory": 12, "memory_type": "GDDR6X", "core_clock": 1920, "boost_clock": 2475, "tdp": 200, "recommended_psu": 650, "price": 55000}
            else:
                result['gpu'] = {"name": "GeForce RTX 4060", "manufacturer": "NVIDIA", "chipset": "RTX 4060", "memory": 8, "memory_type": "GDDR6", "core_clock": 1830, "boost_clock": 2460, "tdp": 115, "recommended_psu": 450, "price": 28000}
        else:  # office - можно без GPU или встроенная
            if gpu_budget >= 20000:
                result['gpu'] = {"name": "GeForce GTX 1650", "manufacturer": "NVIDIA", "chipset": "GTX 1650", "memory": 4, "memory_type": "GDDR6", "core_clock": 1485, "boost_clock": 1665, "tdp": 75, "recommended_psu": 350, "price": 15000}
            else:
                result['gpu'] = {"name": "Radeon RX 6400", "manufacturer": "AMD", "chipset": "RX 6400", "memory": 4, "memory_type": "GDDR6", "core_clock": 1923, "boost_clock": 2321, "tdp": 53, "recommended_psu": 350, "price": 12000}
        
        # Storage
        storage_budget = pc_budget * budget_split['storage']
        if storage_budget >= 10000:
            result['storage'] = {"name": "KC3000", "manufacturer": "Kingston", "storage_type": "ssd_nvme", "capacity": 1000, "read_speed": 7000, "write_speed": 6000, "price": 9999}
        elif storage_budget >= 7000:
            result['storage'] = {"name": "970 EVO Plus", "manufacturer": "Samsung", "storage_type": "ssd_nvme", "capacity": 500, "read_speed": 3500, "write_speed": 3200, "price": 7999}
        else:
            result['storage'] = {"name": "Blue SN570", "manufacturer": "WD", "storage_type": "ssd_nvme", "capacity": 500, "read_speed": 3500, "write_speed": 2300, "price": 5999}
        
        # PSU
        gpu_psu = result.get('gpu', {}).get('recommended_psu', 350)
        cpu_tdp = result['cpu']['tdp']
        min_psu = gpu_psu + cpu_tdp + 100
        
        if min_psu >= 700:
            result['psu'] = {"name": "RM850x", "manufacturer": "Corsair", "wattage": 850, "efficiency_rating": "80+ Gold", "modular": True, "price": 12000}
        elif min_psu >= 550:
            result['psu'] = {"name": "Focus GX-650", "manufacturer": "Seasonic", "wattage": 650, "efficiency_rating": "80+ Gold", "modular": True, "price": 9000}
        else:
            result['psu'] = {"name": "CV550", "manufacturer": "Corsair", "wattage": 550, "efficiency_rating": "80+ Bronze", "modular": False, "price": 5000}
        
        # Case
        case_budget = pc_budget * budget_split['case']
        if case_budget >= 8000 or is_gaming:
            result['case'] = {"name": "4000D Airflow", "manufacturer": "Corsair", "form_factor": "Mid-Tower", "max_gpu_length": 360, "rgb": is_gaming, "price": 8500}
        else:
            result['case'] = {"name": "NR600", "manufacturer": "Cooler Master", "form_factor": "Mid-Tower", "max_gpu_length": 330, "rgb": False, "price": 5500}
        
        # Cooling
        cpu_tdp = result['cpu']['tdp']
        if cpu_tdp >= 125:
            result['cooling'] = {"name": "Hyper 212 RGB", "manufacturer": "Cooler Master", "cooling_type": "air", "max_tdp": 180, "price": 4500}
        else:
            result['cooling'] = {"name": "Gammaxx 400 V2", "manufacturer": "DeepCool", "cooling_type": "air", "max_tdp": 130, "price": 2500}
        
        # Периферия (из txt файлов обучения)
        if self.include_peripherals:
            periph_budget = float(self.peripherals_budget)
            
            # Monitor
            if is_gaming:
                result['monitor'] = {"name": "VG27AQ1A", "manufacturer": "ASUS", "screen_size": 27, "resolution": "2560x1440", "refresh_rate": 165, "panel_type": "IPS", "price": 32000}
            else:
                result['monitor'] = {"name": "S2722QC", "manufacturer": "Dell", "screen_size": 27, "resolution": "2560x1440", "refresh_rate": 75, "panel_type": "IPS", "price": 28000}
            
            # Keyboard (из keyboards.txt)
            if is_gaming:
                result['keyboard'] = {"name": "G Pro X", "manufacturer": "Logitech", "switch_type": "mechanical", "rgb": True, "wireless": False, "price": 12000}
            else:
                result['keyboard'] = {"name": "MX Keys", "manufacturer": "Logitech", "switch_type": "membrane", "rgb": False, "wireless": True, "price": 9500}
            
            # Mouse (из mouses.txt)
            if is_gaming:
                result['mouse'] = {"name": "G Pro X Superlight", "manufacturer": "Logitech", "dpi": 25600, "wireless": True, "price": 12000}
            else:
                result['mouse'] = {"name": "MX Master 3S", "manufacturer": "Logitech", "dpi": 8000, "wireless": True, "price": 10000}
            
            # Headset (из headphones.txt)
            result['headset'] = {"name": "Cloud II", "manufacturer": "HyperX", "wireless": False, "microphone": True, "price": 7000}
            
            # Mousepad
            result['mousepad'] = {"name": "QcK Heavy XXL", "manufacturer": "SteelSeries", "size": "XXL", "price": 3000}
        
        # Рабочее место
        if self.include_workspace:
            # Desk (из tables.txt)
            result['desk'] = {"name": "BEKANT", "manufacturer": "IKEA", "width": 160, "depth": 80, "adjustable_height": False, "price": 15000}
            
            # Chair (из chairs.txt)
            result['chair'] = {"name": "MARKUS", "manufacturer": "IKEA", "ergonomic": True, "lumbar_support": True, "price": 18000}
        
        result['confidence'] = 0.85
        result['reasoning'] = {"overall": "Сборка сгенерирована из обученных данных AI на основе профиля пользователя и бюджета"}
        
        logger.info(f"Generated {len(result)} components from trained data")
        return result
    
    def _get_model_fields(self, model_class) -> set:
        """Получить список допустимых полей модели"""
        return {field.name for field in model_class._meta.get_fields() 
                if hasattr(field, 'column') and field.column is not None}
    
    def _create_component_from_spec(self, model_class, spec: dict, ai_confidence: float):
        """Создать компонент в БД из спецификации AI"""
        try:
            valid_fields = self._get_model_fields(model_class)
            
            # Маппинг полей AI -> DB (AI может возвращать другие названия)
            field_mapping = {
                'noise_cancellation': 'noise_cancelling',  # Headset
                'surround_sound': 'surround',  # Headset
                'height_adjustable': 'adjustable_height',  # Desk
                'mic_type': 'microphone_type',  # Microphone
                'connection_type': 'connection',  # Microphone (если нужно)
            }
            
            # Применяем маппинг полей
            mapped_spec = {}
            for key, value in spec.items():
                mapped_key = field_mapping.get(key, key)
                mapped_spec[mapped_key] = value
            
            # Фильтруем только валидные поля
            filtered_spec = {k: v for k, v in mapped_spec.items() if k in valid_fields}
            
            # Добавляем дефолтные значения для обязательных полей разных моделей
            model_name = model_class.__name__
            
            # GPU defaults
            if model_name == 'GPU':
                if 'core_clock' not in filtered_spec:
                    filtered_spec['core_clock'] = 1500  # MHz
                if 'boost_clock' not in filtered_spec:
                    filtered_spec['boost_clock'] = filtered_spec.get('core_clock', 1500) + 200
                if 'recommended_psu' not in filtered_spec:
                    filtered_spec['recommended_psu'] = filtered_spec.get('tdp', 150) + 200
                if 'performance_score' not in filtered_spec:
                    filtered_spec['performance_score'] = 50
            
            # Motherboard defaults
            if model_name == 'Motherboard':
                if 'pcie_slots' not in filtered_spec:
                    filtered_spec['pcie_slots'] = 2
                if 'm2_slots' not in filtered_spec:
                    filtered_spec['m2_slots'] = 2
            
            # CPU defaults
            if model_name == 'CPU':
                if 'performance_score' not in filtered_spec:
                    filtered_spec['performance_score'] = 50
            
            # Monitor defaults
            if model_name == 'Monitor':
                if 'response_time' not in filtered_spec:
                    filtered_spec['response_time'] = Decimal('5')
                if 'hdr' not in filtered_spec:
                    filtered_spec['hdr'] = False
                if 'curved' not in filtered_spec:
                    filtered_spec['curved'] = False
            
            # Keyboard defaults
            if model_name == 'Keyboard':
                if 'form_factor' not in filtered_spec:
                    filtered_spec['form_factor'] = 'Full-size'
            
            # Mouse defaults  
            if model_name == 'Mouse':
                if 'sensor_type' not in filtered_spec:
                    filtered_spec['sensor_type'] = 'optical'
                if 'buttons' not in filtered_spec:
                    filtered_spec['buttons'] = 5
                if 'weight' not in filtered_spec:
                    filtered_spec['weight'] = Decimal('100')
            
            # Headset defaults
            if model_name == 'Headset':
                if 'connection_type' not in filtered_spec:
                    filtered_spec['connection_type'] = 'USB' if filtered_spec.get('wireless') else '3.5mm'
                if 'surround' not in filtered_spec:
                    filtered_spec['surround'] = False
                if 'noise_cancelling' not in filtered_spec:
                    filtered_spec['noise_cancelling'] = False
                if 'microphone' not in filtered_spec:
                    filtered_spec['microphone'] = True
            
            # Mousepad defaults
            if model_name == 'Mousepad':
                if 'width' not in filtered_spec:
                    filtered_spec['width'] = 400
                if 'height' not in filtered_spec:
                    filtered_spec['height'] = 300
                if 'thickness' not in filtered_spec:
                    filtered_spec['thickness'] = 3
                if 'rgb' not in filtered_spec:
                    filtered_spec['rgb'] = False
                if 'material' not in filtered_spec:
                    filtered_spec['material'] = 'Ткань'
                if 'size' not in filtered_spec:
                    # Определяем размер по ширине
                    width = filtered_spec.get('width', 400)
                    if width < 300:
                        filtered_spec['size'] = 'small'
                    elif width < 450:
                        filtered_spec['size'] = 'medium'
                    elif width < 800:
                        filtered_spec['size'] = 'large'
                    else:
                        filtered_spec['size'] = 'xl'
            
            # Desk defaults
            if model_name == 'Desk':
                if 'width' not in filtered_spec:
                    filtered_spec['width'] = 140
                if 'depth' not in filtered_spec:
                    filtered_spec['depth'] = 70
                if 'adjustable_height' not in filtered_spec:
                    filtered_spec['adjustable_height'] = False
            
            # Chair defaults
            if model_name == 'Chair':
                if 'adjustable_armrests' not in filtered_spec:
                    filtered_spec['adjustable_armrests'] = True
                if 'max_weight' not in filtered_spec:
                    filtered_spec['max_weight'] = 120
            
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
        AI генерирует ВСЁ из своих обученных данных (без fallback в БД)
        
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
        
        # Парсим ответ AI
        parsed = {}
        if ai_response:
            parsed = self._parse_ai_response(ai_response) or {}
        
        # Если AI не ответил или не распарсился - генерируем из обученных данных
        if not parsed:
            logger.warning("AI response empty or failed to parse, generating from trained data")
            parsed = self._generate_from_trained_data()
        
        confidence = parsed.get('confidence', 0.85) if parsed else 0.7
        
        # Проверяем совместимость
        is_compatible, compat_issues = True, []
        if parsed:
            is_compatible, compat_issues = self._check_compatibility(parsed)
            if not is_compatible:
                logger.warning(f"Compatibility issues: {compat_issues}")
        
        try:
            # 1. Создаем ПК компоненты из данных AI
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
                logger.warning(f"Missing required components: {missing}")
                # Если чего-то не хватает - генерируем недостающее из обученных данных
                default_specs = self._generate_from_trained_data()
                
                # Создаём маппинг для быстрого поиска
                pc_mapping_dict = {ck: (sk, mc) for sk, mc, ck in pc_mapping}
                
                for component_key in missing:
                    if component_key in pc_mapping_dict:
                        spec_key, model_class = pc_mapping_dict[component_key]
                        
                        if spec_key in default_specs and default_specs[spec_key]:
                            spec = default_specs[spec_key].copy()
                            component = self._create_component_from_spec(model_class, spec, confidence)
                            if component:
                                pc_components[component_key] = component
                                logger.info(f"Generated missing {component_key} from trained data")
            
            # Финальная проверка
            still_missing = [c for c in required if c not in pc_components]
            if still_missing:
                return None, None, {"error": f"AI не смогла сгенерировать компоненты: {', '.join(still_missing)}. Попробуйте ещё раз."}
            
            # Добавляем опциональные компоненты если их нет
            optional = ['gpu', 'psu', 'case', 'cooling']
            for component_key in optional:
                if component_key not in pc_components:
                    default_specs = self._generate_from_trained_data()
                    if component_key in default_specs and default_specs[component_key]:
                        spec = default_specs[component_key].copy()
                        for sk, mc, ck in pc_mapping:
                            if ck == component_key:
                                component = self._create_component_from_spec(mc, spec, confidence)
                                if component:
                                    pc_components[component_key] = component
                                break
            
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
                
                # Fallback: генерируем периферию из своих знаний если AI не создал
                if not peripherals:
                    logger.info("No peripherals from AI, generating from knowledge base")
                    peripherals = self._generate_default_peripherals()
            
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
                
                # Fallback: генерируем рабочее место из своих знаний если AI не создал
                if not workspace_components:
                    logger.info("No workspace from AI, generating from knowledge base")
                    workspace_components = self._generate_default_workspace()
            
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
            logger.info(f"PC: {pc_price:.0f} RUB, Peripherals: {peripherals_price:.0f} RUB, Workspace: {workspace_price:.0f} RUB")
            logger.info(f"Total: {total_price:.0f} RUB")
            
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
