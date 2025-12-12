
import logging
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
from peripherals.models import Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair
from recommendations.models import PCConfiguration, WorkspaceSetup, Recommendation

try:
    from .ai_service import AIRecommendationService
except ImportError:
    AIRecommendationService = None

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):

    pass


class ConfigurationService:

    
    def __init__(self, user_profile_data, use_ai=False):
        self.user_profile_data = user_profile_data  
        self.user_type = user_profile_data.get('user_type')
        self.min_budget = Decimal(user_profile_data.get('min_budget', 0))
        self.max_budget = Decimal(user_profile_data.get('max_budget', 0))
        self.priority = user_profile_data.get('priority', 'performance')
        self.requirements = {
            'multitasking': user_profile_data.get('multitasking', False),
            'work_with_4k': user_profile_data.get('work_with_4k', False),
            'vr_support': user_profile_data.get('vr_support', False),
            'video_editing': user_profile_data.get('video_editing', False),
            'gaming': user_profile_data.get('gaming', False),
            'streaming': user_profile_data.get('streaming', False),
        }
        
        
        self.ai_service = None
        self.ai_analysis = None
        if use_ai and AIRecommendationService:
            try:
                self.ai_service = AIRecommendationService()
                self.ai_analysis = self.ai_service.analyze_user_profile(
                    self.user_type,
                    self.requirements,
                    float(self.max_budget)
                )
                logger.info(f"AI analysis completed for user type: {self.user_type}")
            except Exception as e:
                logger.warning(f"AI service initialization failed: {e}. Falling back to rule-based system.")
    
    def get_budget_distribution(self):

        distributions = {
            'designer': {
                'cpu': 0.25,
                'gpu': 0.30,
                'ram': 0.15,
                'storage': 0.10,
                'motherboard': 0.08,
                'psu': 0.05,
                'cooling': 0.04,
                'case': 0.03,
            },
            'programmer': {
                'cpu': 0.30,
                'gpu': 0.15,
                'ram': 0.20,
                'storage': 0.15,
                'motherboard': 0.08,
                'psu': 0.05,
                'cooling': 0.04,
                'case': 0.03,
            },
            'gamer': {
                'cpu': 0.20,
                'gpu': 0.40,
                'ram': 0.12,
                'storage': 0.10,
                'motherboard': 0.08,
                'psu': 0.05,
                'cooling': 0.03,
                'case': 0.02,
            },
            'office': {
                'cpu': 0.25,
                'gpu': 0.10,
                'ram': 0.20,
                'storage': 0.20,
                'motherboard': 0.10,
                'psu': 0.07,
                'cooling': 0.05,
                'case': 0.03,
            },
            'student': {
                'cpu': 0.25,
                'gpu': 0.20,
                'ram': 0.18,
                'storage': 0.15,
                'motherboard': 0.10,
                'psu': 0.05,
                'cooling': 0.04,
                'case': 0.03,
            },
            'content_creator': {
                'cpu': 0.25,
                'gpu': 0.30,
                'ram': 0.15,
                'storage': 0.12,
                'motherboard': 0.08,
                'psu': 0.05,
                'cooling': 0.03,
                'case': 0.02,
            },
        }
        
        return distributions.get(self.user_type, distributions['student'])
    
    def select_cpu(self, budget):
        
        try:
            query = CPU.objects.filter(price__lte=budget)
            
            
            preferred_manufacturer = self.user_profile_data.get('preferred_cpu_manufacturer')
            if preferred_manufacturer and preferred_manufacturer != 'any':
                query = query.filter(manufacturer__icontains=preferred_manufacturer)
            
            min_cores = self.user_profile_data.get('min_cpu_cores', 4)
            if self.requirements['multitasking'] or self.requirements['video_editing']:
                min_cores = max(min_cores, 8)
            query = query.filter(cores__gte=min_cores)
            
            if self.priority == 'performance':
                query = query.order_by('-performance_score')
            elif self.priority == 'silence':
                query = query.order_by('tdp')
            else:
                query = query.order_by('-performance_score')
            
            cpu = query.first()
            
            if not cpu:
                logger.warning(f"No CPU found for budget {budget} and requirements")
                raise ConfigurationError(f"Не найден подходящий процессор в пределах бюджета {budget} RUB")
            
            reason = self._generate_cpu_reason(cpu)
            logger.debug(f"Selected CPU: {cpu.name} ({cpu.price} RUB)")
            return cpu, reason
        except Exception as e:
            logger.error(f"Error selecting CPU: {str(e)}")
            raise ConfigurationError(f"Ошибка при подборе процессора: {str(e)}")
    
    def select_gpu(self, budget):
        
        if self.user_type == 'office' and not self.requirements['gaming']:
            return None, "Интегрированной графики достаточно для офисных задач"
        
        query = GPU.objects.filter(price__lte=budget)
        
        if self.requirements['work_with_4k']:
            query = query.filter(memory__gte=8)
        
        if self.requirements['vr_support']:
            query = query.filter(memory__gte=8, performance_score__gte=7000)
        
        if self.priority == 'performance':
            query = query.order_by('-performance_score')
        else:
            query = query.order_by('-performance_score')
        
        gpu = query.first()
        reason = self._generate_gpu_reason(gpu)
        return gpu, reason
    
    def select_motherboard(self, cpu, budget):
        
        if not cpu:
            return None, "Не выбран процессор"
        
        query = Motherboard.objects.filter(
            socket=cpu.socket,
            price__lte=budget
        )
        
        if self.requirements['multitasking']:
            query = query.filter(memory_slots__gte=4)
        
        motherboard = query.order_by('-price').first()
        reason = f"Материнская плата совместима с процессором {cpu.name} (сокет {cpu.socket})"
        return motherboard, reason
    
    def select_ram(self, budget):
        
        min_capacity = 8
        
        if self.user_type in ['designer', 'content_creator'] or self.requirements['video_editing']:
            min_capacity = 32
        elif self.requirements['multitasking'] or self.user_type == 'programmer':
            min_capacity = 16
        elif self.requirements['gaming']:
            min_capacity = 16
        
        query = RAM.objects.filter(
            capacity__gte=min_capacity,
            price__lte=budget
        ).order_by('-speed', '-capacity')
        
        ram = query.first()
        reason = f"Выбран объем {ram.capacity if ram else min_capacity}GB для комфортной работы с выбранными задачами"
        return ram, reason
    
    def select_storage(self, budget, is_primary=True):
        
        if is_primary:
            query = Storage.objects.filter(
                storage_type='ssd_nvme',
                capacity__gte=500,
                price__lte=budget
            ).order_by('-capacity')
            
            storage = query.first()
            reason = "Быстрый NVMe SSD для системы и основных программ"
        else:
            query = Storage.objects.filter(
                price__lte=budget
            ).order_by('-capacity')
            
            storage = query.first()
            reason = "Дополнительный накопитель для хранения данных"
        
        return storage, reason
    
    def select_psu(self, cpu, gpu, budget):
        
        total_tdp = 0
        if cpu:
            total_tdp += cpu.tdp
        if gpu:
            total_tdp += gpu.tdp
        
        recommended_wattage = int(total_tdp * 1.5)
        
        query = PSU.objects.filter(
            wattage__gte=recommended_wattage,
            price__lte=budget
        ).order_by('wattage', '-efficiency_rating')
        
        psu = query.first()
        reason = f"Мощность {psu.wattage if psu else recommended_wattage}Вт с запасом для стабильной работы системы"
        return psu, reason
    
    def select_cooling(self, cpu, budget):
        
        if not cpu:
            return None, "Не выбран процессор"
        
        query = Cooling.objects.filter(
            max_tdp__gte=cpu.tdp,
            price__lte=budget
        )
        
        if self.priority == 'silence':
            query = query.order_by('noise_level')
        elif self.priority == 'performance':
            query = query.order_by('-max_tdp')
        else:
            query = query.order_by('price')
        
        cooling = query.first()
        reason = f"Охлаждение справится с TDP {cpu.tdp}Вт процессора"
        return cooling, reason
    
    def select_case(self, budget):
        
        query = Case.objects.filter(price__lte=budget)
        
        if self.priority == 'compactness':
            query = query.filter(form_factor__in=['Mini-ITX', 'Micro-ATX'])
        elif self.priority == 'aesthetics':
            query = query.filter(rgb=True)
        
        case = query.order_by('-price').first()
        reason = "Корпус подобран с учетом ваших приоритетов"
        return case, reason
    
    @transaction.atomic
    def generate_configuration(self, user, include_workspace=False):

        logger.info(f"Starting configuration generation for user {user.username}, type: {self.user_type}")
        
        try:
            budget_dist = self.get_budget_distribution()
            
            
            if include_workspace:
                peripheral_percent = self.user_profile_data.get('peripheral_budget_percent', 30)
                pc_percent = 100 - peripheral_percent
                pc_budget = self.max_budget * Decimal(str(pc_percent / 100))
                peripheral_budget = self.max_budget * Decimal(str(peripheral_percent / 100))
                logger.info(f"Budget split: PC={pc_percent}% ({pc_budget} RUB), Peripherals={peripheral_percent}% ({peripheral_budget} RUB)")
            else:
                pc_budget = self.max_budget
                peripheral_budget = None
                logger.info(f"PC-only configuration with budget: {pc_budget} RUB")
            
            components = {}
            reasons = {}
            
            
            cpu_budget = pc_budget * Decimal(str(budget_dist['cpu']))
            cpu, cpu_reason = self.select_cpu(cpu_budget)
            components['cpu'] = cpu
            reasons['cpu'] = cpu_reason
            
            
            gpu_budget = pc_budget * Decimal(str(budget_dist['gpu']))
            gpu, gpu_reason = self.select_gpu(gpu_budget)
            components['gpu'] = gpu
            reasons['gpu'] = gpu_reason
            
            
            mb_budget = pc_budget * Decimal(str(budget_dist['motherboard']))
            motherboard, mb_reason = self.select_motherboard(cpu, mb_budget)
            components['motherboard'] = motherboard
            reasons['motherboard'] = mb_reason
            
            
            ram_budget = pc_budget * Decimal(str(budget_dist['ram']))
            ram, ram_reason = self.select_ram(ram_budget)
            components['ram'] = ram
            reasons['ram'] = ram_reason
            
            
            storage_budget = pc_budget * Decimal(str(budget_dist['storage']))
            storage_primary, storage1_reason = self.select_storage(storage_budget, True)
            components['storage_primary'] = storage_primary
            reasons['storage_primary'] = storage1_reason
            
            
            psu_budget = pc_budget * Decimal(str(budget_dist['psu']))
            psu, psu_reason = self.select_psu(cpu, gpu, psu_budget)
            components['psu'] = psu
            reasons['psu'] = psu_reason
            
            
            cooling_budget = pc_budget * Decimal(str(budget_dist['cooling']))
            cooling, cooling_reason = self.select_cooling(cpu, cooling_budget)
            components['cooling'] = cooling
            reasons['cooling'] = cooling_reason
            
            
            case_budget = pc_budget * Decimal(str(budget_dist['case']))
            case, case_reason = self.select_case(case_budget)
            components['case'] = case
            reasons['case'] = case_reason
        
            
            config = PCConfiguration.objects.create(
                user=user,
                name=f"Конфигурация для {self.user_type}",
                **components
            )
            
            config.calculate_total_price()
            config.save()
            logger.info(f"PC Configuration created: {config.name} ({config.total_price} RUB)")
            
            
            for component_type, reason in reasons.items():
                component = components.get(component_type)
                if component:
                    Recommendation.objects.create(
                        configuration=config,
                        component_type=component_type,
                        component_id=component.id,
                        reason=reason
                    )
            
           
            workspace = None
            if include_workspace and peripheral_budget:
                logger.info("Starting workspace peripheral selection...")
               
                peripheral_preferences = {
                'need_monitor': self.user_profile_data.get('need_monitor', True),
                'need_keyboard': self.user_profile_data.get('need_keyboard', True),
                'need_mouse': self.user_profile_data.get('need_mouse', True),
                'need_headset': self.user_profile_data.get('need_headset', True),
                'need_webcam': self.user_profile_data.get('need_webcam', False),
                'need_microphone': self.user_profile_data.get('need_microphone', False),
                'need_desk': self.user_profile_data.get('need_desk', True),
                'need_chair': self.user_profile_data.get('need_chair', True),
                'monitor_min_refresh_rate': self.user_profile_data.get('monitor_min_refresh_rate'),
                'monitor_min_resolution': self.user_profile_data.get('monitor_min_resolution'),
                    'keyboard_type_preference': self.user_profile_data.get('keyboard_type_preference'),
                    'mouse_min_dpi': self.user_profile_data.get('mouse_min_dpi'),
                }
                peripheral_selection = self.select_workspace_peripherals(peripheral_budget, peripheral_preferences)
                
                workspace = WorkspaceSetup.objects.create(
                configuration=config,
                monitor_primary=peripheral_selection['monitor_primary'],
                keyboard=peripheral_selection['keyboard'],
                mouse=peripheral_selection['mouse'],
                headset=peripheral_selection['headset'],
                webcam=peripheral_selection['webcam'],
                microphone=peripheral_selection['microphone'],
                desk=peripheral_selection['desk'],
                    chair=peripheral_selection['chair'],
                    lighting_recommendation=peripheral_selection['lighting_recommendation']
                )
            
                workspace.calculate_total_price()
                workspace.save()
                logger.info(f"Workspace setup created for configuration: {config.name} ({workspace.total_price} RUB)")
            
            logger.info(f"Configuration generation completed successfully. Total: {config.total_price + (workspace.total_price if workspace else 0)} RUB")
            return config, workspace
            
        except ConfigurationError:
            logger.error("Configuration generation failed", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during configuration generation: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Не удалось создать конфигурацию: {str(e)}")
    
    def check_compatibility(self, configuration):
        
        issues = []
        
        
        if configuration.cpu and configuration.motherboard:
            if configuration.cpu.socket != configuration.motherboard.socket:
                issues.append(f"Процессор (сокет {configuration.cpu.socket}) не совместим с материнской платой (сокет {configuration.motherboard.socket})")
        
        
        if configuration.psu and configuration.cpu and configuration.gpu:
            total_tdp = configuration.cpu.tdp + (configuration.gpu.tdp if configuration.gpu else 0)
            if configuration.psu.wattage < total_tdp * 1.3:
                issues.append(f"Мощность БП ({configuration.psu.wattage}Вт) может быть недостаточной для системы (рекомендуется {int(total_tdp * 1.5)}Вт)")
        
        
        if configuration.cooling and configuration.cpu:
            if configuration.cooling.max_tdp < configuration.cpu.tdp:
                issues.append(f"Система охлаждения может не справиться с TDP процессора ({configuration.cpu.tdp}Вт)")
        
        
        if configuration.ram and configuration.motherboard:
            if configuration.ram.memory_type != configuration.motherboard.memory_type:
                issues.append(f"Тип оперативной памяти ({configuration.ram.memory_type}) не совместим с материнской платой ({configuration.motherboard.memory_type})")
        
        configuration.compatibility_check = len(issues) == 0
        configuration.compatibility_notes = "\n".join(issues) if issues else "Все компоненты совместимы"
        configuration.save()
        
        return configuration.compatibility_check, issues
    
    def _generate_cpu_reason(self, cpu):
        
        if not cpu:
            return "Процессор не найден в базе данных"
        
        reasons = [f"Процессор {cpu.name} с {cpu.cores} ядрами и {cpu.threads} потоками"]
        
        if self.user_type == 'designer':
            reasons.append("отлично подходит для работы в графических редакторах")
        elif self.user_type == 'programmer':
            reasons.append("обеспечивает быструю компиляцию и многозадачность")
        elif self.user_type == 'gamer':
            reasons.append("обеспечивает высокий FPS в играх")
        elif self.user_type == 'content_creator':
            reasons.append("идеален для рендеринга и видеомонтажа")
        
        return ". ".join(reasons)
    
    def _generate_gpu_reason(self, gpu):
        
        if not gpu:
            return "Видеокарта не требуется для данного профиля"
        
        reasons = [f"Видеокарта {gpu.name} с {gpu.memory}GB памяти"]
        
        if self.requirements['work_with_4k']:
            reasons.append("справится с 4K контентом")
        elif self.requirements['gaming']:
            reasons.append("обеспечит комфортный гейминг")
        elif self.user_type == 'designer':
            reasons.append("ускорит работу в профессиональных программах")
        
        return ". ".join(reasons)

 
    
    def select_workspace_peripherals(self, peripheral_budget, peripheral_preferences=None):

        logger.info(f"Starting workspace peripheral selection with budget: {peripheral_budget}")
        

        if peripheral_preferences is None:
            peripheral_preferences = {}
        
        need_monitor = peripheral_preferences.get('need_monitor', True)
        need_keyboard = peripheral_preferences.get('need_keyboard', True)
        need_mouse = peripheral_preferences.get('need_mouse', True)
        need_headset = peripheral_preferences.get('need_headset', True)
        need_webcam = peripheral_preferences.get('need_webcam', False)
        need_microphone = peripheral_preferences.get('need_microphone', False)
        need_desk = peripheral_preferences.get('need_desk', True)
        need_chair = peripheral_preferences.get('need_chair', True)
        

        selected_count = sum([
            need_monitor, need_keyboard, need_mouse, need_headset,
            need_webcam, need_microphone, need_desk, need_chair
        ])
        
        if selected_count == 0:
            logger.warning("No peripheral devices selected")
            return {
                'monitor_primary': None,
                'keyboard': None,
                'mouse': None,
                'headset': None,
                'webcam': None,
                'microphone': None,
                'desk': None,
                'chair': None,
                'lighting_recommendation': self._get_lighting_recommendation()
            }
        
        budget_distribution = self._get_peripheral_budget_distribution()
        

        monitor = None
        if need_monitor:
            monitor = self.select_monitor(
                peripheral_budget * Decimal(str(budget_distribution['monitor'])),
                peripheral_preferences
            )
        
        keyboard = None
        if need_keyboard:
            keyboard = self.select_keyboard(
                peripheral_budget * Decimal(str(budget_distribution['keyboard'])),
                peripheral_preferences
            )
        
        mouse = None
        if need_mouse:
            mouse = self.select_mouse(
                peripheral_budget * Decimal(str(budget_distribution['mouse'])),
                peripheral_preferences
            )
        
        headset = None
        if need_headset:
            headset = self.select_headset(peripheral_budget * Decimal(str(budget_distribution['headset'])))
        

        webcam = None
        microphone = None
        if need_webcam:
            webcam_budget = budget_distribution.get('webcam', 0.10)
            webcam = self.select_webcam(peripheral_budget * Decimal(str(webcam_budget)))
            logger.info(f"Webcam selected by user request")
        if need_microphone:
            microphone_budget = budget_distribution.get('microphone', 0.10)
            microphone = self.select_microphone(peripheral_budget * Decimal(str(microphone_budget)))
            logger.info(f"Microphone selected by user request")
        
        desk = None
        if need_desk:
            desk = self.select_desk(peripheral_budget * Decimal(str(budget_distribution['desk'])))
        
        chair = None
        if need_chair:
            chair = self.select_chair(peripheral_budget * Decimal(str(budget_distribution['chair'])))
        
        lighting_recommendation = self._get_lighting_recommendation()
        
        result = {
            'monitor_primary': monitor,
            'keyboard': keyboard,
            'mouse': mouse,
            'headset': headset,
            'webcam': webcam,
            'microphone': microphone,
            'desk': desk,
            'chair': chair,
            'lighting_recommendation': lighting_recommendation
        }
        
        logger.info(f"Workspace peripheral selection completed: {sum(1 for v in result.values() if v and v != lighting_recommendation)} components selected")
        return result
    
    def _get_peripheral_budget_distribution(self):

        distributions = {
            'gamer': {
                'monitor': 0.40,  
                'keyboard': 0.15,  
                'mouse': 0.15,    
                'headset': 0.10,  
                'desk': 0.10,
                'chair': 0.10,
            },
            'designer': {
                'monitor': 0.45,  
                'keyboard': 0.10,
                'mouse': 0.10,    
                'headset': 0.05,
                'desk': 0.15,     
                'chair': 0.15,    
            },
            'programmer': {
                'monitor': 0.35,
                'keyboard': 0.20,  
                'mouse': 0.10,
                'headset': 0.05,
                'desk': 0.15,
                'chair': 0.15,
            },
            'content_creator': {
                'monitor': 0.30,
                'keyboard': 0.10,
                'mouse': 0.10,
                'headset': 0.10,
                'webcam': 0.10,   
                'microphone': 0.10,  
                'desk': 0.10,
                'chair': 0.10,
            },
            'office': {
                'monitor': 0.30,
                'keyboard': 0.15,
                'mouse': 0.10,
                'headset': 0.10,
                'desk': 0.15,
                'chair': 0.20,    
            },
            'student': {
                'monitor': 0.35,
                'keyboard': 0.15,
                'mouse': 0.10,
                'headset': 0.10,
                'desk': 0.15,
                'chair': 0.15,
            }
        }
        
        return distributions.get(self.user_type, distributions['office'])
    
    def select_monitor(self, budget, preferences=None):

        if preferences is None:
            preferences = {}
        
        monitors = Monitor.objects.filter(price__lte=budget).order_by('-price')
        

        min_refresh_rate = preferences.get('monitor_min_refresh_rate', 60)
        min_resolution = preferences.get('monitor_min_resolution', '1920x1080')
        
        if min_refresh_rate:
            monitors = monitors.filter(refresh_rate__gte=min_refresh_rate)
            logger.info(f"Filtering monitors with refresh rate >= {min_refresh_rate}Hz")
        
        if min_resolution:
            monitors = monitors.filter(resolution=min_resolution)
            logger.info(f"Filtering monitors with resolution: {min_resolution}")
        

        if not preferences.get('monitor_min_resolution'):
            if self.requirements.get('work_with_4k'):
                monitors = monitors.filter(resolution='3840x2160')
                logger.info("Auto-filtering monitors for 4K resolution")
        
        if not preferences.get('monitor_min_refresh_rate'):
            if self.user_type == 'gamer':
                monitors = monitors.filter(refresh_rate__gte=144)
                logger.info("Auto-filtering monitors for high refresh rate (gaming)")
        
        if self.user_type == 'designer' and not min_resolution:
            monitors = monitors.filter(panel_type='IPS')
            logger.info("Filtering monitors for IPS panel (design work)")
        
        monitor = monitors.first()
        
        if monitor:
            logger.info(f"Selected monitor: {monitor.name} at ${monitor.price}")
        else:
            logger.warning(f"No suitable monitor found within budget: ${budget}")
        
        return monitor
    
    def select_keyboard(self, budget, preferences=None):

        if preferences is None:
            preferences = {}
        
        keyboards = Keyboard.objects.filter(price__lte=budget).order_by('-price')
        

        keyboard_type = preferences.get('keyboard_type_preference', 'any')
        
        if keyboard_type == 'mechanical':
            keyboards = keyboards.filter(switch_type='mechanical')
            logger.info("User requested mechanical keyboard")
        elif keyboard_type == 'membrane':
            keyboards = keyboards.filter(switch_type='membrane')
            logger.info("User requested membrane keyboard")
        elif keyboard_type == 'any':

            if self.user_type == 'gamer':
                keyboards = keyboards.filter(switch_type='mechanical')
                logger.info("Auto-selecting mechanical keyboard for gamer")
            elif self.user_type == 'programmer':
                keyboards = keyboards.filter(switch_type__in=['mechanical', 'membrane'])
                logger.info("Auto-selecting keyboard for programmer")
            elif self.user_type == 'office':
                keyboards = keyboards.filter(switch_type='membrane')
                logger.info("Auto-selecting quiet membrane keyboard for office")
        
        keyboard = keyboards.first()
        
        if keyboard:
            logger.info(f"Selected keyboard: {keyboard.name} ({keyboard.switch_type}) at ${keyboard.price}")
        else:
            logger.warning(f"No suitable keyboard found within budget: ${budget}")
        
        return keyboard
    
    def select_mouse(self, budget, preferences=None):

        if preferences is None:
            preferences = {}
        
        mice = Mouse.objects.filter(price__lte=budget).order_by('-price')
        

        min_dpi = preferences.get('mouse_min_dpi', 1000)
        
        if min_dpi:
            mice = mice.filter(dpi__gte=min_dpi)
            logger.info(f"Filtering mice with DPI >= {min_dpi}")
        

        if not preferences.get('mouse_min_dpi'):
            if self.user_type == 'gamer':
                mice = mice.filter(dpi__gte=12000, sensor_type='optical')
                logger.info("Auto-filtering high-DPI gaming mice")
            elif self.user_type == 'designer':
                mice = mice.filter(dpi__gte=4000)
                logger.info("Auto-filtering precision mice for design work")
        
        mouse = mice.first()
        
        if mouse:
            logger.info(f"Selected mouse: {mouse.name} ({mouse.dpi} DPI) at ${mouse.price}")
        else:
            logger.warning(f"No suitable mouse found within budget: ${budget}")
        
        return mouse
    
    def select_headset(self, budget):

        headsets = Headset.objects.filter(price__lte=budget).order_by('-price')
        
        if self.user_type == 'gamer':
            
            headsets = headsets.filter(surround_sound=True)
            logger.info("Filtering surround sound headsets for gaming")
        elif self.user_type == 'content_creator':
            
            headsets = headsets.filter(noise_cancellation=True)
            logger.info("Filtering noise-cancelling headsets for content creation")
        
        headset = headsets.first()
        
        if headset:
            logger.info(f"Selected headset: {headset.name} at ${headset.price}")
        else:
            logger.warning(f"No suitable headset found within budget: ${budget}")
        
        return headset
    
    def select_webcam(self, budget):

        webcams = Webcam.objects.filter(price__lte=budget).order_by('-price')
        
        if self.requirements.get('streaming') or self.user_type == 'content_creator':
            # Для стриминга нужно Full HD минимум и 60 FPS
            webcams = webcams.filter(resolution__in=['1920x1080', '2560x1440'])
            webcams = webcams.filter(fps__gte=60)
            logger.info("Filtering high-quality webcams for streaming")
        
        webcam = webcams.first()
        
        if webcam:
            logger.info(f"Selected webcam: {webcam.name} ({webcam.resolution}@{webcam.fps}fps) at ${webcam.price}")
        else:
            logger.warning(f"No suitable webcam found within budget: ${budget}")
        
        return webcam
    
    def select_microphone(self, budget):

        microphones = Microphone.objects.filter(price__lte=budget).order_by('-price')
        
        if self.user_type == 'content_creator':
            
            microphones = microphones.filter(mic_type='condenser')
            logger.info("Filtering condenser microphones for content creation")
        
        microphone = microphones.first()
        
        if microphone:
            logger.info(f"Selected microphone: {microphone.name} ({microphone.mic_type}) at ${microphone.price}")
        else:
            logger.warning(f"No suitable microphone found within budget: ${budget}")
        
        return microphone
    
    def select_desk(self, budget):

        desks = Desk.objects.filter(price__lte=budget).order_by('-price')
        
       
        adjustable = desks.filter(height_adjustable=True).first()
        if adjustable:
            logger.info(f"Selected height-adjustable desk: {adjustable.name} at ${adjustable.price}")
            return adjustable
        
        desk = desks.first()
        if desk:
            logger.info(f"Selected desk: {desk.name} at ${desk.price}")
        else:
            logger.warning(f"No suitable desk found within budget: ${budget}")
        
        return desk
    
    def select_chair(self, budget):

        chairs = Chair.objects.filter(price__lte=budget).order_by('-price')
        

        ergonomic = chairs.filter(ergonomic=True, lumbar_support=True).first()
        if ergonomic:
            logger.info(f"Selected ergonomic chair: {ergonomic.name} at ${ergonomic.price}")
            return ergonomic
        
        chair = chairs.first()
        if chair:
            logger.info(f"Selected chair: {chair.name} at ${chair.price}")
        else:
            logger.warning(f"No suitable chair found within budget: ${budget}")
        
        return chair
    
    def _get_lighting_recommendation(self):

        if self.ai_service and self.ai_analysis:
            try:
                recommendation = self.ai_service.generate_workspace_recommendation(
                    self.ai_analysis,
                    self.user_type,
                    self.requirements
                )
                if 'lighting' in recommendation:
                    logger.info("Using AI-generated lighting recommendation")
                    return recommendation['lighting']
            except Exception as e:
                logger.warning(f"Failed to get AI lighting recommendation: {e}")
        

        lighting_recommendations = {
            'designer': (
                "Рекомендуется нейтральное белое освещение (4000-5000K) с высоким индексом "
                "цветопередачи (CRI > 90) для точной работы с цветом. Установите основной "
                "светильник над рабочим местом (500-1000 люмен) и дополнительную LED-подсветку "
                "за монитором для снижения нагрузки на глаза. Избегайте прямых бликов на экране."
            ),
            'programmer': (
                "Оптимально мягкое теплое освещение (3000-4000K) для снижения усталости глаз "
                "при длительной работе. Рассмотрите настольную лампу с регулировкой яркости "
                "(300-500 люмен) и цветовой температуры. Bias-подсветка за монитором поможет "
                "уменьшить напряжение глаз. Избегайте резких контрастов освещения."
            ),
            'gamer': (
                "RGB-подсветка для создания игровой атмосферы, основное освещение 3000-4000K. "
                "Важна возможность диммирования для игр в темное время суток. Подсветка монитора "
                "(bias lighting) снизит контраст с экраном и уменьшит усталость глаз. Умные "
                "RGB-ленты с синхронизацией с игрой создадут погружение."
            ),
            'content_creator': (
                "Кольцевая лампа (12-18 дюймов, 5500K) или софтбокс для съемки контента, "
                "основное освещение помещения 4000-5000K. Важна равномерность освещения лица "
                "для качественных видео. Рассмотрите двухточечную схему освещения: key light + "
                "fill light. Для стриминга добавьте цветную подсветку фона."
            ),
            'office': (
                "Нейтральное белое освещение (4000K) для поддержания концентрации и бодрости. "
                "Настольная лампа с регулировкой (400-600 люмен) для работы с документами. "
                "Важно обеспечить равномерное освещение без резких теней. Естественный свет "
                "предпочтителен, при его наличии используйте дополнительное освещение."
            ),
            'student': (
                "Комбинация общего и локального освещения (3500-4500K). Настольная лампа "
                "обязательна для чтения и письма (500-700 люмен). Важна возможность регулировки "
                "яркости для разных задач. Теплый свет вечером поможет не нарушать цикл сна. "
                "Избегайте бликов на учебных материалах."
            )
        }
        
        recommendation = lighting_recommendations.get(
            self.user_type,
            lighting_recommendations['office']
        )
        
        logger.info(f"Using fallback lighting recommendation for {self.user_type}")
        return recommendation
