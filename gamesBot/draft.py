from logging import FATAL
from random import randint, shuffle
from typing import Literal
import telegram
import telegram.ext
from main import games

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

    def add_pos_to_team(self, player:telegram.User, pos:str, added_player:str, team:str) -> tuple[bool, Literal["game_error", "curr_player_error", "not_team_error", "picked_team_error", "picked_pos_error", "new_pos", "same_pos", "end_game"]]:
        if self.state != 3 or (not player.id in self.players):
            return False, "game_error"

        if self.players_ids[self.curr_player_idx] != player.id:
            return False, "curr_player_error"

        try:
            team_idx = self.teams.index(team)
        except ValueError:    
            return False, "not_team_error"

        if self.picked_teams[team_idx]:
            return False, "picked_team_error"

        player_ = self.players[player.id]
        if player_[1][pos.lower()] != None:
            return False, "picked_pos_error"

        player_[1][pos.lower()] = added_player.lower()
        if self.curr_player_idx == (self.start_player_idx + self.num_players) % self.num_players:
            if pos == "p11":
                self.state = 4
                return True, "end_game"

            self.start_player_idx = (self.start_player_idx + 1) % self.num_players
            return True, "new_pos"

        self.curr_player_idx = (self.curr_player_idx + 1) % self.num_players
        return True, "same_pos"

    def rand_team(self, player_id):
        if self.state != 3:
            return ""

        if player_id != self.players_ids[self.start_player_idx]:
            return ""

        team_idx = randint(0, len(self.teams) - 1)
        while self.picked_teams[team_idx]:
            team_idx = randint(0, len(self.teams) - 1)

        self.picked_teams[team_idx] = True
        return self.teams[team_idx]

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



        

        


