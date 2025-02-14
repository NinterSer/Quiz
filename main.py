import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

from modules.SQLrequests import SQLtools

CONFIG = {}
with open("config.cfg","r") as f:
    for s in f.readlines():
        s = s.split('=')
        CONFIG[s[0]] = s[1][:-1]
TOKEN = CONFIG['TOKEN']
questions = None
with open(CONFIG['questions'], encoding='utf-8') as f:
    questions = json.load(f)
logging.basicConfig(level=logging.INFO)

sql = SQLtools(CONFIG['DB_NAME'])

#-----------------------------QUIZ функции----------------------------------------
def generate_options_keyboard(answer_options):
    builder = ReplyKeyboardBuilder()

    for option in answer_options:
        builder.add(types.KeyboardButton(text=option))

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    name = message.from_user.first_name
    await sql.update_quiz_index(user_id, current_question_index, name, questions)
    return await sql.get_question(user_id)

async def set_answer(message):
    user_id = message.from_user.id
    option = message.text
    return await sql.set_option(user_id, option)
#---------------------------------------------------------------------------------

#------------------------Взаимодействие с телеграм-ботом---------------------------
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text=='Начать игру')
@dp.message(F.text=='начать заново')
@dp.message(Command('quiz'))
async def cmd_start(message: types.Message): 
    question = await new_quiz(message)
    await message.answer(question[1]['question'], reply_markup=generate_options_keyboard(question[1]['options']))

@dp.message(F.text=='посмотреть статистику')
@dp.message(Command('static'))
async def cmd_statistic(message: types.Message):
    r = await sql.get_statistic(message.from_user.id)
    await message.answer(r, reply_markup=generate_options_keyboard(["начать заново","ответы пользователя"]))

@dp.message(F.text=='ответы пользователя')
@dp.message(Command('answers'))
async def cmd_statistic(message: types.Message):
    r = await sql.get_positions(message.from_user.id)
    await message.answer(r, reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text)
async def cmd_answer(message: types.Message):
    r = await set_answer(message)  
    if r:
        question = await sql.get_question(message.from_user.id)
        await message.answer(question[1]['question'], reply_markup=generate_options_keyboard(question[1]['options']))
#------------------------------------------------------------------------------------

async def main():
    await sql.create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
