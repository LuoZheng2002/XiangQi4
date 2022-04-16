import pickle
from LibraryDriver.struct import Function

from AGI.struct import AGIObject, AGIList
from Exception.agi_exception import AGIException
from SystemConcept.common_concepts import int_obj
import pickle

number_to_letter = {0: 'i', 1: 'j', 2: 'k', 3: 'l', 4: 'm', 5: 'n', 6: 'o', 7: 'p', 8: 'q', 9: 'r',
                    10: 's', 11: 't', 12: 'u', 13: 'v', 14: 'w', 15: 'x', 16: 'y', 17: 'z'}
letter_to_number = dict([(i, j) for (j, i) in number_to_letter.items()])


class Line:
    def __init__(self, line_str, indentation_count, original_line):
        self.line_str = line_str
        self.indentation_count = indentation_count
        self.original_line = original_line


def slice_code(str_code: str) -> list:
    result = list()
    print('Slicing code!')
    if str_code and str_code[0] == '\n':
        str_code = str_code[1:]
    while str_code.find('\\\n') != -1:
        backslash_pos = str_code.find('\\\n')
        str_code = str_code[:backslash_pos] + str_code[backslash_pos + 2:]
    while str_code.find('\n') != -1:
        return_pos = str_code.find('\n')
        line_str_code = str_code[: return_pos]
        if line_str_code == '':
            print('Warning: an empty line.')
        else:
            while line_str_code[-1] == ' ':
                line_str_code = line_str_code[:-1]
            print(line_str_code)
            indentation_count = 0
            original_line = line_str_code
            while line_str_code.find('    ') == 0:
                line_str_code = line_str_code[4:]
                indentation_count += 1
            result.append(Line(line_str_code, indentation_count, original_line))
        str_code = str_code[return_pos + 1:]
    if str_code != '':
        print(str_code)
        indentation_count = 0
        original_line = str_code
        while str_code.find('    ') == 0:
            str_code = str_code[4:]
            indentation_count += 1
        result.append(Line(str_code, indentation_count, original_line))
    print('')
    return result


def slice_line(line: str) -> list:
    result = list()
    in_quotation = False
    while True:
        pos = 1000
        keywords = ['.', ',', '(', ')', '&', '<', '>', '{', '}', ' ', '\'', '=', '+', '-', ':', '!', '[', ']']
        for i in keywords:
            temp_pos = line.find(i)
            if temp_pos != -1 and temp_pos < pos:
                if in_quotation:
                    if line[temp_pos] == "'":
                        pos = temp_pos
                else:
                    pos = temp_pos
        if pos != 1000:
            temp_str = line[: pos]
            if temp_str != '':
                result.append(temp_str)
            if line[pos] == ' ':
                line = line[pos + 1:]
            elif line[pos] == '=':
                if len(line) > pos + 1 and line[pos + 1] == '=':
                    if len(line) > pos + 2 and line[pos + 2] == '=':
                        line = line[pos + 3:]
                        result.append('===')
                    else:
                        line = line[pos + 2:]
                        result.append('==')
                elif len(line) > pos + 1 and line[pos + 1] == '!':
                    assert line[pos + 2] == '='
                    line = line[pos + 3:]
                    result.append('=!=')
                else:
                    line = line[pos + 1:]
                    result.append('=')
            elif line[pos] == '!':
                assert line[pos + 1] == '='
                line = line[pos + 2:]
                result.append('!=')
            elif line[pos] == '>':
                if len(line) > pos + 1 and line[pos + 1] == '=':
                    line = line[pos + 2:]
                    result.append('>=')
                else:
                    line = line[pos + 1:]
                    result.append('>')
            elif line[pos] == '<':
                if len(line) > pos + 1 and line[pos + 1] == '=':
                    line = line[pos + 2:]
                    result.append('<=')
                else:
                    line = line[pos + 1:]
                    result.append('<')
            elif line[pos] == '&':
                assert line[pos + 1] == '='
                line = line[pos + 2:]
                result.append('&=')
            elif line[pos] == "'":
                in_quotation = not in_quotation
                line = line[pos + 1:]
                result.append("'")
            elif line[pos] == '-':
                negative_dict = ['(', '[', '{', ',', '=', '&=', '==', '!=', '===', '=!=',
                                 '>', '<', '>=', '<=']
                if not result or result[-1] in negative_dict:
                    line = line[pos + 1:]
                    result.append('--')
                else:
                    line = line[pos + 1:]
                    result.append('-')
            else:
                temp_str2 = line[pos]
                line = line[pos + 1:]
                result.append(temp_str2)
        else:
            break
    if line != '':
        result.append(line)
    return result


def find_close_bracket(line_pieces: list, bracket_type: str, open_bracket_pos: int):
    scope = 0
    bracket_dict = {'(': ')', '[': ']', '{': '}'}
    assert bracket_type in bracket_dict.keys()
    for i in range(open_bracket_pos + 1, len(line_pieces)):
        if line_pieces[i] == bracket_dict[bracket_type]:
            if scope == 0:
                return i
            else:
                scope -= 1
        elif line_pieces[i] == bracket_type:
            scope += 1
    return -1


def find_naked_symbol(line_pieces: list, symbol: str, start_pos: int = None, end_pos: int = None) -> list:
    result = list()
    if start_pos is None:
        start_pos = 0
    if end_pos is None:
        end_pos = len(line_pieces)
    if end_pos < 0:
        end_pos += len(line_pieces)
    scope = {'(': 0, '[': 0, '{': 0}
    for i in range(start_pos, end_pos):
        if line_pieces[i] == '(' and symbol != '(':
            scope['('] += 1
        elif line_pieces[i] == ')' and symbol != '(':
            if scope['('] == 0:
                raise AGIException('Wrong bracket match.')
            scope['('] -= 1
        elif line_pieces[i] == '[' and symbol != '[':
            scope['['] += 1
        elif line_pieces[i] == ']' and symbol != '[':
            if scope['['] == 0:
                raise AGIException('Wrong bracket match.')
            scope['['] -= 1
        elif line_pieces[i] == '{' and symbol != '{':
            scope['{'] += 1
        elif line_pieces[i] == '}' and symbol != '}':
            if scope['{'] == 0:
                raise AGIException('Wrong bracket match.')
            scope['{'] -= 1
        elif line_pieces[i] == symbol and scope['('] == 0 and scope['['] == 0 and scope['{'] == 0:
            result.append(i)
    return result


def generate_expression(expr: list) -> AGIObject:
    if 'and' in expr and find_naked_symbol(expr, 'and'):
        and_poses = find_naked_symbol(expr, 'and')
        if find_naked_symbol(expr, 'or'):
            raise AGIException('Can not put "and" and "or" in the same scope.')
        params = list()
        params.append(generate_expression(expr[:and_poses[0]]))
        for i in range(len(and_poses) - 1):
            params.append(generate_expression(expr[and_poses[i] + 1: and_poses[i + 1]]))
        params.append(generate_expression(expr[and_poses[-1] + 1:]))
        return AGIObject('sys_and', False,
                         {'sys_params': AGIList(False, params)})
    if 'or' in expr and find_naked_symbol(expr, 'or'):
        or_poses = find_naked_symbol(expr, 'or')
        if find_naked_symbol(expr, 'and'):
            raise AGIException('Can not put "and" and "or" in the same scope.')
        params = list()
        params.append(generate_expression(expr[:or_poses[0]]))
        for i in range(len(or_poses) - 1):
            params.append(generate_expression(expr[or_poses[i] + 1: or_poses[i + 1]]))
        params.append(generate_expression(expr[or_poses[-1] + 1:]))
        return AGIObject('sys_or', False,
                         {'sys_params': AGIList(False, params)})
    if '==' in expr and find_naked_symbol(expr, '=='):
        equal_poses = find_naked_symbol(expr, '==')
        if find_naked_symbol(expr, '!='):
            raise AGIException('"==" and "!=" can not be in the same scope.')
        params = list()
        params.append(generate_expression(expr[:equal_poses[0]]))
        for i in range(len(equal_poses) - 1):
            params.append(generate_expression(expr[equal_poses[i] + 1:equal_poses[i + 1]]))
        params.append(generate_expression(expr[equal_poses[-1] + 1:]))
        return AGIObject('sys_same_concept', False,
                         {'sys_params': AGIList(False, params)})
    if '!=' in expr and find_naked_symbol(expr, '!='):
        unequal_poses = find_naked_symbol(expr, '!=')
        if find_naked_symbol(expr, '=='):
            raise AGIException('"==" and "!=" can not be in the same scope.')
        # 暂时只接受两个参数
        assert len(unequal_poses) == 1
        params = list()
        params.append(generate_expression(expr[:unequal_poses[0]]))
        for i in range(len(unequal_poses) - 1):
            params.append(generate_expression(expr[unequal_poses[i] + 1:unequal_poses[i + 1]]))
        params.append(generate_expression(expr[unequal_poses[-1] + 1:]))
        return AGIObject('sys_not_same_concept', False,
                         {'sys_params': AGIList(False, params)})
    if '===' in expr and find_naked_symbol(expr, '==='):
        equal_poses = find_naked_symbol(expr, '===')
        params = list()
        params.append(generate_expression(expr[:equal_poses[0]]))
        for i in range(len(equal_poses) - 1):
            params.append(generate_expression(expr[equal_poses[i] + 1:equal_poses[i + 1]]))
        params.append(generate_expression(expr[equal_poses[-1] + 1:]))
        return AGIObject('sys_math_equal', False,
                         {'sys_params': AGIList(False, params)})
    if '=!=' in expr and find_naked_symbol(expr, '=!='):
        unequal_poses = find_naked_symbol(expr, '=!=')
        # 暂时只接受两个参数
        assert len(unequal_poses) == 1
        params = list()
        params.append(generate_expression(expr[:unequal_poses[0]]))
        for i in range(len(unequal_poses) - 1):
            params.append(generate_expression(expr[unequal_poses[i] + 1:unequal_poses[i + 1]]))
        params.append(generate_expression(expr[unequal_poses[-1] + 1:]))
        return AGIObject('sys_not_math_equal', False,
                         {'sys_params': AGIList(False, params)})
    if '>' in expr and find_naked_symbol(expr, '>'):
        greater_poses = find_naked_symbol(expr, '>')
        # 暂时只接受两个参数
        assert len(greater_poses) == 1
        params = list()
        params.append(generate_expression(expr[:greater_poses[0]]))
        for i in range(len(greater_poses) - 1):
            params.append(generate_expression(expr[greater_poses[i] + 1:greater_poses[i + 1]]))
        params.append(generate_expression(expr[greater_poses[-1] + 1:]))
        return AGIObject('sys_greater_than', False,
                         {'sys_params': AGIList(False, params)})
    if '>=' in expr and find_naked_symbol(expr, '>='):
        greater_equal_poses = find_naked_symbol(expr, '>=')
        # 暂时只接受两个参数
        assert len(greater_equal_poses) == 1
        params = list()
        params.append(generate_expression(expr[:greater_equal_poses[0]]))
        for i in range(len(greater_equal_poses) - 1):
            params.append(generate_expression(expr[greater_equal_poses[i] + 1:greater_equal_poses[i + 1]]))
        params.append(generate_expression(expr[greater_equal_poses[-1] + 1:]))
        return AGIObject('sys_greater_than_or_equal_to', False,
                         {'sys_params': AGIList(False, params)})
    if '<' in expr and find_naked_symbol(expr, '<'):
        less_poses = find_naked_symbol(expr, '<')
        # 暂时只接受两个参数
        assert len(less_poses) == 1
        params = list()
        params.append(generate_expression(expr[:less_poses[0]]))
        for i in range(len(less_poses) - 1):
            params.append(generate_expression(expr[less_poses[i] + 1:less_poses[i + 1]]))
        params.append(generate_expression(expr[less_poses[-1] + 1:]))
        return AGIObject('sys_less_than', False,
                         {'sys_params': AGIList(False, params)})
    if '<=' in expr and find_naked_symbol(expr, '<='):
        less_equal_poses = find_naked_symbol(expr, '<=')
        # 暂时只接受两个参数
        assert len(less_equal_poses) == 1
        params = list()
        params.append(generate_expression(expr[:less_equal_poses[0]]))
        for i in range(len(less_equal_poses) - 1):
            params.append(generate_expression(expr[less_equal_poses[i] + 1:less_equal_poses[i + 1]]))
        params.append(generate_expression(expr[less_equal_poses[-1] + 1:]))
        return AGIObject('sys_less_than_or_equal_to', False,
                         {'sys_params': AGIList(False, params)})
    if '+' in expr and find_naked_symbol(expr, '+'):
        plus_poses = find_naked_symbol(expr, '+')
        if find_naked_symbol(expr, '-'):
            raise AGIException('Can not put "+" and "-" in the same scope.')
        params = list()
        params.append(generate_expression(expr[:plus_poses[0]]))
        for i in range(len(plus_poses) - 1):
            params.append(generate_expression(expr[plus_poses[i] + 1:plus_poses[i + 1]]))
        params.append(generate_expression(expr[plus_poses[-1] + 1:]))
        return AGIObject('sys_plus', False,
                         {'sys_params': AGIList(False, params)})
    if '-' in expr and find_naked_symbol(expr, '-'):
        minus_poses = find_naked_symbol(expr, '-')
        if find_naked_symbol(expr, '+'):
            raise AGIException('Can not put "+" and "-" in the same scope.')
        # 暂时只接受两个参数
        assert len(minus_poses) == 1
        params = list()
        params.append(generate_expression(expr[:minus_poses[0]]))
        for i in range(len(minus_poses) - 1):
            params.append(generate_expression(expr[minus_poses[i] + 1:minus_poses[i + 1]]))
        params.append(generate_expression(expr[minus_poses[-1] + 1:]))
        return AGIObject('sys_minus', False,
                         {'sys_params': AGIList(False, params)})
    if 'not' in expr and find_naked_symbol(expr, 'not'):
        not_poses = find_naked_symbol(expr, 'not')
        assert len(not_poses) == 1
        not_pos = not_poses[0]
        assert not_pos == 0
        param = generate_expression(expr[not_pos + 1:])
        return AGIObject('sys_not', False,
                         {'sys_param': param})
    if '--' in expr and find_naked_symbol(expr, '--'):
        negative_poses = find_naked_symbol(expr, '--')
        assert len(negative_poses) == 1
        negative_pos = negative_poses[0]
        assert negative_pos == 0
        param = generate_expression(expr[negative_pos + 1:])
        return AGIObject('sys_negative', False,
                         {'sys_param': param})
    if 'size' in expr and find_naked_symbol(expr, 'size'):
        size_poses = find_naked_symbol(expr, 'size')
        assert len(size_poses) == 1
        size_pos = size_poses[0]
        assert size_pos == len(expr) - 1
        assert expr[size_pos - 1] == '.'
        param = generate_expression(expr[:size_pos - 1])
        return AGIObject('sys_size', False,
                         {'sys_param': param})
    if expr[-1] == ']' and find_naked_symbol(expr, '['):
        open_squares = find_naked_symbol(expr, '[')
        open_square = open_squares[0]
        close_square = find_close_bracket(expr, '[', open_square)
        assert close_square == len(expr) - 1
        target_list = generate_expression(expr[:open_square])
        element_index = generate_expression(expr[open_square + 1:close_square])
        return AGIObject('sys_at', False,
                         {'sys_target_list': target_list,
                          'sys_element_index': element_index})
    if '.' in expr and find_naked_symbol(expr, '.'):
        dot_poses = find_naked_symbol(expr, '.')
        dot_pos = dot_poses[-1]
        if expr[dot_pos + 1] == "'":
            assert len(expr) == dot_pos + 4
            assert expr[dot_pos + 3] == "'"
            target_object = generate_expression(expr[:dot_pos])
            member_name = expr[dot_pos + 2]
            return AGIObject('sys_get_member', False,
                             {'sys_target_object': target_object,
                              'sys_member_name': AGIObject(member_name, False)})
        if expr[dot_pos + 1] == 'find':
            assert expr[dot_pos + 2] == '('
            assert expr[-1] == ')'
            target_list = generate_expression(expr[:dot_pos])
            expression_for_constraint = generate_expression(expr[dot_pos + 3:-1])
            return AGIObject('sys_find', False,
                             {'sys_target_list': target_list,
                              'sys_expression_for_constraint': expression_for_constraint})
        if expr[dot_pos + 1] == 'exist':
            assert expr[dot_pos + 2] == '('
            assert expr[-1] == ')'
            target_list = generate_expression(expr[:dot_pos])
            expression_for_constraint = generate_expression(expr[dot_pos + 3:-1])
            return AGIObject('sys_exist', False,
                             {'sys_target_list': target_list,
                              'sys_expression_for_constraint': expression_for_constraint})
        if expr[dot_pos + 1] == 'count':
            assert expr[dot_pos + 2] == '('
            assert expr[-1] == ')'
            target_list = generate_expression(expr[:dot_pos])
            expression_for_constraint = generate_expression(expr[dot_pos + 3:-1])
            return AGIObject('sys_count', False,
                             {'sys_target_list': target_list,
                              'sys_expression_for_constraint': expression_for_constraint})
        print(expr)
        assert False
    if len(expr) == 3 and expr[0] == "'" and expr[2] == "'":
        concept_name = expr[1]
        return AGIObject('sys_concept_instance', False,
                         {'sys_concept_name': AGIObject(concept_name, False)})
    if expr[0] == "'" and expr[-1] == ')':
        assert expr[2] == "'"
        assert expr[3] == '('
        function_name = expr[1]
        function_params = list()
        sub_expr = expr[4:-1]
        if find_naked_symbol(sub_expr, ','):
            has_param = True
        else:
            has_param = False
        while find_naked_symbol(sub_expr, ','):
            comma_pos = find_naked_symbol(sub_expr, ',')[0]
            function_params.append(generate_expression(sub_expr[:comma_pos]))
            sub_expr = sub_expr[comma_pos + 1:]
        if has_param:
            function_params.append(generate_expression(sub_expr))
        return AGIObject('sys_call', False,
                         {'sys_function_name': AGIObject(function_name, False),
                          'sys_function_params': AGIList(False, function_params)})
    if '(' in expr and find_naked_symbol(expr, '('):
        bracket_poses = find_naked_symbol(expr, '(')
        bracket_pos = bracket_poses[0]
        close_bracket_pos = find_close_bracket(expr, '(', bracket_pos)
        assert close_bracket_pos == len(expr) - 1
        return generate_expression(expr[1:-1])
    if len(expr) == 1:
        if expr[0][:5] == 'input' or expr[0][:3] == 'reg' or expr[0][:4] == 'iter':
            if expr[0][:5] == 'input':
                concept_name = 'sys_input'
                assert expr[0][5:].isdigit()
                index = int_obj(int(expr[0][5:]))
            elif expr[0][:3] == 'reg':
                concept_name = 'sys_reg'
                assert expr[0][3:].isdigit()
                index = int_obj(int(expr[0][3:]))
            else:
                concept_name = 'sys_iterator'
                if not expr[0][4:].isdigit():
                    print(expr[0])
                    assert False
                index = int_obj(int(expr[0][4:]))
            return AGIObject(concept_name, False,
                             {'sys_index': index})
        if expr[0] == 'target':
            return AGIObject('sys_target')
        if expr[0] == 'True' or expr[0] == 'False' or expr[0] == 'Fail' or expr[0] == 'None':
            return AGIObject('sys_constexpr', False,
                             {'sys_value': AGIObject('sys_' + expr[0], False, dict())})
        if expr[0].isdigit():
            return AGIObject('sys_constexpr', False,
                             {'sys_value': int_obj(int(expr[0]))})
        if len(expr[0]) == 1 and expr[0].isalpha():
            assert expr[0] in letter_to_number.keys()
            return AGIObject('sys_iterator', False,
                             {'sys_index': int_obj(letter_to_number[expr[0]])})
    print(expr)
    assert False


def generate_block(block: list, indentation_count: int, is_sub_block: bool, real_line_index=None):
    if is_sub_block:
        block_name = 'sys_sub_block'
    else:
        block_name = 'sys_dynamic_code'
    if not block:
        return AGIObject(block_name, False, {'sys_lines': AGIList()})
    if real_line_index is None:
        real_line_index = [1]
    lines = list()
    assert type(block[0]) == Line
    assert block[0].indentation_count == indentation_count
    line_index = 0
    while line_index < len(block):
        print(block[line_index].original_line)
        line_pieces = slice_line(block[line_index].line_str)
        if '=' in line_pieces or '&=' in line_pieces:
            if '=' in line_pieces:
                equal_pos = line_pieces.index('=')
                concept_name = 'sys_assign'
            elif '&=' in line_pieces:
                equal_pos = line_pieces.index('&=')
                concept_name = 'sys_assign_as_reference'
            else:
                assert False
            line_object = AGIObject(concept_name, False,
                                    {'sys_left_value': generate_expression(line_pieces[:equal_pos]),
                                     'sys_right_value': generate_expression(line_pieces[equal_pos + 1:]),
                                     'sys_line_index': int_obj(real_line_index[0])})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'return':
            line_object = AGIObject('sys_return', False,
                                    {'sys_return_value': generate_expression(line_pieces[1:]),
                                     'sys_line_index': int_obj(real_line_index[0])})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'assert':
            line_object = AGIObject('sys_assert', False,
                                    {'sys_assert_expression': generate_expression(line_pieces[1:]),
                                     'sys_line_index': int_obj(real_line_index[0])})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'for':
            for_statement_line_index = real_line_index[0]
            real_line_index[0] += 1
            assert line_pieces[2] == 'in'
            assert line_pieces[3] == 'range'
            assert line_pieces[4] == '('
            assert line_pieces[-2] == ')'
            assert line_pieces[-1] == ':'
            iter_id_str = line_pieces[1]
            if iter_id_str in letter_to_number.keys():
                iter_id = int_obj(letter_to_number[iter_id_str])
            else:
                assert iter_id_str[:4] == 'iter'
                assert iter_id_str[4:].isdigit()
                iter_id = int_obj(int(iter_id_str[4:]))
            close_bracket_pos = find_close_bracket(line_pieces, '(', 4)
            assert close_bracket_pos != -1
            end_value = generate_expression(line_pieces[5: close_bracket_pos])
            line_index += 1
            if line_index == len(block):
                raise AGIException('Unexpected end of code after for statement.')
            for_block = list()
            while block[line_index].indentation_count >= indentation_count + 1:
                for_block.append(block[line_index])
                line_index += 1
                if line_index == len(block):
                    break
            line_object = AGIObject('sys_for', False,
                                    {'sys_iterator_index': iter_id,
                                     'sys_end_value': end_value,
                                     'sys_for_block': generate_block(for_block, indentation_count + 1, True,
                                                                     real_line_index),
                                     'sys_line_index': int_obj(for_statement_line_index)})
            lines.append(line_object)
        elif line_pieces[0] == 'while':
            while_statement_line_index = real_line_index[0]
            real_line_index[0] += 1
            assert line_pieces[-1] == ':'
            expression_for_judging = generate_expression(line_pieces[1:-1])
            line_index += 1
            if line_index == len(block):
                raise AGIException('Unexpected end of code after while statement.')
            while_block = list()
            while block[line_index].indentation_count >= indentation_count + 1:
                while_block.append(block[line_index])
                line_index += 1
                if line_index == len(block):
                    break
            line_object = AGIObject('sys_while', False,
                                    {'sys_expression_for_judging': expression_for_judging,
                                     'sys_while_block': generate_block(while_block, indentation_count + 1,
                                                                       True, real_line_index),
                                     'sys_line_index': int_obj(while_statement_line_index)})
            lines.append(line_object)
        elif line_pieces[0] == 'break':
            assert len(line_pieces) == 1
            line_object = AGIObject('sys_break', False,
                                    {'sys_line_index': int_obj(real_line_index[0])})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'if':
            if_statement_line_index = real_line_index[0]
            real_line_index[0] += 1
            assert line_pieces[-1] == ':'
            expression_for_judging = generate_expression(line_pieces[1:-1])
            line_index += 1
            if line_index == len(block):
                raise AGIException('Unexpected end of code after if statement.')
            if_block = list()
            elif_modules = list()
            else_block = list()
            while block[line_index].indentation_count >= indentation_count + 1:
                if_block.append(block[line_index])
                line_index += 1
                if line_index == len(block):
                    break
            if_block = generate_block(if_block, indentation_count + 1, True, real_line_index)
            if line_index != len(block):
                while len(block) > line_index and block[line_index].line_str[:4] == 'elif':
                    elif_statement_line_index = real_line_index[0]
                    real_line_index[0] += 1
                    line_pieces = slice_line(block[line_index].line_str)
                    assert line_pieces[0] == 'elif'
                    assert line_pieces[-1] == ':'
                    elif_expression = generate_expression(line_pieces[1:-1])
                    print(block[line_index].original_line)
                    line_index += 1
                    if line_index == len(block):
                        raise AGIException('Unexpected end of code after elif statement.')
                    elif_block = list()
                    while block[line_index].indentation_count >= indentation_count + 1:
                        elif_block.append(block[line_index])
                        line_index += 1
                        if line_index == len(block):
                            break
                    elif_module = AGIObject('sys_elif_module', False,
                                            {'sys_expression_for_judging': elif_expression,
                                             'sys_elif_block': generate_block(elif_block,
                                                                              indentation_count + 1,
                                                                              True, real_line_index),
                                             'sys_line_index': int_obj(elif_statement_line_index)})
                    elif_modules.append(elif_module)
            if line_index != len(block) and block[line_index].line_str == 'else:':
                real_line_index[0] += 1
                print(block[line_index].original_line)
                line_index += 1
                if line_index == len(block):
                    raise AGIException('Unexpected end of code after else statement.')
                while block[line_index].indentation_count >= indentation_count + 1:
                    else_block.append(block[line_index])
                    line_index += 1
                    if line_index == len(block):
                        break
            line_object = AGIObject('sys_if', False,
                                    {'sys_expression_for_judging': expression_for_judging,
                                     'sys_if_block': if_block,
                                     'sys_elif_modules': AGIList(False, elif_modules),
                                     'sys_else_block': generate_block(else_block,
                                                                      indentation_count + 1, True,
                                                                      real_line_index),
                                     'sys_line_index': int_obj(if_statement_line_index)})
            lines.append(line_object)
        elif 'append' in line_pieces or 'remove' in line_pieces:
            if 'append' in line_pieces:
                is_append = True
                pos = line_pieces.index('append')
            else:
                is_append = False
                pos = line_pieces.index('remove')
            assert pos != 0 and line_pieces[pos - 1] == '.'
            assert line_pieces[pos + 1] == '('
            assert line_pieces[-1] == ')'
            if is_append:
                line_object = AGIObject('sys_append', False,
                                        {'sys_target_list': generate_expression(line_pieces[:pos - 1]),
                                         'sys_element': generate_expression(line_pieces[pos + 2:-1]),
                                         'sys_line_index': int_obj(real_line_index[0])})
            else:
                line_object = AGIObject('sys_remove', False,
                                        {'sys_target_list': generate_expression(line_pieces[:pos - 1]),
                                         'sys_expression_for_constraint':
                                             generate_expression(line_pieces[pos + 2:-1]),
                                         'sys_line_index': int_obj(real_line_index[0])})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'request':
            request_statement_line_index = real_line_index[0]
            real_line_index[0] += 1
            assert 's' in line_pieces
            s_pos = line_pieces.index('s')
            assert line_pieces[s_pos + 1] == '.'
            assert line_pieces[s_pos + 2] == 't'
            assert line_pieces[s_pos + 3] == '.'
            assert line_pieces[s_pos + 4] == '{'
            sub_pieces = line_pieces[1: s_pos]
            register_indices = list()
            for piece in sub_pieces:
                if piece != ',':
                    assert piece[:3] == 'reg'
                    assert piece[3:].isdigit()
                    register_indices.append(int_obj(int(piece[3:])))
            close_curly_pos = line_pieces.index('}')
            expression_for_constraint = generate_expression(line_pieces[s_pos + 5:close_curly_pos])
            # assert line_pieces[-2] == 'provided'
            # assert line_pieces[-1] == ':'
            line_index += 1
            provided_block = list()
            if line_index < len(block):
                while block[line_index].indentation_count >= indentation_count + 1:
                    provided_block.append(block[line_index])
                    line_index += 1
                    if line_index == len(block):
                        break
            line_object = AGIObject('sys_request', False,
                                    {'sys_requested_registers': AGIList(False, register_indices),
                                     'sys_expression_for_constraint': expression_for_constraint,
                                     'sys_provided_block':
                                         generate_block(provided_block,
                                                        indentation_count + 1, True, real_line_index),
                                     'sys_line_index': int_obj(request_statement_line_index)})
            lines.append(line_object)
        elif line_pieces[0] == "'" and line_pieces[-1] == ')':
            assert line_pieces[2] == "'"
            assert line_pieces[3] == '('
            function_name = AGIObject(line_pieces[1], False)
            sub_pieces = line_pieces[4:-1]
            function_params = list()
            if sub_pieces:
                while find_naked_symbol(sub_pieces, ',') != -1:
                    comma_pos = find_naked_symbol(sub_pieces, ',')[0]
                    function_params.append(generate_expression(sub_pieces[:comma_pos]))
                    sub_pieces = sub_pieces[comma_pos + 1:]
                if sub_pieces:
                    function_params.append(generate_expression(sub_pieces))

            line_object = AGIObject('sys_call_none_return_func', False,
                                    {'sys_function_name': function_name,
                                     'sys_function_params': AGIList(False, function_params),
                                     'sys_line_index': int_obj(real_line_index[0])})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        else:
            raise AGIException('Unknown line.')
    return AGIObject(block_name, False,
                     {'sys_lines': AGIList(False, lines)})


def generate_code(function_code_text):
    sliced_code = slice_code(function_code_text)
    print('Generating code!')
    result = generate_block(sliced_code, 0, False)
    print('Successfully generated!')
    return result


def encode_function(raw_directory, function_name, processed_directory):
    file = open(raw_directory + '/Functions/FunctionCode/' + function_name + '.txt', 'r')
    function_code_text = file.read()
    file.close()
    function_code = generate_code(function_code_text)
    file = open(processed_directory + '/Functions/FunctionCode/' + function_name + '.txt', 'wb')
    pickle.dump(function_code, file)
    file.close()

