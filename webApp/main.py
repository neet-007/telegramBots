from logging import debug
import os
from dotenv import load_dotenv
import telegram
import telegram.ext
from PIL import Image

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")
WEBSITE_URL = os.getenv("WEBSITE_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=telegram.ReplyKeyboardMarkup.from_button(
            telegram.KeyboardButton(
                text="Open the color picker!",
                web_app=telegram.WebAppInfo(url="https://python-telegram-bot.org/static/webappbot"),
            )
        ),
    )

def main():
    if not BOT_TOKEN:
        print("xxxxxxxxxxxxxxx")
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()

    application.run_polling()
    

if __name__ == "__main__":
    main()
