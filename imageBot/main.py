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
        return await update.message.reply_text(f"sory format {to_format} is not supported the supported types are\n {SUPPORTED_FORMATS_STR} ")

    await update.message.reply_text("send the image as docuement")

async def handle_convert_type(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    print("here")
    if not update.message or not update.message.effective_attachment or context.user_data == None:
        return

    to_foramt = context.user_data.get("to_format", None)
    if to_foramt == None:
        return await update.message.reply_text("error happend please try again")

    if to_foramt == SUPPORTED_FORAMTS[1]:
        to_foramt = SUPPORTED_FORAMTS[0]

    file = await update.message.effective_attachment.get_file()
    buffer = io.BytesIO()
    await file.download_to_memory(buffer)

    buffer.seek(0)
    try:
        im = Image.open(buffer)
    except OSError:
        return await update.message.reply_text(f"sory format {to_foramt} is not supported the supported types are\n {SUPPORTED_FORMATS_STR} ")
    
    if im.format not in SUPPORTED_FORAMTS:
        return await update.message.reply_text(f"sory format {to_foramt} is not supported the supported types are\n {SUPPORTED_FORMATS_STR} ")

    if im.format == to_foramt:
        return await update.message.reply_text(f"the image is already {to_foramt}")

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


    elif to_foramt != SUPPORTED_FORAMTS[-1]:
        print("not tiff")
        if bands == ("C", "M", "Y", "K"):
            im = im.convert("RGBA")

    buffer.seek(0)
    im.save(fp=buffer, format=to_foramt)
    buffer.seek(0)
    await update.message.reply_document(buffer, filename=f"image.{to_foramt.lower()}")
    buffer.close()

SUPPORTED_FILTRES = ["blur", "sharpen", "smooth", "smooth more", "black and white", "rotate"]
SUPPORTED_FILTRES_STR = '\n'.join(SUPPORTED_FILTRES)

async def handle_filters_message(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None:
        return

    filter = update.message.text.replace("/filter", "").strip().lower()

    if SUPPORTED_FILTRES[-1] in filter:
        filter = filter.split(" ")
        if len(filter) != 2:
            return await update.message.reply_text("must provide an angle in degrees counter clockwise")

        context.user_data["filter"] = filter[0]
        context.user_data["angle"] = int(filter[1])

    elif filter not in SUPPORTED_FILTRES:
        return await update.message.reply_text(f"{filter} is not supported rigth now")

    else:
        context.user_data["filter"] = filter

    return await update.message.reply_text("send the image as document")

async def handle_filters(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment or context.user_data == None:
        return

    buffer = io.BytesIO()
    file = await update.message.effective_attachment.get_file()
    await file.download_to_memory(buffer)

    buffer.seek(0)
    try:
        im = Image.open(buffer)
    except OSError:
        return await update.message.reply_text("could'nt process the image")
    
    filter = context.user_data.get("filter", None)
    if filter == None:
        return await update.message.reply_text("error happend please try again")

    format = im.format
    print(format)
    if filter == SUPPORTED_FILTRES[0]:
        for _ in range(10):
            im = im.filter(ImageFilter.BLUR)
    elif filter == SUPPORTED_FILTRES[1]:
        im = im.filter(ImageFilter.SHARPEN)
    elif filter == SUPPORTED_FILTRES[2]:
        for _ in range(10):
            im = im.filter(ImageFilter.SMOOTH)
    elif filter == SUPPORTED_FILTRES[3]:
        for _ in range(10):
            im = im.filter(ImageFilter.SMOOTH_MORE)
    elif filter == SUPPORTED_FILTRES[4]:
        if "A" in im.getbands():
            im = im.convert("LA")
        else:
            im = im.convert("L")
    else:
        angle = context.user_data.get("angle", None)
        if angle == None:
            return await update.message.reply_text("error happend please try again and specify the angle in degrees counter clockwise")

        im = im.rotate(angle)

    buffer.seek(0)
    im.save(buffer, format=format)
    buffer.seek(0)

    await update.message.reply_document(buffer, filename=f"image.{format.lower()}")

    buffer.close()
    context.user_data.clear()

async def handle_partial_filters(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment:
        return

def main():
    if not BOT_TOKEN:
        return

    application = ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("filter", handle_filters_message))
    application.add_handler(MessageHandler(ext.filters.ATTACHMENT, handle_filters))

    application.run_polling()

if __name__ == "__main__":
    main()
