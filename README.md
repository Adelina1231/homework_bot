# Бот-ассистент

### Описание проекта

Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнаёт статус вашей домашней работы: взята ли ваша работа в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

Бот может:
- раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;
- при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;
- логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.

### Стек технологий
Python 3.9  
python-dotenv 0.19.0  
python-telegram-bot 13.7  

### Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Adelina1231/homework_bot.git
```
```
cd homework_bot
```

Создать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```

Установить зависимости из файла `requirements.txt`:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

Создаем .env файл с токенами:

```
PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
CHAT_ID=<CHAT_ID>
```

Запускаем бота:

```
python homework.py
```
### Автор

Аделина Тазиева https://github.com/Adelina1231
