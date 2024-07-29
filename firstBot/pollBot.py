import os
from types import TracebackType
from typing import Text
from dotenv import load_dotenv
import telegram
import telegram.ext
from telegram.ext._handlers.commandhandler import CommandHandler
from telegram.ext.filters import POLL

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")


async def handle_start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text("hi, this is the poll and quiz bot, send /poll for poll and /quiz for quiz\n send /preview for poll preview")

async def handle_poll(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    options = ["bad", "good", "very good", "noice"]
    message = await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question="how are you",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True
    )

    payload = {}
    if message.poll:
        payload = {
            message.poll.id:{
            "message_id":message.message_id,
            "chat_id":update.effective_chat.id,
            "options":options,
            "answers":0
            }
        }

    context.bot_data.update(payload)

async def handle_poll_answer(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.poll_answer or not update.effective_user:
        return

    answer = update.poll_answer
    answerd_poll_data = context.bot_data[answer.poll_id]

    try:
        options = answerd_poll_data["options"]
    except KeyError:
        return

    selected_options = answer.option_ids
    text = ""
    for option_id in selected_options:
        if option_id != selected_options[-1]:
            text += options[option_id] + " and "
        else:
            text += options[option_id]

    await context.bot.send_message(
        chat_id=answerd_poll_data["chat_id"],
        text=f"{update.effective_user.mention_html()} feels {text}!",
        parse_mode=telegram.constants.ParseMode.HTML
    )

    answerd_poll_data["answers"] += 1

    if answerd_poll_data["answers"] == 1:
        await context.bot.stop_poll(answerd_poll_data["chat_id"], answerd_poll_data["message_id"])


async def handle_quiz(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_chat:
        return

    options = ["1", "2", "4", "20"]
    message = await update.effective_message.reply_poll(
        question="how many eggs to bake cake",
        options=options,
        correct_option_id=2,
        type=telegram.Poll.QUIZ
    )

    payload = {}
    if message.poll:
        payload = {
            message.poll.id:{
                "message_id":message.message_id,
                "chat_id":update.effective_chat.id
        
            }
        }

    context.bot_data.update(payload)

async def handle_quiz_asnwer(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.poll:
        return
    if update.poll.is_closed:
        return
    
    try:
        poll_data = context.bot_data[update.poll.id]
        await context.bot.stop_poll(chat_id=poll_data["chat_id"], message_id=poll_data["message_id"])
    except KeyError:
        return

async def handle_preview(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_message:
        return

    button = [[telegram.KeyboardButton(text="press me", request_poll=telegram.KeyboardButtonPollType())]]
    await update.effective_message.reply_text("press the button to make pull", reply_markup=telegram.ReplyKeyboardMarkup(button, one_time_keyboard=True))

async def handle_poll_request(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("yyyyyyyyyyyyyyyyy")
    if not update.effective_message:
        return
    acual_poll = update.effective_message.poll
    if not acual_poll:
        return
    print("xxxxxxxxxxxxxxxxxx")
    await update.effective_message.reply_poll(question=acual_poll.question, options=[o.text for o in acual_poll.options], is_closed=True, reply_markup=telegram.ReplyKeyboardRemove())

def main():
    if not BOT_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(telegram.ext.CommandHandler("start", handle_start))
    application.add_handler(telegram.ext.CommandHandler("poll", handle_poll))
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.POLL, handle_poll_request))
    application.add_handler(telegram.ext.PollAnswerHandler(handle_poll_answer))
    application.add_handler(telegram.ext.CommandHandler("quiz", handle_quiz))
    application.add_handler(telegram.ext.PollHandler(handle_quiz_asnwer))
    application.add_handler(CommandHandler("preview", handle_preview))

    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
