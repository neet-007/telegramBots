import os
from dotenv import load_dotenv
import telegram
import telegram.ext
from random import randint

from telegram.ext._handlers.conversationhandler import ConversationHandler
load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")

PLAYERS_COUNT = 2

class QGame:
    def __init__(self, chat_id:int) -> None:
        self.chat_id = chat_id
        self.players = {}
        self.scores = {}
        self.curr_player: telegram.User | None = None
        self.curr_hints = ["","","",]
        self.curr_answer = ""

    def _join_game(self, player:telegram.User):
        if player.id in self.players:
            return False
        self.players[player.id] = player
        return True

    def _start_game(self):
        if len(self.players) < PLAYERS_COUNT:
            return False, {}
        keys = list(self.players.values())
        self.curr_player = keys[randint(0, len(keys) - 1)]
        self.scores = {key:0 for key in self.players.keys()}
        return True, self.curr_player

    def _start_round(self, curr_hints:list[str], curr_answer:str):
        self.curr_answer = curr_answer
        self.curr_hints = curr_hints

    def _end_round(self, is_won:bool, winner_id:int):
        if not is_won:
            self.scores[self.curr_player] += 1
        else:
            self.scores[winner_id] += 1

        self.curr_hints = ["","","",]
        self.curr_answer = ""

        keys = list(self.players.values())
        for i in range(len(keys)):
            if keys[i] == self.curr_player:
                keys.pop(i)
                break

        self.curr_player = keys[randint(0, len(keys) - 1)]
        return self.curr_player


    def _end_game(self):
        scores = self.scores
        self.scores = {}
        self.players = {}
        self.curr_hints = ["", "", ""]
        self.curr_answer = ""
        self.curr_player = None

        return scores

games:dict[int, QGame] = {}

JOIN_GAME, START_GAME, START_ROUND, SEND_ANSWER, PLAY, END_ROUND, END_GAME = range(7) 

async def handle_start(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return telegram.ext.ConversationHandler.END

    if update.effective_chat.id in games:
        await update.message.reply_text("a game has already started")
        return telegram.ext.ConversationHandler.END
    else:
        keyboard = [
            [telegram.InlineKeyboardButton("join", callback_data="join_game")]
        ]
        games[update.effective_chat.id] = QGame(chat_id=update.effective_chat.id)
        await update.message.reply_text("a new game has started click button to join", reply_markup=telegram.InlineKeyboardMarkup(keyboard))
        return JOIN_GAME

async def handle_join(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("joingin game")
    if not update.callback_query or not update.effective_chat:
        return telegram.ext.ConversationHandler.END

    query = update.callback_query
    await query.answer()

    game = games.get(update.effective_chat.id, None)
    if not game:
        await context.bot.send_message(text="game doest not exist please create game then try again", chat_id=update.effective_chat.id)
        return ConversationHandler.END

    res = game._join_game(query.from_user)
    if not res:
        await context.bot.send_message(text=f"user {query.from_user.username} has already joined the game", chat_id=update.effective_chat.id)
    else:
        await context.bot.send_message(text=f"user {query.from_user.username} has joined the game, when ready send /start_game", chat_id=update.effective_chat.id)

    if len(game.players) >= 2:
        print("XXXXXX")
        return START_GAME
    return JOIN_GAME

async def handle_game_start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message:
        return

    game = games.get(update.effective_chat.id, None)
    if not game:
        await update.message.reply_text("there is no game, create a game first")
        return
    
    res, curr_player = game._start_game()
    if not res:
        await context.bot.send_message(text="the number of players is less than two, more players must join", chat_id=update.effective_chat.id)
        return telegram.ext.ConversationHandler.END

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"player {curr_player} send the hints seperated by comma's",
                                   parse_mode=telegram.constants.ParseMode.HTML)

    return START_ROUND

async def handle_round_start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None or not update.message.text or not update.effective_chat or not update.message.from_user:
        return telegram.ext.ConversationHandler.END

    game = games.get(update.effective_chat.id, None)
    print(game.curr_player)
    if not game or not game.curr_player:
        await update.message.reply_text("there ios no game, create a game first")
        return telegram.ext.ConversationHandler.END

    if update.message.from_user.id != game.curr_player.id:
        return START_ROUND

    text = update.message.text.split(",")
    if len(text) != 3:
        await update.message.reply_text("please send only 3 hints seperated by comma's")
        return START_ROUND

    context.user_data["hints"] = update.message.text.split(",")
    await update.message.reply_text("send the answer now")

    return SEND_ANSWER


async def handle_send_answer(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None or not update.message.text or not update.effective_chat or not update.message.from_user:
        return telegram.ext.ConversationHandler.END

    game = games.get(update.effective_chat.id, None)
    if not game or not game.curr_player:
        await update.message.reply_text("there ios no game, create a game first")
        return telegram.ext.ConversationHandler.END

    if update.message.from_user.id != game.curr_player.id:
        return SEND_ANSWER

    game._start_round(context.user_data["hints"], update.message.text.lower().strip())
    context.user_data.clear()
    await update.message.reply_text("the game has start, if you want to answer send answer:<your answer>")

    return PLAY

async def handle_play(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("plaaaaaaaaaaaaaaaay")
    if not update.message or not update.message.text or not update.message.from_user or not update.effective_chat:
        return telegram.ext.ConversationHandler.END

    game = games.get(update.effective_chat.id, None)
    if not game:
        await update.message.reply_text("there is no game, please start a new game first")
        return telegram.ext.ConversationHandler.END

    if game.curr_player.id == update.message.from_user.id:
        return PLAY
    print("nottttttttttttttttt")
    answer = update.message.text.replace("answer:", "").strip().lower()
    print(answer, game.curr_answer)
    if answer != game.curr_answer:
        return PLAY
    print(f"found, {answer}")
    game._end_round(is_won=True, winner_id=update.message.from_user.id)
    await update.message.reply_text("your answer is correct")
    await context.bot.send_message(text="if you want to start a new round send new else send end", chat_id=update.effective_chat.id)

    return END_ROUND

async def handle_round_end(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_chat:
        return telegram.ext.ConversationHandler.END

    game = games.get(update.effective_chat.id, None)
    if not game:
        await update.message.reply_text("there is no game, please start a new game first")
        return telegram.ext.ConversationHandler.END

    if update.message.text.lower() == "end":
        await update.message.reply_text("the game has ended, type scores to get the scores")
        return END_GAME
  
    elif update.message.text.lower() != "new":
        await update.message.reply_text("reply with end or new")
        return END_ROUND

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"player {game.curr_player} send the hints seperated by comma's",
                                   parse_mode=telegram.constants.ParseMode.HTML)
    return START_ROUND

async def handle_end_game(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return telegram.ext.ConversationHandler.END

    game = games.get(update.effective_chat.id, None)
    if not game:
        await context.bot.send_message(text="there is no game, start a new game", chat_id=update.effective_chat.id)
        return telegram.ext.ConversationHandler.END

    scores = game.scores
    game._end_game()
    del games[update.effective_chat.id]   
    text = ""
    for key, val in scores.items():
        text += f"{key}:{val}\n"

    await context.bot.send_message(text=text, chat_id=update.effective_chat.id)
    return telegram.ext.ConversationHandler.END

async def handle_cancel(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return telegram.ext.ConversationHandler.END

    await context.bot.send_message(text="the game is canceld, bye", chat_id=update.effective_chat.id)
    return telegram.ext.ConversationHandler.END

def main():
    if not BOT_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    conv_hanlder = telegram.ext.ConversationHandler(
        entry_points=[telegram.ext.CommandHandler("start", handle_start)],
        states={
            JOIN_GAME:[telegram.ext.CallbackQueryHandler(handle_join, pattern="join_game")],
            START_GAME:[telegram.ext.CommandHandler("start_game", handle_game_start)],
            START_ROUND:[telegram.ext.MessageHandler(~telegram.ext.filters.COMMAND, handle_round_start)],
            SEND_ANSWER:[telegram.ext.MessageHandler(~telegram.ext.filters.COMMAND, handle_send_answer)],
            PLAY:[telegram.ext.MessageHandler(~telegram.ext.filters.COMMAND, handle_play)],
            END_ROUND:[telegram.ext.MessageHandler(telegram.ext.filters.Regex("^(end|new)$"), handle_round_end)],
            END_GAME:[telegram.ext.MessageHandler(telegram.ext.filters.Regex("^scores$"), handle_end_game)]
        },
        fallbacks=[telegram.ext.CommandHandler("cancel", handle_cancel)],
        per_user=False
    )

    application.add_handler(conv_hanlder)
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
