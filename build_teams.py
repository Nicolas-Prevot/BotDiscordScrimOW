from typing import TypeVar
import numpy as np
import copy
import matplotlib.pyplot as plt
Player = TypeVar("Player")



def get_team_elo_mean(team_id:int, teams_dict:dict) -> float:
    team_elo = 0
    for role, player in teams_dict[team_id].items():
        team_elo += player.roles.get_elo(role[:-1])
    return team_elo/6



def global_team_elo_mean(teams_dict:dict) -> float:
    team_elo = 0
    is_there_bench = False
    for team_id, team in teams_dict.items():
        if team_id == "bench":
            is_there_bench = True
            continue
        team_elo += get_team_elo_mean(team_id, teams_dict)
    if not is_there_bench: 
        return team_elo/len(teams_dict)
    else:
        return team_elo/(len(teams_dict)-1)



def add_player_to_team(player: Player, 
                       team: dict,
                       target_priority: int = None) -> bool:
    """
    player : Player
    team : dict
    target_priority : int = None
    """
    if target_priority is None:
        if team["tank1"] is None:
            team["tank1"] = player
        elif team["tank2"] is None:
            team["tank2"] = player
        elif team["dps1"] is None:
            team["dps1"] = player
        elif team["dps2"] is None:
            team["dps2"] = player
        elif team["heal1"] is None:
            team["heal1"] = player
        elif team["heal2"] is None:
            team["heal2"] = player
        else:
            return False
        return True

    if ((team["tank1"] is None or team["tank2"] is None) and
        player.roles.get_tank_is_choosen()):
        if player.roles.get_tank_priority() == target_priority:
            if team["tank1"] is None:
                team["tank1"] = player
            else:
                team["tank2"] = player
            return True

    if ((team["dps1"] is None or team["dps2"] is None) and
        player.roles.get_dps_is_choosen()):
        if player.roles.get_dps_priority() == target_priority:
            if team["dps1"] is None:
                team["dps1"] = player
            else:
                team["dps2"] = player
            return True

    if ((team["heal1"] is None or team["heal2"] is None) and
        player.roles.get_heal_is_choosen()):
        if player.roles.get_heal_priority() == target_priority:
            if team["heal1"] is None:
                team["heal1"] = player
            else:
                team["heal2"] = player
            return True
    return False



def get_score_elo_dict(teams_dict:dict) -> dict:
    score_elo_dict = {}
    mean = global_team_elo_mean(teams_dict)
    for team_id, team in teams_dict.items():
        if team_id == "bench":
            continue
        score_elo_dict[team_id] = abs(get_team_elo_mean(team_id,teams_dict)
                                      - mean)/mean
    return score_elo_dict



def get_score_priority_player(player:Player, role:str) -> int:
    priorities = {}
    if player.roles.tank["Is_choosen"]:
        priorities["tank"] = player.roles.tank["priority"]
    if player.roles.dps["Is_choosen"]:
        priorities["dps"] = player.roles.dps["priority"]
    if player.roles.heal["Is_choosen"]:
        priorities["heal"] = player.roles.heal["priority"]
    best_priority = np.min(list(priorities.values()))
    if role not in priorities.keys():
        return 5
    else:
        return priorities[role]-best_priority



def get_score_priority_dict(teams_dict:dict) -> dict:
    score_priority_dict={}
    for team_id, team in teams_dict.items():
        if team_id == "bench":
            continue
        score_priority_dict[team_id] = 0
        for role, player in team.items():
            player_score = get_score_priority_player(player, role[:-1])
            score_priority_dict[team_id] += player_score/(1+player_score)
        score_priority_dict[team_id] = score_priority_dict[team_id]/6
    return score_priority_dict



def get_player_team(teams_dict:dict, player:Player):
    for team_id, team in teams_dict.items():
        if team_id == "bench":
            if player in team:
                return team_id
        elif player in list(team.values()):
            return team_id
    return None



def switch_two_players(teams_dict:dict, player_1:Player, player_2:Player):
    team_player_1 = get_player_team(teams_dict, player_1)
    team_player_2 = get_player_team(teams_dict, player_2)
    for role, player in teams_dict[team_player_1].items():
        if player == player_1:
            if team_player_1 == "bench":
                teams_dict[team_player_1].append(player_2)
                teams_dict[team_player_1].remove(player_1)
            else:
                teams_dict[team_player_1][role] = player_2
    for role, player in teams_dict[team_player_2].items():
        if player == player_2:
            if team_player_2 == "bench":
                teams_dict[team_player_2].append(player_1)
                teams_dict[team_player_2].remove(player_2)
            else:
                teams_dict[team_player_2][role] = player_1



def switch_2_players_custom(teams_dict:dict, potential_player:Player,
                            team_id:int, role:str):
    player = teams_dict[team_id][role]
    teams_dict["bench"].append(player)
    teams_dict[team_id][role] = potential_player



def switch_2_players_custom_2(teams_dict:dict, potential_player:Player,
                              team_id:int, role:str):
    player = teams_dict[team_id][role]
    teams_dict[team_id][role] = potential_player
    return player



def switch_2_players_custom_team(teams_dict:dict, potential_player:Player, 
                                team_id_of_potential_player:int, 
                                role_of_potential_player:str, 
                                team_id:int, role:str, 
                                player:Player = None):
    if team_id != "bench":
        player = teams_dict[team_id][role]
        teams_dict[team_id][role] = potential_player
    else:
        teams_dict["bench"].append(potential_player)
        teams_dict["bench"].remove(player)
    teams_dict[team_id_of_potential_player][role_of_potential_player] = player



def create_global_score(score_elo:float, score_priority:float) -> float:
    return score_elo*0.8 + score_priority



def try_switch_bench(potential_player:Player, team_id:int, role:str,
                     teams_dict:dict, best_position:dict):
    teams_dict = copy.deepcopy(teams_dict)
    switch_2_players_custom(teams_dict, potential_player, team_id, role)

    score_elo_dict = get_score_elo_dict(teams_dict)
    score_priority_dict = get_score_priority_dict(teams_dict)
    score_elo_scrim = np.mean(list(score_elo_dict.values()))
    score_priority_scrim = np.mean(list(score_priority_dict.values()))
    
    if (create_global_score(score_elo_scrim,score_priority_scrim) < 
        create_global_score(best_position["score_elo"],
                            best_position["score_priority"])):
        best_position["score_elo"] = score_elo_scrim
        best_position["score_priority"] = score_priority_scrim
        best_position["team_id"] = team_id
        best_position["role"] = role
    return best_position



def try_switch_team(potential_player:Player, team_id_of_potential_player:int,
                    role_of_potential_player:str, team_id:int, role:str, 
                    teams_dict:dict, best_position:dict,
                    player:Player = None) -> dict:
    teams_dict = copy.deepcopy(teams_dict)
    
    switch_2_players_custom_team(teams_dict, potential_player,
                                 team_id_of_potential_player,
                                 role_of_potential_player,
                                 team_id, role, player)

    score_elo_dict = get_score_elo_dict(teams_dict)
    score_priority_dict = get_score_priority_dict(teams_dict)
    score_elo_scrim = np.mean(list(score_elo_dict.values()))
    score_priority_scrim = np.mean(list(score_priority_dict.values()))
    
    if (create_global_score(score_elo_scrim,score_priority_scrim) <
        create_global_score(best_position["score_elo"],
                            best_position["score_priority"])):
        best_position["score_elo"] = score_elo_scrim
        best_position["score_priority"] = score_priority_scrim
        best_position["team_id"] = team_id
        best_position["role"] = role
        best_position["player_bench"] = player
        
    return best_position



def bench_rotation(teams_dict:dict, nb_teams:int, 
                   score_elo_scrim_history:list,
                   score_priority_scrim_history:list,
                   score_elo_scrim:float,
                   score_priority_scrim:float):
    nb_iteration_max_bench = 20
    bench_temp=[]
    for i in range(nb_iteration_max_bench):
        if teams_dict["bench"] == []:
            teams_dict["bench"] = bench_temp.copy()
            bench_temp = []

        potential_player = teams_dict["bench"].pop()
        best_position = {"score_elo":1,
                        "score_priority":1,
                        "team_id":None,
                        "role":None}
        for team_id in range(nb_teams):
            if potential_player.roles.tank["Is_choosen"]:
                best_position = try_switch_bench(potential_player,team_id,
                                                 role="tank1",
                                                 teams_dict=teams_dict,
                                                 best_position=best_position)
                best_position = try_switch_bench(potential_player,team_id,
                                                 role="tank2",
                                                 teams_dict=teams_dict,
                                                 best_position=best_position)
            if potential_player.roles.dps["Is_choosen"]:
                best_position = try_switch_bench(potential_player,team_id,
                                                 role="dps1",
                                                 teams_dict=teams_dict,
                                                 best_position=best_position)
                best_position = try_switch_bench(potential_player,team_id,
                                                 role="dps2",
                                                 teams_dict=teams_dict,
                                                 best_position=best_position)
            if potential_player.roles.heal["Is_choosen"]:
                best_position = try_switch_bench(potential_player,team_id,
                                                 role="heal1",
                                                 teams_dict=teams_dict,
                                                 best_position=best_position)
                best_position = try_switch_bench(potential_player,team_id,
                                                 role="heal2",
                                                 teams_dict=teams_dict,
                                                 best_position=best_position)
        
        if (create_global_score(score_elo_scrim,score_priority_scrim) >
            create_global_score(best_position["score_elo"],
                                best_position["score_priority"])):
            if best_position["team_id"] is None:
                bench_temp.append(potential_player)
            else:
                old_player = switch_2_players_custom_2(
                                teams_dict, potential_player,
                                best_position["team_id"],
                                best_position["role"])
                bench_temp.append(old_player)
                score_elo_scrim = best_position["score_elo"]
                score_priority_scrim = best_position["score_priority"]
        else:
            bench_temp.append(potential_player)

        score_elo_scrim_history.append(score_elo_scrim)
        score_priority_scrim_history.append(score_priority_scrim)

    for player in bench_temp:
        teams_dict["bench"].append(player)

    return score_elo_scrim, score_priority_scrim
    


def team_rotation(teams_dict:dict, team_id_potentiel:int, nb_teams:int,
                  score_elo_scrim_history:list,
                  score_priority_scrim_history:list,
                  score_elo_scrim, score_priority_scrim):
                  
    nb_iteration_max_team = 20
    
    for i in range(nb_iteration_max_team):
        id_player=i%6

        role_potentiel = list(teams_dict[team_id_potentiel])[id_player]
        potential_player = teams_dict[team_id_potentiel][role_potentiel]
        best_position = {"score_elo":1,
                         "score_priority":1,
                         "team_id":None,
                         "role":None,
                         "player_bench":None}
        for team_id in range(nb_teams):
            if potential_player.roles.tank["Is_choosen"]:
                best_position = try_switch_team(potential_player,
                                                team_id_potentiel,
                                                role_potentiel,
                                                team_id,
                                                role="tank1",
                                                teams_dict=teams_dict,
                                                best_position=best_position)
                best_position = try_switch_team(potential_player,
                                                team_id_potentiel,
                                                role_potentiel,
                                                team_id,
                                                role="tank2",
                                                teams_dict=teams_dict,
                                                best_position=best_position)
            if potential_player.roles.dps["Is_choosen"]:
                best_position = try_switch_team(potential_player,
                                                team_id_potentiel,
                                                role_potentiel,
                                                team_id,
                                                role="dps1",
                                                teams_dict=teams_dict,
                                                best_position=best_position)
                best_position = try_switch_team(potential_player,
                                                team_id_potentiel,
                                                role_potentiel,
                                                team_id,
                                                role="dps2",
                                                teams_dict=teams_dict,
                                                best_position=best_position)
            if potential_player.roles.heal["Is_choosen"]:
                best_position = try_switch_team(potential_player,
                                                team_id_potentiel,
                                                role_potentiel,
                                                team_id,
                                                role="heal1",
                                                teams_dict=teams_dict,
                                                best_position=best_position)
                best_position = try_switch_team(potential_player,
                                                team_id_potentiel,
                                                role_potentiel,
                                                team_id,
                                                role="heal2",
                                                teams_dict=teams_dict,
                                                best_position=best_position)
        
        for player in teams_dict["bench"]:
             best_position = try_switch_team(potential_player,
                                             team_id_potentiel,
                                             role_potentiel,
                                             "bench",
                                             role=None,
                                             teams_dict=teams_dict,
                                             best_position=best_position,
                                             player=player)

        if (create_global_score(score_elo_scrim,score_priority_scrim) >
            create_global_score(best_position["score_elo"],
                                best_position["score_priority"])):
            if best_position["team_id"] is not None:
                switch_2_players_custom_team(teams_dict, potential_player,
                                             team_id_potentiel,
                                             role_potentiel,
                                             best_position["team_id"],
                                             best_position["role"],
                                             best_position["player_bench"])
                score_elo_scrim = best_position["score_elo"]
                score_priority_scrim = best_position["score_priority"]

        score_elo_scrim_history.append(score_elo_scrim)
        score_priority_scrim_history.append(score_priority_scrim)

    return score_elo_scrim, score_priority_scrim

def build_team_main_1(player_list: list[Player]):
    """
    player_list : list[Player]
    """
    nb_teams = len(player_list)//6
    player_pool = []
    teams_dict = {}

    ############################## Initialization ############################
    for k in range(nb_teams):
        teams_dict[k] = {"tank1": None, "tank2": None, "dps1": None,
                         "dps2": None, "heal1": None, "heal2": None}
    for player in player_list:
        i = 0
        while(add_player_to_team(player, teams_dict[i], 1) == False):
            i += 1
            if i == nb_teams:
                player_pool.append(player)
                break
    for priority in range(2, 4):
        players_to_remove = []
        for player in player_pool:
            i = 0
            ok = True
            while (add_player_to_team(player, teams_dict[i], priority) ==
                  False):
                i += 1
                if i == nb_teams:
                    ok = False
                    break
            if ok:
                players_to_remove.append(player)
        for player in players_to_remove:
            player_pool.remove(player)

    players_to_remove = []
    for player in player_pool:
        i = 0
        ok = True
        while(add_player_to_team(player, teams_dict[i]) == False):
            i += 1
            if i == nb_teams:
                ok = False
                break
        if ok:
            players_to_remove.append(player)
    for player in players_to_remove:
        player_pool.remove(player)

    teams_dict["bench"] = player_pool

    print(teams_dict)
    ############################## End Initialization ########################
    
    
    
    score_elo_dict = {}
    score_priority_dict = {}
    score_elo_scrim = 1
    score_priority_scrim = 1
    score_elo_scrim_history = []
    score_priority_scrim_history = []
    
    score_elo_dict = get_score_elo_dict(teams_dict)
    score_priority_dict = get_score_priority_dict(teams_dict)
    score_elo_scrim = np.mean(list(score_elo_dict.values()))
    score_priority_scrim = np.mean(list(score_priority_dict.values()))

    score_elo_scrim_history.append(score_elo_scrim)
    score_priority_scrim_history.append(score_priority_scrim)

    ############################# rotation ###################################
    if (nb_teams >= 2):
        nb_rotation = len(teams_dict)*5
        for i in range(nb_rotation):

            team_id = list(teams_dict.keys())[i%len(teams_dict)]

            if team_id == "bench":
                if teams_dict["bench"] == []:
                    continue
                print("doing bench rotations")
                score_elo_scrim, score_priority_scrim = bench_rotation(
                        teams_dict, nb_teams, score_elo_scrim_history, 
                        score_priority_scrim_history, score_elo_scrim, 
                        score_priority_scrim)
            else:
                print(f"doing team {team_id} rotation")
                score_elo_scrim, score_priority_scrim = team_rotation(
                        teams_dict, team_id, nb_teams,
                        score_elo_scrim_history, score_priority_scrim_history,
                        score_elo_scrim, score_priority_scrim)

    ############################ End rotation ################################
    print(score_elo_scrim)
    print(score_priority_scrim)
    """plt.plot(score_elo_scrim_history[:], label="elo_score")
    plt.plot(score_priority_scrim_history[:], label="priority_score")
    plt.legend()
    plt.show()"""


    return teams_dict