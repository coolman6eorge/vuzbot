import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove
import time
from config import BOT_TOKEN
from llms import generate_response, models
import db

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

logging.basicConfig(level=logging.INFO)

router = Router()

class LLMSelection(StatesGroup):
    chosen_llm = State()

async def main_menu(telegram_uid, state: FSMContext):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖Выбрать LLM", callback_data='choose_llm')],
        [InlineKeyboardButton(text="👤Профиль", callback_data='profile')]
    ])
    await state.update_data(chosen_llm="None")
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [
            types.KeyboardButton(text="🤖Выбрать LLM"),
            types.KeyboardButton(text="👤Профиль")
        ],
    ])
    await bot.send_message(telegram_uid, "Вы в главном меню", reply_markup=keyboard)
    await bot.send_message(telegram_uid, "Выберите действие", reply_markup=inline_keyboard)

# CALLBACKS

@dp.callback_query(F.data == 'profile')
async def profile_info(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(chosen_llm='None')
    llm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵Пополнить баланс", callback_data='topup')],
        [InlineKeyboardButton(text="⬅️Назад в меню", callback_data='back_to_menu')],
    ])
    
    await bot.answer_callback_query(callback_query.id)
    user = await db.get_user_by_tid(callback_query.from_user.id)
    keyboard_remove = await bot.send_message(callback_query.from_user.id, f"{callback_query.from_user.first_name}, \n\nВаш баланс: {user['balance']}", reply_markup=ReplyKeyboardRemove())
    await keyboard_remove.delete()
    await bot.send_message(callback_query.from_user.id, f"{callback_query.from_user.first_name}, \n\nВаш баланс: {user['balance']}", reply_markup=llm_keyboard)

@dp.callback_query(F.data == 'topup')
async def balance_topup(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(chosen_llm='balance_topup')
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Введите сумму")

@dp.callback_query(F.data == 'choose_llm')
async def llm_choose_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(chosen_llm='None')
    llm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Gemma 2 9B", callback_data='llm_gemma')],
        [InlineKeyboardButton(text="Llama 3.1 405B", callback_data='llm_llama')],
        [InlineKeyboardButton(text="Mixtral 8x7B", callback_data='llm_mixtral')],
        [InlineKeyboardButton(text="⬅️Назад в меню", callback_data='back_to_menu')],
    ])
    
    await bot.answer_callback_query(callback_query.id)
    keyboard_remove = await bot.send_message(callback_query.from_user.id, "Выберите LLM:", reply_markup=ReplyKeyboardRemove())
    await keyboard_remove.delete()
    await bot.send_message(callback_query.from_user.id, "Выберите LLM:", reply_markup=llm_keyboard)

@dp.callback_query(F.data.startswith('llm_'))
async def handle_llm_selection(callback_query: CallbackQuery, state: FSMContext):
    chosen_llm = callback_query.data
    model_id = "None"

    for i in range(len(models)):
        if chosen_llm == models[i][0]:
            model_id = i

    await state.update_data(chosen_llm=model_id)

    await bot.answer_callback_query(callback_query.id)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text=f"ℹ️Вы общаетесь с {models[model_id][1]}ℹ️"), types.KeyboardButton(text=f"ℹ️Цена модели: {models[model_id][3]}ℹ️"),],
        [types.KeyboardButton(text="⬅️Назад в меню"), types.KeyboardButton(text="🤖Выбрать LLM")],
    ])
    await bot.send_message(callback_query.from_user.id, f"Вы общаетесь с {models[model_id][1]}", reply_markup=keyboard)

@dp.callback_query(F.data == 'back_to_menu')
async def back_to_main_menu(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await main_menu(callback_query.from_user.id, state)

# MESSAGES

@dp.message(F.text.startswith('ℹ️Вы общаетесь с '))
async def pass_on_press(message: types.Message):
    pass

@dp.message(F.text.startswith('ℹ️Цена модели: '))
async def pass_on_press(message: types.Message):
    pass

@dp.message(F.text == '👤Профиль')
async def llm_choose_handler(message: types.Message, state: FSMContext):
    await state.update_data(chosen_llm='None')
    llm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵Пополнить баланс", callback_data='topup')],
        [InlineKeyboardButton(text="⬅️Назад в меню", callback_data='back_to_menu')],
    ])
    
    user = await db.get_user_by_tid(message.from_user.id)
    keyboard_remove = await bot.send_message(message.from_user.id, f"{message.from_user.first_name}, \n\nВаш баланс: {user['balance']}", reply_markup=ReplyKeyboardRemove())
    await keyboard_remove.delete()
    await bot.send_message(message.from_user.id, f"{message.from_user.first_name}, \n\nВаш баланс: {user['balance']}", reply_markup=llm_keyboard)

@dp.message(F.text == '🤖Выбрать LLM')
async def llm_choose_handler(message: types.Message, state: FSMContext):
    await state.update_data(chosen_llm='None')
    llm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Gemma 2 9B", callback_data='llm_gemma')],
        [InlineKeyboardButton(text="Llama 3.1 405B", callback_data='llm_llama')],
        [InlineKeyboardButton(text="Mixtral 8x7B", callback_data='llm_mixtral')],
        [InlineKeyboardButton(text="⬅️Назад в меню", callback_data='back_to_menu')],
    ])
    
    keyboard_remove = await bot.send_message(message.from_user.id, "Выберите LLM:", reply_markup=ReplyKeyboardRemove())
    await keyboard_remove.delete()
    await bot.send_message(message.from_user.id, "Выберите LLM:", reply_markup=llm_keyboard)

@dp.message(F.text == '⬅️Назад в меню')
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await main_menu(message.from_user.id, state)

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    user = await db.get_user_by_tid(message.from_user.id)
    if not(user):
        await bot.send_message(message.from_user.id, f"Привет {message.from_user.first_name}!")
        await db.create_user(message.from_user.id, message.from_user.first_name)
    await main_menu(message.from_user.id, state)

@dp.message(F.text)
async def handle_user_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    chosen_llm = user_data.get('chosen_llm', "None")
    if chosen_llm == "None":
        await bot.send_message(message.from_user.id, f"Вы не выбрали LLM")
    elif chosen_llm == "balance_topup":
        try:
            amount = float(message.text)
            if amount < 0.01:
                raise Exception()
            await db.update_user_balance(message.from_user.id, float(message.text))
            await bot.send_message(message.from_user.id, f"Вы успешно пополнили баланс!")
            await main_menu(message.from_user.id, state)
        except:
            await bot.send_message(message.from_user.id, f"Введите число в формате 0.00")
    else:
        user = await db.get_user_by_tid(message.from_user.id)
        if float(user['balance']) - models[chosen_llm][3] < 0:
            await bot.send_message(message.from_user.id, f"Недостаточно средств")
        else:
            await db.update_user_balance(message.from_user.id, models[chosen_llm][3] * -1)
            llm_msg = await bot.send_message(message.from_user.id, f"{models[chosen_llm][1]} думает")
            msg = ''
            for chunk in generate_response(models[chosen_llm][2], message.text):
                msg += chunk
                await llm_msg.edit_text(text=msg)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
