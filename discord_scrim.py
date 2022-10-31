import numpy as np
from scrim import *



class Discord_scrim():
	def __init__(self):
		self.scrim_brain = Scrim_brain()
		self.create_fresh_panel()


	def create_fresh_panel(self):
		self.panel_memory = {
		"removeplayer": {"team":None,"discord_id":None},
		"switch2player":{"team1":None,"discord_id1":None,
						 "team2":None,"discord_id2":None}
		}


	def can_register(self):
		return self.scrim_brain.can_register()


	def is_registered(self,discord_id):
		for player in self.scrim_brain.players_list:
			if player.discord_id == str(discord_id):
				return True
		return False


	def get_player_from_discord_id(self, discord_id):
		for player in self.scrim_brain.players_list:
			if player.discord_id == str(discord_id):
				return player
		for player in self.scrim_brain.players_list_registering:
			if player.discord_id == str(discord_id):
				return player
		return False


	###################### REGISTER FUNCTIONS ################################

	def can_begin_registration(self):
		return self.scrim_brain.can_begin_registration()

	def begin_registration(self):
		self.scrim_brain.begin_registration()


	def add_register_player(self, discord_id, is_tank: bool,
							is_dps: bool, is_heal: bool):
		player = self.get_player_from_discord_id(discord_id)
		if player is False: # This discord_id is not registered
			roles = Roles()
			roles.set_Is_choosen_info(is_tank, is_dps, is_heal)

			if isinstance(discord_id,str): # for bot creation
				name = discord_id.split("#")[0]
			else:
				name = discord_id.nick
				if name is None:
					name = discord_id.name
			# check if this name is used be someone else
			if self._is_name_taken(name):
				name = str(discord_id)

			player = Player(name, str(discord_id), roles)
			self.scrim_brain.add_player(player)
		else: # This discord_id is in registeration
			player.roles.set_Is_choosen_info(is_tank,is_dps,is_heal)
		return player



	def validate_registration(self,discord_id):
		player = self.get_player_from_discord_id(discord_id)
		self.scrim_brain.validate_registration(player)


	def _is_name_taken(self,name):
		for player in self.scrim_brain.players_list:
			if player.name == name:
				player.name = player.discord_id
				return True
		return False


	def remove_register_player(self,discord_id):
		player = self.get_player_from_discord_id(discord_id)
		self.scrim_brain.remove_player(player)


	def set_priority_register(self,discord_id,role_concerned,priority):
		player = self.get_player_from_discord_id(discord_id)
		if role_concerned == "tank":
			player.roles.set_tank_priority(priority)
		elif role_concerned == "dps":
			player.roles.set_dps_priority(priority)
		elif role_concerned == "heal":
			player.roles.set_heal_priority(priority)


	def set_elo_register(self,discord_id,role_concerned,elo):
		player = self.get_player_from_discord_id(discord_id)
		if role_concerned == "tank":
			player.roles.set_tank_elo(elo)
		elif role_concerned == "dps":
			player.roles.set_dps_elo(elo)
		elif role_concerned == "heal":
			player.roles.set_heal_elo(elo)


	def get_is_choosen(self,discord_id,role_concerned):
		player = self.get_player_from_discord_id(discord_id)
		if not player:
			return False
		if role_concerned == "tank":
			return player.roles.get_tank_is_choosen()
		elif role_concerned == "dps":
			return player.roles.get_dps_is_choosen()
		elif role_concerned == "heal":
			return player.roles.get_heal_is_choosen()


	def get_list_player(self):
		return self.scrim_brain.players_list

	def get_sum_up_player(self,discord_id):
		player = self.get_player_from_discord_id(discord_id)
		return player.roles.get_all()

	def get_sum_up_player2(self,player):
		return player.roles.get_all()

	def get_nb_players_roles(self):
		nb_register = len(self.scrim_brain.players_list)
		nb_tank = 0
		nb_dps  = 0
		nb_heal = 0
		for player in self.scrim_brain.players_list:
			is_tank,_,_,is_dps,_,_,is_heal,_,_ = self.get_sum_up_player(
					player.discord_id)
			if is_tank:
				nb_tank += 1
			if is_dps:
				nb_dps += 1
			if is_heal:
				nb_heal += 1
		return nb_register,nb_tank,nb_dps,nb_heal


	######################### START SCRIM FUNCTIONS ##########################


	def start_scrim(self):
		######################################################################
		#self._temp_add_bots(nb=12)################ Testing only ##############
		######################################################################
		self.scrim_brain.build_teams()

	def _temp_add_bots(self,nb):		
		names = ["Adams","Baker","Clark","Davis","Evans","Frank","Ghosh",
				 "Hills","Irwin","Jones","Klein","Lopez","Mason","Nalty",
				 "Ochoa","Patel","Quinn","Reily","Smith","Trott","Usman",
				 "Valdo","White","Xiang","Yakub","Zafar"]
		if len(names)<nb:
			nb = len(names)
		role_priority_matrix = np.random.randint(3,size=(nb,3))+1
		role_elo_matrix = np.random.randint(7,size=(nb,3))
		role_bool_matrix = np.random.choice([True,False],size=(nb,3))
		np.random.shuffle(names)
		for i, name in enumerate(names[:nb]):
			discord_id = name+"#"+str(i)
			if np.sum(role_bool_matrix[i]) == 0:
				role_bool_matrix[i,np.random.randint(3)] = True
			player = self.add_register_player(discord_id,
											  role_bool_matrix[i,0],
											  role_bool_matrix[i,1],
											  role_bool_matrix[i,2])

			player.roles.set_tank_priority(role_priority_matrix[i,0])
			player.roles.set_dps_priority(role_priority_matrix[i,1])
			player.roles.set_heal_priority(role_priority_matrix[i,2])

			player.roles.set_tank_elo(role_elo_matrix[i,0])
			player.roles.set_dps_elo(role_elo_matrix[i,1])
			player.roles.set_heal_elo(role_elo_matrix[i,2])
			
			self.validate_registration(discord_id)

	def get_nb_teams(self):
		return self.scrim_brain.get_nb_teams()

	def is_bench_team(self):
		return self.scrim_brain.is_bench_team()

	def get_bench_players_info(self):
		list_players_info = []
		list_player_bench = self.scrim_brain.get_bench_team_players()
		for player in list_player_bench:
			player_info = {"name":player.name,
						   "info":(self.get_sum_up_player(player.discord_id))}
			list_players_info.append(player_info)
		return list_players_info

	def get_team_players_info(self, team_id):
		list_players_info = []
		dict_player_team = self.scrim_brain.get_team_players(team_id)
		for key_role in dict_player_team.keys():
			player = dict_player_team[key_role]
			player_info = {"name":player.name,
						   "role":key_role,
						   "info":(self.get_sum_up_player(player.discord_id))}
			list_players_info.append(player_info)
		return list_players_info


	####################### PANEL FUNCTIONS ##################################


	def is_registration_over(self):
		return self.scrim_brain.is_registration_over()


	def set_panel_info(self,info1,info2,info3):
		self.panel_memory[info1][info2] = info3

	def get_panel_info(self,info1,info2):
		return self.panel_memory[info1][info2]


	def get_panel_namesanddiscordid_team(self,team_id):
		return self.scrim_brain.get_panel_namesanddiscordid_team(team_id)


	def get_panel_namesanddiscordidrole_team(self,team_id):
		dict_players_id = self.scrim_brain.get_panel_namesanddiscordid_team(
			team_id)
		if team_id == "bench":
			return dict_players_id
		roles = ["tank","dps1","dps2","heal1","heal2"]
		dict_emoji_role = {"tank":"🛡️","dps":"⚔️","heal":"❤️"}
		roles_selected = []
		for discord_id in dict_players_id.keys():
			player = self.get_player_from_discord_id(discord_id)
			role = self.scrim_brain.get_panel_role(team_id,player)
			roles_selected.append(role)
		for role in roles:
			if role not in roles_selected:
				dict_players_id[role] = f"{dict_emoji_role[role[:-1]]} "\
										f"{role[-1]} leaver"
		return dict_players_id

	def panel_removeplayer(self):
		team_id = self.panel_memory["removeplayer"]["team"]
		discord_id = self.panel_memory["removeplayer"]["discord_id"]
		player = self.get_player_from_discord_id(discord_id)
		self.scrim_brain.panel_remove_player(team_id,player)
		self.create_fresh_panel()

	def panel_switch2player(self):
		roles = ["tank","dps1","dps2","heal1","heal2"]
		team1_id = self.panel_memory["switch2player"]["team1"]
		discord_id1 = self.panel_memory["switch2player"]["discord_id1"]
		if discord_id1 in roles:
			player1 = {"team_id":team1_id,"role":discord_id1}
		else:
			player1 = self.get_player_from_discord_id(discord_id1)
		team2_id = self.panel_memory["switch2player"]["team2"]
		discord_id2 = self.panel_memory["switch2player"]["discord_id2"]
		if discord_id2 in roles:
			player2 = {"team_id":team2_id,"role":discord_id2}
		else:
			player2 = self.get_player_from_discord_id(discord_id2)
		self.scrim_brain.panel_switch2players(player1,player2)
		self.create_fresh_panel()

	def panel_reset_teams(self):
		self.scrim_brain.panel_reset_teams()

