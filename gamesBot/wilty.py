from telegram import User
from random import shuffle

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

    def __join_game(self, player:User):
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

    def __set_players_statements(self, statements:dict[int, list[str]]):
        if self.state != 1:
            return False

        return_val = True
        for player, statement in statements.items():
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
            return False
        state = self.__update_game_state()
        if state:
            self.state = 3
        return state,self.round_type, self.players[self.curr_mod_id], self.players[self.players_ids[self.curr_player_idx]]
    
    def __set_mod_state(self,mode_statement:str):
        if self.state != 3:
            return
        self.state = 4
        self.mod_statement = mode_statement.lower()

    def __end_round(self, votes:tuple[int, int]):
        if self.state != 4 or sum(votes) != self.num_players - 2:
            return False, False, "end_game"
    
        return_val = True, True
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



