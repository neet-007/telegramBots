from dotenv import load_dotenv
from os import getenv
import telegram
import telegram.ext
from wilty import Wilty
from guess_the_player import GuessThePlayer
from draft import Draft

load_dotenv()

BOT_API_TOKEN = getenv("BOT_API_TOKEN")


async def handle_start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context == None:
        return

    await update.message.reply_text("")

games = {
    "wilty":{},
    "guess_the_player":{},
    "draft":{}
}

async def handle_wilty_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context == None or not update.effective_chat:
        return

    wilty_games = games["wilty"]
    if update.effective_chat.id in wilty_games:
        return await update.message.reply_text("a game has already started")

    wilty_games[update.effective_chat.id] = Wilty(chat_id=update.effective_chat.id)

    keyboard = [
        [telegram.InlineKeyboardButton(text="join", callback_data="join_wilty")]
    ]

    return await update.message.reply_text("a game has started use /join or press the button", reply_markup=telegram.InlineKeyboardMarkup(keyboard))

async def handle_wilty_join_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context == None or not update.effective_user or not update.effective_chat:
        return
    
    game:Wilty = games["wilty"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game please start one first /new_wilty")

    res = game.__join_game(player=update.effective_user)
    if not res:
        return await update.message.reply_text("player has already joined the game")

    await update.message.reply_text(f"{update.effective_user.mention_html()} has joined the game", parse_mode=telegram.constants.ParseMode.HTML)
    
async def handle_wilty_join_callback(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.effective_chat or not update.effective_user or context == None:
        return

    q = update.callback_query
    await q.answer()

    game:Wilty = games["wilty"].get(update.effective_chat.id, None)
    if game == None:
        return await context.bot.send_message(text="the is no game please start one first /new_wilty", chat_id=update.effective_chat.id)

    res = game.__join_game(player=update.effective_user)
    if not res:
        return await context.bot.send_message(text="player has already joined the game", chat_id=update.effective_chat.id)

    return await context.bot.send_message(text=f"{update.effective_user.mention_html()} has joined the gage", chat_id=update.effective_chat.id,
                                          parse_mode=telegram.constants.ParseMode.HTML)

async def handle_wilty_start_game(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context == None or not update.effective_user or not update.effective_chat:
        return
    
    game:Wilty = games["wilty"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game please start one first /new_wilty")

    res, curr_mode, curr_player = game.__start_game()
    if not res:
        return await update.message.reply_text("cant start game with less than 3 players")

    if curr_mode == None or curr_player == None:
        del games["wilty"][update.effective_chat.id]
        return await update.message.reply_text("and error happend please start a new game")

    await update.message.reply_text(f"the game has started the mod is {curr_mode.metion_html()} and you are quistioning {curr_player.metion_html()}")


def main():
    if not BOT_API_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_API_TOKEN).build()

    application.run_polling()

if __name__ == "__main__":
    main()
