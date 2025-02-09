import asyncio
import os

from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from aiogram import Router
from aiogram.methods import SendPhoto
from aiogram.types import FSInputFile

from data import bot, create_histogram
import keyboards as kb
from data import add_response, update_quiz_index, quiz_data, statistic
from data import  get_quiz_index, get_question, get_result, new_quiz


router = Router()


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):

    await message.answer(f"Добро пожаловать в квиз! {message.from_user.username}", reply_markup=kb.main)


# Хэндлер на команду /quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    sent_message = await message.answer(f"Давайте начнем квиз!")
    await asyncio.sleep(2)
    await sent_message.delete()
    await new_quiz(message)


@router.message(F.text=='Общая статистика')
@router.message(Command("statistic"))
async def send_statistic(message: types.Message):
    stats = await statistic()
    if stats:
        file_path = create_histogram(stats)
        chat_id = message.chat.id

        await bot.send_photo(chat_id=chat_id, photo=FSInputFile(path=file_path))

    else:
        await message.answer("Нет данных для отображения.")


#обработка колбэк запросов
async def answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    username = callback.from_user.username
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)

    if callback.data == 'right_answer':
         is_correct = True
         sent_message = await callback.message.answer("Верно!")

    else:
       is_correct = False
       correct_option = quiz_data[current_question_index]['correct_option']
       sent_message = await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Удаляем статус ответа
    await asyncio.sleep(2)
    await sent_message.delete()
    # удаление текста предидущеего вопроса
    await callback.message.chat.delete_message(callback.message.message_id)
    # Обновление номера текущего вопроса в базе данных и сохранение ответа
    await add_response(user_id, current_question_index, is_correct)
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)

    else:
        result = await get_result(user_id, username)
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await callback.message.answer(f"{callback.from_user.username} ваш результат {result} % правильных ответов")


router.callback_query.register(answer, (F.data == "right_answer"))

router.callback_query.register(answer, (F.data == "wrong_answer"))



