"""
Django management command to import 2025 PC components from the big unified text file.
Supports: GPU, CPU, Motherboard, RAM, Storage, PSU, Case, Cooling
"""
import os
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling


# Component specs databases - base models only, variants inherit specs
CPU_BASE_SPECS = {
    # AMD Ryzen 9000 Series (AM5)
    'Ryzen 9 9950X3D': {'socket': 'AM5', 'cores': 16, 'threads': 32, 'base_clock': 4.3, 'boost_clock': 5.7, 'tdp': 170, 'score': 95000},
    'Ryzen 9 9950X': {'socket': 'AM5', 'cores': 16, 'threads': 32, 'base_clock': 4.3, 'boost_clock': 5.7, 'tdp': 170, 'score': 90000},
    'Ryzen 9 9900X': {'socket': 'AM5', 'cores': 12, 'threads': 24, 'base_clock': 4.4, 'boost_clock': 5.6, 'tdp': 120, 'score': 75000},
    'Ryzen 7 9800X3D': {'socket': 'AM5', 'cores': 8, 'threads': 16, 'base_clock': 4.7, 'boost_clock': 5.2, 'tdp': 120, 'score': 85000},
    'Ryzen 7 9700X': {'socket': 'AM5', 'cores': 8, 'threads': 16, 'base_clock': 3.8, 'boost_clock': 5.5, 'tdp': 65, 'score': 55000},
    'Ryzen 5 9600X': {'socket': 'AM5', 'cores': 6, 'threads': 12, 'base_clock': 3.9, 'boost_clock': 5.4, 'tdp': 65, 'score': 45000},
    'Ryzen 5 9500G': {'socket': 'AM5', 'cores': 6, 'threads': 12, 'base_clock': 3.8, 'boost_clock': 5.1, 'tdp': 65, 'score': 35000},
    'Ryzen 5 9300G': {'socket': 'AM5', 'cores': 4, 'threads': 8, 'base_clock': 3.4, 'boost_clock': 4.9, 'tdp': 65, 'score': 25000},
    'Ryzen 5 8600G': {'socket': 'AM5', 'cores': 6, 'threads': 12, 'base_clock': 4.3, 'boost_clock': 5.0, 'tdp': 65, 'score': 30000},
    # AMD Ryzen 7000 Series (AM5)
    'Ryzen 9 7950X3D': {'socket': 'AM5', 'cores': 16, 'threads': 32, 'base_clock': 4.2, 'boost_clock': 5.7, 'tdp': 120, 'score': 88000},
    'Ryzen 9 7950X': {'socket': 'AM5', 'cores': 16, 'threads': 32, 'base_clock': 4.5, 'boost_clock': 5.7, 'tdp': 170, 'score': 85000},
    'Ryzen 9 7900X': {'socket': 'AM5', 'cores': 12, 'threads': 24, 'base_clock': 4.7, 'boost_clock': 5.6, 'tdp': 170, 'score': 70000},
    'Ryzen 9 7900': {'socket': 'AM5', 'cores': 12, 'threads': 24, 'base_clock': 3.7, 'boost_clock': 5.4, 'tdp': 65, 'score': 65000},
    'Ryzen 7 7800X3D': {'socket': 'AM5', 'cores': 8, 'threads': 16, 'base_clock': 4.2, 'boost_clock': 5.0, 'tdp': 120, 'score': 75000},
    'Ryzen 7 7700X': {'socket': 'AM5', 'cores': 8, 'threads': 16, 'base_clock': 4.5, 'boost_clock': 5.4, 'tdp': 105, 'score': 50000},
    'Ryzen 7 7700': {'socket': 'AM5', 'cores': 8, 'threads': 16, 'base_clock': 3.8, 'boost_clock': 5.3, 'tdp': 65, 'score': 45000},
    'Ryzen 5 7600X': {'socket': 'AM5', 'cores': 6, 'threads': 12, 'base_clock': 4.7, 'boost_clock': 5.3, 'tdp': 105, 'score': 40000},
    'Ryzen 5 7600': {'socket': 'AM5', 'cores': 6, 'threads': 12, 'base_clock': 3.8, 'boost_clock': 5.1, 'tdp': 65, 'score': 35000},
    # AMD Ryzen 5000 Series (AM4)
    'Ryzen 9 5950X': {'socket': 'AM4', 'cores': 16, 'threads': 32, 'base_clock': 3.4, 'boost_clock': 4.9, 'tdp': 105, 'score': 65000},
    'Ryzen 9 5900X': {'socket': 'AM4', 'cores': 12, 'threads': 24, 'base_clock': 3.7, 'boost_clock': 4.8, 'tdp': 105, 'score': 55000},
    'Ryzen 7 5800X3D': {'socket': 'AM4', 'cores': 8, 'threads': 16, 'base_clock': 3.4, 'boost_clock': 4.5, 'tdp': 105, 'score': 60000},
    'Ryzen 7 5800X': {'socket': 'AM4', 'cores': 8, 'threads': 16, 'base_clock': 3.8, 'boost_clock': 4.7, 'tdp': 105, 'score': 45000},
    'Ryzen 7 5700X3D': {'socket': 'AM4', 'cores': 8, 'threads': 16, 'base_clock': 3.0, 'boost_clock': 4.1, 'tdp': 105, 'score': 50000},
    'Ryzen 7 5700X': {'socket': 'AM4', 'cores': 8, 'threads': 16, 'base_clock': 3.4, 'boost_clock': 4.6, 'tdp': 65, 'score': 40000},
    'Ryzen 5 5600X': {'socket': 'AM4', 'cores': 6, 'threads': 12, 'base_clock': 3.7, 'boost_clock': 4.6, 'tdp': 65, 'score': 32000},
    'Ryzen 5 5600': {'socket': 'AM4', 'cores': 6, 'threads': 12, 'base_clock': 3.5, 'boost_clock': 4.4, 'tdp': 65, 'score': 30000},
    'Ryzen 5 5500': {'socket': 'AM4', 'cores': 6, 'threads': 12, 'base_clock': 3.6, 'boost_clock': 4.2, 'tdp': 65, 'score': 25000},
    'Ryzen 5 3600': {'socket': 'AM4', 'cores': 6, 'threads': 12, 'base_clock': 3.6, 'boost_clock': 4.2, 'tdp': 65, 'score': 20000},
    # Intel 14th Gen (LGA1700)
    'Core i9-14900K': {'socket': 'LGA1700', 'cores': 24, 'threads': 32, 'base_clock': 3.2, 'boost_clock': 6.0, 'tdp': 253, 'score': 85000},
    'Core i9-14900KF': {'socket': 'LGA1700', 'cores': 24, 'threads': 32, 'base_clock': 3.2, 'boost_clock': 6.0, 'tdp': 253, 'score': 84000},
    'Core i7-14700K': {'socket': 'LGA1700', 'cores': 20, 'threads': 28, 'base_clock': 3.4, 'boost_clock': 5.6, 'tdp': 253, 'score': 70000},
    'Core i7-14700KF': {'socket': 'LGA1700', 'cores': 20, 'threads': 28, 'base_clock': 3.4, 'boost_clock': 5.6, 'tdp': 253, 'score': 69000},
    'Core i5-14600K': {'socket': 'LGA1700', 'cores': 14, 'threads': 20, 'base_clock': 3.5, 'boost_clock': 5.3, 'tdp': 181, 'score': 50000},
    'Core i5-14600KF': {'socket': 'LGA1700', 'cores': 14, 'threads': 20, 'base_clock': 3.5, 'boost_clock': 5.3, 'tdp': 181, 'score': 49000},
    'Core i5-14500': {'socket': 'LGA1700', 'cores': 14, 'threads': 20, 'base_clock': 2.6, 'boost_clock': 5.0, 'tdp': 65, 'score': 40000},
    'Core i5-14400F': {'socket': 'LGA1700', 'cores': 10, 'threads': 16, 'base_clock': 2.5, 'boost_clock': 4.7, 'tdp': 65, 'score': 32000},
    # Intel 13th Gen (LGA1700)
    'Core i7-13700K': {'socket': 'LGA1700', 'cores': 16, 'threads': 24, 'base_clock': 3.4, 'boost_clock': 5.4, 'tdp': 253, 'score': 65000},
    'Core i5-13600K': {'socket': 'LGA1700', 'cores': 14, 'threads': 20, 'base_clock': 3.5, 'boost_clock': 5.1, 'tdp': 181, 'score': 48000},
    'Core i5-13500': {'socket': 'LGA1700', 'cores': 14, 'threads': 20, 'base_clock': 2.5, 'boost_clock': 4.8, 'tdp': 65, 'score': 38000},
    'Core i5-13400F': {'socket': 'LGA1700', 'cores': 10, 'threads': 16, 'base_clock': 2.5, 'boost_clock': 4.6, 'tdp': 65, 'score': 30000},
    # Intel 12th Gen (LGA1700)
    'Core i5-12400F': {'socket': 'LGA1700', 'cores': 6, 'threads': 12, 'base_clock': 2.5, 'boost_clock': 4.4, 'tdp': 65, 'score': 25000},
    'Core i3-12100F': {'socket': 'LGA1700', 'cores': 4, 'threads': 8, 'base_clock': 3.3, 'boost_clock': 4.3, 'tdp': 58, 'score': 18000},
    # Intel Core Ultra 200 (LGA1851)
    'Core Ultra 9 285K': {'socket': 'LGA1851', 'cores': 24, 'threads': 24, 'base_clock': 3.7, 'boost_clock': 5.7, 'tdp': 125, 'score': 82000},
    'Core Ultra 7 265K': {'socket': 'LGA1851', 'cores': 20, 'threads': 20, 'base_clock': 3.9, 'boost_clock': 5.5, 'tdp': 125, 'score': 65000},
    'Core Ultra 5 245K': {'socket': 'LGA1851', 'cores': 14, 'threads': 14, 'base_clock': 4.2, 'boost_clock': 5.2, 'tdp': 125, 'score': 48000},
    'Core Ultra 7 270K Plus': {'socket': 'LGA1851', 'cores': 20, 'threads': 20, 'base_clock': 4.0, 'boost_clock': 5.6, 'tdp': 125, 'score': 68000},
}

GPU_BASE_SPECS = {
    # NVIDIA RTX 50 Series
    'GeForce RTX 5090': {'memory': 24, 'memory_type': 'GDDR7', 'core_clock': 2010, 'boost_clock': 2520, 'tdp': 575, 'psu': 1000, 'score': 100000},
    'GeForce RTX 5080': {'memory': 16, 'memory_type': 'GDDR7', 'core_clock': 2010, 'boost_clock': 2620, 'tdp': 360, 'psu': 750, 'score': 85000},
    'GeForce RTX 5070 Ti': {'memory': 16, 'memory_type': 'GDDR7', 'core_clock': 2010, 'boost_clock': 2450, 'tdp': 285, 'psu': 700, 'score': 70000},
    'GeForce RTX 5070': {'memory': 12, 'memory_type': 'GDDR7', 'core_clock': 2010, 'boost_clock': 2380, 'tdp': 220, 'psu': 650, 'score': 60000},
    'GeForce RTX 5060 Ti 16GB': {'memory': 16, 'memory_type': 'GDDR7', 'core_clock': 1980, 'boost_clock': 2250, 'tdp': 180, 'psu': 550, 'score': 48000},
    'GeForce RTX 5060 Ti 8GB': {'memory': 8, 'memory_type': 'GDDR7', 'core_clock': 1980, 'boost_clock': 2250, 'tdp': 180, 'psu': 550, 'score': 45000},
    'GeForce RTX 5060': {'memory': 8, 'memory_type': 'GDDR7', 'core_clock': 1950, 'boost_clock': 2150, 'tdp': 150, 'psu': 500, 'score': 38000},
    'GeForce RTX 5050': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1920, 'boost_clock': 2000, 'tdp': 115, 'psu': 450, 'score': 28000},
    # NVIDIA RTX 40 Series
    'GeForce RTX 4090': {'memory': 24, 'memory_type': 'GDDR6X', 'core_clock': 2235, 'boost_clock': 2520, 'tdp': 450, 'psu': 850, 'score': 95000},
    'GeForce RTX 4080 Super': {'memory': 16, 'memory_type': 'GDDR6X', 'core_clock': 2295, 'boost_clock': 2550, 'tdp': 320, 'psu': 750, 'score': 75000},
    'GeForce RTX 4080': {'memory': 16, 'memory_type': 'GDDR6X', 'core_clock': 2205, 'boost_clock': 2505, 'tdp': 320, 'psu': 750, 'score': 72000},
    'GeForce RTX 4070 Ti Super': {'memory': 16, 'memory_type': 'GDDR6X', 'core_clock': 2340, 'boost_clock': 2610, 'tdp': 285, 'psu': 700, 'score': 65000},
    'GeForce RTX 4070 Ti': {'memory': 12, 'memory_type': 'GDDR6X', 'core_clock': 2310, 'boost_clock': 2610, 'tdp': 285, 'psu': 700, 'score': 60000},
    'GeForce RTX 4070 Super': {'memory': 12, 'memory_type': 'GDDR6X', 'core_clock': 1980, 'boost_clock': 2475, 'tdp': 220, 'psu': 650, 'score': 55000},
    'GeForce RTX 4070': {'memory': 12, 'memory_type': 'GDDR6X', 'core_clock': 1920, 'boost_clock': 2475, 'tdp': 200, 'psu': 650, 'score': 50000},
    'GeForce RTX 4060 Ti 16GB': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 2310, 'boost_clock': 2535, 'tdp': 165, 'psu': 550, 'score': 42000},
    'GeForce RTX 4060 Ti': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 2310, 'boost_clock': 2535, 'tdp': 160, 'psu': 550, 'score': 40000},
    'GeForce RTX 4060': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1830, 'boost_clock': 2460, 'tdp': 115, 'psu': 450, 'score': 32000},
    # NVIDIA RTX 30 Series
    'GeForce RTX 3090 Ti': {'memory': 24, 'memory_type': 'GDDR6X', 'core_clock': 1560, 'boost_clock': 1860, 'tdp': 450, 'psu': 850, 'score': 65000},
    'GeForce RTX 3090': {'memory': 24, 'memory_type': 'GDDR6X', 'core_clock': 1395, 'boost_clock': 1695, 'tdp': 350, 'psu': 750, 'score': 60000},
    'GeForce RTX 3080 Ti': {'memory': 12, 'memory_type': 'GDDR6X', 'core_clock': 1365, 'boost_clock': 1665, 'tdp': 350, 'psu': 750, 'score': 55000},
    'GeForce RTX 3080 12GB': {'memory': 12, 'memory_type': 'GDDR6X', 'core_clock': 1260, 'boost_clock': 1710, 'tdp': 350, 'psu': 750, 'score': 52000},
    'GeForce RTX 3080': {'memory': 10, 'memory_type': 'GDDR6X', 'core_clock': 1440, 'boost_clock': 1710, 'tdp': 320, 'psu': 750, 'score': 50000},
    'GeForce RTX 3070 Ti': {'memory': 8, 'memory_type': 'GDDR6X', 'core_clock': 1575, 'boost_clock': 1770, 'tdp': 290, 'psu': 650, 'score': 45000},
    'GeForce RTX 3070': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1500, 'boost_clock': 1725, 'tdp': 220, 'psu': 650, 'score': 42000},
    'GeForce RTX 3060 Ti': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1410, 'boost_clock': 1665, 'tdp': 200, 'psu': 600, 'score': 38000},
    'GeForce RTX 3060': {'memory': 12, 'memory_type': 'GDDR6', 'core_clock': 1320, 'boost_clock': 1777, 'tdp': 170, 'psu': 550, 'score': 32000},
    'GeForce RTX 3050 8GB': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1552, 'boost_clock': 1777, 'tdp': 130, 'psu': 450, 'score': 22000},
    'GeForce RTX 3050 6GB': {'memory': 6, 'memory_type': 'GDDR6', 'core_clock': 1470, 'boost_clock': 1740, 'tdp': 70, 'psu': 350, 'score': 18000},
    'GeForce RTX 3050 4GB': {'memory': 4, 'memory_type': 'GDDR6', 'core_clock': 1470, 'boost_clock': 1740, 'tdp': 70, 'psu': 350, 'score': 15000},
    # NVIDIA RTX 20 Series
    'GeForce RTX 2080 Ti': {'memory': 11, 'memory_type': 'GDDR6', 'core_clock': 1350, 'boost_clock': 1545, 'tdp': 250, 'psu': 650, 'score': 45000},
    'GeForce RTX 2080 Super': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1650, 'boost_clock': 1815, 'tdp': 250, 'psu': 650, 'score': 40000},
    'GeForce RTX 2080': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1515, 'boost_clock': 1710, 'tdp': 215, 'psu': 600, 'score': 38000},
    'GeForce RTX 2070 Super': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1605, 'boost_clock': 1770, 'tdp': 215, 'psu': 600, 'score': 35000},
    'GeForce RTX 2070': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1410, 'boost_clock': 1620, 'tdp': 175, 'psu': 550, 'score': 32000},
    'GeForce RTX 2060 Super': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1470, 'boost_clock': 1650, 'tdp': 175, 'psu': 550, 'score': 30000},
    'GeForce RTX 2060': {'memory': 6, 'memory_type': 'GDDR6', 'core_clock': 1365, 'boost_clock': 1680, 'tdp': 160, 'psu': 500, 'score': 28000},
    # NVIDIA GTX 16 Series
    'GeForce GTX 1660 Super': {'memory': 6, 'memory_type': 'GDDR6', 'core_clock': 1530, 'boost_clock': 1785, 'tdp': 125, 'psu': 450, 'score': 22000},
    'GeForce GTX 1660 Ti': {'memory': 6, 'memory_type': 'GDDR6', 'core_clock': 1500, 'boost_clock': 1770, 'tdp': 120, 'psu': 450, 'score': 21000},
    'GeForce GTX 1660': {'memory': 6, 'memory_type': 'GDDR5', 'core_clock': 1530, 'boost_clock': 1785, 'tdp': 120, 'psu': 450, 'score': 19000},
    'GeForce GTX 1650': {'memory': 4, 'memory_type': 'GDDR5', 'core_clock': 1485, 'boost_clock': 1665, 'tdp': 75, 'psu': 350, 'score': 12000},
    # AMD RX 9000 Series
    'Radeon RX 9070 XT': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 2100, 'boost_clock': 2950, 'tdp': 300, 'psu': 700, 'score': 68000},
    'Radeon RX 9070': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 2100, 'boost_clock': 2800, 'tdp': 250, 'psu': 650, 'score': 58000},
    'Radeon RX 9060 XT 16GB': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 2000, 'boost_clock': 2500, 'tdp': 180, 'psu': 550, 'score': 42000},
    'Radeon RX 9060 XT 8GB': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 2000, 'boost_clock': 2500, 'tdp': 180, 'psu': 550, 'score': 38000},
    # AMD RX 7000 Series
    'Radeon RX 7900 XTX': {'memory': 24, 'memory_type': 'GDDR6', 'core_clock': 1900, 'boost_clock': 2500, 'tdp': 355, 'psu': 800, 'score': 70000},
    'Radeon RX 7900 XT': {'memory': 20, 'memory_type': 'GDDR6', 'core_clock': 1500, 'boost_clock': 2400, 'tdp': 315, 'psu': 750, 'score': 62000},
    'Radeon RX 7900 GRE': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 1500, 'boost_clock': 2245, 'tdp': 260, 'psu': 650, 'score': 55000},
    'Radeon RX 7800 XT': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 1295, 'boost_clock': 2430, 'tdp': 263, 'psu': 650, 'score': 50000},
    'Radeon RX 7700 XT': {'memory': 12, 'memory_type': 'GDDR6', 'core_clock': 1700, 'boost_clock': 2544, 'tdp': 245, 'psu': 600, 'score': 45000},
    'Radeon RX 7600 XT': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 1720, 'boost_clock': 2755, 'tdp': 190, 'psu': 550, 'score': 35000},
    'Radeon RX 7600': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1720, 'boost_clock': 2655, 'tdp': 165, 'psu': 500, 'score': 30000},
    # AMD RX 6000 Series
    'Radeon RX 6950 XT': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 1860, 'boost_clock': 2310, 'tdp': 335, 'psu': 750, 'score': 55000},
    'Radeon RX 6900 XT': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 1825, 'boost_clock': 2250, 'tdp': 300, 'psu': 700, 'score': 52000},
    'Radeon RX 6800 XT': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 1825, 'boost_clock': 2250, 'tdp': 300, 'psu': 700, 'score': 48000},
    'Radeon RX 6800': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 1700, 'boost_clock': 2105, 'tdp': 250, 'psu': 650, 'score': 42000},
    'Radeon RX 6750 XT': {'memory': 12, 'memory_type': 'GDDR6', 'core_clock': 2150, 'boost_clock': 2600, 'tdp': 250, 'psu': 600, 'score': 38000},
    'Radeon RX 6700 XT': {'memory': 12, 'memory_type': 'GDDR6', 'core_clock': 2321, 'boost_clock': 2581, 'tdp': 230, 'psu': 550, 'score': 35000},
    'Radeon RX 6650 XT': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 2055, 'boost_clock': 2635, 'tdp': 180, 'psu': 500, 'score': 30000},
    'Radeon RX 6600 XT': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1968, 'boost_clock': 2589, 'tdp': 160, 'psu': 500, 'score': 28000},
    'Radeon RX 6600': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1626, 'boost_clock': 2491, 'tdp': 132, 'psu': 450, 'score': 25000},
    'Radeon RX 6500 XT': {'memory': 4, 'memory_type': 'GDDR6', 'core_clock': 2310, 'boost_clock': 2815, 'tdp': 107, 'psu': 400, 'score': 15000},
    # Intel Arc
    'Intel Arc B580': {'memory': 12, 'memory_type': 'GDDR6', 'core_clock': 2670, 'boost_clock': 2670, 'tdp': 190, 'psu': 550, 'score': 35000},
    'Intel Arc B570': {'memory': 10, 'memory_type': 'GDDR6', 'core_clock': 2500, 'boost_clock': 2500, 'tdp': 150, 'psu': 500, 'score': 28000},
    'Intel Arc A770 16GB': {'memory': 16, 'memory_type': 'GDDR6', 'core_clock': 2100, 'boost_clock': 2400, 'tdp': 225, 'psu': 600, 'score': 32000},
    'Intel Arc A770 8GB': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 2100, 'boost_clock': 2400, 'tdp': 225, 'psu': 600, 'score': 30000},
    'Intel Arc A750': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 2050, 'boost_clock': 2400, 'tdp': 225, 'psu': 600, 'score': 28000},
    'Intel Arc A580': {'memory': 8, 'memory_type': 'GDDR6', 'core_clock': 1700, 'boost_clock': 2000, 'tdp': 185, 'psu': 500, 'score': 22000},
    'Intel Arc A380': {'memory': 6, 'memory_type': 'GDDR6', 'core_clock': 2000, 'boost_clock': 2000, 'tdp': 75, 'psu': 350, 'score': 12000},
}

MOTHERBOARD_CHIPSETS = {
    # AMD AM5
    'X870E': {'socket': 'AM5', 'memory_type': 'DDR5', 'max_memory': 256, 'memory_slots': 4, 'pcie_slots': 3, 'm2_slots': 5, 'form_factor': 'ATX'},
    'X870': {'socket': 'AM5', 'memory_type': 'DDR5', 'max_memory': 192, 'memory_slots': 4, 'pcie_slots': 2, 'm2_slots': 4, 'form_factor': 'ATX'},
    'B850': {'socket': 'AM5', 'memory_type': 'DDR5', 'max_memory': 192, 'memory_slots': 4, 'pcie_slots': 2, 'm2_slots': 3, 'form_factor': 'ATX'},
    'B650': {'socket': 'AM5', 'memory_type': 'DDR5', 'max_memory': 128, 'memory_slots': 4, 'pcie_slots': 2, 'm2_slots': 2, 'form_factor': 'ATX'},
    'A620': {'socket': 'AM5', 'memory_type': 'DDR5', 'max_memory': 128, 'memory_slots': 2, 'pcie_slots': 1, 'm2_slots': 1, 'form_factor': 'Micro-ATX'},
    # Intel LGA1851 (Arrow Lake)
    'Z890': {'socket': 'LGA1851', 'memory_type': 'DDR5', 'max_memory': 256, 'memory_slots': 4, 'pcie_slots': 3, 'm2_slots': 5, 'form_factor': 'ATX'},
    'B860': {'socket': 'LGA1851', 'memory_type': 'DDR5', 'max_memory': 192, 'memory_slots': 4, 'pcie_slots': 2, 'm2_slots': 3, 'form_factor': 'ATX'},
    # Intel LGA1700
    'Z790': {'socket': 'LGA1700', 'memory_type': 'DDR5', 'max_memory': 192, 'memory_slots': 4, 'pcie_slots': 3, 'm2_slots': 4, 'form_factor': 'ATX'},
    'B760': {'socket': 'LGA1700', 'memory_type': 'DDR5', 'max_memory': 128, 'memory_slots': 4, 'pcie_slots': 2, 'm2_slots': 2, 'form_factor': 'ATX'},
}


class Command(BaseCommand):
    help = 'Import 2025 PC components from the big unified text file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing components before import',
        )
    
    def handle(self, *args, **options):
        uploads_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'AI', 'uploads')
        uploads_dir = os.path.abspath(uploads_dir)
        
        big_file = os.path.join(uploads_dir, 'all_pc_parts_and_peripherals_rub_2025_big.txt')
        
        if not os.path.exists(big_file):
            self.stdout.write(self.style.ERROR(f'File not found: {big_file}'))
            return
        
        if options['clear']:
            self.stdout.write('Clearing existing components...')
            CPU.objects.all().delete()
            GPU.objects.all().delete()
            Motherboard.objects.all().delete()
            RAM.objects.all().delete()
            Storage.objects.all().delete()
            PSU.objects.all().delete()
            Case.objects.all().delete()
            Cooling.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all components'))
        
        # Parse the big file
        self.stdout.write(f'Parsing {big_file}...')
        sections = self.parse_big_file(big_file)
        
        # Import each section
        if 'Видеокарты' in sections:
            self.import_gpus(sections['Видеокарты'])
        if 'Процессоры' in sections:
            self.import_cpus(sections['Процессоры'])
        if 'Материнские платы' in sections:
            self.import_motherboards(sections['Материнские платы'])
        if 'Оперативная память' in sections:
            self.import_ram(sections['Оперативная память'])
        if 'Накопители' in sections:
            self.import_storage(sections['Накопители'])
        if 'Блоки питания' in sections:
            self.import_psus(sections['Блоки питания'])
        if 'Корпуса' in sections:
            self.import_cases(sections['Корпуса'])
        if 'Охлаждение' in sections:
            self.import_coolers(sections['Охлаждение'])
        
        # Show summary
        self.stdout.write(self.style.SUCCESS(f'\nImport complete!'))
        self.stdout.write(f'CPUs: {CPU.objects.count()}')
        self.stdout.write(f'GPUs: {GPU.objects.count()}')
        self.stdout.write(f'Motherboards: {Motherboard.objects.count()}')
        self.stdout.write(f'RAM: {RAM.objects.count()}')
        self.stdout.write(f'Storage: {Storage.objects.count()}')
        self.stdout.write(f'PSUs: {PSU.objects.count()}')
        self.stdout.write(f'Cases: {Case.objects.count()}')
        self.stdout.write(f'Coolers: {Cooling.objects.count()}')
    
    def parse_big_file(self, filepath):
        """Parse the big file into sections"""
        sections = {}
        current_section = None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Check for section headers first (they start with ## )
                if line.startswith('## '):
                    current_section = line[3:].strip()
                    sections[current_section] = []
                    continue
                
                # Skip comment lines (single # only, not section headers)
                if line.startswith('#'):
                    continue
                
                # Add data to current section
                if current_section and '|' in line:
                    sections[current_section].append(line)
        
        return sections
    
    def parse_price(self, price_str):
        """Parse price string like '185 203' to Decimal"""
        clean = price_str.replace(' ', '').replace(',', '')
        return Decimal(clean)
    
    def parse_line(self, line):
        """Parse a pipe-separated line"""
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 4:
            return {
                'brand': parts[0],
                'series': parts[1],
                'model': parts[2],
                'price': self.parse_price(parts[3])
            }
        return None
    
    def get_base_model(self, model_name):
        """Extract base model name without V2/RGB/White/Plus/OEM suffixes"""
        suffixes = [' V2', ' RGB', ' White', ' Plus', ' OEM']
        base = model_name
        for suffix in suffixes:
            base = base.replace(suffix, '')
        return base.strip()
    
    def find_specs(self, model_name, specs_dict):
        """Find specs for a model, checking base model if variant"""
        # Try exact match first
        if model_name in specs_dict:
            return specs_dict[model_name]
        
        # Try base model
        base_model = self.get_base_model(model_name)
        if base_model in specs_dict:
            return specs_dict[base_model]
        
        # Try partial match
        for key in specs_dict:
            if key in model_name or key in base_model:
                return specs_dict[key]
        
        return None
    
    def import_gpus(self, lines):
        count = 0
        for line in lines:
            data = self.parse_line(line)
            if not data:
                continue
            
            model_name = data['model']
            specs = self.find_specs(model_name, GPU_BASE_SPECS)
            
            if not specs:
                self.stdout.write(self.style.WARNING(f'No specs for GPU: {model_name}'))
                continue
            
            GPU.objects.update_or_create(
                name=model_name,
                manufacturer=data['brand'],
                defaults={
                    'chipset': data['series'],
                    'memory': specs.get('memory', 8),
                    'memory_type': specs.get('memory_type', 'GDDR6'),
                    'core_clock': specs.get('core_clock', 1500),
                    'boost_clock': specs.get('boost_clock', 2000),
                    'tdp': specs.get('tdp', 200),
                    'recommended_psu': specs.get('psu', 550),
                    'price': data['price'],
                    'performance_score': specs.get('score', 30000),
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} GPUs'))
    
    def import_cpus(self, lines):
        count = 0
        for line in lines:
            data = self.parse_line(line)
            if not data:
                continue
            
            model_name = data['model']
            specs = self.find_specs(model_name, CPU_BASE_SPECS)
            
            if not specs:
                self.stdout.write(self.style.WARNING(f'No specs for CPU: {model_name}'))
                continue
            
            CPU.objects.update_or_create(
                name=model_name,
                manufacturer=data['brand'],
                defaults={
                    'socket': specs.get('socket', 'Unknown'),
                    'cores': specs.get('cores', 8),
                    'threads': specs.get('threads', 16),
                    'base_clock': specs.get('base_clock', 3.5),
                    'boost_clock': specs.get('boost_clock', 5.0),
                    'tdp': specs.get('tdp', 125),
                    'price': data['price'],
                    'performance_score': specs.get('score', 30000),
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} CPUs'))
    
    def import_motherboards(self, lines):
        count = 0
        for line in lines:
            data = self.parse_line(line)
            if not data:
                continue
            
            chipset = data['series']
            specs = MOTHERBOARD_CHIPSETS.get(chipset, {})
            
            if not specs:
                # Default specs based on chipset name
                if 'X8' in chipset or 'B8' in chipset or 'A6' in chipset:
                    socket = 'AM5'
                elif 'Z8' in chipset or 'B8' in chipset:
                    socket = 'LGA1851'
                else:
                    socket = 'LGA1700'
                specs = {
                    'socket': socket,
                    'memory_type': 'DDR5',
                    'max_memory': 128,
                    'memory_slots': 4,
                    'pcie_slots': 2,
                    'm2_slots': 2,
                    'form_factor': 'ATX'
                }
            
            Motherboard.objects.update_or_create(
                name=data['model'],
                manufacturer=data['brand'],
                defaults={
                    'socket': specs.get('socket', 'AM5'),
                    'chipset': chipset,
                    'form_factor': specs.get('form_factor', 'ATX'),
                    'memory_slots': specs.get('memory_slots', 4),
                    'max_memory': specs.get('max_memory', 128),
                    'memory_type': specs.get('memory_type', 'DDR5'),
                    'pcie_slots': specs.get('pcie_slots', 2),
                    'm2_slots': specs.get('m2_slots', 2),
                    'price': data['price'],
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} Motherboards'))
    
    def import_ram(self, lines):
        count = 0
        for line in lines:
            data = self.parse_line(line)
            if not data:
                continue
            
            model = data['model']
            memory_type = data['series']
            
            # Parse capacity and speed from model name
            capacity_match = re.search(r'(\d+)GB', model)
            speed_match = re.search(r'(\d{4,5})', model)
            modules_match = re.search(r'(\d)x\d+', model)
            
            capacity = int(capacity_match.group(1)) if capacity_match else 32
            speed = int(speed_match.group(1)) if speed_match else 6000
            modules = int(modules_match.group(1)) if modules_match else 2
            
            RAM.objects.update_or_create(
                name=model,
                manufacturer=data['brand'],
                defaults={
                    'memory_type': memory_type,
                    'capacity': capacity,
                    'speed': speed,
                    'modules': modules,
                    'cas_latency': 'CL36' if memory_type == 'DDR5' else 'CL16',
                    'price': data['price'],
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} RAM kits'))
    
    def import_storage(self, lines):
        count = 0
        for line in lines:
            data = self.parse_line(line)
            if not data:
                continue
            
            model = data['model']
            series = data['series']
            
            # Determine storage type
            if 'NVMe' in series:
                storage_type = 'ssd_nvme'
                read_speed = 7000 if 'PCIe 5' in model or '990' in model else 5000
                write_speed = 6000 if 'PCIe 5' in model or '990' in model else 4000
            elif 'SATA' in series:
                storage_type = 'ssd_sata'
                read_speed = 550
                write_speed = 520
            else:
                storage_type = 'hdd'
                read_speed = 200
                write_speed = 180
            
            # Parse capacity
            capacity_match = re.search(r'(\d+)([TG]B)', model)
            if capacity_match:
                capacity = int(capacity_match.group(1))
                if capacity_match.group(2) == 'TB':
                    capacity *= 1000
            else:
                capacity = 1000
            
            Storage.objects.update_or_create(
                name=model,
                manufacturer=data['brand'],
                defaults={
                    'storage_type': storage_type,
                    'capacity': capacity,
                    'read_speed': read_speed,
                    'write_speed': write_speed,
                    'price': data['price'],
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} Storage devices'))
    
    def import_psus(self, lines):
        count = 0
        for line in lines:
            data = self.parse_line(line)
            if not data:
                continue
            
            model = data['model']
            
            # Parse wattage
            wattage_match = re.search(r'(\d{3,4})W', model)
            wattage = int(wattage_match.group(1)) if wattage_match else 750
            
            # Parse efficiency
            if 'Titanium' in model:
                efficiency = '80+ Titanium'
            elif 'Platinum' in model:
                efficiency = '80+ Platinum'
            elif 'Gold' in model:
                efficiency = '80+ Gold'
            elif 'Bronze' in model:
                efficiency = '80+ Bronze'
            else:
                efficiency = '80+ Gold'
            
            modular = 'Modular' in model or wattage >= 750
            
            PSU.objects.update_or_create(
                name=model,
                manufacturer=data['brand'],
                defaults={
                    'wattage': wattage,
                    'efficiency_rating': efficiency,
                    'modular': modular,
                    'price': data['price'],
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} PSUs'))
    
    def import_cases(self, lines):
        count = 0
        for line in lines:
            data = self.parse_line(line)
            if not data:
                continue
            
            model = data['model']
            
            # Determine size based on price/model
            if 'Mini' in model or 'SFF' in model:
                form_factor = 'Mini-ITX'
                max_gpu = 320
                fans = 4
            elif 'Micro' in model:
                form_factor = 'Micro-ATX'
                max_gpu = 340
                fans = 5
            else:
                form_factor = 'ATX'
                max_gpu = 400
                fans = 7
            
            rgb = 'RGB' in model or 'Flow' in model
            
            Case.objects.update_or_create(
                name=model,
                manufacturer=data['brand'],
                defaults={
                    'form_factor': form_factor,
                    'max_gpu_length': max_gpu,
                    'fan_slots': fans,
                    'rgb': rgb,
                    'price': data['price'],
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} Cases'))
    
    def import_coolers(self, lines):
        count = 0
        for line in lines:
            data = self.parse_line(line)
            if not data:
                continue
            
            model = data['model']
            series = data['series']
            
            # Determine cooling type
            if 'AIO' in series or 'mm' in model:
                cooling_type = 'aio'
                # Parse radiator size for TDP
                if '360' in model:
                    max_tdp = 350
                elif '280' in model:
                    max_tdp = 280
                elif '240' in model:
                    max_tdp = 250
                else:
                    max_tdp = 200
            else:
                cooling_type = 'air'
                if 'D15' in model or 'Dark Rock Pro' in model:
                    max_tdp = 250
                elif 'U12' in model or 'AK620' in model:
                    max_tdp = 200
                else:
                    max_tdp = 150
            
            Cooling.objects.update_or_create(
                name=model,
                manufacturer=data['brand'],
                defaults={
                    'cooling_type': cooling_type,
                    'socket_compatibility': 'AM4, AM5, LGA1700, LGA1851',
                    'max_tdp': max_tdp,
                    'noise_level': 30 if cooling_type == 'air' else 25,
                    'price': data['price'],
                }
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} Coolers'))
