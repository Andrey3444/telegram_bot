import aiosqlite
import json
from aiogram import Bot
import matplotlib.pyplot as plt

import io
from keyboards import generate_options_keyboard
from config import API_TOKEN

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather


# Объект бота
bot = Bot(token=API_TOKEN)

with open('/home/andrey/Projects/VisualStudioCodeProjects/telegram_bot/main/quiz_data.json', 'r') as file:
    quiz_data = json.load(file)

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'


# создаем таблицу с ответами пользователя
async def responses_table():

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS responses 
            (
            user_id INT,
            question_index INTEGER NOT NULL,
            is_correct BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES quiz_state(user_id)) '''
        )

        await db.commit()


#добавляем ответ пользователя в таблицу ответов
async def add_response(user_id, question_index, is_correct):
    async with aiosqlite.connect(DB_NAME) as db:

        async with db.execute('''
                   SELECT COUNT(*) FROM responses
                   WHERE user_id = ? AND question_index = ?
               ''', (user_id, question_index)) as cursor:
            exists = await cursor.fetchone()

        if exists[0]:
            # Обновление строки, если она существует
            await db.execute('''
                       UPDATE responses
                       SET is_correct = ?
                       WHERE user_id = ? AND question_index = ?
                   ''', (is_correct, user_id, question_index))
        else:
            # Добавление новой строки, если она не существует
            await db.execute('''
                       INSERT INTO responses (user_id, question_index, is_correct)
                       VALUES (?, ?, ?)
                   ''', (user_id, question_index, is_correct))

        # Сохраняем изменения
        await db.commit()


#получаем статистику правельных ответов
async def get_result(user_id, username):

    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT is_correct FROM responses WHERE user_id = (?)', (user_id,)) as cursor:
            rows= await cursor.fetchall()
            result = [row[0] for row in rows]
            result = int(round(sum(result) / len(result), 2) * 100)
            # записываем результат в бд
            await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, username, statistic) VALUES (?, ?, ?)', (user_id, username, result))
            
            await db.commit()
            return result



# создание таблицы с мндексом квиза
async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER AUTO_INCREMENT PRIMARY KEY, username STRING, question_index INTEGER, statistic INTEGER)''')
        # Сохраняем изменения
        await db.commit()


# обноыление индекса вопроса
async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()


# получение индекса вопроса для текущего пользователя
async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:

            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


#из сообщения узнаем пользователя, сбрасываем счетчик вопросов в 0,
# и запрашиваем асинхронно следующий вопрос для отправки пользователю в чат.
async def new_quiz(message):

    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


#Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


def create_histogram(stats):
    user_ids = [username if username else 'Noname' for username, _ in stats]
    correct_answers = [ca if ca else 0 for _, ca in stats]

    # Создаем гистограмму
    plt.figure(figsize=(10, 5))
    plt.bar(user_ids, correct_answers, color='blue')

    plt.xlabel('Пользователи')
    plt.ylabel('Количество правильных ответов')
    plt.title('Гистограмма правильных ответов пользователей')

     # Сохраняем график в файл
    file_path = 'img/histogram.png'
    plt.savefig(file_path)
    plt.close()  # Закрываем фигуру
    return file_path


async def statistic():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT username, statistic FROM quiz_state') as cursor:
            results = await cursor.fetchall()

            return results                                                                           