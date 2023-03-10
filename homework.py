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
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Бот отправил сообщение в чат')
    except Exception as error:
        logger.error(f'Ошибка при отправке сооющения в чат: {error}')


def get_api_answer(timestamp):
    """Ответ сервера."""
    try:
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params={'from_date': timestamp})
        if response.status_code != HTTPStatus.OK:
            message = f'Код ответа {response.status_code}'
            logger.error(message)
            raise TypeError(message)
        return response.json()
    except Exception as error:
        raise error('Сервер недоступен.')


def check_response(response):
    """Проверяет ответ на соответствие документации."""
    if type(response) != dict:
        message = f'Тип данных не соответствует ожиданиям: {type(response)}'
        logger.error(message)
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'Ответ API не соответствует ожиданиям'
        logger.error(message)
        raise KeyError(message)
    homework_list = response['homeworks']
    if type(homework_list) != list:
        message = 'Ответ API не в виде списка'
        logger.error(message)
        raise TypeError(message)
    return homework_list


def parse_status(homework):
    """Извлекает статус работы."""
    try:
        homework_name = homework['homework_name']
    except KeyError as error:
        message = f'homework_name недоступен {error}'
        logger.error(message)
        raise ValueError(message)
    try:
        homework_status = homework['status']
        logger.debug(f'Найден статус {homework_status}')
    except KeyError as error:
        message = f'Домашняя работа не найдена: {error}'
        logger.error(message)
        raise ValueError(message)
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError:
        message = f'Неизвестный статус: {homework_status}'
        logger.error(message)
        raise ValueError(message)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = 'Отсутствует обязательная переменная окружения'
        logger.critical(message)
        sys.exit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_error = 'Сбой работы программы'
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework:
                send_message(bot, parse_status(homework[0]))
            timestamp = response.get('current_date', timestamp)
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
