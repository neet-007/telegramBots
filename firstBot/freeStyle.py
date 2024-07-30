import os
import re
from dotenv import load_dotenv
import telegram
from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
import telegram.ext
from telegram.ext._handlers.messagehandler import MessageHandler

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")


LEAGUE, TEAM, NAME, NUMBER, POSITION, SUMMERY = range(6)

async def handle_player(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None or not update.effective_chat:
        return
    context.user_data["chat_id"] = update.effective_chat.id
    keyboard = [
        [telegram.InlineKeyboardButton("PL", callback_data="pl"), telegram.InlineKeyboardButton("LALIGA", callback_data="laliga"),
         telegram.InlineKeyboardButton("BDL", callback_data="bdl")],
        [telegram.InlineKeyboardButton("SA", callback_data="sa"), telegram.InlineKeyboardButton("LA", callback_data="la"),
         telegram.InlineKeyboardButton("cancel", callback_data="cancel")]
    ]

    await update.message.reply_text("hello to player creation please choose one of theese league,\n or send cancel to cancel",
                                reply_markup=telegram.InlineKeyboardMarkup(keyboard))

    return LEAGUE

async def handle_league(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or context.user_data == None:
        return
    print("xxxxxxxxxxxxxxxxxx")
    await query.answer()
    await query.edit_message_text(f"you chose {query.data} league,\n now enter the team name")

    context.user_data["team"] = query.data

    return TEAM


async def handle_team(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None:
        return

    context.user_data["team"] = update.message.text

    await update.message.reply_text(f"you choce tha team {update.message.text},\n now choose your name")

    return NAME

async def handle_name(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None:
        return

    context.user_data["name"] = update.message.text

    await update.message.reply_text(f"you choce tha name {update.message.text},\n now choose your number")

    return NUMBER


async def handle_number(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None:
        return

    keyboard = [
        [InlineKeyboardButton("GK", callback_data="gk"), InlineKeyboardButton("DF", callback_data="df")],
        [InlineKeyboardButton("MF", callback_data="mf"), InlineKeyboardButton("ST", callback_data="st")]
    ]

    context.user_data["number"] = update.message.text

    await update.message.reply_text(f"you choce tha number {update.message.text},\n now choose your position",
                                    reply_markup=telegram.InlineKeyboardMarkup(keyboard))

    return POSITION

async def handle_poistion(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or context.user_data == None:
        return

    await query.answer()
    context.user_data["position"] = query.data

    await query.edit_message_text(f"you chose postion {query.data}\n now you will get a summery")

    await handle_summery(update, context)
    return telegram.ext.ConversationHandler.END

async def handle_summery(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if context.user_data == None or not update.effective_chat:
        return

    data = ""
    for key, val in context.user_data.items():
        data += f"{key}-{val}\n"
    context.user_data.clear()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"here is your summery {data}")

    return telegram.ext.ConversationHandler.END

async def handle_cancel(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.user_data or not update.message:
        return

    context.user_data.clear()
    await update.message.reply_text("bye comeback again")

    return telegram.ext.ConversationHandler.END


def league_str(data):
    print(data)
    if data in ["pl", "bdl", "sa", "la", "laliga"]:
        return True
    return False

def position_str(data):
    if data in ["gk", "df", "mf", "st"]:
        return True
    return False

def main():
    if not BOT_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    conv_handle = telegram.ext.ConversationHandler(
        entry_points=[telegram.ext.CommandHandler("player", handle_player)],
        states={
            LEAGUE:[telegram.ext.CallbackQueryHandler(handle_league, pattern=league_str)],
            TEAM:[telegram.ext.MessageHandler(telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND, handle_team)],
            NAME:[telegram.ext.MessageHandler(telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND, handle_name)],
            NUMBER:[telegram.ext.MessageHandler(telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND, handle_number)],
            POSITION:[telegram.ext.CallbackQueryHandler(handle_poistion, pattern=position_str)],
        },
        fallbacks=[MessageHandler(telegram.ext.filters.Regex("^cancel$"), handle_cancel)]
    )

    application.add_handler(conv_handle)
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
