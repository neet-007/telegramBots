from os import getpid
from random import randint, shuffle
from typing import Literal
from apscheduler.util import re
import telegram
from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import telegram.ext
from datetime import datetime

from telegram.ext._handlers.commandhandler import CommandHandler
from telegram.ext._handlers.messagehandler import MessageHandler
from telegram.ext._handlers.pollanswerhandler import PollAnswerHandler
from main import games, remove_jobs

FORMATIONS = {
    "442":{"p1":"gk", "p2":"rb", "p3":"rcb", "p4":"lcb", "p5":"lb",
           "p6":"rw", "p7":"rcm", "p8":"lcm", "p9":"lw", "p10":"rst",
          "p11":"lst"},
    "433":{"p1":"gk", "p2":"rb", "p3":"rcb", "p4":"lcb", "p5":"lb",
           "p6":"rcm", "p7":"cdm", "p8":"lcm", "p9":"rw", "p10":"lw",
           "p11":"st"},
    "4231":{"p1":"gk", "p2":"rb", "p3":"rcb", "p4":"lcb", "p5":"lb",
            "p6":"rcdm", "p7":"lcdm", "p8":"rw", "p9":"am", "p10":"lw",
            "p11":"st"},
    "352":{"p1":"gk", "p2":"rcb", "p3":"cb", "p4":"lcb", "p5":"rwb",
           "p6":"rcm","p7":"cdm", "p8":"lcm", "p9":"lwb", "p10":"rst", 
           "p11":"lst"},
    "532":{"p1":"gk", "p2":"rwb", "p3":"rcb", "p4":"cb", "p5":"lcb",
           "p6":"lwb", "p7":"rcm", "p8":"cdm", "p9":"lcm", "p10":"rst",
           "p11":"lst"}
}

class Draft():
    def __init__(self) -> None:
        self.players = {}
        self.num_players = 0
        self.category = ""
        self.formation = ["", {}]
        self.teams = []
        self.picked_teams = []
        self.players_ids = []
        self.start_player_idx = -1
        self.curr_player_idx = -1
        self.state = 0
        self.curr_pos = "p1"
        self.curr_team_idx = -1

    def join_game(self, player:telegram.User):
        if self.state != 0 or player.id in self.players:
            return False

        self.players[player.id] = [player, {"p1":None, "p2":None, "p3":None, "p4":None, "p5":None,
                                            "p6":None, "p7":None, "p8":None, "p9":None, "p10":None,
                                            "p11":None}]
        self.players_ids.append(player.id)
        self.num_players += 1
        self.state = 1

        return True

    def start_game(self):
        if self.state != 1 or self.num_players < 2:
            return False

        self.state = 2
        return True

    def set_game_states(self, category:str, teams:list[str], formation:str):
        if self.state != 2 or not category or len(teams) != (11 + self.num_players):
            return False
    
        formation_ = FORMATIONS.get(formation, None)
        if formation_ == None:
            return False

        if len(set(teams)) != len(teams):
            return False

        self.formation[0] = formation
        self.formation[1] = formation_
        self.teams = teams
        self.picked_teams = [False] * len(teams)
        self.category = category
        self.start_player_idx = 0
        self.curr_player_idx = 0
        shuffle(self.players_ids)
        self.state = 3

        return True

    def add_pos_to_team(self, player:telegram.User, added_player:str) -> tuple[bool, Literal["game_error", "curr_player_error", "picked_team_error", "picked_pos_error", "new_pos", "same_pos", "end_game"]]:
        if self.state != 3 or (not player.id in self.players):
            return False, "game_error"

        if self.players_ids[self.curr_player_idx] != player.id:
            return False, "curr_player_error"

        if self.picked_teams[self.curr_team_idx]:
            return False, "picked_team_error"

        player_ = self.players[player.id]
        if player_[1][self.curr_pos] != None:
            return False, "picked_pos_error"

        player_[1][self.curr_pos] = added_player.lower()
        if self.curr_player_idx == (self.start_player_idx + self.num_players) % self.num_players:
            if self.curr_pos == "p11":
                self.state = 4
                return True, "end_game"

            self.start_player_idx = (self.start_player_idx + 1) % self.num_players
            return True, "new_pos"

        self.curr_player_idx = (self.curr_player_idx + 1) % self.num_players
        self.curr_pos = "p" + f"{int(self.curr_pos[1]) + 1}" if len(self.curr_pos) == 2 else  "p" + f"{int(self.curr_pos[1:3]) + 1}"
        return True, "same_pos"

    def rand_team(self, player_id):
        if self.state != 3:
            return ""

        if player_id != self.players_ids[self.start_player_idx]:
            return ""

        self.curr_team_idx = randint(0, len(self.teams) - 1)
        while self.picked_teams[self.curr_team_idx]:
            self.curr_team_idx = randint(0, len(self.teams) - 1)

        self.picked_teams[self.curr_team_idx] = True
        return self.teams[self.curr_team_idx]

    def end_game(self, votes:dict[int, int]):
        if self.state != 4:
            return []

        max_vote = float("-inf")
        max_vote_ids = []
        for id, vote_count in votes.items():
            if vote_count > max_vote:
                max_vote = vote_count
                max_vote_ids.clear()
                max_vote_ids.append(id)
            elif vote_count == max_vote:
                max_vote_ids.append(id)

        return [self.players[x] for x in max_vote_ids]

async def handle_draft_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or not context.job_queue:
        return

    if update.effective_chat.id in games["draft"]:
        return await update.message.reply_text("a game has already started")

    games["draft"][update.effective_chat.id] = Draft()

    data = {"game_id":update.effective_chat.id, "time":datetime.now()}
    context.job_queue.run_repeating(handle_draft_reapting_join_job, interval=20, first=10, data=data, chat_id=update.effective_chat.id, name="draft_reapting_join_job")
    context.job_queue.run_once(handle_draft_start_game_job, when=60, data=data, chat_id=update.effective_chat.id, name="draft_start_game_job")
    await update.message.reply_text(text="a game has started /draft_join or press the button", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="join game", callback_data="draft_join")]
        ]
    ))

async def handle_draft_reapting_join_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict):
        return

    game:Draft = games["draft"].get(context.job.data["game_id"], None)
    if not game or game.state!= 0:
        return

    await context.bot.send_message(chat_id=context.job.chat_id, text=f"to join the game send /draft_join\n reaming time {round((context.job.data['time'] - datetime.now()).seconds)}")

async def handle_draft_start_game_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict):
        return

    game:Draft = games["draft"].get(context.job.data["game_id"], None)
    if not game or game.state!= 0:
        return
    
    remove_jobs("draft_reapting_join_job", context)
    res = game.start_game()
    if not res:
        del games["draft"][context.job.data["game_id"]]
        return await context.bot.send_message(text="not enougp players joined", chat_id=context.job.chat_id)

    await context.bot.send_message(text=f"the game has started decide the category, teams and formations\n then the admin should send as /set_draft_state category, teams,teams should be separated by - and the number of teams must be {11 + game.num_players} formations in that order with commas\n supported formations are 442 443 4231 352 532 in this foramt",
                                   chat_id=context.job.chat_id)
    

async def handle_draft_join_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or not update.effective_user:
        return

    game:Draft = games["draft"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game please start one first /new_draft")

    res = game.join_game(player=update.effective_user)
    if not res:
        return await update.message.reply_text("player has already joined game")

    await update.message.reply_text(f"player {update.effective_user.mention_html()} has joined the game", parse_mode=telegram.constants.ParseMode.HTML)
    
async def handle_draft_join_callback(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.effective_chat or not update.effective_user:
        return

    q = update.callback_query
    await q.answer()

    game:Draft = games["draft"].get(update.effective_chat.id, None)
    if game == None:
        return await context.bot.send_message(text=f"{update.effective_user.mention_html()} there is no game please start one first /new_draft",
                                              chat_id=update.effective_chat.id, parse_mode=telegram.constants.ParseMode.HTML)

    res = game.join_game(player=update.effective_user)
    if not res:
        return await context.bot.send_message(text=f"player {update.effective_user.mention_html()} has already joined game",
                                              chat_id=update.effective_chat.id, parse_mode=telegram.constants.ParseMode.HTML)

    await context.bot.send_message(text=f"player {update.effective_user.mention_html()} has joined the game",
                                   chat_id=update.effective_chat.id, parse_mode=telegram.constants.ParseMode.HTML)

async def handle_draft_start_game_command(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or not context.job_queue:
        return

    game:Draft = games["draft"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game please start one first /new_draft")

    res = game.start_game()
    if not res:
        del games["draft"][update.effective_chat.id]
        return await update.message.reply_text("cant start game with less than two players start new game /new_draft")

    data = {"game_id":update.effective_chat.id, "time":datetime.now()}
    context.job_queue.run_repeating(handle_draft_reapting_statement_job, interval=20, first=10, data=data, chat_id=update.effective_chat.id, name="draft_reapting_statement_job")
    context.job_queue.run_once(handle_draft_set_state_command_job, when=60, data=data, chat_id=update.effective_chat.id, name="draft_set_state_command_job")

    await update.message.reply_text(f"the game has started decide the category, teams and formations\n then the admin should send as /set_draft_state category, teams,teams should be separated by - and the number of teams must be {11 + game.num_players} formations in that order with commas\n supported formations are 442 443 4231 352 532 in this foramt")

async def handle_draft_reapting_statement_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict):
        return

    game:Draft = games["draft"].get(context.job.data["game_id"], None)
    if not game or game.state != 2:
        return

    await context.bot.send_message(chat_id=context.job.chat_id, text=f"reaming time to decide statements {round((context.job.data['time'] - datetime.now()).seconds)}")

async def handle_draft_set_state_command_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict):
        return

    remove_jobs("draft_reapting_statement_job", context)
    game:Draft = games["draft"].get(context.job.data["game_id"], None)
    if not game or game.state != 2:
        return

    await context.bot.send_message(chat_id=context.job.chat_id, text=f"the admin should send the state as /set_draft_state category, teams,teams should be separated by - and the number of teams must be {11 + game.num_players} formations in that order with commas\n supported formations are 442 443 4231 352 532 in this foramt")

async def handle_draft_set_state_command(update: telegram.Update, context:telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_chat or not update.effective_user:
        return

    admins_list = [admin.id for admin in context.bot.get_chat_administrators(update.effective_chat.id)]
    if not update.effective_user.id in admins_list:
        return

    game:Draft = games["draft"].get(update.effective_chat.id, None)
    if game == None:
        return await update.message.reply_text("there is no game please start one first /new_draft")

    text = update.message.text.lower().replace("/set_draft_state", "").strip().split(",")
    if len(text) != 3:
        return await update.message.reply_text("there is something missing")

    res = game.set_game_states(category=text[0], teams=text[1].split("-"), formation=text[2])
    if not res:
        return await update.message.reply_text(f"number of teams must be {11 + game.num_players} with no duplicates")

    await update.message.reply_text(f"the category is {game.category} the formation is {game.formation[0]} the availabe teams are f{'\n'.join(game.teams)}",
                                    parse_mode=telegram.constants.ParseMode.HTML)
    await update.message.reply_text(f"player {game.players[game.players_ids[game.curr_player_idx]].mention_html()} choose your {game.formation[1][game.curr_pos]}"
                                    , parse_mode=telegram.constants.ParseMode.HTML)

async def handle_draft_pick_team_callback(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.callback_query or not update.effective_chat or not update.effective_user:
        return

    q = update.callback_query
    await q.answer()
    
    game:Draft = games["draft"].get(update.effective_chat.id, None)
    if game == None:
        return

    res = game.rand_team(update.effective_user.id)
    if res == "":
        return 

    await context.bot.send_message(text=f"the team is {res}", chat_id=update.effective_chat.id)

async def handle_draft_add_pos(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or not update.effective_chat or not context.job_queue:
        return

    game:Draft = games["draft"].get(update.effective_chat.id, None)
    if game == None:
        return

    if game.players_ids[game.curr_player_idx] != update.effective_chat.id:
        return

    res, status = game.add_pos_to_team(player=update.effective_user, added_player=update.message.text.lower().strip())
    if not res:
        if status == "game_error":
            del games["draft"][update.effective_chat.id]
            return await update.message.reply_text("an error happend game aported")
        elif status == "picked_pos_error":
            return await update.message.reply_text("player has already picked this position")
        elif status == "curr_player_error":
            return
        elif status == "picked_team_error":
            return await update.message.reply_text("this team has already passed")
        else:
            del games["draft"][update.effective_chat.id]
            return await update.message.reply_text("an error happend game aported")
    if status == "new_pos":
        return await update.message.reply_text(f"player {game.players[game.players_ids[game.start_player_idx]].mention_html()} press the button to pick team",
                                               parse_mode=telegram.constants.ParseMode.HTML,
                                               reply_markup=InlineKeyboardMarkup([
                                                    [InlineKeyboardButton(text="pick team", callback_data="draft_random_player")]
                                               ]))
    elif status == "same_pos":
        return await update.message.reply_text(f"player {game.players[game.players_ids[game.curr_player_idx]].mention_html()} choose your player for {game.formation[1][game.curr_pos]}", parse_mode=telegram.constants.ParseMode.HTML)
    elif status == "end_game":
        data = {"game_id":update.effective_chat.id, "time":datetime.now()}
        context.job_queue.run_repeating(handle_draft_reapting_votes_job, interval=20, first=10, data=data, chat_id=update.effective_chat.id, name="draft_reapting_votes_job")
        context.job_queue.run_once(handle_draft_set_votes_job, when=60, data=data, chat_id=update.effective_chat.id, name="draft_set_votes_job")
        await context.bot.send_message(text="the drafting has ended discuss the teams for 3 minutes then vote for the best", chat_id=update.effective_chat.id)
        return
    else:
        del games["draft"][update.effective_chat.id]
        return await update.message.reply_text("an error happend game aported")

async def handle_draft_reapting_votes_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict):
        return

    game:Draft = games["draft"].get(context.job.data["game_id"], None)
    if not game or game.state != 2:
        return

    await context.bot.send_message(chat_id=context.job.chat_id, text=f"reaming time to decide votings {round((context.job.data['time'] - datetime.now()).seconds)}")

async def handle_draft_set_votes_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict) or not context.job_queue:
        return

    remove_jobs("draft_reapting_votes_job", context)
    chat_id = context.job.data["game_id"]
    game:Draft = games["draft"].get(chat_id, None)
    if not game or game.state != 2:
        return

    poll_data = {
        "chat_id":chat_id,
        "questions":[username for username in game.players.values()],
        "votes_count":{username:0 for username in game.players.values()},
        "answers":0
    }
    message = await context.bot.send_poll(question="you has the best team" ,options=poll_data["questions"], chat_id=chat_id,
                                is_anonymous=False, allows_multiple_answers=False)

    poll_data["message_id"] = message.message_id
    context.bot_data[f"poll_{message.poll.id}"] = poll_data

    data = {"game_id":chat_id, "time":datetime.now(), "poll_id":message.poll.id}
    context.job_queue.run_repeating(handle_draft_reapting_votes_end_job, interval=20, first=10, data=data, chat_id=chat_id, name="draft_reapting_votes_end_job")
    context.job_queue.run_once(handle_draft_end_votes_job, when=60, data=data, chat_id=chat_id ,name="draft_end_votes_job")

async def handle_draft_reapting_votes_end_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict):
        return

    game:Draft = games["draft"].get(context.job.data["game_id"], None)
    if not game or game.state != 2:
        return

    await context.bot.send_message(chat_id=context.job.chat_id, text=f"reaming time to vote {round((context.job.data['time'] - datetime.now()).seconds)}")

async def handle_draft_vote_recive(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.poll_answer or not update.effective_chat or not update.effective_user or not context.job_queue:
        return

    answer = update.poll_answer
    poll_data = context.bot_data[answer.poll_id]
    chat_id = poll_data["chat_id"]
    game:Draft = games["draft"].get(chat_id, None)
    if game == None:
        return

    try:
        questions = poll_data["questions"]
    except KeyError:
        return

    poll_data["votes_count"][questions[answer.option_ids[0]]] += 1 
    poll_data["answers"] += 1

    if poll_data["answers"] == game.num_players:
        votes = poll_data["votes_count"]
        del context.bot_data[answer.poll_id]
        remove_jobs("draft_reapting_votes_job", context)
        remove_jobs("draft_end_votes_job", context)
        await context.bot.stop_poll(chat_id=chat_id, message_id=poll_data["message_id"])
        data = {"game_id":chat_id, "time":datetime.now(), "votes":votes}
        context.job_queue.run_once(handle_draft_end_game_job, when=0, data=data, chat_id=chat_id ,name="draft_end_game_job")
    

async def handle_draft_end_votes_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict) or not context.job_queue:
        return

    remove_jobs("draft_reapting_votes_job", context)
    chat_id = context.job.data["game_id"]
    game:Draft = games["draft"].get(chat_id, None)
    if not game:
        return
    
    poll_id = context.job.data["poll_id"]
    poll_data = context.bot_data[poll_id]
    chat_id = poll_data["chat_id"]


    votes = poll_data["votes_count"]
    del context.bot_data[poll_id]
    await context.bot.stop_poll(chat_id=chat_id, message_id=poll_data["message_id"])
    data = {"game_id":chat_id, "time":datetime.now(), "votes":votes}
    context.job_queue.run_once(handle_draft_end_game_job, when=0, data=data, chat_id=chat_id ,name="draft_end_game_job")


async def handle_draft_end_game_job(context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job or not context.job.chat_id or not isinstance(context.job.data, dict) or not context.job_queue:
        return

    remove_jobs("draft_reapting_votes_job", context)
    chat_id = context.job.data["game_id"]
    game:Draft = games["draft"].get(chat_id, None)
    if not game or game.state != 2:
        return

    try:
        votes = context.job.data["votes"]
        username_to_id = {player[0].username:id for id, player in game.players.items()}
        votes = {username_to_id[username]:count for username, count in votes.items()}
    except KeyError:
        return

    winners = game.end_game(votes=votes)
    winners_text = ""
    for winner in winners:
        winners += f"{winner.mention_html()}\n"

    await context.bot.send_message(text=f"the winners are {winners_text}", chat_id=context.job.chat_id)

async def handle_draft_cancel_game(update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message:
        return

    if not update.effective_chat.id in games["draft"]:
        return await update.message.reply_text("there is no game")

    remove_jobs("draft_reapting_votes_job", context)
    remove_jobs("draft_reapting_end_votes_job", context)
    remove_jobs("draft_end_votes_job", context)
    remove_jobs("draft_set_votes_job", context)
    remove_jobs("draft_reapting_join_job", context)
    remove_jobs("draft_start_game_job", context)
    remove_jobs("draft_reapting_statement_job", context)
    remove_jobs("draft_set_statement_command_job", context)
    del games["draft"][update.effective_chat.id]

    await update.message.reply_text("game has been canceled")

new_draft_game_command_handler = CommandHandler("new_draft", handle_draft_command)
join_draft_game_command_handler = CommandHandler("join_draft", handle_draft_join_command)
start_draft_game_command_handler = CommandHandler("start_draft", handle_draft_start_game_command)
set_draft_game_state_command_handler = CommandHandler("set_draft_state", handle_draft_set_state_command)
cancel_draft_game_command_handler = CommandHandler("cancel_draft", handle_draft_cancel_game)
position_draft_message_handler = MessageHandler((telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND), handle_draft_add_pos)
vote_recive_poll_answer_handler = PollAnswerHandler(handle_draft_vote_recive)

