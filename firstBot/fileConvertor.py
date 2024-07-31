import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
import io
from dotenv import load_dotenv
import telegram
import telegram.ext

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")


async def handle_file(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment:
        return

    file = await update.message.effective_attachment[-1].get_file()
    await file.download_to_drive()

async def handle_send_file(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_photo(open("file_0.jpg", "rb"))

async def handle_echo_file(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment:
        return

    file = await update.message.effective_attachment[-1].get_file()
    await update.message.reply_photo(file.file_id)

async def handle_read_in_memory(update: telegram.Update, _):
    if not update.message or not update.message.effective_attachment:
        return

    file = await update.message.effective_attachment[-1].get_file()

    buffer = io.BytesIO()

    await file.download_to_memory(out=buffer)

    buffer.seek(0)

    file_contents = buffer.read()

    im = Image.open(buffer)

    pdf_buffer = io.BytesIO()

    c = canvas.Canvas(pdf_buffer)
    c.drawInlineImage(image=im, x=0, y=0)
    c.showPage()
    c.save()

    pdf_buffer.seek(0)
    await update.message.reply_document(document=pdf_buffer, filename="test.pdf")
    print(im.size, im.format_description, im.mode)

def main():
    if not BOT_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.PHOTO, handle_read_in_memory))
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.TEXT, handle_send_file))
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
