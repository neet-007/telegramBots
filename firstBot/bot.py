import aiogram
import aiohttp
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_TOKEN')

bot = aiogram.Bot(BOT_TOKEN)

