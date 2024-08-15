from datetime import datetime
from typing import Literal
import telegram
import telegram.ext
from random import shuffle

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
        if self.curr_state != 0:
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
        if self.state != 1 and self.state != 4:
            return False, "game error"
        if len(curr_hints) != 3:
            return False, "num hints error"
        if self.players[self.players_ids[self.curr_player_idx]][0].id != player.id:
            return False, "curr player error"
        if curr_hints == ["", "", ""] or curr_answer == "":
            return False, "empty inputs"

        self.curr_answer = curr_answer
        self.curr_hints = curr_hints
        self.state = 2

        return True, ""

    def start_play(self):
        if self.state != 2 and self.state != 5:
            return False
        self.curr_state = 3
        return True

    def check_question(self, player:telegram.User):
        if self.state != 3:
            return False, "game error"

        if self.players[player.id][1] <= 0:
            return False, "no questions"

        return True, "has questions"

    def ask_question(self, player:telegram.User, question:str):
        if self.state !=3:
            return False

        if self.players[self.players_ids[self.curr_player_idx]][0].id == player.id:
            return False

        self.players[player.id][1] -= 1
        self.asked_questions[question.lower()] = ""
        return True

    def answer_question(self, player:telegram.User, question:str, answer:str):
        if self.state != 3:
            return False
    
        if self.players[self.players_ids[self.curr_player_idx]][0].id != player.id:
            return False

        if not question in self.asked_questions:
            return False

        self.asked_questions[question] = answer
        return True

    def proccess_answer(self, player:telegram.User, answer:str):
        if self.state != 3:
            return False, "game error"

        if self.players[self.players_ids[self.curr_player_idx]][0].id == player.id:
            return False, "curr player error"

        player_ = self.players[player.id]
        if player.id in self.muted_players:
            return False, "muted player"

        player_[2] -= 1
        if player_[2] == 0:
            self.muted_players.append(player.id)

        if answer.lower() == self.curr_answer:
            self.state = 4
            return True, "correct"

        if len(self.muted_players) == self.num_players - 1:
            self.state = 4
            self.winner_id = -1
            return True, "all players muted"

        self.winner_id = player.id
        return True, "false"

    def end_round(self):
        if self.state != 4:
            return False, "game error"

        if self.winner_id == -1:
            self.players[self.players_ids[self.curr_player_idx]][3] += 1
        else:
            self.players[self.winner_id][3] += 1

        self.curr_hints = ["","","",]
        self.curr_answer = ""
        self.winner_id = -1
        self.asked_questions = {}
        self.muted_players = [-1] * self.num_players
        self.curr_state = 4

        self.curr_player_idx += 1
        if self.curr_player_idx == self.num_players:
            self.state = 5
            return True, "game end"

        return True, "round end"

    def end_game(self):
        scores = {id:player[3] for id, player in self.players.items()}
        self.players = {}
        self.curr_hints = ["", "", ""]
        self.curr_answer = ""
        self.curr_player_idx = -1
        self.state = 0
        self.muted_players = [-1] * self.num_players
        self.asked_questions = {}
        self.winner_id = -1
        return scores

games = {"guess_the_player":{}}

def remove_jobs(name:str, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job_queue:
        return

    jobs = context.job_queue.get_jobs_by_name(name)
    if not jobs:
        return

    for job in jobs:
        job.schedule_removal()
    

