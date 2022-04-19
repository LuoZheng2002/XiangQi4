from SystemConcept.common_concepts import int_obj, tag_obj
from Game.structures import *


def vector_object(numbers):
    value = list()
    for number in numbers:
        value.append(int_obj(number))
    return AGIObject('vector', True,
                     {'content': AGIList(True, value)})


def piece_object(owner: str, name: str, position: list) -> AGIObject:
    return AGIObject('xq_piece', True,
                     {'xq_piece_owner': tag_obj(owner),
                      'xq_piece_name': tag_obj(name),
                      'xq_position': vector_object(position)})


def create_xq_chessboard():
    pieces_list = [
        piece_object('xq_red_team', 'xq_Che', [0, 0]),
        piece_object('xq_red_team', 'xq_Ma', [1, 0]),
        piece_object('xq_red_team', 'xq_Xiang', [2, 0]),
        piece_object('xq_red_team', 'xq_Shi', [3, 0]),
        piece_object('xq_red_team', 'xq_Jiang', [4, 0]),
        piece_object('xq_red_team', 'xq_Shi', [5, 0]),
        piece_object('xq_red_team', 'xq_Xiang', [6, 0]),
        piece_object('xq_red_team', 'xq_Ma', [7, 0]),
        piece_object('xq_red_team', 'xq_Che', [8, 0]),
        piece_object('xq_red_team', 'xq_Pao', [1, 2]),
        piece_object('xq_red_team', 'xq_Pao', [7, 2]),
        piece_object('xq_red_team', 'xq_Bing', [0, 3]),
        piece_object('xq_red_team', 'xq_Bing', [2, 3]),
        piece_object('xq_red_team', 'xq_Bing', [4, 3]),
        piece_object('xq_red_team', 'xq_Bing', [6, 3]),
        piece_object('xq_red_team', 'xq_Bing', [8, 3]),
        piece_object('xq_black_team', 'xq_Che', [0, 9]),
        piece_object('xq_black_team', 'xq_Ma', [1, 9]),
        piece_object('xq_black_team', 'xq_Xiang', [2, 9]),
        piece_object('xq_black_team', 'xq_Shi', [3, 9]),
        piece_object('xq_black_team', 'xq_Jiang', [4, 9]),
        piece_object('xq_black_team', 'xq_Shi', [5, 9]),
        piece_object('xq_black_team', 'xq_Xiang', [6, 9]),
        piece_object('xq_black_team', 'xq_Ma', [7, 9]),
        piece_object('xq_black_team', 'xq_Che', [8, 9]),
        piece_object('xq_black_team', 'xq_Pao', [1, 7]),
        piece_object('xq_black_team', 'xq_Pao', [7, 7]),
        piece_object('xq_black_team', 'xq_Bing', [0, 6]),
        piece_object('xq_black_team', 'xq_Bing', [2, 6]),
        piece_object('xq_black_team', 'xq_Bing', [4, 6]),
        piece_object('xq_black_team', 'xq_Bing', [6, 6]),
        piece_object('xq_black_team', 'xq_Bing', [8, 6]),
    ]
    pieces = AGIList(True, pieces_list)
    whose_turn = tag_obj('xq_red_team')
    xq_chessboard = xq_chessboard_object(pieces, whose_turn)
    return xq_chessboard


def create_xq_teams():
    teams = [
        team_object('xq_red_team',
                    AGIList(True, [player_object('xq_red_player', 'xq_player_occupation')]),
                    'xq_player_benefit'),
        team_object('xq_black_team',
                    AGIList(True, [player_object('xq_black_player', 'xq_player_occupation')]),
                    'xq_player_benefit')
    ]
    return teams


def create_xq_game(lib):
    operation_func = lib.get_code('func_operation_func')
    occupations = [occupation_object('xq_player_occupation', operation_func)]
    who_is_next_func = lib.get_code('func_who_is_next_func')
    rule = rule_object(AGIList(False, create_xq_teams()), AGIList(False, occupations),
                       who_is_next_func, tag_obj('xq_red_team'))
    end_game_func = lib.get_code('func_end_game_func')
    benefit_func = lib.get_code('func_end_game_benefit')
    end_game_benefits = [end_game_benefit('xq_player_benefit', benefit_func)]
    winning_criteria = winning_criteria_object(end_game_func, AGIList(False, end_game_benefits))
    elephant_chess = game_object(create_xq_chessboard(), rule, winning_criteria)
    return elephant_chess
