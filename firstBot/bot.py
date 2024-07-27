import aiogram
import aiogram.filters
import aiogram.utils
import aiohttp
import asyncio
from dotenv import load_dotenv
from random import randint
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_TOKEN')

router = aiogram.Router()

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
    await message.answer(message.text)

async def handle_func1(message: aiogram.types.Message):
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

async def handle_func2(message: aiogram.types.Message):
    choices = ['fuck you', 'dont text again bitch', 'i will break you you slut']
    return message.reply(choices[randint(0, len(choices) - 1)])

router.message.register(handle_start, aiogram.filters.Command('start'))
router.message.register(handle_help, aiogram.filters.Command('help'))
router.message.register(handle_func1, aiogram.filters.Command('func1'))
router.message.register(handle_func2, aiogram.filters.Command('func2'))
router.message.register(handle_echo)

async def main():
    bot = aiogram.Bot(BOT_TOKEN)

    dp = aiogram.Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as exp:
        print(exp)



