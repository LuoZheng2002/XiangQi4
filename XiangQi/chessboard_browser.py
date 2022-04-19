from AGI.struct import AGIObject, AGIList
from SystemConcept.common_concepts import to_int


def print_chessboard(xq_chessboard: AGIObject):
    chessboard = [[None for i in range(9)] for i in range(10)]
    for i in xq_chessboard.attributes['xq_pieces'].value:
        name = i.attributes['xq_piece_name'].concept_name[3:]
        if i.attributes['xq_piece_owner'].concept_name == 'xq_red_team':
            name = name.upper()
        else:
            name = name.lower()
        position = [None, None]
        position[0] = to_int(i.attributes['xq_position'].agi_list().get_element(0))
        position[1] = to_int(i.attributes['xq_position'].agi_list().get_element(1))
        if chessboard[position[1]][position[0]] is not None:
            assert False
        chessboard[position[1]][position[0]] = name
    print('#################################################################################')
    print('####### 0 ##### 1 ##### 2 ##### 3 ##### 4 ##### 5 ##### 6 ##### 7 ##### 8 #######')

    for k, j in enumerate(chessboard):
        print(str(k).rjust(4, '#') + ' ', end='')
        for i in j:
            if i is None:
                print('[     ] ', end='')
            else:
                if len(i) <= 3:
                    i = ' ' + i
                print('[' + i.ljust(5, ' ') + '] ', end='')
        print('####')
    print('#################################################################################')