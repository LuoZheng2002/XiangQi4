from Exception.dynamic_code_exception import DynamicCodeException, show_dynamic_code_exception
from XiangQi.instance import create_xq_game
from XiangQi.chessboard_browser import print_chessboard
from AGI.code_driver import run_dynamic_function
from AGI.struct import AGIObject, AGIList
from SystemConcept.common_concepts import tag_obj, to_int
from AGI.translate_struct import print_obj
from dynamic_code_manager import DynamicCodeDatabase
from Library.library import Library
lib = Library('Library')
try:
    xq_game = create_xq_game(lib)
    current_chessboard = xq_game.attributes['tb_game_chessboard']
    while True:
        print('Now chessboard is:')
        print_chessboard(current_chessboard)
        whose_turn = run_dynamic_function('func_who_is_next_func',
                                          AGIList(True, [current_chessboard]), lib, True)
        if whose_turn.concept_name == 'xq_red_team':
            print('Now it\'s red team\'s turn to go!')
        elif whose_turn.concept_name == 'xq_black_team':
            print('Now it\'s black team\'s turn to go!')
        current_chessboard = run_dynamic_function('func_operation_func',
                                                  AGIList(True, [current_chessboard, whose_turn]), lib, True)
        end_game = run_dynamic_function('func_end_game_func', AGIList(True, [current_chessboard]), lib, True)
        if end_game.concept_name == 'sys_True':
            print_chessboard(current_chessboard)
            print('Game ended!')
            red_benefit = run_dynamic_function('func_end_game_benefit',
                                               AGIList(True, [current_chessboard, tag_obj('xq_red_team')]), lib, True)
            black_benefit = run_dynamic_function('func_end_game_benefit',
                                                 AGIList(True, [current_chessboard, tag_obj('xq_black_team')]), lib, True)
            print('Red team\'s benefit is:')
            print(to_int(red_benefit))
            print('Black team\'s benefit is:')
            print(to_int(black_benefit))
            break
except DynamicCodeException as d:
    show_dynamic_code_exception(d, 'Library/Functions')
