"""
Сервис для подбора конфигурации компьютера на основе профиля пользователя
"""
from decimal import Decimal
from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
from peripherals.models import Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair
from recommendations.models import PCConfiguration, WorkspaceSetup, Recommendation


class ConfigurationService:
    """Сервис для подбора и проверки конфигурации"""
    
    def __init__(self, user_profile_data):
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
    
    def get_budget_distribution(self):
        """Распределение бюджета по компонентам в зависимости от типа пользователя"""
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
        """Подбор процессора"""
        query = CPU.objects.filter(price__lte=budget)
        
        if self.requirements['multitasking'] or self.requirements['video_editing']:
            query = query.filter(cores__gte=8)
        
        if self.priority == 'performance':
            query = query.order_by('-performance_score')
        elif self.priority == 'silence':
            query = query.order_by('tdp')
        else:
            query = query.order_by('-performance_score')
        
        cpu = query.first()
        
        reason = self._generate_cpu_reason(cpu)
        return cpu, reason
    
    def select_gpu(self, budget):
        """Подбор видеокарты"""
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
        """Подбор материнской платы"""
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
        """Подбор оперативной памяти"""
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
        """Подбор накопителя"""
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
        """Подбор блока питания"""
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
        """Подбор системы охлаждения"""
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
        """Подбор корпуса"""
        query = Case.objects.filter(price__lte=budget)
        
        if self.priority == 'compactness':
            query = query.filter(form_factor__in=['Mini-ITX', 'Micro-ATX'])
        elif self.priority == 'aesthetics':
            query = query.filter(rgb=True)
        
        case = query.order_by('-price').first()
        reason = "Корпус подобран с учетом ваших приоритетов"
        return case, reason
    
    def generate_configuration(self, user):
        """Генерация полной конфигурации"""
        budget_dist = self.get_budget_distribution()
        pc_budget = self.max_budget * Decimal('0.7')
        
        components = {}
        reasons = {}
        
        # Подбор процессора
        cpu_budget = pc_budget * Decimal(str(budget_dist['cpu']))
        cpu, cpu_reason = self.select_cpu(cpu_budget)
        components['cpu'] = cpu
        reasons['cpu'] = cpu_reason
        
        # Подбор видеокарты
        gpu_budget = pc_budget * Decimal(str(budget_dist['gpu']))
        gpu, gpu_reason = self.select_gpu(gpu_budget)
        components['gpu'] = gpu
        reasons['gpu'] = gpu_reason
        
        # Подбор материнской платы
        mb_budget = pc_budget * Decimal(str(budget_dist['motherboard']))
        motherboard, mb_reason = self.select_motherboard(cpu, mb_budget)
        components['motherboard'] = motherboard
        reasons['motherboard'] = mb_reason
        
        # Подбор оперативной памяти
        ram_budget = pc_budget * Decimal(str(budget_dist['ram']))
        ram, ram_reason = self.select_ram(ram_budget)
        components['ram'] = ram
        reasons['ram'] = ram_reason
        
        # Подбор накопителей
        storage_budget = pc_budget * Decimal(str(budget_dist['storage']))
        storage_primary, storage1_reason = self.select_storage(storage_budget, True)
        components['storage_primary'] = storage_primary
        reasons['storage_primary'] = storage1_reason
        
        # Подбор блока питания
        psu_budget = pc_budget * Decimal(str(budget_dist['psu']))
        psu, psu_reason = self.select_psu(cpu, gpu, psu_budget)
        components['psu'] = psu
        reasons['psu'] = psu_reason
        
        # Подбор охлаждения
        cooling_budget = pc_budget * Decimal(str(budget_dist['cooling']))
        cooling, cooling_reason = self.select_cooling(cpu, cooling_budget)
        components['cooling'] = cooling
        reasons['cooling'] = cooling_reason
        
        # Подбор корпуса
        case_budget = pc_budget * Decimal(str(budget_dist['case']))
        case, case_reason = self.select_case(case_budget)
        components['case'] = case
        reasons['case'] = case_reason
        
        # Создание конфигурации
        config = PCConfiguration.objects.create(
            user=user,
            name=f"Конфигурация для {self.user_type}",
            **components
        )
        
        config.calculate_total_price()
        config.save()
        
        # Сохранение обоснований
        for component_type, reason in reasons.items():
            component = components.get(component_type)
            if component:
                Recommendation.objects.create(
                    configuration=config,
                    component_type=component_type,
                    component_id=component.id,
                    reason=reason
                )
        
        return config
    
    def check_compatibility(self, configuration):
        """Проверка совместимости компонентов"""
        issues = []
        
        # Проверка совместимости CPU и материнской платы
        if configuration.cpu and configuration.motherboard:
            if configuration.cpu.socket != configuration.motherboard.socket:
                issues.append(f"Процессор (сокет {configuration.cpu.socket}) не совместим с материнской платой (сокет {configuration.motherboard.socket})")
        
        # Проверка мощности БП
        if configuration.psu and configuration.cpu and configuration.gpu:
            total_tdp = configuration.cpu.tdp + (configuration.gpu.tdp if configuration.gpu else 0)
            if configuration.psu.wattage < total_tdp * 1.3:
                issues.append(f"Мощность БП ({configuration.psu.wattage}Вт) может быть недостаточной для системы (рекомендуется {int(total_tdp * 1.5)}Вт)")
        
        # Проверка охлаждения
        if configuration.cooling and configuration.cpu:
            if configuration.cooling.max_tdp < configuration.cpu.tdp:
                issues.append(f"Система охлаждения может не справиться с TDP процессора ({configuration.cpu.tdp}Вт)")
        
        # Проверка памяти и материнской платы
        if configuration.ram and configuration.motherboard:
            if configuration.ram.memory_type != configuration.motherboard.memory_type:
                issues.append(f"Тип оперативной памяти ({configuration.ram.memory_type}) не совместим с материнской платой ({configuration.motherboard.memory_type})")
        
        configuration.compatibility_check = len(issues) == 0
        configuration.compatibility_notes = "\n".join(issues) if issues else "Все компоненты совместимы"
        configuration.save()
        
        return configuration.compatibility_check, issues
    
    def _generate_cpu_reason(self, cpu):
        """Генерация обоснования выбора процессора"""
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
        """Генерация обоснования выбора видеокарты"""
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
