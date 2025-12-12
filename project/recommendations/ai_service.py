
import logging
import requests
import json
import os
from decimal import Decimal
from typing import Optional, Tuple
from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling



OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
AI_SERVER_URL = os.environ.get("AI_SERVER_URL", "http://localhost:5050")
NOVA_API_URL = f"{AI_SERVER_URL}/api/chat"
MODEL_NAME = os.environ.get("AI_MODEL_NAME", "deepseek-project-model:latest")
USE_NOVA_SERVER = os.environ.get("USE_NOVA_SERVER", "true").lower() == "true"


logger = logging.getLogger(__name__)


class AIConfigurationService:
    
    
    def __init__(self, user_profile_data: dict):
        self.user_type = user_profile_data.get('user_type', 'gamer')
        self.min_budget = Decimal(str(user_profile_data.get('min_budget', 50000)))
        self.max_budget = Decimal(str(user_profile_data.get('max_budget', 100000)))
        self.priority = user_profile_data.get('priority', 'performance')
        self.requirements = {
            'multitasking': user_profile_data.get('multitasking', False),
            'work_with_4k': user_profile_data.get('work_with_4k', False),
            'vr_support': user_profile_data.get('vr_support', False),
            'video_editing': user_profile_data.get('video_editing', False),
            'gaming': user_profile_data.get('gaming', False),
            'streaming': user_profile_data.get('streaming', False),
        }
    
    def _get_available_components(self) -> dict:
        
        return {
            'cpus': list(CPU.objects.filter(price__lte=self.max_budget * Decimal('0.3')).values(
                'id', 'name', 'manufacturer', 'socket', 'cores', 'threads', 
                'base_clock', 'boost_clock', 'tdp', 'price', 'performance_score'
            )),
            'gpus': list(GPU.objects.filter(price__lte=self.max_budget * Decimal('0.5')).values(
                'id', 'name', 'manufacturer', 'memory', 'memory_type',
                'tdp', 'price', 'performance_score'
            )),
            'motherboards': list(Motherboard.objects.filter(price__lte=self.max_budget * Decimal('0.15')).values(
                'id', 'name', 'manufacturer', 'socket', 'chipset', 
                'form_factor', 'memory_type', 'memory_slots', 'price'
            )),
            'ram': list(RAM.objects.filter(price__lte=self.max_budget * Decimal('0.15')).values(
                'id', 'name', 'manufacturer', 'memory_type', 'capacity', 
                'speed', 'modules', 'price'
            )),
            'storage': list(Storage.objects.filter(price__lte=self.max_budget * Decimal('0.15')).values(
                'id', 'name', 'manufacturer', 'storage_type', 'capacity',
                'read_speed', 'write_speed', 'price'
            )),
            'psu': list(PSU.objects.filter(price__lte=self.max_budget * Decimal('0.1')).values(
                'id', 'name', 'manufacturer', 'wattage', 'efficiency_rating', 
                'modular', 'price'
            )),
            'cases': list(Case.objects.filter(price__lte=self.max_budget * Decimal('0.1')).values(
                'id', 'name', 'manufacturer', 'form_factor', 'rgb', 'price'
            )),
            'cooling': list(Cooling.objects.filter(price__lte=self.max_budget * Decimal('0.1')).values(
                'id', 'name', 'manufacturer', 'cooling_type', 'max_tdp', 
                'noise_level', 'price'
            )),
        }
    
    def _build_ai_prompt(self, components: dict) -> str:
    
        active_requirements = [k for k, v in self.requirements.items() if v]
        requirements_text = ", ".join(active_requirements) if active_requirements else "стандартное использование"
        
        
        components_text = json.dumps(components, ensure_ascii=False, indent=2, default=str)
        
        prompt = f"""Ты - эксперт по сборке компьютеров. Подбери оптимальную конфигурацию ПК.

ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
- Тип: {self.user_type}
- Бюджет: от {self.min_budget} до {self.max_budget} рублей
- Приоритет: {self.priority}
- Требования: {requirements_text}

ДОСТУПНЫЕ КОМПОНЕНТЫ:
{components_text}

ЗАДАЧА:
Выбери по одному компоненту каждого типа, которые:
1. Совместимы между собой (сокет CPU = сокет материнской платы, тип RAM совпадает)
2. Укладываются в бюджет {self.max_budget} рублей
3. Оптимальны для профиля "{self.user_type}" с требованиями "{requirements_text}"

ВАЖНО: Ответь СТРОГО в формате JSON без дополнительного текста:
{{
    "cpu_id": <число>,
    "gpu_id": <число или null>,
    "motherboard_id": <число>,
    "ram_id": <число>,
    "storage_id": <число>,
    "psu_id": <число>,
    "case_id": <число>,
    "cooling_id": <число>,
    "reasoning": {{
        "cpu": "<причина выбора CPU>",
        "gpu": "<причина выбора GPU>",
        "motherboard": "<причина выбора материнской платы>",
        "ram": "<причина выбора RAM>",
        "storage": "<причина выбора накопителя>",
        "psu": "<причина выбора БП>",
        "case": "<причина выбора корпуса>",
        "cooling": "<причина выбора охлаждения>"
    }},
    "total_estimated_price": <общая цена>,
    "summary": "<краткое описание сборки на русском языке>"
}}"""
        
        return prompt
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
       
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  
                    "top_p": 0.9
                }
            }
            
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                print(f"[AI] Ollama error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("[AI] Cannot connect to Ollama. Is it running?")
            return None
        except requests.exceptions.Timeout:
            print("[AI] Ollama request timed out")
            return None
        except Exception as e:
            print(f"[AI] Error calling Ollama: {e}")
            return None
    
    def _parse_ai_response(self, response: str) -> Optional[dict]:
        
        try:
            
            import re
            
            
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return None
    
    def generate_ai_configuration(self, user) -> Tuple[Optional[dict], dict]:
   
        from recommendations.models import PCConfiguration, Recommendation
        
      
        components = self._get_available_components()
        
        
        if not any(components.values()):
            return None, {"error": "Нет доступных компонентов в базе данных"}
        
        
        prompt = self._build_ai_prompt(components)
        logger.info("Sending request to Ollama...")
        
        ai_response = self._call_ollama(prompt)
        
        if not ai_response:
            logger.warning("No response from Ollama, falling back to rule-based selection")
            return None, {"error": "ИИ недоступен, используется алгоритмический подбор"}
        
        
        parsed = self._parse_ai_response(ai_response)
        
        if not parsed:
            logger.error(f"Failed to parse AI response: {ai_response[:200]}...")
            return None, {"error": "Не удалось распознать ответ ИИ"}
        
        
        try:
            cpu = CPU.objects.filter(id=parsed.get('cpu_id')).first()
            gpu = GPU.objects.filter(id=parsed.get('gpu_id')).first() if parsed.get('gpu_id') else None
            motherboard = Motherboard.objects.filter(id=parsed.get('motherboard_id')).first()
            ram = RAM.objects.filter(id=parsed.get('ram_id')).first()
            storage = Storage.objects.filter(id=parsed.get('storage_id')).first()
            psu = PSU.objects.filter(id=parsed.get('psu_id')).first()
            case = Case.objects.filter(id=parsed.get('case_id')).first()
            cooling = Cooling.objects.filter(id=parsed.get('cooling_id')).first()
            
            
            config = PCConfiguration.objects.create(
                user=user,
                name=f"AI-сборка для {self.user_type}",
                cpu=cpu,
                gpu=gpu,
                motherboard=motherboard,
                ram=ram,
                storage_primary=storage,
                psu=psu,
                case=case,
                cooling=cooling
            )
            
            config.calculate_total_price()
            config.save()
            
            
            reasoning = parsed.get('reasoning', {})
            for component_type, reason in reasoning.items():
                component = locals().get(component_type)
                if component and reason:
                    Recommendation.objects.create(
                        configuration=config,
                        component_type=component_type,
                        component_id=component.id if hasattr(component, 'id') else 0,
                        reason=reason
                    )
            
            return config, {
                "reasoning": reasoning,
                "summary": parsed.get('summary', 'Конфигурация подобрана ИИ'),
                "ai_used": True
            }
            
        except Exception as e:
            logger.error(f"Error creating AI configuration: {e}")
            return None, {"error": f"Ошибка создания конфигурации: {str(e)}"}
    
    def check_ollama_available(self) -> bool:
       
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error checking Ollama availability: {e}")
            return False
