from AGI.struct import AGIObject, AGIList
from AGI.objects import obj


def game_object(chessboard: AGIObject,
                rule: AGIObject,
                winning_criteria: AGIObject) -> AGIObject:
    return AGIObject('tb_game_game', True,
                     {'tb_game_chessboard': chessboard,
                      'tb_game_rule': rule,
                      'tb_game_winning_criteria': winning_criteria})


def xq_chessboard_object(pieces: AGIList, whose_turn: AGIObject) -> AGIObject:
    return AGIObject('xq_chessboard', True,
                     {'xq_pieces': pieces,
                      'xq_whose_turn': whose_turn})


def rule_object(teams: AGIList,
                occupations: AGIList,
                who_is_next_func: AGIObject or None,
                my_team_id: AGIObject) -> AGIObject:
    return AGIObject('tb_game_rule', True,
                     {'tb_game_teams': teams,
                      'tb_game_occupations': occupations,
                      'tb_game_who_is_next_func': who_is_next_func,
                      'tb_game_my_team_id': my_team_id})


def winning_criteria_object(end_game_func: AGIObject or None, end_game_benefits: AGIList):
    return AGIObject('tb_game_winning_criteria', False,
                     {'tb_game_end_game_func': end_game_func,
                      'tb_game_end_game_benefits': end_game_benefits})


def team_object(team_name: str, players: AGIList, end_game_benefit_name: str) -> AGIObject:
    return AGIObject('tb_game_team', False,
                     {'name': obj(team_name),
                      'tb_game_players': players,
                      'tb_game_end_game_benefit_id': obj(end_game_benefit_name)})


def occupation_object(occupation_name: str, operation_func: AGIObject or None) -> AGIObject:
    return AGIObject('tb_game_occupation', False,
                     {'name': obj(occupation_name),
                      'tb_game_operation_func': operation_func})


def end_game_benefit(benefit_name: str, benefit_func: AGIObject or None) -> AGIObject:
    return AGIObject('tb_game_end_game_benefit', False,
                     {'name': obj(benefit_name),
                      'tb_game_benefit_func': benefit_func})


def player_object(player_name: str, occupation_name: str) -> AGIObject:
    return AGIObject('tb_game_player', False,
                     {'name': obj(player_name),
                      'tb_game_occupation_id': obj(occupation_name)})
