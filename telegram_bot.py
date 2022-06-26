import asyncio
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand
from dotenv import load_dotenv

from app.telegram.common import register_handlers_common
from app.telegram.schedule import register_handlers_schedule
from config import FlaskConfig

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s, [%(levelname)s], %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        RotatingFileHandler(
            os.path.join(FlaskConfig.LOG_FILE_DIR, "telegram_bot.log"),
            maxBytes=5000000,
            backupCount=5,
        ),
    ],
)


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


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/schedule", description="Расписание"),
        BotCommand(command="/cancel", description="Отменить текущее действие"),
    ]
    await bot.set_my_commands(commands)


# @dp.errors_handler(exception=BotBlocked)
# async def error_bot_blocked(update: types.Update, exception: BotBlocked):
#     # Update: объект события от Telegram. Exception: объект исключения
#     # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
#     logging.info(f"Меня заблокировал пользователь!\n"
#                  f"Сообщение: {update}\nОшибка: {exception}")
#     # Такой хэндлер должен всегда возвращать True,
#     # если дальнейшая обработка не требуется.
#     return True


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


async def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit("Программа принудительно остановлена.")

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handlers_schedule(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
