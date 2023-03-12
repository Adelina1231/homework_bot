import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='main.log',
    encoding='UTF-8',
)
logger = logging.getLogger(__name__)

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    logger.debug('Бот начал отправку сообщения')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Бот отправил сообщение в чат')
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения в чат: {error}')


def get_api_answer(timestamp):
    """Ответ сервера."""
    logger.debug('Запрос к эндпоинту API-сервиса')
    try:
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params={'from_date': timestamp})
        if response.status_code != HTTPStatus.OK:
            raise TypeError(f'Код ответа {response.status_code}')
        return response.json()
    except Exception as error:
        raise error('Сервер недоступен.')


def check_response(response):
    """Проверяет ответ на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем')
    if 'homeworks' not in response:
        raise KeyError('Ответ API не соответствует ожиданиям')
    if 'current_date' not in response:
        raise KeyError('В ответе API нет даты')
    homework_list = response['homeworks']
    if not isinstance(homework_list, list):
        raise TypeError('Ответ API не в виде списка')
    return homework_list


def parse_status(homework):
    """Извлекает статус работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if 'homework_name' not in homework:
        raise KeyError('Ключа "homework_name" нет в словаре')
    if 'status' not in homework:
        raise KeyError('Ключа "status" нет в словаре')
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError('Ключ homework_status не найден')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_error = ''
    new_status = ''
    if not check_tokens():
        message = 'Отсутствует обязательная переменная окружения'
        logger.critical(message)
        sys.exit(message)
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if not homework:
                logger.debug('Статус не обновлен')
            else:
                homework_status = parse_status(homework[0])
                if homework_status == new_status:
                    logger.debug(homework_status)
                else:
                    new_status = homework_status
                    send_message(bot, homework_status)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            new_error = message
            if new_error != old_error:
                send_message(bot, message)
                old_error = new_error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
