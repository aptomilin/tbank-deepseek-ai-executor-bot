# Tinkoff Executor Bot with DeepSeek AI

Telegram бот для управления инвестициями с интеграцией DeepSeek AI для интеллектуального анализа портфеля и рынка.

## 🚀 Возможности

- 🤖 **AI анализ портфеля** - глубокая аналитика ваших инвестиций
- 📊 **Анализ рынка** - оценка рыночной ситуации через AI
- 🎯 **Торговые стратегии** - персональные рекомендации на основе AI
- ⚡ **Динамическое управление** - адаптация стратегий к рынку

## 🛠 Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd tinkoff-executor-bot

2. Установите зависимости:
pip install -r requirements.txt

3. Настройте окружение:
cp .env.example .env
# Отредактируйте .env файл, добавив ваши токены

4. Запустите бота:
python main.py

⚙️ Конфигурация
В файле .env укажите:
BOT_TOKEN=your_telegram_bot_token
TINKOFF_TOKEN=your_tinkoff_invest_token
DEEPSEEK_API_KEY=your_deepseek_api_key

📋 Команды бота

/ai - главное меню AI функционала
/ai_analysis - анализ инвестиционного портфеля
/market_analysis - анализ рыночной ситуации
/ai_strategy - управление AI стратегиями

🏗 Архитектура
tinkoff-executor-bot/
├── config/                 # Конфигурация
├── services/ai_strategy/   # AI сервисы
├── app/handlers/          # Обработчики бота
├── app/keyboards/         # Клавиатуры
└── main.py               # Точка входа

🔧 Технологии

Aiogram 3.x - Telegram Bot Framework
DeepSeek API - AI для финансового анализа
Tinkoff Invest API - работа с биржей
Aiohttp - асинхронные HTTP запросы


## 🚀 **ИНСТРУКЦИЯ ПО ЗАПУСКУ:**

1. **Создайте структуру папок:**
```bash
mkdir -p tinkoff-executor-bot/{config,services/ai_strategy,app/{handlers,keyboards}}

2. Скопируйте все файлы в соответствующие папки
3. Установите зависимости:
pip install -r requirements.txt

4. Настройте окружение:
cp .env.example .env
# Добавьте ваши токены в .env файл

5. Запустите бота:
python main.py

Бот готов к работе! 🎯

Теперь у вас есть полнофункциональный Telegram бот с интеграцией DeepSeek AI для интеллектуального управления инвестициями!