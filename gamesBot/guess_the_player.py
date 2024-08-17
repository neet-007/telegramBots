from datetime import datetime
import telegram
from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import telegram.ext
from random import shuffle

from telegram.ext._handlers.callbackqueryhandler import CallbackQueryHandler
from telegram.ext._handlers.commandhandler import CommandHandler
from telegram.ext._handlers.messagehandler import MessageHandler


PLAYERS_COUNT = 2

class GuessThePlayer:
    def __init__(self) -> None:
        self.players = {}
        self.muted_players:list[int] = []
        self.players_ids:list[int] = []
        self.curr_player_idx:int = -1
        self.num_players:int = 0 
        self.curr_hints:list[str] = ["","","",]
        self.curr_answer:str = ""
        self.asked_questions:dict[str, str] = {}
        self.state:int = 0
        self.winner_id:int = -1

    def join_game(self, player:telegram.User):
        if self.state != 0:
            return False
        if player.id in self.players:
            return False
        self.num_players += 1
        self.players[player.id] = [player, 3, 3, 0]
        self.players_ids.append(player.id)
        return True

    def start_game(self):
        if self.state != 0:
            return False, "game error"
        if self.num_players < PLAYERS_COUNT:
            return False, "num players error"
    
        shuffle(self.players_ids)
        self.curr_player_idx = 0
        self.state = 1
        return True, ""

    def start_round(self, player: telegram.User, curr_hints:list[str], curr_answer:str):
        if self.state != 1 and self.state != 3:
            return False, "game error"
        if len(curr_hints) != 3:
            return False, "num hints error"
        if self.players[self.players_ids[self.curr_player_idx]][0].id != player.id:
            return False, "curr player error"
        if curr_hints == ["", "", ""] or curr_answer == "":
            return False, "empty inputs"

        self.curr_answer = curr_answer.strip().lower()
        self.curr_hints = [hint.strip().capitalize() for hint in curr_hints]
        self.state = 2

        return True, ""

    def ask_question(self, player:telegram.User, question:str):
        if self.state != 2:
            return False, "game_error"

        if self.players[self.players_ids[self.curr_player_idx]][0].id == player.id:
            return False, "curr player error"

        if self.players[player.id][1] <= 0:
            return False, "no questions"

        self.players[player.id][1] -= 1
        self.asked_questions[question.lower()] = ""
        return True, ""

    def answer_question(self, player:telegram.User, question:str, answer:str):
        if self.state != 2:
            return False, "game error"
    
        if self.players[self.players_ids[self.curr_player_idx]][0].id != player.id:
            return False, "curr player error"

        if not question in self.asked_questions:
            return False, "question error"

        self.asked_questions[question] = answer
        return True, ""

    def proccess_answer(self, player:telegram.User, answer:str):
        if self.state != 2:
            return False, "game error"

        if self.players[self.players_ids[self.curr_player_idx]][0].id == player.id:
            return False, "curr player error"

        player_ = self.players[player.id]
        if player.id in self.muted_players:
            return False, "muted player"

        player_[2] -= 1
        if player_[2] == 0:
            self.muted_players.append(player.id)

        if answer.strip().lower() == self.curr_answer:
            self.state = 3
            self.winner_id = player.id
            return True, "correct"

        if len(self.muted_players) == self.num_players - 1:
            self.state = 3
            self.winner_id = -1
            return True, "all players muted"

        return True, "false"

    def end_round(self):
        if self.state != 3:
            return False, "game error"

        if self.winner_id == -1:
            self.players[self.players_ids[self.curr_player_idx]][3] += 1
        else:
            self.players[self.winner_id][3] += 1

        self.curr_hints = ["","","",]
        for id, player in self.players.items():
            self.players[id] = [player[0], 3, 3, player[3]]
        self.curr_answer = ""
        self.winner_id = -1
        self.asked_questions = {}
        self.muted_players = []
        self.curr_state = 2

        self.curr_player_idx += 1
        if self.curr_player_idx == self.num_players:
            self.state = 4
            return True, "game end"

        return True, "round end"

    def end_game(self):
        scores = {player[0]:player[3] for player in self.players.values()}
        winners = ""
        max_score = float('-inf')
        for player, score in scores.items():
            if score == max_score:
                winners += f"{player.mention_html()}\n"
            if score > max_score:
                max_score = score
                winners = ""
                winners += f"{player.mention_html()}\n"

        self.players = {}
        self.curr_hints = ["", "", ""]
        self.curr_answer = ""
        self.curr_player_idx = -1
        self.state = 0
        self.muted_players = []
        self.asked_questions = {}
        self.winner_id = -1
        return scores, winners

games = {"guess_the_player":{}}

def remove_jobs(name:str, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job_queue:
        return

    jobs = context.job_queue.get_jobs_by_name(name)
    if not jobs:
        return

    for job in jobs:
        job.schedule_removal()
    
async def handle_guess_the_player_new_game(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or not context.job_queue:
        return

    if update.effective_chat.id in games["guess_the_player"]:
        return update.message.reply_text("a game has already started")

    games["guess_the_player"][update.effective_chat.id] = GuessThePlayer()
    
    data = {"chat_id":update.effective_chat.id, "time":datetime.now()}
    context.job_queue.run_repeating(handle_guess_the_player_reapting_join_job, data=data, interval=20, first=10,
                                    chat_id=update.effective_chat.id, name="guess_the_player_reapting_join_job")
    context.job_queue.run_once(handle_guess_the_player_start_game_job, when=60, data=data, chat_id=update.effective_chat.id,
                               name="guess_the_player_start_game_job")
    
    await update.message.reply_text("a game has started you can join with the join command /join_guess_the_player or click the button\ngame starts after 1 minute"
                                    , reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="join", callback_data="guess_the_player_join")]]))

async def handle_guess_the_player_join_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or not update.effective_user:
        return

    game:GuessThePlayer = games["guess_the_player"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game start one first /new_guess_the_player")

    res = game.join_game(player=update.effective_user)
    if not res:
        return await update.message.reply_text(f"player f{update.effective_user.mention_html()} has already joined the game",
                                               parse_mode=telegram.constants.ParseMode.HTML)

    await update.message.reply_text(f"player {update.effective_user.mention_html()} has joined the game",
                                    parse_mode=telegram.constants.ParseMode.HTML)

async def handle_guess_the_player_reapting_join_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict):
        return

    game:GuessThePlayer = games["guess_the_player"].get(context.job.data["chat_id"], None)
    if not game or game.state != 0:
        return

    await context.bot.send_message(chat_id=context.job.chat_id, text=f"reaming time to join {round((context.job.data['time'] - datetime.now()).seconds)}")

async def handle_guess_the_player_join_game_callback(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.effective_chat or not update.effective_user:
        return

    q = update.callback_query
    await q.answer()

    game:GuessThePlayer = games["guess_the_player"].get(update.effective_chat.id, None)
    if game == None:
        return await context.bot.send_message(text="no game found please make game first /new_guess_the_player", chat_id=update.effective_chat.id)

    res = game.join_game(player=update.effective_user)
    if not res:
        return await context.bot.send_message(text=f"player {update.effective_user.mention_html()} has already joined game", chat_id=update.effective_chat.id,
                                              parse_mode=telegram.constants.ParseMode.HTML)

    await context.bot.send_message(text=f"player {update.effective_user.mention_html()} has joined the game", chat_id=update.effective_chat.id,
                                   parse_mode=telegram.constants.ParseMode.HTML)

async def handle_guess_the_player_start_game_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict):
        return

    game:GuessThePlayer = games["guess_the_player"].get(context.job.data["chat_id"], None)
    if not game or game.state != 0:
        return

    remove_jobs("guess_the_player_reapting_join_job", context)
    res, err = game.start_game()
    if not res:
        del games["guess_the_player"][context.job.chat_id]
        if err == "game error":
            return await context.bot.send_message(text="game error game aborted", chat_id=context.job.chat_id)
        if err == "num players error":
            return await context.bot.send_message(text="not enough players", chat_id=context.job.chat_id)
        else:
            return await context.bot.send_message(text="game error game aborted", chat_id=context.job.chat_id)

    context.bot_data[game.players_ids[game.curr_player_idx]] = context.job.chat_id
    print(context.bot_data)
    await context.bot.send_message(text=f"gane started the curr player is {game.players[game.players_ids[game.curr_player_idx]][0].mention_html()} send your the player and hints separated by comma ',' and the hints separated by a dash '-'",
                                   chat_id=context.job.chat_id, parse_mode=telegram.constants.ParseMode.HTML)

async def handle_guess_the_player_start_game_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    game:GuessThePlayer = games["guess_the_player"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game start one first /new_guess_the_player")

    remove_jobs("guess_the_player_reapting_join_job", context)
    remove_jobs("guess_the_player_start_game_job", context)
    res, err = game.start_game()
    if not res:
        del games["guess_the_player"][update.effective_chat.id]
        if err == "game error":
            return await update.message.reply_text("game error game aborted")
        if err == "num players error":
            return await update.message.reply_text("not enough players")
        else:
            return await update.message.reply_text("game error game aborted")

    context.bot_data[game.players_ids[game.curr_player_idx]] = update.effective_chat.id
    print(context.bot_data)
    await update.message.reply_text(f"gane started the curr player is {game.players[game.players_ids[game.curr_player_idx]][0].mention_html()} send your the player and hints separated by comma ',' and the hints separated by a dash '-'",
                                    parse_mode=telegram.constants.ParseMode.HTML)

async def handle_guess_the_player_start_round(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("private")
    if not update.message or not update.message.text or not update.effective_user or not update.effective_chat or update.effective_chat.type != "private":
        return

    print(context.bot_data)
    print("if found")
    chat_id = context.bot_data.get(update.effective_user.id, None)
    if chat_id == None:
        return

    print("chat found")
    game:GuessThePlayer = games["guess_the_player"].get(chat_id, None)
    if game == None:
        del context.bot_data[update.effective_user.id]
        return await update.message.reply_text("use this bot at a group")

    print("game found")
    if game.state != 1 and game.state != 3:
        del context.bot_data[update.effective_user.id]
        return 

    print("state if passed")
    if update.effective_user.id != game.players[game.players_ids[game.curr_player_idx]][0].id:
        return 

    print("currect user found")
    text = update.message.text.lower().split(",")
    if len(text) != 2:
        return await update.message.reply_text("must provide the player and hints separated by comma ','")

    res, err = game.start_round(player=update.effective_user, curr_answer=text[0], curr_hints=text[1].split("-"))
    if not res:
        if err == "game error":
            del context.bot_data[update.effective_user.id]
            return await update.message.reply_text("game error game aborted")
        if err == "empty inputs":
            return await update.message.reply_text("must provide the player and hints separated by comma ','")
        if err == "num hints error":
            return await update.message.reply_text("must provide 3 hints separeated by dash '-'")
        if err == "curr player error":
            return
        else:
            del context.bot_data[update.effective_user.id]
            return await update.message.reply_text("game error game aborted")

    text = "\n".join([f"{index}. {hint}" for index, hint in enumerate(game.curr_hints, start=1)])
    await context.bot.send_message(text=f"the curr hints are\n{text}\n every player has 3 questions and 2 treis", chat_id=chat_id)

async def handle_guess_the_player_ask_question_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_chat or not update.effective_user or not context.job_queue:
        return

    game:GuessThePlayer = games["guess_the_player"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game start one first /new_guess_the_player")

    res, err = game.ask_question(player=update.effective_user, question=update.message.text.replace("/guess_the_player_ask_q", "").lower().strip())
    if not res:
        if err == "game_error":
            return await update.message.reply_text("game error game aborted")
        if err == "curr player error":
            return 
        if err == "no questions":
            return await update.message.reply_text("you have used all your questions")
        else:
            return await update.message.reply_text("game error game aborted")

    await update.message.reply_text(f"{game.players[game.players_ids[game.curr_player_idx]][0].mention_html()} answer the question using the command /guess_the_player_answer_q", parse_mode=telegram.constants.ParseMode.HTML)

async def handle_guess_the_player_answer_question_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_chat or not update.effective_user or not context.job_queue:
        return

    game:GuessThePlayer = games["guess_the_player"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game start one first /new_guess_the_player")

    res, err = game.answer_question(player=update.effective_user, question="",
                                    answer=update.message.text.replace("/guess_the_player_answer_q", "").lower().strip())
    if not res:
        if err == "game error":
            return await update.message.reply_text("game error game aborted")
        if err == "curr player error":
            return
        if err == "question error":
            return await update.message.reply_text("question is not asked")
        else:
            return await update.message.reply_text("game error game aborted")

async def handle_guess_the_player_proccess_answer_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("proccessa answer")
    if not update.message or not update.message.text or not update.effective_chat or not update.effective_user or not context.job_queue:
        return

    print("if passed")
    game:GuessThePlayer = games["guess_the_player"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game start one first /new_guess_the_player")

    print("game found")
    res, err = game.proccess_answer(player=update.effective_user, answer=update.message.text.replace("/answer_player_guess_the_player", "").lower().strip())
    if not res:
        if err == "game error":
            return await update.message.reply_text("game error game aborted")
        if err == "curr player error":
            return
        if err == "muted player":
            return
        else:
            return await update.message.reply_text("game error game aborted")
    
    print(err)
    if err == "false":
        return await update.message.reply_text("the answer is wrong")
    if err == "correct":
        context.job_queue.run_once(handle_guess_the_player_end_round_job, when=0, chat_id=update.effective_chat.id)
        return await update.message.reply_text("your answer is correct")
    if err == "all players muted":
        context.job_queue.run_once(handle_guess_the_player_end_round_job, when=0, chat_id=update.effective_chat.id)
        return await update.message.reply_text("you have lost")
    else:
        return await update.message.reply_text("game error game aborted")

async def handle_guess_the_player_end_round_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("end round")
    if not context.job or not context.job.chat_id or not context.job_queue:
        return

    print("if passed")
    game:GuessThePlayer = games["guess_the_player"].get(context.job.chat_id, None)
    if game == None:
        return await context.bot.send_message(text="there is no game start one first /new_guess_the_player", chat_id=context.job.chat_id)

    print("game found")
    res, err = game.end_round()
    if not res:
        if err == "game error":
            return await context.bot.send_message(text="game error game aborted", chat_id=context.job.chat_id)
        else:
            pass

    print("no error")
    if err == "game end":
        print("end game")
        context.job_queue.run_once(handle_guess_the_player_end_game_job, when=0, chat_id=context.job.chat_id)
        return await context.bot.send_message(text="the game has ended the results will come now", chat_id=context.job.chat_id)
    if err == "round end":
        print("rouind end")
        context.bot_data[game.players_ids[game.curr_player_idx]] = context.job.chat_id
        print(context.bot_data)
        await context.bot.send_message(text=f"gane started the curr player is {game.players[game.players_ids[game.curr_player_idx]][0].mention_html()} send your the player and hints separated by comma ',' and the hints separated by a dash '-'",
                                       chat_id=context.job.chat_id, parse_mode=telegram.constants.ParseMode.HTML)
    else:
        return await context.bot.send_message(text="game error game aborted", chat_id=context.job.chat_id)

async def handle_guess_the_player_end_game_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    print("end game")
    if not context.job or not context.job.chat_id or not context.job_queue:
        return

    print("if passed")
    game:GuessThePlayer = games["guess_the_player"].get(context.job.chat_id, None)
    if game == None:
        return await context.bot.send_message(text="there is no game start one first /new_guess_the_player", chat_id=context.job.chat_id)

    print("game found")
    del games["guess_the_player"][context.job.chat_id]
    scores, winners = game.end_game()
    text = ""
    for player, score in scores.items():
        text += f"{player.mention_html()}:{score}\n"

    return await context.bot.send_message(text=f"scores:\n{text}\nwinners:\n{winners}", chat_id=context.job.chat_id, parse_mode=telegram.constants.ParseMode.HTML)

async def handle_guess_the_player_cancel_game(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    game:GuessThePlayer = games["guess_the_player"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game start one first /new_guess_the_player")

    del games["guess_the_player"][update.effective_chat.id]
    remove_jobs("guess_the_player_reapting_join_job", context)
    remove_jobs("guess_the_player_start_game_job", context)
    remove_jobs("guess_the_player_end_round_job", context)
    remove_jobs("guess_the_player_end_game_job", context)
    await update.message.reply_text("game cancel")

guess_the_player_new_game_command_handler = CommandHandler("new_guess_the_player", handle_guess_the_player_new_game)
guess_the_player_join_game_command_handler = CommandHandler("join_guess_the_player", handle_guess_the_player_join_command)
guess_the_player_start_game_command_handler = CommandHandler("start_game_guess_the_player", handle_guess_the_player_start_game_command)
guess_the_player_ask_question_command_handler = CommandHandler("ask_q_guess_the_player", handle_guess_the_player_ask_question_command)
guess_the_player_answer_question_command_handler = CommandHandler("answer_q_guess_the_player", handle_guess_the_player_answer_question_command)
guess_the_player_proccess_answer_command_handler = CommandHandler("answer_player_guess_the_player", handle_guess_the_player_proccess_answer_command)
guess_the_player_cancel_game_command_handler = CommandHandler("cancel_guess_the_player", handle_guess_the_player_cancel_game)
guess_the_player_start_round_command_handler = MessageHandler((telegram.ext.filters.TEXT & ~ telegram.ext.filters.COMMAND), handle_guess_the_player_start_round)
guess_the_player_join_game_callback_handler = CallbackQueryHandler(handle_guess_the_player_join_game_callback, pattern="^guess_the_player_join$")


