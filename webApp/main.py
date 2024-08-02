from logging import debug
import requests
import os
from dotenv import load_dotenv
import telegram
import telegram.ext
from PIL import Image
import json
import io

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")
WEBAPP_HOST = os.getenv("WEBAPP_HOST")

async def start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE) -> None:
    if not WEBAPP_HOST or not update.message:
        return
    print(WEBAPP_HOST)



    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=telegram.ReplyKeyboardMarkup.from_button(
            telegram.KeyboardButton(
                text="Open the color picker!",
                web_app=telegram.WebAppInfo(url=WEBAPP_HOST),
            )
        ),
    )

async def handle_web_data(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_message or not update.effective_message.web_app_data:
        return

    data = json.loads(update.effective_message.web_app_data.data)
    print(data)

    await update.message.reply_text(text=data)

async def handle_photo(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment or context.user_data == None or not WEBAPP_HOST:
        return

    file = await update.message.effective_attachment[-1].get_file()
    context.user_data["photo"] = file

    await update.message.reply_text("recived picture: proccessin ...")
    res = await send_photo_to_server(file)
    
    if res:
        await update.message.reply_text(
            "Please press the button to open the web app ",
            reply_markup=telegram.ReplyKeyboardMarkup.from_button(
                telegram.KeyboardButton(
                    text="Open the web app",
                    web_app=telegram.WebAppInfo(url=WEBAPP_HOST),
                )
            ),
        )
    else:
        await update.message.reply_text(
            text="could not upload photo"
        )

async def send_photo_to_server(file: telegram.File):
    buffer = io.BytesIO()
    await file.download_to_memory(out=buffer)
    
    try:
        im = Image.open(buffer)
    except OSError:
        return False

    w, h = im.size
    print(f"Original size: {w}x{h}")

    ui_width = 387
    if w > ui_width:
        h = int(h * (ui_width / w))
        w = ui_width

    im = im.resize((w, h))
    print(f"Resized size: {im.size}")

    resized_buffer = io.BytesIO()
    im.save(resized_buffer, format="JPEG")

    resized_buffer.seek(0)

    files = {"file": ("uploaded_img.jpg", resized_buffer, "image/jpeg")}
    
    res = requests.post(url=f"{WEBAPP_HOST}/media", files=files)

    if res.status_code == 200:
        return True
    else:
        return False

def main():
    if not BOT_TOKEN:
        print("xxxxxxxxxxxxxxx")
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(telegram.ext.CommandHandler("start", start))
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.PHOTO, handle_photo))

    application.run_polling()
    

if __name__ == "__main__":
    main()
