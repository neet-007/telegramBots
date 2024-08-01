import os
import base64
from dotenv import load_dotenv
import telegram
import telegram.ext
from random import randint

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
        self.curr_state = 0

    def _join_game(self, player:telegram.User):
        if self.curr_state != 0:
            return False
        if player.id in self.players:
            return False
        self.players[player.id] = player
        return True

    def _start_game(self):
        if self.curr_state != 0:
            return False, {}
        if len(self.players) < PLAYERS_COUNT:
            return False, {}
        keys = list(self.players.values())
        self.curr_player = keys[randint(0, len(keys) - 1)]
        self.scores = {key:0 for key in self.players.keys()}
        self.curr_state = 1
        return True, self.curr_player

    def _start_round(self, curr_hints:list[str], curr_answer:str):
        if self.curr_state != 1 and self.curr_state != 4:
            return False
        if curr_hints == ["", "", ""] or curr_answer == "":
            return False
        self.curr_answer = curr_answer
        self.curr_hints = curr_hints
        self.curr_state = 2
        return True

    def _start_play(self):
        if self.curr_state != 2 and self.curr_state != 5:
            return False
        self.curr_state = 3
        return True

    def _end_round(self, is_won:bool, winner_id:int):
        if self.curr_state != 3:
            return False
        if not is_won:
            self.scores[self.curr_player] += 1
        else:
            self.scores[winner_id] += 1

        self.curr_hints = ["","","",]
        self.curr_answer = ""
        self.curr_state = 4

        keys = list(self.players.values())
        for i in range(len(keys)):
            if keys[i] == self.curr_player:
                keys.pop(i)
                break

        self.curr_player = keys[randint(0, len(keys) - 1)]
        return True, self.curr_player


    def _end_game(self):
        if self.curr_state == 0:
            return False, {}
        scores = self.scores
        self.scores = {}
        self.players = {}
        self.curr_hints = ["", "", ""]
        self.curr_answer = ""
        self.curr_player = None
        self.curr_state = 0
        return True, scores

games:dict[int, QGame] = {}


async def handle_start(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return 
    if update.effective_chat.id in games:
        await update.message.reply_text("a game has already started")
        return
    else:
        keyboard = [
            [telegram.InlineKeyboardButton("join", callback_data="join_game")]
        ]
        games[update.effective_chat.id] = QGame(chat_id=update.effective_chat.id)
        await update.message.reply_text("a new game has started click button to join", reply_markup=telegram.InlineKeyboardMarkup(keyboard))

async def handle_join(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("joingin game")
    if not update.callback_query or not update.effective_chat:
        return  

    query = update.callback_query
    await query.answer()

    game = games.get(update.effective_chat.id, None)
    if not game:
        await context.bot.send_message(text="game doest not exist please create game then try again", chat_id=update.effective_chat.id)
        return 

    res = game._join_game(query.from_user)
    if not res:
        await context.bot.send_message(text=f"user {query.from_user.username} has already joined the game or this is not the joining state", chat_id=update.effective_chat.id)
    else:
        await context.bot.send_message(text=f"user {query.from_user.username} has joined the game, when ready send /start_game", chat_id=update.effective_chat.id)

async def handle_game_start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message:
        return

    game = games.get(update.effective_chat.id, None)
    if not game:
        await update.message.reply_text("there is no game, create a game first")
        return
    
    res, curr_player = game._start_game()
    if not res:
        await context.bot.send_message(text="the number of players is less than two, more players must join or this is not start game stage", chat_id=update.effective_chat.id)
        return 

    keyboard = [
        [telegram.InlineKeyboardButton(text="press to send hits", callback_data="hints")]
    ]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"player {curr_player.mention_html()} press the button to send the hints",
                                   parse_mode=telegram.constants.ParseMode.HTML, reply_markup=telegram.InlineKeyboardMarkup(keyboard))


async def handle_round_start_callback(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or context.user_data == None:
        return

    query = update.callback_query
    if not query:
        return
    
    await query.answer()
    game = games[update.effective_chat.id]
    if not game:
        await context.bot.send_message(text="there is no game", chat_id=update.effective_chat.id)
        return

    if game.curr_state != 1 and game.curr_state != 4:
        return

    if game.curr_player.id != query.from_user.id:
        return

    context.user_data["game_id"] = update.effective_chat.id
    await query.delete_message()
    await query.from_user.send_message(text="send 3 hints seperated by commas ',' ")


async def handle_round_start(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None or not update.message.text or not update.effective_chat or not update.message.from_user or update.effective_chat.type != "private":
        return await handle_send_answer(update, context)

    if "hints" in context.user_data:
        return await handle_send_answer(update, context)

    game = games.get(int(context.user_data.get("game_id")), None)
    if not game or not game.curr_player:
        await update.message.reply_text("there ios no game, create a game first")
        return  await handle_send_answer(update, context)

    if game.curr_state != 1 and game.curr_state != 4:
        return await handle_send_answer(update, context)

    if update.message.from_user.id != game.curr_player.id:
        return await handle_send_answer(update, context)

    text = update.message.text.split(",")
    if len(text) != 3:
        await update.message.reply_text("please send only 3 hints seperated by comma's")
        return await handle_send_answer(update, context)

    context.user_data["hints"] = update.message.text.split(",")
    await update.message.reply_text("send the answer now")


async def handle_send_answer(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or context.user_data == None or not update.message.text or not update.effective_chat or not update.message.from_user or update.effective_chat.type != "private":
        return await handle_play(update, context)
    print("1111111111111111111")

    game = games.get(context.user_data["game_id"], None)
    if not game or not game.curr_player:
        await update.message.reply_text("there ios no game, create a game first")
        return 

    print("2222222222222222222")

    if (game.curr_state != 1 and game.curr_state != 4) or not "hints" in context.user_data:
        return await handle_play(update, context)

    print("3333333333333333333")

    if update.message.from_user.id != game.curr_player.id:
        return await handle_play(update, context)

    print("444444444444444444444444")

    a = game._start_round(context.user_data["hints"], update.message.text.lower().strip())
    if not a:
        print("itsssssssss falllllllllllse")
    b = game._start_play()
    if not b:
        print("bbbbbbbbbbbbbbbb falaaaaaaaaase")
    await context.bot.send_message(text=f"the game has start,\n the hints are {','.join(context.user_data['hints'])} if you want to answer send answer:<your answer>", chat_id=context.user_data["game_id"])

    context.user_data.clear()

async def handle_play(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("plaaaaaaaaaaaaaaaay")
    if not update.message or not update.message.text or not update.message.from_user or not update.effective_chat:
        return 

    game = games.get(update.effective_chat.id, None)
    if not game:
        await update.message.reply_text("there is no game, please start a new game first")
        return 

    print(f"222222222222222222222 {game.curr_state}")
    if game.curr_state != 3:
        return await handle_round_end(update, context)

    if game.curr_player.id == update.message.from_user.id:
        return await handle_round_end(update, context)
    
    print("nottttttttttttttttt")

    answer = update.message.text.replace("answer:", "").strip().lower()
    print(answer, game.curr_answer)
    if answer != game.curr_answer:
        return
    
    print(f"found, {answer}")

    game._end_round(is_won=True, winner_id=update.message.from_user.id)
    await update.message.reply_text("your answer is correct")
    await context.bot.send_message(text="if you want to start a new round send new else send end", chat_id=update.effective_chat.id)

    return 

async def handle_round_end(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_chat:
        return 

    game = games.get(update.effective_chat.id, None)
    if not game:
        await update.message.reply_text("there is no game, please start a new game first")
        return 

    if game.curr_state != 4:
        return

    answer = update.message.text.lower()
        
    if answer == "scores":
        return await handle_end_game(update, context)

    if answer == "end":
        await update.message.reply_text("the game has ended, type scores to get the scores")
        return
  
    if answer != "new":
        await update.message.reply_text("reply with end or new")
        return 

    keyboard = [
        [telegram.InlineKeyboardButton(text="send hints", callback_data="hints")]
    ]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"player {game.curr_player} press the button to send the hits",
                                   parse_mode=telegram.constants.ParseMode.HTML, reply_markup=telegram.InlineKeyboardMarkup(keyboard))
    return 

async def handle_end_game(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return 

    game = games.get(update.effective_chat.id, None)
    if not game:
        await context.bot.send_message(text="there is no game, start a new game", chat_id=update.effective_chat.id)
        return 

    if game.curr_state != 4:
        return

    text = ""
    for key, val in game.scores.items():
        user = game.players.get(key)
        text += f"{user.username if user.username else user.first_name}:{val}\n"
    
    game._end_game()
    del games[update.effective_chat.id]   

    await context.bot.send_message(text=text, chat_id=update.effective_chat.id)

async def handle_cancel(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return 

    game = games.get(update.effective_chat.id, None)
    if game == None:
        await context.bot.send_message(text="the game is canceld, bye", chat_id=update.effective_chat.id)
        return 

    if game.curr_state == 0:
        return

    text = ""
    for key, val in game.scores.items():
        user = game.players.get(key)
        text += f"{user.username if user.username else user.first_name}:{val}\n"
    
    game._end_game()
    del games[update.effective_chat.id]

    await context.bot.send_message(text=f"the game has ended, here are the socres\n {text}", chat_id=update.effective_chat.id)


def main():
    if not BOT_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_TOKEN).build()
    application.add_handler(telegram.ext.CommandHandler("start", handle_start))
    application.add_handler(telegram.ext.CallbackQueryHandler(handle_join, pattern="join"))
    application.add_handler(telegram.ext.CommandHandler("start_game", handle_game_start))
    application.add_handler(telegram.ext.CallbackQueryHandler(handle_round_start_callback, pattern="hints"))
    application.add_handler(telegram.ext.MessageHandler((telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND), handle_round_start))
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.Regex("^(end|new)$"), handle_round_end))
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.Regex("^scores$"), handle_end_game))
    application.add_handler(telegram.ext.CommandHandler("cancel", handle_cancel))
    application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)

if __name__ == "__main__":
    main()
