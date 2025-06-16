# DropDiceBot 🎲

**DropDiceBot** — это Telegram-бот, автоматизирующий участие в игре **"Drop Dice"**. Бот написан на Python и предназначен для взаимодействия с Telegram-ботами, поддерживающими игровой формат выпадения кубиков.

## ⚙️ Возможности

- Автоматическое выполнение бросков кубика
- Поддержка конфигурации через внешние файлы
- Фоновая обработка событий
- Интеграция с systemd для автозапуска
- Удобная архитектура с разделением на вспомогательные модули

## 🛠️ Стек технологий

- Python 3.10+
- Telegram Bot API
- systemd (для автозапуска и управления сервисом)

## 📁 Структура проекта

```

DropDiceBot/
├── main.py             # Главная точка входа
├── cfg/                # Конфигурационные файлы
├── helpers/            # Утилиты и вспомогательные функции
├── workers/            # Модули обработки игровых процессов
├── systemd/            # Файлы для запуска как systemd-сервиса
├── requirements.txt    # Список зависимостей
└── .gitignore          # Исключения Git

````

## 🚀 Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/vladrunk/DropDiceBot.git
cd DropDiceBot
````

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Настройте конфигурационные файлы в каталоге `cfg/`, включая токен Telegram и параметры игры.

4. Запустите бота:

```bash
python main.py
```

## 🔧 Автозапуск через systemd (опционально)

1. Скопируйте файл сервиса:

```bash
sudo cp systemd/bot_dice.service /etc/systemd/system/
```

2. Перезапустите демон и активируйте сервис:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable dropdicebot
sudo systemctl start dropdicebot
```

3. Проверка статуса:

```bash
sudo systemctl status dropdicebot
```

## ✅ Требования

* Python 3.10 или новее
* Telegram Bot Token
* Доступ к системе для запуска systemd (если нужен автозапуск)

## 📄 Лицензия

Добавьте файл `LICENSE`, чтобы определить условия использования (например, MIT или Apache 2.0).

## 📬 Обратная связь

Разработчик: [@vladrunk](https://github.com/vladrunk)

---

> ❗ Убедитесь, что ваш токен Telegram хранится в `.env` или конфигурационных файлах, исключённых из Git (`.gitignore`), чтобы не допустить утечки ключей доступа.
