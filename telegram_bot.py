import logging
import os
import sys
from datetime import date
from logging.handlers import RotatingFileHandler

from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv

from app.common.classes.EducationStaff import EducationStaff
from app.common.func import get_departments
from config import FlaskConfig

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# RETRY_TIME: int = 600


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s, [%(levelname)s], %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        RotatingFileHandler(
            FlaskConfig.LOG_FILE_DIR + "telegram_bot.log",
            maxBytes=5000000,
            backupCount=5,
        ),
    ],
)


# def send_message(bot: Bot, message: str) -> None:
#     """Отправка сообщения в Telegram."""
#     try:
#         bot.send_message(TELEGRAM_CHAT_ID, message)
#         logging.info(f'Бот отправил сообщение: "{message}"')
#     except TelegramError as error:
#         logging.error(f"Ошибка при отправке сообщения в Telegram: {error}")


def check_tokens() -> bool:
    """Проверяем переменные окружения."""
    required_env = {
        "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
        # "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
    }
    missing_env = []
    for key in required_env:
        if not required_env[key]:
            missing_env.append(key)
    if not missing_env:
        return True
    else:
        logging.critical(
            "Отсутствуют необходимые переменные окружения: " f'{", ".join(missing_env)}'
        )
        return False


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['Расписание', 'Как пользоваться?']
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text='Спасибо, что вы включили меня, {}!'.format(name),
        reply_markup=button
    )


def help_info(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['Расписание']
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text='Пока это вся помощь, {}!'.format(name),
        reply_markup=button
    )


def departments(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name

    dept_lst = [v[1] for v in get_departments().values()]
    button = ReplyKeyboardMarkup([
        [dept_lst[i], dept_lst[i + 1]] for i in range(0, len(dept_lst), 2)
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text='{}, выберите вашу кафедру'.format(name),
        reply_markup=button
    )

def staff(update, context):
    department = 12
    staff = EducationStaff(date.today().month, date.today().year)
    list(staff.department_staff(department).items())


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit("Программа принудительно остановлена.")
    bot = Bot(token=TELEGRAM_TOKEN)
    updater = Updater(token=TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('help', help_info))

    updater.start_polling()
    updater.idle()



    # current_timestamp = int(time.time()) - RETRY_TIME
    # last_message = ""
    #
    # while True:
    #     try:
    #         response = get_api_answer(current_timestamp)
    #         homeworks = check_response(response)
    #         if homeworks:
    #             for homework in homeworks:
    #                 status = parse_status(homework)
    #                 send_message(bot, status)
    #         else:
    #             logging.debug("Нет новых статусов")
    #         current_timestamp = response.get("current_date") or int(time.time())
    #     except Exception as error:
    #         message = f"Сбой в работе программы: {error}"
    #         if message != last_message:
    #             send_message(bot, message)
    #             last_message = message
    #     finally:
    #         time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
