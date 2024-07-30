import os
from dotenv import load_dotenv
import telegram
from telegram.constants import ParseMode
import telegram.ext
from pprint import pprint

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")


async def first_to_send(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user or not update.effective_chat:
        return

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=f"user {update.message.from_user.mention_html()} replyed first",
                                    parse_mode=ParseMode.HTML)

def main():
    if not BOT_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.TEXT, first_to_send))

    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
