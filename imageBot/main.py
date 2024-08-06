import os
import io
import telegram
from PIL import Image, ImageFilter
from telegram import Update, ext
from dotenv import load_dotenv
from telegram.ext._handlers.commandhandler import CommandHandler
from telegram.ext._handlers.messagehandler import MessageHandler

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")
WEB_APP_HOST = os.getenv("WEB_APP_HOST")

async def handle_start(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text("")

async def handle_to_pdf(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment:
        return

SUPPORTED_FORAMTS = ["JPEG", "JPG", "PNG", "WEBP", "TIFF"]
SUPPORTED_FORMATS_STR = '\n'.join(SUPPORTED_FORAMTS)

async def handle_convert_message(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None:
        return

    to_format = update.message.text.replace("/convert", "").strip().upper()

    context.user_data["to_format"] = to_format

    if to_format not in SUPPORTED_FORAMTS:
        return await update.message.reply_text(f"sory this format is not supported the supported types are\n {SUPPORTED_FORMATS_STR} ")
    await update.message.reply_text("send image now")

async def handle_convert_type(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    print("here")
    if not update.message or not update.message.effective_attachment or context.user_data == None:
        return

    to_foramt = context.user_data.get("to_format")

    file = await update.message.effective_attachment.get_file()
    buffer = io.BytesIO()
    await file.download_to_memory(buffer)

    buffer.seek(0)
    try:
        im = Image.open(buffer)
    except OSError:
        return await update.message.reply_text(f"sory this format is not supported the supported types are\n {SUPPORTED_FORMATS_STR} ")
    
    if im.format not in SUPPORTED_FORAMTS:
        return await update.message.reply_text(f"sory this format is not supported the supported types are\n {SUPPORTED_FORMATS_STR} ")

    bands = im.getbands()
    print("bands", bands)
    if to_foramt == SUPPORTED_FORAMTS[0] or to_foramt == SUPPORTED_FORAMTS[1]:
        print("is jpeg")
        if bands == ("L", "A"):
            print("LA")
            im = im.convert("L")
        elif bands == ("R", "G", "B", "A"):
            print("RGBA")
            im = im.convert("RGB")

        if to_foramt == SUPPORTED_FORAMTS[1]:
            to_foramt = SUPPORTED_FORAMTS[0]

    elif to_foramt != SUPPORTED_FORAMTS[-1]:
        print("not tiff")
        if bands == ("C", "M", "Y", "K"):
            im = im.convert("RGBA")

    buffer.seek(0)
    im.save(fp=buffer, format=to_foramt)
    buffer.seek(0)
    await update.message.reply_document(buffer, filename=f"image.{to_foramt.lower()}")

async def handle_filters(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment:
        return

async def handle_partial_filters(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment:
        return

def main():
    if not BOT_TOKEN:
        return

    application = ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("convert", handle_convert_message))
    application.add_handler(MessageHandler(ext.filters.ATTACHMENT, handle_convert_type))

    application.run_polling()

if __name__ == "__main__":
    main()
