#!/usr/bin/env python
import os
import sys
import json
import subprocess
from datetime import datetime

print("🚀 Запуск тестов для MVP-7")
print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
print("=" * 60)

# Запускаем тесты
test_files = ['test_models.py', 'test_views.py', 'test_performance.py']

results = []
for test_file in test_files:
    print(f"\n📋 Запуск {test_file}...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', f'tests/{test_file}', '-v'],
        capture_output=True,
        text=True
    )
    
    success = result.returncode == 0
    results.append({
        'file': test_file,
        'success': success,
        'exit_code': result.returncode,
        'output': result.stdout[-300:] if result.stdout else ''
    })
    
    if success:
        print(f"✅ {test_file}: PASSED")
    else:
        print(f"❌ {test_file}: FAILED (код: {result.returncode})")

# Создаем отчет
report = {
    'project': 'Aicfgpc Backend',
    'mvp': 'MVP-7',
    'date': datetime.now().isoformat(),
    'results': results,
    'summary': {
        'total': len(results),
        'passed': sum(1 for r in results if r['success']),
        'failed': sum(1 for r in results if not r['success'])
    }
}

with open('test_report_mvp7.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n📊 Итог: {report['summary']['passed']}/{report['summary']['total']} тестов пройдено")
print(f"📄 Отчет сохранен в test_report_mvp7.json")