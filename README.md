# AI-Configure - платформа для сборки ПК или рабочего места с использованием ИИ помощника 

> ### Цель проекта: Создание интеллектуального веб-приложения для автоматической подборки конфигурации компьютера и организации рабочего места на основе профиля пользователя, бюджета и предпочтений.

---

> ## Основная ветка для работы Dev

---

## Стек разработки

> ### Backend
![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0.1-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)

---

> ### AI/ML
![Ollama](https://img.shields.io/badge/Ollama-000000?logo=ollama&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-FF6600?logoColor=white)

---

> ### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwind-css&logoColor=white)

---

## 📚 Документация

Для детальной информации о текущем состоянии проекта, установке и использовании см. файл [CURRENT_PROJECT.md](./CURRENT_PROJECT.md)

## 🚀 Быстрый старт

### Backend
```powershell
cd project
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Настройте MySQL в файле .env (см. ниже)
python manage.py migrate
python manage.py populate_db
python manage.py runserver
```

### AI Server
```powershell
# Убедитесь, что Ollama запущен: ollama serve
cd AI/server
pip install -r ../requirements.txt
python main.py
```

### Frontend
```powershell
cd frontend
npm install
npm start
```

### Конфигурация .env
```env
# Создайте файл project/.env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL Database
DB_BACKEND=mysql
DB_NAME=pckonfai
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# AI Server
AI_SERVER_URL=http://localhost:5050
```

## 🔗 Ссылки

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001/api
- **AI Server:** http://localhost:5050
- **API Documentation:** http://localhost:8001/api/docs
- **Health Check:** http://localhost:8001/api/health/
- **Admin Panel:** http://localhost:8001/admin
- **Public Frontend:** https://impulsively-visionary-fieldfare.cloudpub.ru
- **Public Backend:** https://inanely-visionary-ibis.cloudpub.ru
- **Public AI Server:** https://smoothly-shrewd-trembler.cloudpub.ru

## 📋 Статус задач

См. [Tasks/tasks.md](./Tasks/tasks.md) для полного списка задач

## 📊 Отчеты

См. [Отчеты/project_report.md](./Отчеты/project_report.md) для детального отчета о прогрессе

## 👨‍💻 Разработка

**Автор:** Sunder32  
**Репозиторий:** [github.com/Sunder32/Ai](https://github.com/Sunder32/Ai)  
**Ветка:** dev

## 🚀 Технологии

### Frontend
- **React 18** + TypeScript
- **React Router** - навигация
- **Axios** - HTTP запросы
- **Tailwind CSS** - стилизация
- **GSAP** - анимации
- **Three.js** (@react-three/fiber, @react-three/drei, @react-three/rapier) - 3D графика
- **React Icons** - иконки

### Backend
- **Django 5.0.1** - основной фреймворк
- **Django REST Framework** - API
- **MySQL** - основная база данных (SQLite для разработки)
- **PyMySQL + cryptography** - MySQL драйвер
- **drf-spectacular** - документация API
- **django-filter** - фильтрация
- **django-cors-headers** - CORS

### AI
- **FastAPI** - AI-сервер на порту 5050
- **Ollama** - локальный LLM
- **DeepSeek** - модель для генерации рекомендаций
- **RAG Engine** - поиск по базе знаний

### Дизайн
- **Glassmorphism** - стеклянный эффект с backdrop-blur
- **Magic Bento** - интерактивные карточки с частицами и свечением
- **PillNav** - анимированная навигация с GSAP

## 📦 Структура проекта

```
D:\Aicfgpc\
├── frontend/                 # React приложение
│   ├── src/
│   │   ├── components/      # Компоненты (Header, Footer, MagicCard, BentoMenu)
│   │   ├── pages/           # Страницы (Home, Login, Components, Configurator)
│   │   ├── services/        # API сервисы
│   │   └── types/           # TypeScript типы
│   └── public/
│
├── project/                 # Django приложение
│   ├── accounts/           # Пользователи и аутентификация
│   ├── computers/          # Компоненты ПК (CPU, GPU, RAM, Storage, etc.)
│   ├── peripherals/        # Периферия (Monitor, Keyboard, Mouse, etc.)
│   ├── recommendations/    # Конфигурации и рекомендации
│   └── config/            # Настройки Django
│
└── README.md              # Этот файл
```

## 🛠 Установка и запуск

### 1. Backend (Django)

```powershell
# Перейти в папку проекта
cd D:\Aicfgpc\project

# Создать виртуальное окружение (если еще не создано)
python -m venv venv

# Активировать окружение
.\venv\Scripts\Activate.ps1

# Установить зависимости
pip install django djangorestframework django-cors-headers drf-spectacular django-filter python-decouple

# Выполнить миграции
python manage.py migrate

# Создать суперпользователя (опционально)
python manage.py createsuperuser

# Заполнить базу тестовыми данными
python manage.py populate_db

# Запустить сервер
python manage.py runserver
```

Backend будет доступен на: **http://localhost:8000**

### 2. Frontend (React)

```powershell
# Перейти в папку frontend
cd D:\Aicfgpc\frontend

# Установить зависимости
npm install

# Запустить development сервер
npm start
```

Frontend будет доступен на: **http://localhost:3000**

## 🔑 Тестовый аккаунт

После выполнения `python manage.py populate_db`:

- **Логин:** testuser
- **Пароль:** testpass123

## 📚 API Endpoints

### Аутентификация
- `POST /api/accounts/login/` - вход
- `POST /api/accounts/register/` - регистрация
- `POST /api/accounts/logout/` - выход

### Компоненты ПК
- `GET /api/computers/cpu/` - процессоры (8 шт)
- `GET /api/computers/gpu/` - видеокарты (8 шт)
- `GET /api/computers/ram/` - оперативная память (6 шт)
- `GET /api/computers/storage/` - накопители (8 шт)
- `GET /api/computers/motherboard/` - материнские платы
- `GET /api/computers/psu/` - блоки питания
- `GET /api/computers/case/` - корпуса
- `GET /api/computers/cooling/` - охлаждение

### Периферия
- `GET /api/peripherals/monitors/` - мониторы
- `GET /api/peripherals/keyboards/` - клавиатуры
- `GET /api/peripherals/mice/` - мыши
- `GET /api/peripherals/headsets/` - гарнитуры

### Конфигурации
- `GET /api/recommendations/configurations/` - список конфигураций (5 готовых)
- `POST /api/recommendations/configurations/generate/` - генерация конфигурации
- `GET /api/recommendations/configurations/{id}/` - детали конфигурации
- `POST /api/recommendations/configurations/{id}/check_compatibility/` - проверка совместимости

### Документация API
- **Swagger UI:** http://localhost:8000/api/docs/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

## 🎨 Особенности дизайна

### Glassmorphism
Все компоненты используютк стеклянный эффет:
- `backdrop-blur-xl` - размытие фона
- `bg-white/5` - полупрозрачный фон
- `border border-white/10` - тонкая граница

### Magic Bento Cards
Интерактивные карточки с эффектами:
- **Particles** - 6 частиц при наведении с радиальной анимацией
- **Spotlight** - свечение следует за курсором
- **Tilt** - 3D наклон карточки
- **Border glow** - светящаяся граница

### PillNav Header
Анимированная навигация:
- Круг расширяется снизу при наведении
- Текст поднимается и меняет цвет
- Логотип вращается на 360°
- Плавные GSAP анимации

## 📊 База данных

После выполнения `populate_db` содержит:

### Процессоры (8 шт)
- Intel Core i9-14900K (₽64,999) - 98 баллов
- Intel Core i7-14700K (₽49,999) - 92 балла
- Intel Core i5-14600K (₽35,999) - 85 баллов
- Intel Core i5-13400F (₽19,999) - 75 баллов
- AMD Ryzen 9 7950X (₽59,999) - 96 баллов
- AMD Ryzen 7 7800X3D (₽44,999) - 94 балла
- AMD Ryzen 5 7600X (₽29,999) - 82 балла
- AMD Ryzen 5 5600 (₽14,999) - 70 баллов

### Видеокарты (8 шт)
- NVIDIA RTX 4090 (₽179,999) - 100 баллов
- NVIDIA RTX 4080 (₽129,999) - 92 балла
- NVIDIA RTX 4070 Ti (₽94,999) - 85 баллов
- NVIDIA RTX 4060 Ti (₽49,999) - 75 баллов
- NVIDIA RTX 3060 (₽34,999) - 65 баллов
- AMD Radeon RX 7900 XTX (₽109,999) - 90 баллов
- AMD Radeon RX 7800 XT (₽64,999) - 80 баллов
- AMD Radeon RX 6700 XT (₽44,999) - 72 балла

### Оперативная память (6 шт)
- Corsair Vengeance RGB DDR5 6000MHz 32GB (₽14,999)
- G.Skill Trident Z5 RGB DDR5 6400MHz 32GB (₽16,999)
- Kingston FURY Beast DDR5 5200MHz 16GB (₽7,999)
- Corsair Vengeance LPX DDR4 3200MHz 32GB (₽9,999)
- G.Skill Ripjaws V DDR4 3600MHz 16GB (₽5,999)
- Kingston FURY Beast DDR4 3200MHz 16GB (₽4,999)

### Накопители (8 шт)
- Samsung 990 Pro 2TB NVMe (₽19,999) - 7450/6900 MB/s
- WD Black SN850X 2TB NVMe (₽17,999) - 7300/6600 MB/s
- Samsung 980 Pro 1TB NVMe (₽11,999) - 7000/5000 MB/s
- Kingston KC3000 1TB NVMe (₽9,999) - 7000/6000 MB/s
- Samsung 870 EVO 1TB SATA SSD (₽7,999) - 560/530 MB/s
- Crucial MX500 500GB SATA SSD (₽5,499) - 560/510 MB/s
- Seagate BarraCuda 2TB HDD (₽5,999) - 7200 RPM
- WD Blue 1TB HDD (₽3,999) - 7200 RPM

### Готовые конфигурации (5 шт)
- **Игровая станция 4K** (₽279,996) - RTX 4090 + i9-14900K
- **Профессиональная рабочая станция** (₽204,996) - RTX 4080 + Ryzen 9 7950X
- **Сбалансированный ПК для работы** (₽122,996) - RTX 4070 Ti + i7-14700K
- **Бюджетный игровой ПК** (₽61,996) - RTX 3060 + i5-13400F
- **Офисный ПК** (₽33,997) - базовая конфигурация

## 🔧 Настройки

### CORS
Backend настроен для работы с frontend:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

### Token Authentication
API использует Token Authentication:
- Токен сохраняется в `localStorage`
- Автоматически добавляется к каждому запросу через axios interceptor
- При 401 ошибке пользователь перенаправляется на `/login`

## 🐛 Решение проблем

### CORS ошибки
Убедитесь что:
1. Django сервер запущен на порту 8000
2. React запущен на порту 3000
3. В `settings.py` настроены `CORS_ALLOWED_ORIGINS` и `CORS_ALLOW_CREDENTIALS = True`

### 404 на API endpoints
Проверьте что URLs в `computers/urls.py` используют единственное число:
- `cpu/` вместо `cpus/`
- `gpu/` вместо `gpus/`
- `motherboard/` вместо `motherboards/`
- `case/` вместо `cases/`

### Не работает авторизация
1. Выполните миграции: `python manage.py migrate`
2. Проверьте что `rest_framework.authtoken` в `INSTALLED_APPS`
3. Очистите `localStorage` в браузере

### WebSocket ошибки в консоли
Это нормально - это React Hot Module Replacement пытается установить соединение. Не влияет на работу приложения.

## 📱 Страницы приложения

- **/** - Главная страница с 3D анимацией и BentoMenu
- **/login** - Вход и регистрация
- **/components** - Каталог компонентов (CPU, GPU, RAM, Storage)
- **/configurator** - Конфигуратор ПК
- **/my-configurations** - Мои сборки

## 🎯 Основные компоненты

### Frontend Components
- `Header` - PillNav навигация с GSAP анимациями
- `MagicCard` - универсальная обертка для Magic Bento эффектов
- `ComponentCard` - карточка компонента с ценой и характеристиками
- `BentoMenu` - меню с анимированными карточками
- `Galaxy` - 3D фон с Three.js
- `LanyardTooltip` - визитка автора

### Backend Apps
- `accounts` - пользователи, профили, аутентификация
- `computers` - компоненты ПК (CPU, GPU, RAM, Storage, Motherboard, PSU, Case, Cooling)
- `peripherals` - периферия (Monitor, Keyboard, Mouse, Headset, Webcam, Microphone, Desk, Chair)
- `recommendations` - конфигурации ПК и рекомендации

## 📝 Лицензия

MIT

## 👨‍💻 Автор

**Sunder32**

GitHub: [@Sunder32](https://github.com/Sunder32)

---

**Дата создания:** Декабрь 2025
