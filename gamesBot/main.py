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

    keyboard = [
        [telegram.InlineKeyboardButton(text="send statments", callback_data="statements_wilty")]
    ]
    await update.message.reply_text(f"""the game has started the mod is {curr_mode.metion_html()} and you are quistioning {curr_player.metion_html()}\n 
    all players must click the button to send the statments to the bot in a private chat\n
    there is a 2 minutes limit
    """, reply_markup=telegram.InlineKeyboardMarkup(keyboard))

async def handle_wilty_statemnts_callback(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.effective_chat or not update.effective_user or context.user_data == None:
        return

    q = update.callback_query
    await q.answer()

    game:Wilty = games["wilty"].get(update.effective_chat.id, None)
    if game == None:
        return 

    if update.effective_user.id in game.statements:
        return

    context.user_data["wilty_chat_id"] = update.effective_chat.id
    await update.effective_user.send_message(text="send me the statements in the order of separated by commas ','")

async def handle_wilty_statements_add(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_chat or not update.effective_user or context.user_data == None:
        return

    chat_id = context.user_data.get("wilty_chat_id", None)
    if chat_id == None:
        context.user_data.clear()
        return

    game:Wilty = games["wilty"].get(chat_id, None)
    if game == None:
        context.user_data.clear()
        return 

    if update.effective_user.id in game.statements:
        context.user_data.clear()
        return
        
    text = update.message.text.split(",")
    if len(text) != 4:
        return await update.message.reply_text("you must send four statemets in the order of separated by commas ','")

    res = game.__add_player_statements(update.effective_user.id, text)
    if not res:
        return await update.message.reply_text("you must send four statemets in the order of separated by commas ','")

    if len(game.statements) == game.num_players:
        context.user_data.clear()
        res_ = game.__set_players_statements()
        if not res_:
            return
        await handle_wilty_start_round(context, chat_id)

    await update.message.reply_text("the statemnst have been recived wait until the rest of the players respond")

async def handle_wilty_start_round(context:telegram.ext.ContextTypes.DEFAULT_TYPE, chat_id:int):
    game:Wilty = games["wilty"].get(chat_id, None)
    if game == None:
        return

    started, round_type, curr_mod, curr_player = game.__start_round()
    if not started:
        return await context.bot.send_message(text="could not start the round", chat_id=chat_id)
    if not curr_mod or not curr_player:
        return

    keyboard = [
        [telegram.InlineKeyboardButton(text="send mod statement")]
    ]
    await context.bot.send_message(text=f"""round with type {round_type} started the mod {curr_mod.mention_html()} and questioning player
    {curr_player.metion_html()} the mod {curr_mod.mention_html()} press the button to send your statemtent""",
                                   parse_mode=telegram.constants.ParseMode.HTML, chat_id=chat_id, reply_markup=telegram.InlineKeyboardMarkup(keyboard))

async def handle_wilty_mod_statement_callback(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.effective_user or context.user_data == None:
        return

    q = update.callback_query
    await q.answer()

    if not q.message or not q.message.chat:
        return

    game:Wilty = games["wilty"].get(q.message.chat.id, None)
    if game == None:
        return 

    if update.effective_user.id != game.curr_mod_id:
        return

    context.user_data["wilty_chat_id"] = q.message.chat.id
    await update.effective_user.send_message("send me the statement")
    
async def handle_wilty_mod_statement_message(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or context.user_data == None:
        return

    chat_id = context.user_data.get("wility_chat_id", None)
    if not chat_id:
        return

    game:Wilty = games["wilty"].get(chat_id, None)
    if not game:
        return

    if update.effective_user.id != game.curr_mod_id:
        return

    text = update.message.text
    game.__set_mod_state(text)

    accussed = game.players.get(game.players_ids[game.curr_player_idx], None)
    if not accussed:
        return 

    await context.bot.send_message(text=f"the statement is {game.curr_statement.capitalize()} the accussed is {accussed}",
                                   chat_id=chat_id)

async def handle_wilty_round_vote_message(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        return

    game:Wilty = games["wilty"].get(update.effective_chat.id, None)
    if game == None:
        return

    options = ["true", "false"]
    message = await context.bot.send_poll(chat_id=update.effective_chat.id, question="is he lying",
                                options=options, is_anonymous=False, allows_multiple_answers=False)

    poll_data = {
        "chat_id":update.effective_chat.id,
        "question":"is he lying",
        "options":options,
        "message_id":message.message_id,
        "answers":[]
    }

    context.bot_data[message.poll.id] = poll_data

async def handle_wilty_round_vote(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.poll_answer or not update.poll or not update.poll.options or not update.effective_chat or not update.effective_user:
        return


    game:Wilty = games["wilty"].get(update.effective_chat.id, None)
    if game == None:
        return

    answer = update.poll_answer
    if not answer.user:
        return

    if answer.user.id == game.curr_mod_id or answer.user.id == game.players[game.players_ids[game.curr_player_idx]].id:
        return

    poll_data = context.bot_data.get(answer.poll_id, None)
    if poll_data == None:
        return

    try:
        answers = poll_data["answers"]
    except KeyError:
        return

    if answer.user.id in answers:
        return

    chat_id = poll_data["chad_id"]
    answers.append(answer.user.id)
    await context.bot.send_message(text=f"player {answer.user.mention_html()} voted", chat_id=chat_id, parse_mode=telegram.constants.ParseMode.HTML)

    if len(answers) == game.num_players - 2:
        context.bot_data.clear()
        context.bot_data["options"] = update.poll.options
        await handle_wilty_end_round(update, context, chat_id)
        return await context.bot.stop_poll(chat_id=chat_id, message_id=poll_data["message_id"])

async def handle_wilty_end_round(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE, chat_id:int):
    game:Wilty = games["wilty"].get(chat_id, None)
    if game == None:
        return
    try:
        options = context.bot_data["options"]
    except KeyError:
        return

    votes = [0, 0]
    for option in options:
        if option.text == "false":
            votes[0] += 1
        else:
            votes[1] += 1

    err, players_won, next_state = game.__end_round(votes=tuple(votes))
    if err:
        return await context.bot.send_message(text="an error happend", chat_id=chat_id)

    if players_won:
        await context.bot.send_message(text="you were rigth you got it right", chat_id=chat_id)
    else:
        await context.bot.send_message(text=f"you were wrong {game.players[game.players_ids[game.curr_player_idx]].mention_html()}", chat_id=chat_id)

    if next_state == "end_game":
        return await handle_wilty_end_game(update, context)
    elif next_state == "end_round_type":
        pass
    elif next_state == "continue_round":
        await context.bot.send_message(text=f"the next accussed is f{game.players[game.players_ids[game.curr_player_idx]].metion_html()}",
                                       chat_id=chat_id, parse_mode=telegram.constants.ParseMode.HTML)
    else:
        await context.bot.send_message(text="an error happend", chat_id=chat_id)

async def handle_wilty_end_game(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    return

def main():
    if not BOT_API_TOKEN:
        return

    application = telegram.ext.Application.builder().token(BOT_API_TOKEN).build()

    application.run_polling()

if __name__ == "__main__":
    main()
