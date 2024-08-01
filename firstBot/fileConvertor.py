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

async def handle_read_in_memory(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment or context.user_data == None or not update.effective_chat:
        return
    
    images_list = []
    if "images_list" in context.user_data:
        images_list = context.user_data["images_list"]

    await context.bot.send_chat_action(action=telegram.constants.ChatAction.TYPING, chat_id=update.effective_chat.id)
    file = await update.message.effective_attachment[-1].get_file()

    buffer = io.BytesIO()

    await file.download_to_memory(out=buffer)

    buffer.seek(0)

    im = Image.open(buffer)

    images_list.append(im)

    context.user_data["images_list"] = images_list
    keyboard = [
        [telegram.InlineKeyboardButton(text="convert", callback_data="convert_img_pdf")]
    ]
    await update.message.reply_text(f"there are {len(images_list)} items now. send more or click the button to convert",
                                    reply_markup=telegram.InlineKeyboardMarkup(keyboard))

async def handle_convert_img_pdf(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or context.user_data == None:
        return

    query = update.callback_query
    if not query:
        return

    await query.answer()
    if not "images_list" in context.user_data:
        return

    images_list = context.user_data["images_list"]


    pdf_buffer = io.BytesIO()

    c = canvas.Canvas(pdf_buffer)
    for im in images_list:
        c.setPageSize(tuple([float(im.width), float(im.height)]))
        c.drawInlineImage(image=im, x=0, y=0)
        c.showPage()
        im.close()
        
    c.save()

    pdf_buffer.seek(0)
    
    keyboard = [
        [telegram.InlineKeyboardButton("change name", callback_data="change_pdf_name")]
    ]

    context.user_data.clear()
    await query.delete_message()
    await query.from_user.send_document(document=pdf_buffer, filename="test.pdf", reply_markup=telegram.InlineKeyboardMarkup(keyboard))
    pdf_buffer.seek(0)
    pdf_buffer.truncate(0)

async def handle_change_pdf_name_callback(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or context.user_data == None:
        return

    query = update.callback_query
    await query.answer()

    buffer = io.BytesIO()

    file = await query._get_message().effective_attachment.get_file() 
    buffer.seek(0)
    await file.download_to_memory(out=buffer)

    context.user_data["to_change_pdf"] = buffer
    
    await query.from_user.send_message("send the new file name")

    buffer.seek(0)
    buffer.truncate(0)

async def handle_change_pdf_name(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None:
        return

    c = canvas.Canvas(context.user_data["to_change_pdf"])
    c.save()

    await update.message.reply_document(filename=f"{update.message.text}.pdf", document=context.user_data["to_change_pdf"])
    context.user_data.clear()
    
    

def main():
    if not BOT_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.PHOTO, handle_read_in_memory))
    application.add_handler(telegram.ext.CallbackQueryHandler(handle_convert_img_pdf, pattern="convert_img_pdf"))
    application.add_handler(telegram.ext.CallbackQueryHandler(handle_change_pdf_name_callback, pattern="change_pdf_name"))
    application.add_handler(telegram.ext.MessageHandler((telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND), handle_change_pdf_name))
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
