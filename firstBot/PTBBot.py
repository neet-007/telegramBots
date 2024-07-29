import asyncio
import os
from typing import Dict
import telegram
import telegram.ext
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_TOKEN')


CHOOSING, TYPING_CHOICE, TYPING_REPLY = range(3)

keyboard = [
    ["age", "favorite color"],
    ["number of sibilings", "...something else"],
    ["done"]

]

reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def print_user_data(user_date:Dict[str, str]):
    return '\n'.join([f"{key}-{val}" for key, val in user_date.items()]).join(["\n", "\n"])

async def handle_start(update: telegram.Update, _):
    if not update.message:
        return

    await update.message.reply_text(text="hi, im your bot, please choose one of these to talk about,\n whene you are done send done",
                                    reply_markup=reply_markup
                                    )
    return CHOOSING

async def handle_choosing(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None:
        print(update.message)
        print(context.user_data)
        return

    context.user_data["choice"] = update.message.text
    await update.message.reply_text(f"nice you chose {update.message.text}, tell me more", reply_markup=telegram.ReplyKeyboardRemove())

    return TYPING_REPLY

async def handle_choosing_custom(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not context:
        return

    await update.message.reply_text("alright, then tell me the category", reply_markup=telegram.ReplyKeyboardRemove())

    return TYPING_CHOICE

async def handle_replying(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not context.user_data:
        return

    context.user_data[context.user_data["choice"]] = update.message.text
    del context.user_data["choice"]

    await update.message.reply_text(f"nice, just to let you know you told me this {print_user_data(context.user_data)}, tell me more", reply_markup=reply_markup)

    return CHOOSING

async def handle_done(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None:
        return

    if "choice" in context.user_data:
        del context.user_data["choice"]

    await update.message.reply_text(f"nice, this is what i learned today {print_user_data(context.user_data)}, comebakc later", reply_markup=telegram.ReplyKeyboardRemove())
    context.user_data.clear()

    return telegram.ext.ConversationHandler.END 

def main():
    if not BOT_TOKEN:
        return

    applicaton = telegram.ext.Application.builder().token(BOT_TOKEN).build()

    conv_handler = telegram.ext.ConversationHandler(
                   entry_points=[telegram.ext.CommandHandler("start", handle_start)],
                   states={
                        CHOOSING:[telegram.ext.MessageHandler(telegram.ext.filters.Regex("^(age|favorite color|number of sibilings)$"), handle_choosing),
                                  telegram.ext.MessageHandler(telegram.ext.filters.Regex("^...something else$"), handle_choosing_custom)],
                        TYPING_CHOICE:[telegram.ext.MessageHandler(telegram.ext.filters.TEXT & ~(telegram.ext.filters.COMMAND | telegram.ext.filters.Regex("^done$")), handle_choosing)],
                        TYPING_REPLY:[telegram.ext.MessageHandler(telegram.ext.filters.TEXT & ~(telegram.ext.filters.COMMAND | telegram.ext.filters.Regex("^done$")), handle_replying)]
                   },
                   fallbacks=[telegram.ext.MessageHandler(telegram.ext.filters.Regex("^done$"), handle_done)]
    )

    applicaton.add_handler(conv_handler)
    applicaton.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
