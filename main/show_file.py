import json


with open('/home/andrey/Projects/VisualStudioCodeProjects/telegram_bot/main/quiz_data.json') as file:
    quiz_data = json.load(file)

print(quiz_data[0])