from typing import Any
import aiogram
import aiogram.filters
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import aiohttp
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_TOKEN')

router = aiogram.Router()

class StateTest(StatesGroup):
    name = State()
    launguge = State()
    experience = State()

async def handle_start(message: aiogram.types.Message):
    await message.reply('hello this is start')

async def handle_help(message: aiogram.types.Message):
    await message.reply("""
list of commad:
/start: to start the bot
/help: to show help menu
/echo: try me
/func1:caluculation pass 2 numbers
/func2:surprise
""")

async def handle_echo(message: aiogram.types.Message):
    if message.text:
        await message.answer(message.text)


async def handle_func1(message: aiogram.types.Message):
    if not message.text:
        return

    params = message.text.split(' ')[1:]
    if (len(params)) != 2:
        await message.reply('must pass two numbers')
        return

    a = 0
    b = 0
    try:
        a = int(params[0])
    except ValueError:
        await message.reply('must pass integers')
        return

    try:
        b = int(params[1])
    except ValueError:
        await message.reply('must pass intgers')
        return

    await message.reply(str(a * b))

async def handle_func2(message: aiogram.types.Message, state: FSMContext):
    await state.set_state(StateTest.name)
    await message.reply('what is your name')

async def handle_name_state(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(StateTest.launguge)
    await message.reply(f'hello {message.text} what is your luanguae of choice')

async def handle_lauguage_state(message: aiogram.types.Message, state: FSMContext):
    await state.update_data(launguge=message.text)
    await state.set_state(StateTest.experience)
    await message.reply(f'i see you like {message.text} launguge, what is your level of experinec',
                        reply_markup=aiogram.types.ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                aiogram.types.KeyboardButton(text='beginner'),
                                aiogram.types.KeyboardButton(text='intermediate'),
                                aiogram.types.KeyboardButton(text='advanced')
                            ],


                        ],
                        resize_keyboard=True
                        ))

async def handle_expeience(message: aiogram.types.Message, state: FSMContext):
    data = await state.update_data(experience=message.text)
    await state.clear()

    await message.reply(f'i see you are a {message.text}', reply_markup=aiogram.types.ReplyKeyboardRemove(),)

    await show_summery(message=message, data=data)

async def show_summery(message: aiogram.types.Message, data: dict[str, Any]):
    name = data["name"]
    launguge = data["launguge"]
    experience = data["experience"]

    await message.reply(f'i see you are a {launguge} {experience} developer, we may need you help in the futer {name}')



router.message.register(handle_start, aiogram.filters.Command('start'))
router.message.register(handle_help, aiogram.filters.Command('help'))
router.message.register(handle_func1, aiogram.filters.Command('func1'))
router.message.register(handle_func2, aiogram.filters.Command('func2'))
router.message.register(handle_name_state, aiogram.filters.StateFilter(StateTest.name))
router.message.register(handle_lauguage_state, aiogram.filters.StateFilter(StateTest.launguge))
router.message.register(handle_expeience, aiogram.filters.StateFilter(StateTest.experience))
router.message.register(handle_echo)

async def main():
    if not BOT_TOKEN:
        raise ValueError('could not find bot token')
    bot = aiogram.Bot(BOT_TOKEN)

    dp = aiogram.Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as exp:
        print(exp)



