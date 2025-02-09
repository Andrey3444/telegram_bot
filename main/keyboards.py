from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Общая статистика')],
    [KeyboardButton(text='Начать игру')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню'
)


#создает колбек-клавиатуру с вариантами ответов.
def generate_options_keyboard(answer_options, right_answer):

    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )
    builder.adjust(1)


    return builder.as_markup()

