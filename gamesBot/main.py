from contextlib import contextmanager
from dotenv import load_dotenv
from os import getenv
import telegram
import telegram.ext
from wilty import Wilty
from guess_the_player import GuessThePlayer
from draft import Draft

load_dotenv()

BOT_API_TOKEN = getenv("BOT_API_TOKEN")

def remove_jobs(name:str, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job_queue:
        return

    jobs = context.job_queue.get_jobs_by_name(name)
    if not jobs:
        return

    for job in jobs:
        job.schedule_removal()

async def handle_start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context == None:
        return

    await update.message.reply_text("")

games = {
    "wilty":{},
    "guess_the_player":{},
    "draft":{}
}


def main():
    if not BOT_API_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_API_TOKEN).build()

    application.run_polling()

if __name__ == "__main__":
    main()
