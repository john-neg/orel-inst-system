from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        'Спасибо, что вы включили меня, {}!'.format(message.from_user.first_name),
        reply_markup=types.ReplyKeyboardRemove()
    )
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Загрузить расписание"]
    keyboard.add(*buttons)
    await message.answer(
        'Чтобы выбрать нужное действие, '
        'нажмите на кнопку внизу или воспользуйтесь меню',
        reply_markup=keyboard
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


# Просто функция, которая доступна только администратору,
# чей ID указан в файле конфигурации.
# async def secret_command(message: types.Message):
#     await message.answer("Поздравляю! Эта команда доступна только администратору бота.")


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")