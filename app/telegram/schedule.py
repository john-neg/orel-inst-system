import logging
import os
from datetime import datetime, timedelta

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.common.classes.EducationStaff import EducationStaff
from app.common.func import get_departments
from config import FlaskConfig


class GetSchedule(StatesGroup):
    waiting_for_date = State()
    waiting_for_department = State()
    waiting_for_staff = State()


async def schedule_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cur_date = datetime.now().replace(day=1)
    buttons = [
        cur_date.strftime("%m.%Y"),
        (cur_date + timedelta(days=32)).replace(day=1).strftime("%m.%Y"),
    ]
    keyboard.add(*buttons)
    await message.answer(
        "Выберите месяц за который вы хотите загрузить расписание:",
        reply_markup=keyboard,
    )
    await GetSchedule.waiting_for_date.set()


async def schedule_date_chosen(message: types.Message, state: FSMContext):
    cur_date = datetime.now().replace(day=1)
    available_dates = [
        cur_date.strftime("%m.%Y"),
        (cur_date + timedelta(days=32)).replace(day=1).strftime("%m.%Y"),
    ]
    if message.text.lower() not in available_dates:
        await message.answer("Пожалуйста, выберите месяц, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_month=int(message.text.lower().split(".")[0]))
    await state.update_data(chosen_year=int(message.text.lower().split(".")[1]))

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    departments = await get_departments()
    dept_list = [v.get("short") for v in departments.values()]
    for i in range(1, len(dept_list), 2):
        keyboard.add(dept_list[i - 1], dept_list[i])

    await GetSchedule.next()
    await message.answer("Теперь выберите вашу кафедру:", reply_markup=keyboard)


async def schedule_department_chosen(message: types.Message, state: FSMContext):
    departments = await get_departments()
    dept_dict = {}
    for key, val in departments.items():
        dept_dict[val.get("short").lower()] = key
    if message.text.lower() not in dept_dict:
        await message.answer(
            "Пожалуйста, выберите вашу кафедру, используя клавиатуру ниже."
        )
        return
    department_id = dept_dict.get(message.text.lower())
    await state.update_data(chosen_department=department_id)

    saved_data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # TODO добавить запросы и передать их в класс (попробовать хранить запрос в state чтобы не перезапрашивать потом)
    staff_list = EducationStaff(
        saved_data["chosen_month"], saved_data["chosen_year"]
    ).department_staff(department_id, reverse=True)
    staff_list = [*staff_list]

    for i in range(1, len(staff_list), 2):
        keyboard.add(staff_list[i - 1], staff_list[i])

    # для простых шагов можно не указывать название состояния, обходясь next()
    await GetSchedule.next()
    await message.answer("Теперь выберите преподавателя:", reply_markup=keyboard)


async def schedule_staff_chosen(message: types.Message, state: FSMContext):
    saved_data = await state.get_data()

    #TODO добавить запросы и передать их в класс
    staff_list = EducationStaff(
        saved_data["chosen_month"],
        saved_data["chosen_month"],
        saved_data["chosen_year"],
    ).department_staff(saved_data['chosen_department'], reverse=True)
    # staff_list = {y: x for x, y in staff_list.items()}

    if message.text not in staff_list:
        await message.answer(
            "Пожалуйста, выберите преподавателя, используя клавиатуру ниже."
        )
        return

    staff_id = staff_list.get(message.text)

    #TODO добавить запросы и передать их в класс
    filename = lessons_ical_exp(
        staff_id, message.text, saved_data['chosen_month'], saved_data['chosen_year']
    )

    if filename == 'no data':
        await message.answer(
            f'У {message.text} отсутствуют занятия за указанный период!',
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        file = open(FlaskConfig.EXPORT_FILE_DIR + filename, 'rb')
        await message.answer(
            '{}, Ваш файл готов!'.format(message.from_user.first_name),
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await message.answer_document(document=file)

        os.remove(FlaskConfig.EXPORT_FILE_DIR + filename)

    await message.answer(
        '{}, если Вам что-то еще необходимо, '
        'воспользуйтесь кнопкой "Меню"!'.format(message.from_user.first_name),
        reply_markup=types.ReplyKeyboardRemove(),
    )

    logging.debug(
        f"Данные выбраны успешно: "
        f"год: {saved_data['chosen_year']} "
        f"месяц: {saved_data['chosen_month']} "
        f"кафедра: {saved_data['chosen_department']} "
        f"преподаватель: {staff_id}",
    )

    await state.finish()


def register_handlers_schedule(dp: Dispatcher):
    dp.register_message_handler(schedule_start, commands="schedule", state="*")
    dp.register_message_handler(
        schedule_start,
        Text(equals="Загрузить расписание", ignore_case=True),
        state="*"
    )
    dp.register_message_handler(
        schedule_date_chosen, state=GetSchedule.waiting_for_date
    )
    dp.register_message_handler(
        schedule_department_chosen, state=GetSchedule.waiting_for_department
    )
    dp.register_message_handler(
        schedule_staff_chosen, state=GetSchedule.waiting_for_staff
    )
