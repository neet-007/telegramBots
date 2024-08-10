import json
import os
import aiohttp 
import io
import telegram
from PIL import Image, ImageFilter, ImageDraw
from telegram import Update, constants, ext
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

async def handle_partial_filters_command(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text("send the photo as document")

async def handle_partial_filters(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.effective_attachment or not WEB_APP_HOST or context.user_data == None:
        return

    file = await update.message.effective_attachment.get_file()

    res = await send_photo_to_server(file, context)

    if res:
        await update.message.reply_text("press the button to open the app to select the parts to modify",
                                        reply_markup=telegram.ReplyKeyboardMarkup.from_button(telegram.KeyboardButton(text="open the app", 
                                                                                                                    web_app=telegram.WebAppInfo(url=WEB_APP_HOST))))
    else:
        await update.message.reply_text("couldnt upload photo")

async def send_photo_to_server(file: telegram.File, context: ext.ContextTypes.DEFAULT_TYPE):
    if not WEB_APP_HOST or not file or context.user_data == None:
        return False

    buffer = io.BytesIO()
    await file.download_to_memory(out=buffer)
    
    try:
        im = Image.open(buffer)
    except OSError:
        buffer.close()
        print("didnt open message")
        return False

    w, h = im.size
    format = im.format
    print(f"Original size: {w}x{h}")

    ui_width = 420
    w_ratio = -1
    h_ratio = -1
    new_h = -1
    if w >= ui_width:
        w_ratio = w / ui_width
        new_h = int(h * (ui_width / w))
        h_ratio = h / new_h
        w = ui_width
    else:
        im.close()
        buffer.close()
        return False

    buffer.seek(0)
    values = buffer.getvalue()

    outBuffer = io.BytesIO()
    im2 = im.resize((w, new_h))
    print(f"Resized size: {im2.size}")

    outBuffer.seek(0)
    im2 = im2.convert("RGB")
    im2.save(outBuffer, format="JPEG")
    print("saved")
    outBuffer.seek(0)
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field("file", outBuffer, filename="image.jpeg", content_type="image/jpeg")
            
            async with session.post(url=f'{WEB_APP_HOST}/media', data=data) as response:
                buffer.close()
                outBuffer.close()
                im.close()
                if response.status == 200:
                    context.user_data["w_ratio"] = w_ratio
                    context.user_data["h_ratio"] = h_ratio
                    context.user_data["image"] = values
                    context.user_data["format"] = format
                    return True
                print(response.text)
                return False
    except Exception as e:
        print("error", e)
        im.close()
        outBuffer.close()
        buffer.close()
        context.user_data.clear()
        return False

async def handle_web_app_data(update: Update, context: ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.web_app_data or not update.effective_chat or context.user_data == None:
        return

    data = json.loads(update.effective_message.web_app_data.data)
    if data == None:
        context.user_data.clear();
        return await context.bot.send_message(text="an error happend when you sent the data or you didnt specify any changes", chat_id=update.effective_chat.id)

    print("data:", data)
    w_ratio = context.user_data.get("w_ratio", None)
    h_ratio = context.user_data.get("h_ratio", None)
    buffer_data= context.user_data.get("image", None)
    format = context.user_data.get("format", "JPEG")

    if not w_ratio or not h_ratio or not buffer_data:
        context.user_data.clear()
        return await context.bot.send_message(text="an error happend please try again", chat_id=update.effective_chat.id)

    buffer = io.BytesIO()
    buffer.write(buffer_data)
    buffer.seek(0)
    try:
        im = Image.open(buffer)
    except OSError:
        context.user_data.clear()
        buffer.close()
        return await context.bot.send_message(text="an error happend please tty again", chat_id=update.effective_chat.id)

    filters = {
        "blur":ImageFilter.BLUR,
        "sharpen":ImageFilter.SHARPEN,
        "smooth":ImageFilter.SMOOTH,
        "smooth_more":ImageFilter.SMOOTH_MORE
    }

    crop_list = []
    for key in data:
        print("key", key)
        if key == "rect":
            for f in data[key]:
                mode = f["mode"]
                print(mode)
                box = (int(f["x1"] * w_ratio), int(f["y1"] * h_ratio), int(f["x2"] * w_ratio), int(f["y2"] * h_ratio))
                print(box)
                r = im.crop(box)
                if mode in filters:
                    if mode == "blur":
                        for _ in range(10):
                            r = r.filter(filters[mode])
                    else:
                        r.filter(filters[mode])
                    im.paste(r, box)
                else:
                    if mode == "baw":
                        r = r.convert("L")
                        im.paste(r, box)
                    elif mode == "rotate":
                        continue
                    elif mode == "crop":
                        im = r
                    else:
                        context.user_data.clear();
                        buffer.close()
                        return await context.bot.send_message(text="the filter is not supported", chat_id=update.effective_chat.id)
        elif key == "pen":
            continue
        elif key == "circle" or key == "ellipse":
            im.convert("RGBA")
            for f in data[key]:
                mask = Image.new("L", im.size, 0)
                mask = mask.filter(ImageFilter.GaussianBlur(2))
                draw = ImageDraw.Draw(mask)
                box = ()
                if key == "circle":
                    center = f["center"]
                    radius = f["radius"]
                    mode = f["mode"]
                    box = (
                        int((center["x"] - radius) * w_ratio),
                        int((center["y"] - radius) * h_ratio),
                        int((center["x"] + radius) * w_ratio),
                        int((center["y"] + radius) * h_ratio)
                    )
                else:
                    center = f["center"]
                    radiusX = f["radiusX"]
                    radiusY = f["radiusY"]
                    mode = f["mode"]
                    box = (
                        int((center["x"] - radiusX) * w_ratio),
                        int((center["y"] - radiusY) * h_ratio),
                        int((center["x"] + radiusX) * w_ratio),
                        int((center["y"] + radiusY) * h_ratio)
                    )

                draw.ellipse(box, fill=255, width=0)
                r = Image.new("RGBA", im.size, (0,0,0,0))
                r.paste(im, mask=mask)
                r = r.crop(box)

                if mode in filters:
                    if mode == "blur":
                        for _ in range(10):
                            r = r.filter(filters[mode])
                    else:
                        r.filter(filters[mode])
                    im.paste(r, box, mask=r)
                else:
                    if mode == "baw":
                        r = r.convert("L")
                        im.paste(r, box, mask=r)
                    elif mode == "rotate":
                        continue
                    elif mode == "crop":
                        im = r
                    else:
                        context.user_data.clear()
                        buffer.close()
                        return await context.bot.send_message(text="the filter is not supported", chat_id=update.effective_chat.id)

        else:
            for shape in data[key]:
                if shape == "rect":
                    for f in data[key][shape]:
                        box = (int(f["x1"] * w_ratio), int(f["y1"] * h_ratio), int(f["x2"] * w_ratio), int(f["y2"] * h_ratio))
                        print(box)
                        r = im.crop(box)
                        crop_list.append(r)
                elif shape == "pen":
                    continue
                else:
                    im.convert("RGBA")
                    for f in data[key][shape]:
                        mask = Image.new("L", im.size, 0)
                        mask = mask.filter(ImageFilter.GaussianBlur(2))
                        draw = ImageDraw.Draw(mask)
                        box = ()
                        if key == "circle":
                            center = f["center"]
                            radius = f["radius"]
                            box = (
                                int((center["x"] - radius) * w_ratio),
                                int((center["y"] - radius) * h_ratio),
                                int((center["x"] + radius) * w_ratio),
                                int((center["y"] + radius) * h_ratio)
                            )
                        else:
                            center = f["center"]
                            radiusX = f["radiusX"]
                            radiusY = f["radiusY"]
                            box = (
                                int((center["x"] - radiusX) * w_ratio),
                                int((center["y"] - radiusY) * h_ratio),
                                int((center["x"] + radiusX) * w_ratio),
                                int((center["y"] + radiusY) * h_ratio)
                            )

                        draw.ellipse(box, fill=255, width=0)
                        r = Image.new("RGBA", im.size, (0,0,0,0))
                        r.paste(im, mask=mask)
                        r = r.crop(box)
                        crop_list.append(r)
    buffer.seek(0)
    try:
        print("format:",format)
        if format == "JPEG":
            im = im.convert("RGB")
            im.save(buffer, format="JPEG")
        else:
            im.save(buffer, format=format)
    except Exception as e:
        context.user_data.clear();
        buffer.close()
        print(e)
        return await context.bot.send_message(text="an error happend pleaser try again", chat_id=update.effective_chat.id)

    buffer.seek(0)

    print(crop_list)
    if len(crop_list) > 0:
        out_list = []
        for r in crop_list:
            try:
                buffer_ = io.BytesIO()
                buffer_.seek(0)
                if format == "JPEG":
                    r.convert("RGB")
                    r.save(buffer_, format=format)
                else:
                    r.save(buffer_, format=format)
                out_list.append(buffer_)
                print(out_list)
            except Exception as e:
                buffer_.close()
                print(e)

        for b in out_list:
            b.seek(0)
            await context.bot.send_document(document=b, filename=f"image.{format.lower()}", chat_id=update.effective_chat.id)
            b.close()

    await context.bot.send_document(document=buffer, filename=f"image.{format.lower()}", chat_id=update.effective_chat.id)
    context.user_data.clear()
    buffer.close()

def main():
    if not BOT_TOKEN:
        return

    application = ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("partial", handle_partial_filters_command))
    application.add_handler(MessageHandler(ext.filters.ATTACHMENT, handle_partial_filters))
    application.add_handler(MessageHandler(ext.filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    application.run_polling()

if __name__ == "__main__":
    main()
