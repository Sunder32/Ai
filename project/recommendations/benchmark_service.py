"""
Сервис парсинга бенчмарков и предсказания производительности
- Данные 3DMark, Cinebench, Geekbench
- Предсказание FPS в играх
- Сравнение с реальными тестами
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class BenchmarkType(Enum):
    CINEBENCH_R23_SINGLE = "cinebench_r23_single"
    CINEBENCH_R23_MULTI = "cinebench_r23_multi"
    GEEKBENCH_6_SINGLE = "geekbench_6_single"
    GEEKBENCH_6_MULTI = "geekbench_6_multi"
    TIMESPY = "3dmark_timespy"
    TIMESPY_EXTREME = "3dmark_timespy_extreme"
    FIRESTRIKE = "3dmark_firestrike"
    PORT_ROYAL = "3dmark_port_royal"  # Ray Tracing
    PASSMARK_CPU = "passmark_cpu"
    PASSMARK_GPU = "passmark_gpu"


@dataclass
class BenchmarkResult:
    """Результат бенчмарка"""
    benchmark_type: str
    score: float
    component_name: str
    source: str  # Источник данных
    test_date: Optional[datetime] = None
    percentile: Optional[float] = None  # Процентиль среди всех результатов
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        if self.test_date:
            result['test_date'] = self.test_date.isoformat()
        return result


@dataclass
class GameFPSPrediction:
    """Предсказание FPS в игре"""
    game_name: str
    resolution: str  # 1080p, 1440p, 4K
    quality_preset: str  # Low, Medium, High, Ultra
    predicted_fps: float
    fps_1_low: float  # 1% low FPS
    confidence: float  # Уверенность в предсказании 0-100%
    ray_tracing: bool
    dlss_fsr: Optional[str]  # DLSS/FSR версия если применимо
    
    def to_dict(self) -> Dict:
        return asdict(self)


class BenchmarkDatabase:
    """
    База данных бенчмарков
    В production - загружается из внешних источников и БД
    """
    
    # CPU бенчмарки (Cinebench R23)
    CPU_BENCHMARKS = {
        # AMD Ryzen 9000
        "AMD Ryzen 9 9950X": {"single": 2280, "multi": 42000},
        "AMD Ryzen 9 9900X": {"single": 2200, "multi": 32000},
        "AMD Ryzen 7 9700X": {"single": 2150, "multi": 20000},
        "AMD Ryzen 5 9600X": {"single": 2100, "multi": 14500},
        
        # AMD Ryzen 7000
        "AMD Ryzen 9 7950X": {"single": 2050, "multi": 38500},
        "AMD Ryzen 9 7950X3D": {"single": 2000, "multi": 37000},
        "AMD Ryzen 9 7900X": {"single": 2020, "multi": 29500},
        "AMD Ryzen 9 7900X3D": {"single": 1980, "multi": 28500},
        "AMD Ryzen 7 7800X3D": {"single": 1950, "multi": 18000},
        "AMD Ryzen 7 7700X": {"single": 1980, "multi": 19500},
        "AMD Ryzen 5 7600X": {"single": 1970, "multi": 15000},
        "AMD Ryzen 5 7600": {"single": 1900, "multi": 14000},
        
        # Intel 14th Gen
        "Intel Core i9-14900K": {"single": 2320, "multi": 41000},
        "Intel Core i9-14900KS": {"single": 2400, "multi": 42500},
        "Intel Core i7-14700K": {"single": 2200, "multi": 35000},
        "Intel Core i5-14600K": {"single": 2100, "multi": 24000},
        "Intel Core i5-14400": {"single": 1850, "multi": 17000},
        
        # Intel 13th Gen
        "Intel Core i9-13900K": {"single": 2250, "multi": 40000},
        "Intel Core i7-13700K": {"single": 2100, "multi": 30000},
        "Intel Core i5-13600K": {"single": 2000, "multi": 24500},
        
        # Intel 12th Gen
        "Intel Core i9-12900K": {"single": 2050, "multi": 27500},
        "Intel Core i7-12700K": {"single": 1950, "multi": 22500},
        "Intel Core i5-12600K": {"single": 1900, "multi": 17500},
    }
    
    # GPU бенчмарки (3DMark Time Spy)
    GPU_BENCHMARKS = {
        # NVIDIA RTX 50 Series
        "NVIDIA GeForce RTX 5090": {"timespy": 48000, "firestrike": 85000, "port_royal": 32000},
        "NVIDIA GeForce RTX 5080": {"timespy": 38000, "firestrike": 70000, "port_royal": 25000},
        "NVIDIA GeForce RTX 5070 Ti": {"timespy": 32000, "firestrike": 58000, "port_royal": 20000},
        "NVIDIA GeForce RTX 5070": {"timespy": 28000, "firestrike": 50000, "port_royal": 17000},
        
        # NVIDIA RTX 40 Series
        "NVIDIA GeForce RTX 4090": {"timespy": 36500, "firestrike": 65000, "port_royal": 26000},
        "NVIDIA GeForce RTX 4080 Super": {"timespy": 29000, "firestrike": 52000, "port_royal": 20500},
        "NVIDIA GeForce RTX 4080": {"timespy": 28000, "firestrike": 50000, "port_royal": 19500},
        "NVIDIA GeForce RTX 4070 Ti Super": {"timespy": 24500, "firestrike": 44000, "port_royal": 16500},
        "NVIDIA GeForce RTX 4070 Ti": {"timespy": 22500, "firestrike": 41000, "port_royal": 15000},
        "NVIDIA GeForce RTX 4070 Super": {"timespy": 21000, "firestrike": 38000, "port_royal": 13500},
        "NVIDIA GeForce RTX 4070": {"timespy": 18000, "firestrike": 33000, "port_royal": 11000},
        "NVIDIA GeForce RTX 4060 Ti": {"timespy": 13500, "firestrike": 26000, "port_royal": 8500},
        "NVIDIA GeForce RTX 4060": {"timespy": 10500, "firestrike": 21000, "port_royal": 6500},
        
        # NVIDIA RTX 30 Series
        "NVIDIA GeForce RTX 3090 Ti": {"timespy": 21500, "firestrike": 42000, "port_royal": 14500},
        "NVIDIA GeForce RTX 3090": {"timespy": 19500, "firestrike": 39000, "port_royal": 13500},
        "NVIDIA GeForce RTX 3080 Ti": {"timespy": 19000, "firestrike": 38000, "port_royal": 13000},
        "NVIDIA GeForce RTX 3080": {"timespy": 17500, "firestrike": 35000, "port_royal": 12000},
        "NVIDIA GeForce RTX 3070 Ti": {"timespy": 14500, "firestrike": 30000, "port_royal": 9500},
        "NVIDIA GeForce RTX 3070": {"timespy": 13500, "firestrike": 28000, "port_royal": 8500},
        "NVIDIA GeForce RTX 3060 Ti": {"timespy": 11500, "firestrike": 25000, "port_royal": 7000},
        "NVIDIA GeForce RTX 3060": {"timespy": 8500, "firestrike": 20000, "port_royal": 5000},
        
        # AMD RX 9000 Series
        "AMD Radeon RX 9070 XT": {"timespy": 26000, "firestrike": 48000, "port_royal": 15000},
        "AMD Radeon RX 9070": {"timespy": 22000, "firestrike": 42000, "port_royal": 12000},
        
        # AMD RX 7000 Series
        "AMD Radeon RX 7900 XTX": {"timespy": 24000, "firestrike": 47000, "port_royal": 14000},
        "AMD Radeon RX 7900 XT": {"timespy": 21000, "firestrike": 42000, "port_royal": 12000},
        "AMD Radeon RX 7900 GRE": {"timespy": 18000, "firestrike": 36000, "port_royal": 10000},
        "AMD Radeon RX 7800 XT": {"timespy": 15000, "firestrike": 31000, "port_royal": 8000},
        "AMD Radeon RX 7700 XT": {"timespy": 13000, "firestrike": 27000, "port_royal": 7000},
        "AMD Radeon RX 7600 XT": {"timespy": 10000, "firestrike": 22000, "port_royal": 5000},
        "AMD Radeon RX 7600": {"timespy": 9000, "firestrike": 20000, "port_royal": 4500},
        
        # Intel Arc
        "Intel Arc A770": {"timespy": 12000, "firestrike": 24000, "port_royal": 6000},
        "Intel Arc A750": {"timespy": 10500, "firestrike": 21000, "port_royal": 5000},
    }
    
    # Игровые бенчмарки - базовые FPS для RTX 4090 + i9-14900K @ 1080p Ultra
    # cpu_bound: 0.0-1.0 (насколько игра зависит от CPU, 1.0 = очень CPU-зависима)
    # stability_factor: коэффициент для 1% Low (0.65-0.85, ниже = больше просадок)
    # vram_req: минимально рекомендуемый VRAM в GB для 1080p/1440p/4K
    GAME_BASE_FPS = {
        "Cyberpunk 2077": {
            "1080p": 145, "1440p": 105, "4k": 58,
            "rt_penalty": 0.45, "cpu_bound": 0.35, "stability_factor": 0.72,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "Hogwarts Legacy": {
            "1080p": 130, "1440p": 95, "4k": 52,
            "rt_penalty": 0.50, "cpu_bound": 0.30, "stability_factor": 0.70,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "The Last of Us Part I": {
            "1080p": 120, "1440p": 88, "4k": 48,
            "rt_penalty": 0.55, "cpu_bound": 0.40, "stability_factor": 0.68,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "Red Dead Redemption 2": {
            "1080p": 155, "1440p": 115, "4k": 65,
            "rt_penalty": 0.60, "cpu_bound": 0.45, "stability_factor": 0.75,
            "vram_req": {"1080p": 6, "1440p": 8, "4k": 10}
        },
        "Alan Wake 2": {
            "1080p": 95, "1440p": 65, "4k": 35,
            "rt_penalty": 0.35, "cpu_bound": 0.25, "stability_factor": 0.65,
            "vram_req": {"1080p": 10, "1440p": 12, "4k": 16}
        },
        "Starfield": {
            "1080p": 110, "1440p": 80, "4k": 45,
            "rt_penalty": 0.70, "cpu_bound": 0.50, "stability_factor": 0.68,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "Baldur's Gate 3": {
            "1080p": 140, "1440p": 105, "4k": 60,
            "rt_penalty": 0.80, "cpu_bound": 0.55, "stability_factor": 0.78,
            "vram_req": {"1080p": 6, "1440p": 8, "4k": 10}
        },
        "Call of Duty: Modern Warfare III": {
            "1080p": 195, "1440p": 155, "4k": 95,
            "rt_penalty": 0.55, "cpu_bound": 0.40, "stability_factor": 0.80,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "Forza Horizon 5": {
            "1080p": 175, "1440p": 140, "4k": 90,
            "rt_penalty": 0.60, "cpu_bound": 0.35, "stability_factor": 0.82,
            "vram_req": {"1080p": 6, "1440p": 8, "4k": 10}
        },
        "Elden Ring": {
            "1080p": 60, "1440p": 60, "4k": 60,  # Locked 60 FPS
            "rt_penalty": 1.0, "cpu_bound": 0.30, "stability_factor": 0.85,
            "vram_req": {"1080p": 4, "1440p": 6, "4k": 8}
        },
        "Counter-Strike 2": {
            "1080p": 450, "1440p": 350, "4k": 200,
            "rt_penalty": 1.0, "cpu_bound": 0.75, "stability_factor": 0.80,
            "vram_req": {"1080p": 4, "1440p": 6, "4k": 8}
        },
        "Valorant": {
            "1080p": 550, "1440p": 420, "4k": 250,
            "rt_penalty": 1.0, "cpu_bound": 0.80, "stability_factor": 0.85,
            "vram_req": {"1080p": 2, "1440p": 4, "4k": 6}
        },
        "Apex Legends": {
            "1080p": 280, "1440p": 210, "4k": 125,
            "rt_penalty": 1.0, "cpu_bound": 0.55, "stability_factor": 0.78,
            "vram_req": {"1080p": 6, "1440p": 8, "4k": 10}
        },
        "GTA V": {
            "1080p": 185, "1440p": 145, "4k": 85,
            "rt_penalty": 1.0, "cpu_bound": 0.50, "stability_factor": 0.80,
            "vram_req": {"1080p": 4, "1440p": 6, "4k": 8}
        },
        "Minecraft (Shaders)": {
            "1080p": 200, "1440p": 150, "4k": 80,
            "rt_penalty": 0.40, "cpu_bound": 0.60, "stability_factor": 0.70,
            "vram_req": {"1080p": 6, "1440p": 8, "4k": 12}
        },
        "Microsoft Flight Simulator": {
            "1080p": 85, "1440p": 65, "4k": 38,
            "rt_penalty": 0.85, "cpu_bound": 0.65, "stability_factor": 0.72,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "Avatar: Frontiers of Pandora": {
            "1080p": 90, "1440p": 62, "4k": 32,
            "rt_penalty": 0.40, "cpu_bound": 0.25, "stability_factor": 0.68,
            "vram_req": {"1080p": 10, "1440p": 12, "4k": 16}
        },
        "Black Myth: Wukong": {
            "1080p": 85, "1440p": 58, "4k": 30,
            "rt_penalty": 0.45, "cpu_bound": 0.30, "stability_factor": 0.70,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        # Новые игры 2025 года
        "S.T.A.L.K.E.R. 2": {
            "1080p": 75, "1440p": 52, "4k": 28,
            "rt_penalty": 0.50, "cpu_bound": 0.45, "stability_factor": 0.65,
            "vram_req": {"1080p": 10, "1440p": 12, "4k": 16}
        },
        "Indiana Jones and the Great Circle": {
            "1080p": 95, "1440p": 68, "4k": 38,
            "rt_penalty": 0.45, "cpu_bound": 0.35, "stability_factor": 0.72,
            "vram_req": {"1080p": 10, "1440p": 12, "4k": 14}
        },
        "Dragon Age: The Veilguard": {
            "1080p": 110, "1440p": 78, "4k": 42,
            "rt_penalty": 0.55, "cpu_bound": 0.40, "stability_factor": 0.75,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "Warhammer 40K: Space Marine 2": {
            "1080p": 105, "1440p": 75, "4k": 40,
            "rt_penalty": 0.60, "cpu_bound": 0.35, "stability_factor": 0.78,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "Silent Hill 2 Remake": {
            "1080p": 115, "1440p": 82, "4k": 45,
            "rt_penalty": 0.50, "cpu_bound": 0.30, "stability_factor": 0.75,
            "vram_req": {"1080p": 8, "1440p": 10, "4k": 12}
        },
        "Path of Exile 2": {
            "1080p": 140, "1440p": 100, "4k": 55,
            "rt_penalty": 0.70, "cpu_bound": 0.50, "stability_factor": 0.72,
            "vram_req": {"1080p": 6, "1440p": 8, "4k": 10}
        },
    }


class BenchmarkService:
    """Сервис бенчмарков"""
    
    def __init__(self):
        self.db = BenchmarkDatabase()
    
    def get_cpu_benchmarks(self, cpu_name: str) -> Dict[str, BenchmarkResult]:
        """Получение бенчмарков CPU"""
        benchmarks = {}
        
        # Ищем совпадение
        matched_name = self._find_component_match(cpu_name, self.db.CPU_BENCHMARKS)
        
        if matched_name:
            data = self.db.CPU_BENCHMARKS[matched_name]
            
            benchmarks['cinebench_single'] = BenchmarkResult(
                benchmark_type=BenchmarkType.CINEBENCH_R23_SINGLE.value,
                score=data['single'],
                component_name=matched_name,
                source="Cinebench R23",
                percentile=self._calculate_percentile(data['single'], 'cpu_single')
            )
            
            benchmarks['cinebench_multi'] = BenchmarkResult(
                benchmark_type=BenchmarkType.CINEBENCH_R23_MULTI.value,
                score=data['multi'],
                component_name=matched_name,
                source="Cinebench R23",
                percentile=self._calculate_percentile(data['multi'], 'cpu_multi')
            )
        
        return benchmarks
    
    def get_gpu_benchmarks(self, gpu_name: str) -> Dict[str, BenchmarkResult]:
        """Получение бенчмарков GPU"""
        benchmarks = {}
        
        matched_name = self._find_component_match(gpu_name, self.db.GPU_BENCHMARKS)
        
        if matched_name:
            data = self.db.GPU_BENCHMARKS[matched_name]
            
            benchmarks['timespy'] = BenchmarkResult(
                benchmark_type=BenchmarkType.TIMESPY.value,
                score=data['timespy'],
                component_name=matched_name,
                source="3DMark Time Spy",
                percentile=self._calculate_percentile(data['timespy'], 'gpu_timespy')
            )
            
            benchmarks['firestrike'] = BenchmarkResult(
                benchmark_type=BenchmarkType.FIRESTRIKE.value,
                score=data['firestrike'],
                component_name=matched_name,
                source="3DMark Fire Strike",
                percentile=self._calculate_percentile(data['firestrike'], 'gpu_firestrike')
            )
            
            benchmarks['port_royal'] = BenchmarkResult(
                benchmark_type=BenchmarkType.PORT_ROYAL.value,
                score=data['port_royal'],
                component_name=matched_name,
                source="3DMark Port Royal (Ray Tracing)",
                percentile=self._calculate_percentile(data['port_royal'], 'gpu_rt')
            )
        
        return benchmarks
    
    def _find_component_match(self, name: str, database: Dict) -> Optional[str]:
        """Поиск соответствия компонента в базе"""
        name_lower = name.lower()
        
        # Точное совпадение
        for db_name in database:
            if db_name.lower() == name_lower:
                return db_name
        
        # Частичное совпадение
        for db_name in database:
            # Извлекаем модель
            db_model = self._extract_model(db_name)
            if db_model and db_model.lower() in name_lower:
                return db_name
        
        return None
    
    def _extract_model(self, name: str) -> Optional[str]:
        """Извлечение модели из названия"""
        # RTX 4090, RX 7900 XTX, i9-14900K, Ryzen 9 7950X
        patterns = [
            r'(RTX\s*\d{4}(?:\s*Ti)?(?:\s*Super)?)',
            r'(RX\s*\d{4}\s*(?:XT|XTX|GRE)?)',
            r'(Arc\s*A\d{3})',
            r'(i[3579]-\d{4,5}[A-Z]*)',
            r'(Ryzen\s*[3579]\s*\d{4}[A-Z0-9]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_percentile(self, score: float, category: str) -> float:
        """Расчет процентиля"""
        if category == 'cpu_single':
            all_scores = [v['single'] for v in self.db.CPU_BENCHMARKS.values()]
        elif category == 'cpu_multi':
            all_scores = [v['multi'] for v in self.db.CPU_BENCHMARKS.values()]
        elif category == 'gpu_timespy':
            all_scores = [v['timespy'] for v in self.db.GPU_BENCHMARKS.values()]
        elif category == 'gpu_firestrike':
            all_scores = [v['firestrike'] for v in self.db.GPU_BENCHMARKS.values()]
        elif category == 'gpu_rt':
            all_scores = [v['port_royal'] for v in self.db.GPU_BENCHMARKS.values()]
        else:
            return 50.0
        
        below = sum(1 for s in all_scores if s < score)
        return round((below / len(all_scores)) * 100, 1)


class FPSPredictionService:
    """Сервис предсказания FPS"""
    
    def __init__(self):
        self.db = BenchmarkDatabase()
        self.benchmark_service = BenchmarkService()
        
        # Эталонные показатели (RTX 4090 + i9-14900K)
        self.reference_gpu_score = 36500  # Time Spy
        self.reference_cpu_score = 2320   # Cinebench Single
    
    def predict_fps(
        self,
        gpu_name: str,
        cpu_name: str,
        game: str,
        resolution: str = "1080p",
        ray_tracing: bool = False,
        dlss_fsr: Optional[str] = None
    ) -> Optional[GameFPSPrediction]:
        """
        Предсказание FPS в игре с улучшенной точностью
        
        Учитывает:
        - cpu_bound: насколько игра зависит от CPU (0-1)
        - stability_factor: стабильность FPS (влияет на 1% Low)
        - Разрешение: при 4K CPU влияет меньше
        - VRAM требования: недостаток = штраф производительности
        """
        # Получаем бенчмарки
        gpu_benchmarks = self.benchmark_service.get_gpu_benchmarks(gpu_name)
        cpu_benchmarks = self.benchmark_service.get_cpu_benchmarks(cpu_name)
        
        if not gpu_benchmarks or 'timespy' not in gpu_benchmarks:
            return None
        
        # Находим игру
        game_data = self._find_game(game)
        if not game_data:
            return None
        
        game_name, base_fps_data = game_data
        
        # Базовый FPS для разрешения
        base_fps = base_fps_data.get(resolution, base_fps_data.get('1080p', 60))
        
        # GPU скейлинг
        gpu_score = gpu_benchmarks['timespy'].score
        gpu_ratio = gpu_score / self.reference_gpu_score
        
        # Получаем cpu_bound из данных игры (по умолчанию 0.35)
        cpu_bound = base_fps_data.get('cpu_bound', 0.35)
        
        # Разрешение влияет на CPU weight
        # При 4K CPU влияет меньше, при 1080p - больше
        resolution_cpu_modifier = {
            '1080p': 1.0,
            '1440p': 0.75,
            '4k': 0.5
        }.get(resolution, 1.0)
        
        # Итоговый вес CPU в расчёте
        # Формула: cpu_bound * resolution_modifier, но не более 50%
        cpu_weight = min(0.50, cpu_bound * resolution_cpu_modifier)
        
        if cpu_benchmarks and 'cinebench_single' in cpu_benchmarks:
            cpu_score = cpu_benchmarks['cinebench_single'].score
            cpu_ratio = cpu_score / self.reference_cpu_score
        else:
            cpu_ratio = 0.85  # Предполагаем средний CPU
        
        # Комбинированный скейлинг с учётом cpu_bound
        # GPU weight = 1 - cpu_weight
        gpu_weight = 1 - cpu_weight
        combined_ratio = (gpu_ratio * gpu_weight) + (cpu_ratio * cpu_weight)
        
        # Ray Tracing штраф
        if ray_tracing:
            rt_penalty = base_fps_data.get('rt_penalty', 0.5)
            combined_ratio *= rt_penalty
            
            # RT работает лучше на NVIDIA (аппаратное ускорение)
            if 'NVIDIA' not in gpu_name and 'GeForce' not in gpu_name:
                combined_ratio *= 0.80  # AMD/Intel RT penalty
        
        # DLSS/FSR буст с учётом качества
        upscaling_boost = 1.0
        if dlss_fsr:
            dlss_lower = dlss_fsr.lower()
            if 'dlss' in dlss_lower:
                # DLSS 3.5+ имеет лучшее качество при том же бусте
                if 'quality' in dlss_lower:
                    upscaling_boost = 1.5
                elif 'balanced' in dlss_lower:
                    upscaling_boost = 1.8
                elif 'performance' in dlss_lower:
                    upscaling_boost = 2.2
                elif 'ultra' in dlss_lower:
                    upscaling_boost = 2.8
                else:
                    upscaling_boost = 1.6  # Default DLSS
            elif 'fsr' in dlss_lower:
                # FSR 3.0+ качество
                if 'quality' in dlss_lower:
                    upscaling_boost = 1.35
                elif 'balanced' in dlss_lower:
                    upscaling_boost = 1.55
                elif 'performance' in dlss_lower:
                    upscaling_boost = 1.85
                elif 'ultra' in dlss_lower:
                    upscaling_boost = 2.4
                else:
                    upscaling_boost = 1.45  # Default FSR
            elif 'xess' in dlss_lower:
                # Intel XeSS
                if 'quality' in dlss_lower:
                    upscaling_boost = 1.4
                elif 'balanced' in dlss_lower:
                    upscaling_boost = 1.6
                elif 'performance' in dlss_lower:
                    upscaling_boost = 1.9
                else:
                    upscaling_boost = 1.5
        
        # Финальный FPS
        predicted_fps = base_fps * combined_ratio * upscaling_boost
        
        # 1% Low с использованием stability_factor игры
        # Более стабильные игры имеют higher stability_factor (ближе к 0.85)
        # Нестабильные игры имеют lower stability_factor (около 0.65)
        stability_factor = base_fps_data.get('stability_factor', 0.75)
        
        # Дополнительные факторы влияющие на стабильность:
        # - При низком FPS просадки ощущаются меньше
        # - RT увеличивает нестабильность
        # - CPU bottleneck увеличивает нестабильность
        
        stability_modifier = 1.0
        if ray_tracing:
            stability_modifier *= 0.95  # RT уменьшает стабильность
        
        # Если CPU слабее GPU значительно, это влияет на 1% Low
        if cpu_benchmarks and 'cinebench_single' in cpu_benchmarks:
            cpu_gpu_balance = cpu_ratio / gpu_ratio
            if cpu_gpu_balance < 0.7:  # CPU bottleneck
                stability_modifier *= 0.92
        
        final_stability = stability_factor * stability_modifier
        fps_1_low = predicted_fps * final_stability
        
        # Уверенность в предсказании
        confidence = 88.0
        if not cpu_benchmarks:
            confidence -= 12  # Большой штраф за отсутствие данных CPU
        if ray_tracing:
            confidence -= 5
        if dlss_fsr:
            confidence -= 3  # Меньший штраф, upscaling хорошо изучен
        
        # Бонус к уверенности для популярных конфигураций
        if gpu_score > 20000:  # High-end GPU
            confidence += 3
        
        confidence = max(50.0, min(95.0, confidence))  # Clamp
        
        return GameFPSPrediction(
            game_name=game_name,
            resolution=resolution,
            quality_preset="Ultra",
            predicted_fps=round(predicted_fps, 1),
            fps_1_low=round(fps_1_low, 1),
            confidence=round(confidence, 1),
            ray_tracing=ray_tracing,
            dlss_fsr=dlss_fsr
        )
    
    def predict_all_games(
        self,
        gpu_name: str,
        cpu_name: str,
        resolution: str = "1080p"
    ) -> List[GameFPSPrediction]:
        """Предсказание FPS для всех игр"""
        predictions = []
        
        for game in self.db.GAME_BASE_FPS.keys():
            # Без RT
            pred = self.predict_fps(gpu_name, cpu_name, game, resolution, False)
            if pred:
                predictions.append(pred)
            
            # С RT (для игр с RT)
            if self.db.GAME_BASE_FPS[game].get('rt_penalty', 1.0) < 1.0:
                pred_rt = self.predict_fps(gpu_name, cpu_name, game, resolution, True)
                if pred_rt:
                    predictions.append(pred_rt)
        
        return predictions
    
    def _find_game(self, game_query: str) -> Optional[Tuple[str, Dict]]:
        """Поиск игры в базе"""
        query_lower = game_query.lower()
        
        for game_name, data in self.db.GAME_BASE_FPS.items():
            if game_name.lower() == query_lower:
                return (game_name, data)
        
        # Частичное совпадение
        for game_name, data in self.db.GAME_BASE_FPS.items():
            if query_lower in game_name.lower() or game_name.lower() in query_lower:
                return (game_name, data)
        
        return None
    
    def get_game_list(self) -> List[str]:
        """Список доступных игр"""
        return list(self.db.GAME_BASE_FPS.keys())
    
    def get_resolution_recommendation(
        self,
        gpu_name: str,
        cpu_name: str,
        target_fps: int = 60
    ) -> Dict[str, str]:
        """
        Рекомендация разрешения для достижения целевого FPS
        """
        recommendations = {}
        
        for game in self.db.GAME_BASE_FPS.keys():
            for resolution in ['4k', '1440p', '1080p']:
                pred = self.predict_fps(gpu_name, cpu_name, game, resolution)
                if pred and pred.predicted_fps >= target_fps:
                    recommendations[game] = resolution
                    break
            else:
                recommendations[game] = "1080p (может не достичь цели)"
        
        return recommendations


class ConfigurationPerformanceAnalyzer:
    """Анализатор производительности конфигурации"""
    
    def __init__(self):
        self.benchmark_service = BenchmarkService()
        self.fps_service = FPSPredictionService()
    
    def analyze_configuration(self, configuration) -> Dict:
        """Полный анализ конфигурации"""
        result = {
            'cpu_benchmarks': {},
            'gpu_benchmarks': {},
            'gaming_performance': {},
            'bottleneck_analysis': {},
            'recommendations': []
        }
        
        cpu_name = configuration.cpu.name if configuration.cpu else None
        gpu_name = configuration.gpu.name if configuration.gpu else None
        
        # CPU бенчмарки
        if cpu_name:
            result['cpu_benchmarks'] = {
                k: v.to_dict() 
                for k, v in self.benchmark_service.get_cpu_benchmarks(cpu_name).items()
            }
        
        # GPU бенчмарки
        if gpu_name:
            result['gpu_benchmarks'] = {
                k: v.to_dict() 
                for k, v in self.benchmark_service.get_gpu_benchmarks(gpu_name).items()
            }
        
        # Игровая производительность
        if cpu_name and gpu_name:
            for resolution in ['1080p', '1440p', '4k']:
                predictions = []
                for game in self.fps_service.get_game_list()[:10]:  # Топ 10 игр
                    pred = self.fps_service.predict_fps(gpu_name, cpu_name, game, resolution)
                    if pred:
                        predictions.append(pred.to_dict())
                result['gaming_performance'][resolution] = predictions
            
            # Анализ bottleneck
            result['bottleneck_analysis'] = self._analyze_bottleneck(cpu_name, gpu_name)
            
            # Рекомендации
            result['recommendations'] = self._get_recommendations(
                cpu_name, gpu_name, result['bottleneck_analysis']
            )
        
        return result
    
    def _analyze_bottleneck(self, cpu_name: str, gpu_name: str) -> Dict:
        """Анализ bottleneck"""
        cpu_benchmarks = self.benchmark_service.get_cpu_benchmarks(cpu_name)
        gpu_benchmarks = self.benchmark_service.get_gpu_benchmarks(gpu_name)
        
        if not cpu_benchmarks or not gpu_benchmarks:
            return {'status': 'unknown', 'message': 'Недостаточно данных'}
        
        cpu_percentile = cpu_benchmarks.get('cinebench_single', {})
        gpu_percentile = gpu_benchmarks.get('timespy', {})
        
        if hasattr(cpu_percentile, 'percentile') and hasattr(gpu_percentile, 'percentile'):
            cpu_p = cpu_percentile.percentile
            gpu_p = gpu_percentile.percentile
            
            diff = abs(cpu_p - gpu_p)
            
            if diff < 15:
                return {
                    'status': 'balanced',
                    'cpu_percentile': cpu_p,
                    'gpu_percentile': gpu_p,
                    'message': 'Сбалансированная система'
                }
            elif cpu_p < gpu_p:
                return {
                    'status': 'cpu_bottleneck',
                    'cpu_percentile': cpu_p,
                    'gpu_percentile': gpu_p,
                    'severity': 'high' if diff > 30 else 'medium',
                    'message': f'CPU ограничивает GPU на {diff:.0f}%'
                }
            else:
                return {
                    'status': 'gpu_bottleneck',
                    'cpu_percentile': cpu_p,
                    'gpu_percentile': gpu_p,
                    'severity': 'high' if diff > 30 else 'medium',
                    'message': f'GPU ограничивает CPU на {diff:.0f}%'
                }
        
        return {'status': 'unknown', 'message': 'Не удалось определить'}
    
    def _get_recommendations(
        self, 
        cpu_name: str, 
        gpu_name: str, 
        bottleneck: Dict
    ) -> List[str]:
        """Рекомендации по улучшению"""
        recommendations = []
        
        status = bottleneck.get('status', 'unknown')
        
        if status == 'cpu_bottleneck':
            recommendations.append(
                "Рассмотрите апгрейд CPU для раскрытия потенциала GPU"
            )
            recommendations.append(
                "При 1440p/4K влияние CPU bottleneck снижается"
            )
        elif status == 'gpu_bottleneck':
            recommendations.append(
                "GPU является ограничивающим фактором - апгрейд повысит FPS"
            )
        elif status == 'balanced':
            recommendations.append(
                "Отличный баланс компонентов!"
            )
        
        return recommendations


# Вспомогательные функции для views
def get_benchmarks_for_cpu(cpu_name: str) -> Dict:
    """Получение бенчмарков CPU"""
    service = BenchmarkService()
    return {k: v.to_dict() for k, v in service.get_cpu_benchmarks(cpu_name).items()}


def get_benchmarks_for_gpu(gpu_name: str) -> Dict:
    """Получение бенчмарков GPU"""
    service = BenchmarkService()
    return {k: v.to_dict() for k, v in service.get_gpu_benchmarks(gpu_name).items()}


def predict_game_fps(gpu_name: str, cpu_name: str, game: str, resolution: str = "1080p") -> Optional[Dict]:
    """Предсказание FPS"""
    service = FPSPredictionService()
    result = service.predict_fps(gpu_name, cpu_name, game, resolution)
    return result.to_dict() if result else None


def get_available_games() -> List[str]:
    """Список игр"""
    service = FPSPredictionService()
    return service.get_game_list()


def analyze_configuration_performance(configuration) -> Dict:
    """Анализ конфигурации"""
    analyzer = ConfigurationPerformanceAnalyzer()
    return analyzer.analyze_configuration(configuration)
