from typing import Optional, Union
import telegram
import telegram.ext
from typing import Literal
from random import shuffle, randint

def remove_jobs(name:str, context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    if not context.job_queue:
        return

    jobs = context.job_queue.get_jobs_by_name(name)
    if not jobs:
        return

    for job in jobs:
        job.schedule_removal()

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

        return True

    def start_game(self):
        if self.state != 0 or self.num_players < 2:
            return False

        self.state = 1
        return True

    def set_game_states(self, category:str, teams:list[str], formation:str) -> tuple[bool, Literal["game error", "no category error", "num of teams error", "formation error", "duplicate teams error", ""]]:
        if self.state != 1 :
            return False, "game error"
        if not category:
            return False, "no category error"
        if len(teams) != (11 + self.num_players):
            return False, "num of teams error"
        print(formation)
        formation_ = FORMATIONS.get(formation, None)
        if formation_ == None:
            return False, "formation error"

        if len(set(teams)) != len(teams):
            return False, "duplicate teams error"

        self.formation[0] = formation
        self.formation[1] = formation_
        self.teams = [team.strip() for team in teams]
        self.picked_teams = [False] * len(teams)
        self.category = category
        self.start_player_idx = 0
        self.curr_player_idx = 0
        shuffle(self.players_ids)
        self.state = 2

        return True, ""

    def add_pos_to_team(self, player:telegram.User, added_player:str) -> tuple[bool, Literal["game_error", "curr_player_error", "picked_team_error", "picked_pos_error", "new_pos", "same_pos", "end_game"]]:
        if self.state != 2 or (not player.id in self.players):
            return False, "game_error"

        if self.players_ids[self.curr_player_idx] != player.id:
            return False, "curr_player_error"

        if self.picked_teams[self.curr_team_idx]:
            return False, "picked_team_error"

        player_ = self.players[player.id]
        if player_[1][self.curr_pos] != None:
            return False, "picked_pos_error"

        player_[1][self.curr_pos] = added_player.lower()
        if self.curr_player_idx == (self.start_player_idx + self.num_players - 1) % self.num_players:
            if self.curr_pos == "p11":
                self.state = 3
                return True, "end_game"

            self.start_player_idx = (self.start_player_idx + 1) % self.num_players
            self.picked_teams[self.curr_team_idx] = True
            self.curr_pos = "p" + f"{int(self.curr_pos[1]) + 1}" if len(self.curr_pos) == 2 else  "p" + f"{int(self.curr_pos[1:3]) + 1}"
            return True, "new_pos"

        self.curr_player_idx = (self.curr_player_idx + 1) % self.num_players
        return True, "same_pos"

    def rand_team(self, player_id):
        if self.state != 2:
            return ""

        if player_id != self.players_ids[self.start_player_idx]:
            return ""

        self.curr_team_idx = randint(0, len(self.teams) - 1)
        while self.picked_teams[self.curr_team_idx]:
            self.curr_team_idx = randint(0, len(self.teams) - 1)

        return self.teams[self.curr_team_idx]

    def end_game(self, votes:dict[int, int]):
        if self.state != 3:
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

class Wilty():
    def __init__(self, chat_id:int) -> None:
        self.chat_id = chat_id
        self.num_players:int = 0
        self.curr_mod_id:int | None = None
        self.players = dict()
        self.players_ids = []
        self.curr_mod_idx = -1
        self.curr_player_idx = -1
        self.state = 0
        self.round_type = "none"
        self.mod_statement = ""
        self.curr_statement = ""
        self.statements = dict()

    def __join_game(self, player:telegram.User):
        if self.state != 0:
            return False
        if player in self.players:
            return False

        self.players[player.id] = [player, [], 0]
        self.players_ids.append(player.id)
        self.num_players += 1
        return True

    def __start_game(self):
        if self.state != 0 or self.num_players < 3:
            return False, None, None

        shuffle(self.players_ids)
        continue_game, new_round = self.__update_game_state()
        if not continue_game or new_round:
            return False, None, None

        self.state = 1

        return True, self.players.get(self.curr_mod_id, None), self.players.get(self.players_ids[self.curr_player_idx], None)

    def __add_player_statements(self, player_id:int, statements:list[str]):
        if len(statements) != 4:
            return False

        self.statements[player_id] = statements
        return True

    def __set_players_statements(self):
        if self.state != 1 or len(self.statements) != self.num_players:
            return False

        return_val = True
        for player, statement in self.statements.items():
            if len(statement) != 4:
                return_val = False
                break

            statement = [x.lower() for x in statement]
            self.players[player][1] = statement

        if return_val:
            self.state = 2
        return return_val

    def __update_game_state(self):
        if self.curr_mod_idx == -1:
            self.curr_mod_idx = self.num_players - 1
            self.curr_player_idx = 0
            self.round_type = ""
            return True, False

        if self.curr_player_idx == self.num_players - 1 or (self.curr_player_idx == self.num_players - 2 and self.curr_mod_idx == self.num_players - 1):
            if self.round_type == "":
                return False, True

            self.curr_mod_idx -= 1
            if self.curr_mod_idx < 0:
                self.curr_mod_idx = self.num_players - 1

            self.curr_player_idx = 0
            if self.curr_mod_idx == 0:
                self.curr_player_idx = 1

            if self.round_type == "":
                self.round_type = ""
            elif self.round_type == "":
                self.round_type = ""
            elif self.round_type == "":
                self.round_type = ""

            return True, True

        self.curr_player_idx += 1
        if self.curr_player_idx == self.curr_mod_idx:
            self.curr_player_idx += 1

        return True, False

    def __start_round(self):
        if self.state != 2:
            return False, "", None, None
        state, _ = self.__update_game_state()
        if state:
            self.state = 3
        return state, self.round_type, self.players.get(self.curr_mod_id, None), self.players.get(self.players_ids[self.curr_player_idx], None)
    
    def __set_mod_state(self,mode_statement:str):
        if self.state != 3:
            return
        self.state = 4
        self.mod_statement = mode_statement.lower()

    def __end_round(self, votes) -> tuple[bool, bool, str]:
        if self.state != 4:
            return False, False, "end_game"
    
        return_val = True, True, ""
        if votes[0] > votes[1]:
            if self.mod_statement == self.curr_statement:
                return_val =  True, False
            else:
                return_val = True, True
        else:
            if self.mod_statement == self.curr_statement:
                return_val = True, True
            else:
                return_val = True, False
    
        if return_val[1]:
            for id in self.players_ids:
                if id == self.players_ids[self.curr_player_idx] or id == self.curr_mod_id:
                    continue
                self.players[id][2] += 1
        else:
            self.players[self.curr_player_idx][2] += 1

        continue_game, round_type_end = self.__update_game_state()
        if not continue_game:
            return_val += tuple(["end_game"])
        if round_type_end:
            return_val += tuple(["end_round_type"])
        if len(return_val) < 3:
            return_val += tuple(["continue_round"])
        return return_val

    def __get_scores(self):
        return {id:data[2] for id, data in self.players.items()}

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
        self.curr_asking_player:int = -1
        self.curr_question = ""
        self.asked_questions = {}
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

    def leave_game(self, player:telegram.User):
        try:
            del self.players[player.id]
        except KeyError:
            return False, "player not in game error"

        self.num_players -= 1
        idx = self.players_ids.index(player.id)
        self.players_ids.remove(player.id)
        if player.id in self.muted_players:
            self.muted_players.remove(player.id)

        if self.num_players == 1:
            self.state = 4
            self.winner_id = -2
            return False, "end game"
            
        if len(self.muted_players) == self.num_players or self.curr_player_idx == idx:
            self.winner_id = -2
            self.state = 3
            return False, "end round"

        return True, ""

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

        if self.curr_asking_player != -1:
            return False, "there is askin player error"

        if self.players[self.players_ids[self.curr_player_idx]][0].id == player.id:
            return False, "curr player error"

        if self.players[player.id][1] <= 0:
            return False, "no questions"

        self.curr_question = question.lower().strip()
        self.curr_asking_player = player.id
        return True, ""

    def answer_question(self, player:telegram.User, player_asked:telegram.User, question:str, answer:str):
        if self.state != 2:
            return False, "game error"
    
        if self.curr_asking_player == -1:
            return False, "no asking player error"

        if self.curr_asking_player != player_asked.id:
            return False, "player is not the asking error"

        question = question.lower().strip()
        if self.curr_question != question:
            return False, "not the question"

        if self.players[self.players_ids[self.curr_player_idx]][0].id != player.id:
            return False, "curr player error"

        self.asked_questions[question] = answer.lower().strip()
        self.players[self.curr_asking_player][1] -= 1
        self.curr_asking_player = -1
        self.curr_question = ""

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
        elif self.winner_id == -2:
            pass
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

games:dict[int, Optional[Union[GuessThePlayer, Draft, Wilty]]] = {}
