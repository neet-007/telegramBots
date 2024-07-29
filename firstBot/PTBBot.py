import asyncio
import os
import re
import telegram
import telegram.ext
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_TOKEN')

GENDER, PHOTO, LOCATION, BIO = range(4)

async def handle_start(update: telegram.Update, _):
    if not update.message:
        return

    keyboard = [["boy", "girl", "other"]]

    await update.message.reply_text(text="hi, what is your gender\n\n send /cancel any time to cancel",
                                    reply_markup=telegram.ReplyKeyboardMarkup(keyboard)
                                    )
    return GENDER

async def handle_gender(update: telegram.Update, _):
    if not update.message:
        return
    
    if update.message.text == "other":
        await update.message.reply_text(text="it is ok if you dont prefer not share, maybe send me a photo or sned /skip", 
                                        reply_markup=telegram.ReplyKeyboardRemove())
    else:
        await update.message.reply_text(text=f"i see you are a ${update.message.text}, maybe send a photo", reply_markup=telegram.ReplyKeyboardRemove())

    return PHOTO

async def handle_photo(update: telegram.Update, _):
    if not update.message:
        return

    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    await update.message.reply_text("nice photo, maybe you would like to share you locaion or send /skip")

    return LOCATION

async def handle_photo_skip(update: telegram.Update, _):
    if not update.message:
        return

    await update.message.reply_text("ok how about you share you location")

    return LOCATION

async def handle_loaction(update: telegram.Update, _):
    if not update.message:
        return

    await update.message.reply_text("wow nice city i may visit someday")

    return telegram.ext.ConversationHandler.END

async def handle_loaction_skip(update: telegram.Update, _):
    if not update.message:
        return

    await update.message.reply_text("you are paranoid")

    return telegram.ext.ConversationHandler.END

async def handle_cancel(update: telegram.Update, _):
    if not update.message:
        return

    await update.message.reply_text("bye", reply_markup=telegram.ReplyKeyboardRemove())

    return telegram.ext.ConversationHandler.END



def main():
    if not BOT_TOKEN:
        return

    applicaton = telegram.ext.Application.builder().token(BOT_TOKEN).build()

    conv_handler = telegram.ext.ConversationHandler(
                   entry_points=[telegram.ext.CommandHandler("start", handle_start)],
                   states={
                        GENDER:[telegram.ext.MessageHandler(telegram.ext.filters.Regex("^(boy|girl|other)$"), handle_gender)],
                        PHOTO:[telegram.ext.MessageHandler(telegram.ext.filters.PHOTO, handle_photo), telegram.ext.CommandHandler("skip", handle_photo_skip)],
                        LOCATION:[telegram.ext.MessageHandler(telegram.ext.filters.LOCATION, handle_loaction), 
                                  telegram.ext.CommandHandler("skip", handle_loaction_skip)],
                   },
                   fallbacks=[telegram.ext.CommandHandler("cancel", handle_cancel)]
                )

    applicaton.add_handler(conv_handler)
    applicaton.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
