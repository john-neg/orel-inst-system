import logging
import os
import sys
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv
from json.decoder import JSONDecodeError

from exceptions import HomeworkApiException

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME: int = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, [%(levelname)s], %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        RotatingFileHandler('program.log', maxBytes=5000000, backupCount=5)
    ]
)


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправка сообщения в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Бот отправил сообщение: "{message}"')
    except telegram.TelegramError as error:
        logging.error(f'Ошибка при отправке сообщения в Telegram: {error}')


def get_api_answer(current_timestamp: str) -> dict:
    """Получаем информацию о статусе работы от Яндекса."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except ConnectionError as error:
        message = f'Ошибка при запросе к основному API: {error}'
        logging.error(message)
        raise ConnectionError(message)
    else:
        if response.status_code != HTTPStatus.OK:
            message = f'API вернул неверный код: {response.status_code}'
            logging.error(message)
            raise HomeworkApiException(message)
        try:
            return response.json()
        except JSONDecodeError as error:
            logging.error(f'Ошибка конвертации ответа API в JSON: {error}')


def check_response(response: dict) -> list:
    """Проверяем ответ Яндекса."""
    if not isinstance(response, dict):
        message = 'Ответ API содержит некорректный тип данных (dict expected)'
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'В ответе API отсутствует ключ "homeworks"'
        raise HomeworkApiException(message)
    if not isinstance(response.get('homeworks'), list):
        message = 'Ответ API содержит некорректный тип данных (list expected)'
        raise TypeError(message)
    return response.get('homeworks')


def parse_status(homework: dict) -> str:
    """Отправляем информацию о статусе домашней работы."""
    if not isinstance(homework, dict):
        message = 'Некорректный тип данных "homework"'
        raise TypeError(message)
    if homework.get('homework_name') is None:
        message = 'Ошибка - в ответе API отсутствует ключ "homework_name"'
        raise KeyError(message)
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        message = ('API вернул недокументированный статус работы: '
                   f'{homework_status}')
        raise HomeworkApiException(message)
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяем переменные окружения."""
    required_env = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    missing_env = []
    for key in required_env:
        if not required_env[key]:
            missing_env.append(key)
    if not missing_env:
        return True
    else:
        logging.critical('Отсутствуют необходимые переменные окружения: '
                         f'{", ".join(missing_env)}')
        return False


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit('Программа принудительно остановлена.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time()) - RETRY_TIME
    last_message = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    status = parse_status(homework)
                    send_message(bot, status)
            else:
                logging.debug('Нет новых статусов')
            current_timestamp = (response.get('current_date')
                                 or int(time.time()))
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != last_message:
                send_message(bot, message)
                last_message = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
