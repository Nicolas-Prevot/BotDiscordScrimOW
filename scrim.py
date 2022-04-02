from typing import TypeVar
from build_teams import *

Player = TypeVar("Player")

class Roles():
	def __init__(self):
		self.tank = {"Is_choosen" : True, "priority" : 3, "elo" : 4}
		self.dps  = {"Is_choosen" : True, "priority" : 3, "elo" : 4}
		self.heal = {"Is_choosen" : True, "priority" : 3, "elo" : 4}

	def set_Is_choosen_info(self, is_tank: bool, is_dps: bool, is_heal: bool):
		self.tank["Is_choosen"] = is_tank
		self.dps["Is_choosen"]  = is_dps
		self.heal["Is_choosen"] = is_heal

	def set_tank_priority(self, priority : int):
		self.tank["priority"] = priority
	def set_dps_priority(self, priority : int):
		self.dps["priority"] = priority
	def set_heal_priority(self, priority : int):
		self.heal["priority"] = priority
	def set_tank_elo(self, elo : int):
		self.tank["elo"] = elo
	def set_dps_elo(self, elo : int):
		self.dps["elo"] = elo
	def set_heal_elo(self, elo : int):
		self.heal["elo"] = elo
	def get_tank_priority(self):
		return self.tank["priority"]
	def get_heal_priority(self):
		return self.heal["priority"]
	def get_dps_priority(self):
		return self.dps["priority"]
	def get_tank_is_choosen(self):
		return self.tank["Is_choosen"]
	def get_dps_is_choosen(self):
		return self.dps["Is_choosen"]
	def get_heal_is_choosen(self):
		return self.heal["Is_choosen"]
	def get_all(self):
		return [self.tank["Is_choosen"],self.tank["priority"],
				self.tank["elo"],self.dps["Is_choosen"],self.dps["priority"],
				self.dps["elo"],self.heal["Is_choosen"],self.heal["priority"],
				self.heal["elo"]]
	def get_elo(self, role: str):
		if role == "tank":
			if self.get_tank_is_choosen():
				return self.tank["elo"]
			else:
				return self.__get_mean_elo()
		elif role == "dps":
			if self.get_dps_is_choosen():
				return self.dps["elo"]
			else:
				return self.__get_mean_elo()
		elif role == "heal":
			if self.get_heal_is_choosen():
				return self.heal["elo"]
			else:
				return self.__get_mean_elo()
	def __get_mean_elo(self):
		mean=0
		n=0
		if self.tank["Is_choosen"]:
			n+=1
			mean += self.tank["elo"]
		if self.dps["Is_choosen"]:
			n+=1
			mean += self.dps["elo"]
		if self.heal["Is_choosen"]:
			n+=1
			mean += self.heal["elo"]
		return mean/n




class Player():
	def __init__(self, name, discord_id, roles: Roles):
		"""
		name : str, Nomiia, Zygoto, ...
		discord_id : str, Nomiia#81621, Zygoto#78618, ...
		"""
		self.name = name
		self.discord_id = discord_id
		self.roles = roles

	def __eq__(self, player : Player):
		return self.discord_id == player.discord_id
	def __str__(self):
		return self.name
	def __repr__(self) -> str:
		return self.name



class Teams():
	def __init__(self, players_list): # player_list : [Player(), Player(),...]
		self._players_list = players_list.copy()
		self._teams_dict = {"bench":[]} 
		# {"bench": [pl1,...], 0:{"tank1":pl1,.."heal2":pl6}, ...}
		self._build_teams()

	def _build_teams(self):
		nb_teams = len(self._players_list)//6
		if nb_teams < 2:
			next_team_id = 0
			for player in self._players_list:
				self._add_player_in_team("bench", "rolebidon", player)
				#Because team_key=="bench",role="rolebidon" will never be used
				if len(self._teams_dict["bench"]) == 6:
					bench_players = self._teams_dict["bench"]
					new_team = {
					"tank1":bench_players[0],
					"tank2":bench_players[1],
					"dps1" :bench_players[2],
					"dps2" :bench_players[3],
					"heal1":bench_players[4],
					"heal2":bench_players[5]}
					self._teams_dict[next_team_id] = new_team
					self._teams_dict["bench"] = []
					next_team_id += 1
		else:
			self._teams_dict = build_team_main_1(self._players_list)
	def get_teams_dict(self):
		return self._teams_dict
	def get_nb_teams(self):
		if self.is_bench_team():
			return len(self._teams_dict)
		return len(self._teams_dict)-1
	def is_bench_team(self):
		return not self._teams_dict["bench"] == []
	def get_bench_team_players(self):
		return self._teams_dict["bench"]
	def get_team_players(self, team_id):
		return self._teams_dict[team_id]
	def get_panel_namesanddiscordid_team(self,team_id):
		res = {} # {discord_id:name , ...}
		if team_id == "bench":
			list_players = self._teams_dict["bench"]
		else:
			list_players = list(self._teams_dict[int(team_id)].values())
		for player in list_players:
			res[player.discord_id] = player.name
		return res

	def panel_remove_player(self, team_id, player):
		self._remove_player_in_team(team_id, player)
		self._players_list.remove(player)

	def add_late_player(self, player):
		self._players_list.append(player)
		self._add_player_in_team("bench", False , player)

	def switch_2_players(self, player1, player2):
		if (type(player1) is dict) and (type(player2) is dict):
			return True
		elif type(player1) is dict:
			keyteam2 = self._get_team_player(player2)
			if keyteam2 is False:
				return False
			role2 = self.get_role_player(keyteam2,player2)
			self._remove_player_in_team(keyteam2,player2)
			keyteam1 = player1["team_id"]
			role1 = player1["role"]
			self._add_player_in_team(keyteam1,role1,player2)
		elif type(player2) is dict:
			keyteam1 = self._get_team_player(player1)
			if keyteam1 is False:
				return False
			role1 = self.get_role_player(keyteam1,player1)
			self._remove_player_in_team(keyteam1,player1)
			keyteam2 = player2["team_id"]
			role2 = player2["role"]
			self._add_player_in_team(keyteam2,role2,player1)
		else:
			if player1 == player2:
				return True
			keyteam1 = self._get_team_player(player1)
			keyteam2 = self._get_team_player(player2)
			if keyteam1 is False or keyteam2 is False:
				return False
			role1 = self.get_role_player(keyteam1,player1)
			role2 = self.get_role_player(keyteam2,player2)
			if keyteam1 == "bench":
				self._remove_player_in_team(keyteam1,player1)
			if keyteam2 == "bench":
				self._remove_player_in_team(keyteam2,player2)
			self._add_player_in_team(keyteam2,role2,player1)
			self._add_player_in_team(keyteam1,role1,player2)
		return True

	def _get_team_player(self, player: Player):
		if player not in self._players_list:
			return False
		for key_team in self._teams_dict.keys():
			if key_team == "bench":
				for playeri in self._teams_dict["bench"]:
					if player == playeri:
						return key_team
			else:
				for key_role in self._teams_dict[key_team].keys():
					if player == self._teams_dict[key_team][key_role]:
						return key_team

	def _add_player_in_team(self, team_key, role, player:Player):
		if team_key == "bench":
			self._teams_dict[team_key].append(player)
		else:
			team_key = int(team_key)
			self._teams_dict[team_key][role] = player

	def _remove_player_in_team(self, team_key, player:Player):
		if team_key == "bench":
			self._teams_dict[team_key].remove(player)
		else:
			team_key = int(team_key)
			role = self.get_role_player(team_key,player)
			self._teams_dict[team_key].pop(role)

	def get_role_player(self, team_key, player:Player):
		if team_key == "bench":
			return False
		team_key = int(team_key)
		for key_role in self._teams_dict[team_key].keys():
			if player == self._teams_dict[team_key][key_role]:
				return key_role
		





class Scrim_brain():
	def __init__(self):
		self.teams = None
		self.players_list = [] # [Player(), Player(), ...]
		self.players_list_registering = []
		self.state = "WAITING_TO_BEGIN"

	def can_begin_registration(self):
		return self.state == "WAITING_TO_BEGIN"
	def begin_registration(self):
		self.state = "REGISTRATION"
	def can_register(self):
		return self.state == "REGISTRATION"
	def is_registration_over(self):
		return self.state == "TEAM_BUILT"

	def add_player(self, player: Player):
		if player in self.players_list_registering:
			return False
		else:
			self.players_list_registering.append(player)
			return True

	def validate_registration(self, player: Player):
		if player in self.players_list_registering:
			self.players_list_registering.remove(player)
			self.players_list.append(player)
			if self.state == "TEAM_BUILT":
				self.teams.add_late_player(player)

	def remove_player(self, player: Player):
		if player in self.players_list:
			self.players_list.remove(player)
			return True
		else:
			return False

	def build_teams(self):
		self.teams = Teams(self.players_list)
		self.state = "TEAM_BUILT"
		self.players_list_registering = []
	def get_nb_teams(self):
		return self.teams.get_nb_teams()
	def is_bench_team(self):
		return self.teams.is_bench_team()
	def get_bench_team_players(self):
		return self.teams.get_bench_team_players()
	def get_team_players(self, team_id):
		return self.teams.get_team_players(team_id)
	def get_panel_namesanddiscordid_team(self,team_id):
		return self.teams.get_panel_namesanddiscordid_team(team_id)
	def panel_switch2players(self, player1, player2):
		# playeri : Player type or str type, ex :"tank1"
		self.teams.switch_2_players(player1, player2)
	def get_panel_role(self, team_id, player: Player):
		return self.teams.get_role_player(team_id, player)

	def panel_reset_teams(self):
		self.build_teams()

	def panel_remove_player(self, team_id, player):
		self.players_list.remove(player)
		self.teams.panel_remove_player(team_id, player)




