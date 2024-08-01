from logging import debug
import os
from dotenv import load_dotenv
import telegram
import telegram.ext
from PIL import Image

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")


def main():
    if not BOT_TOKEN:
        print("xxxxxxxxxxxxxxx")
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()

    application.run_polling()
    

if __name__ == "__main__":
    main()
