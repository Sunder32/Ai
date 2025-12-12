import os
import sys
import django
import requests
import json
import re
import time
from datetime import datetime


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from computers.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooling
from peripherals.models import Monitor, Keyboard, Mouse, Headset


OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-project-model:latest" 
DEFAULT_MODEL = MODEL_NAME

INPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'AI', 'uploads', 'all_pc_parts_and_peripherals_rub_2025_big.txt')

def get_llm_response(prompt, model=DEFAULT_MODEL):
    
    print(f"DEBUG: Sending prompt to {model}...")
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        json_resp = response.json()
        
        return json_resp.get('response', '')
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None

def parse_json_response(response_text):
    
    try:
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            
            json_str = response_text
            
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON: {response_text[:200]}...")
        return None

def enrich_cpu(brand, series, model_name, price):
    prompt = f"""
    You are a PC hardware expert. Provide technical specifications for the CPU: {brand} {series} {model_name}.
    Return ONLY a JSON object with the following fields:
    - socket (string, e.g., "AM5", "LGA1700")
    - cores (integer)
    - threads (integer)
    - base_clock (float, in GHz)
    - boost_clock (float, in GHz)
    - tdp (integer, in Watts)
    - performance_score (integer, estimate PassMark or similar score, e.g., 20000)
    
    If you are unsure, provide a reasonable estimate based on the model name.
    """
    response = get_llm_response(prompt)
    if response:
        data = parse_json_response(response)
        if data:
            return CPU(
                name=f"{series} {model_name}",
                manufacturer=brand,
                socket=data.get('socket', 'Unknown'),
                cores=data.get('cores', 6),
                threads=data.get('threads', 12),
                base_clock=data.get('base_clock', 3.5),
                boost_clock=data.get('boost_clock', 4.5),
                tdp=data.get('tdp', 65),
                price=price,
                performance_score=data.get('performance_score', 10000),
                is_ai_generated=True,
                ai_generation_date=datetime.now(),
                ai_confidence=0.9
            )
    return None

def enrich_gpu(brand, series, model_name, price):
    prompt = f"""
    You are a PC hardware expert. Provide technical specifications for the GPU: {brand} {series} {model_name}.
    Return ONLY a JSON object with the following fields:
    - chipset (string, e.g., "GeForce RTX 4060")
    - memory (integer, in GB)
    - memory_type (string, e.g., "GDDR6")
    - core_clock (integer, in MHz)
    - boost_clock (integer, in MHz)
    - tdp (integer, in Watts)
    - recommended_psu (integer, in Watts)
    - performance_score (integer, estimate 3DMark Time Spy or similar, e.g., 10000)

    If you are unsure, provide a reasonable estimate based on the model name.
    """
    response = get_llm_response(prompt)
    if response:
        data = parse_json_response(response)
        if data:
            return GPU(
                name=f"{series} {model_name}",
                manufacturer=brand,
                chipset=data.get('chipset', model_name),
                memory=data.get('memory', 8),
                memory_type=data.get('memory_type', 'GDDR6'),
                core_clock=data.get('core_clock', 1500),
                boost_clock=data.get('boost_clock', 2000),
                tdp=data.get('tdp', 200),
                recommended_psu=data.get('recommended_psu', 600),
                price=price,
                performance_score=data.get('performance_score', 8000),
                is_ai_generated=True,
                ai_generation_date=datetime.now(),
                ai_confidence=0.9
            )
    return None

def enrich_motherboard(brand, series, model_name, price):
    prompt = f"""
    You are a PC hardware expert. Provide technical specifications for the Motherboard: {brand} {series} {model_name}.
    Return ONLY a JSON object with the following fields:
    - socket (string, e.g., "AM5", "LGA1700")
    - chipset (string, e.g., "B650", "Z790")
    - form_factor (string, e.g., "ATX", "Micro-ATX")
    - memory_slots (integer)
    - max_memory (integer, in GB)
    - memory_type (string, e.g., "DDR5", "DDR4")
    - pcie_slots (integer)
    - m2_slots (integer)

    If you are unsure, provide a reasonable estimate based on the model name.
    """
    response = get_llm_response(prompt)
    if response:
        data = parse_json_response(response)
        if data:
            return Motherboard(
                name=f"{series} {model_name}",
                manufacturer=brand,
                socket=data.get('socket', 'Unknown'),
                chipset=data.get('chipset', 'Unknown'),
                form_factor=data.get('form_factor', 'ATX'),
                memory_slots=data.get('memory_slots', 4),
                max_memory=data.get('max_memory', 128),
                memory_type=data.get('memory_type', 'DDR5'),
                pcie_slots=data.get('pcie_slots', 2),
                m2_slots=data.get('m2_slots', 2),
                price=price,
                is_ai_generated=True,
                ai_generation_date=datetime.now(),
                ai_confidence=0.9
            )
    return None

def process_file():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    current_category = None
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Found {len(lines)} lines to process.")
    
    count = 0
    for line in lines:
        if count > 5: break
        line = line.strip()
        if not line or line.startswith('#') and not line.startswith('##'):
            continue
            
        if line.startswith('##'):
            current_category = line.strip('# ').strip()
            print(f"\nProcessing category: {current_category}")
            continue
            
        if not current_category:
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:
            continue
            
        brand = parts[0]
        series = parts[1]
        model_name = parts[2]
        try:
            price = float(parts[3].replace(' ', '').replace('RUB', ''))
        except ValueError:
            print(f"Skipping invalid price: {parts[3]}")
            continue

        print(f"  Importing: {brand} {model_name}...", end='', flush=True)
        
        
        exists = False
        if current_category == "Видеокарты":
            if GPU.objects.filter(name__icontains=model_name).exists(): exists = True
        elif current_category == "Процессоры":
            if CPU.objects.filter(name__icontains=model_name).exists(): exists = True
        elif current_category == "Материнские платы":
            if Motherboard.objects.filter(name__icontains=model_name).exists(): exists = True
            
        if exists:
            print(" SKIPPED (Exists)")
            continue

        obj = None
        try:
            if current_category == "Видеокарты":
                obj = enrich_gpu(brand, series, model_name, price)
            elif current_category == "Процессоры":
                obj = enrich_cpu(brand, series, model_name, price)
            elif current_category == "Материнские платы":
                obj = enrich_motherboard(brand, series, model_name, price)
            
            
            if obj:
                obj.save()
                print(" DONE")
            else:
                print(" FAILED (LLM Error)")
                
        except Exception as e:
            print(f" ERROR: {e}")
            
       
if __name__ == "__main__":
    process_file()
