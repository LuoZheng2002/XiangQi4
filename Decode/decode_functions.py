from AGI.struct import AGIObject, AGIList
from SystemConcept.common_concepts import to_int
import pickle
from AGI.code_generator import number_to_letter
from AGI.translate_struct import print_obj
from AGI.dynamic_code_getter import get_dynamic_code


class SingleLine:
    def __init__(self, lines: list, indentation, line_index):
        self.lines = lines
        self.indentation = indentation
        self.line_index = line_index


def slice_code(code_object: AGIObject, indentation) -> list:
    result = list()
    for line in code_object.attributes['sys_lines'].value:
        if line.concept_name == 'sys_for':
            result.append(SingleLine(translate_line(line), indentation, to_int(line.attributes['sys_line_index'])))
            result += slice_code(line.attributes['sys_for_block'], indentation + 1)
            continue
        if line.concept_name == 'sys_while':
            result.append(SingleLine(translate_line(line), indentation, to_int(line.attributes['sys_line_index'])))
            result += slice_code(line.attributes['sys_while_block'], indentation + 1)
            continue
        if line.concept_name == 'sys_if':
            result.append(SingleLine(translate_line(line), indentation, to_int(line.attributes['sys_line_index'])))
            result += slice_code(line.attributes['sys_if_block'], indentation + 1)
            for elif_module in line.attributes['sys_elif_modules'].value:
                result.append(SingleLine(translate_line(elif_module),
                                         indentation, to_int(line.attributes['sys_line_index'])))
                result += slice_code(elif_module.attributes['sys_elif_block'], indentation + 1)
            if line.attributes['sys_else_block'].agi_list().size() > 0:
                result.append(SingleLine(['else:'], indentation, 0))
                result += slice_code(line.attributes['sys_else_block'], indentation + 1)
            continue
        if line.concept_name == 'sys_request':
            result.append(SingleLine(translate_line(line), indentation, to_int(line.attributes['sys_line_index'])))
            result += slice_code(line.attributes['sys_provided_block'], indentation + 1)
            continue
        result.append(SingleLine(translate_line(line), indentation, to_int(line.attributes['sys_line_index'])))
    return result


def translate_expression(expr: AGIObject) -> str:
    if expr.concept_name == 'sys_input':
        return 'input' + str(to_int(expr.attributes['sys_index']))
    if expr.concept_name == 'sys_reg':
        return 'reg' + str(to_int(expr.attributes['sys_index']))
    if expr.concept_name == 'sys_iterator':
        iter_id = to_int(expr.attributes['sys_index'])
        if iter_id in number_to_letter.keys():
            return number_to_letter[iter_id]
        return 'iter' + str(iter_id)
    if expr.concept_name == 'sys_call':
        result = "'" + expr.attributes['sys_function_name'].concept_name + "'("
        function_params = expr.attributes['sys_function_params'].value
        for function_param in function_params:
            result += translate_expression(function_param) + ', '
        if function_params:
            result = result[:-2]
        result += ')'
        return result
    if expr.concept_name == 'sys_concept_instance':
        result = "'" + expr.attributes['sys_concept_name'].concept_name + "'"
        return result
    if expr.concept_name == 'sys_size':
        target_list = translate_expression(expr.attributes['sys_target_list'])
        result = target_list + '.size'
        return result
    if expr.concept_name == 'sys_get_member':
        target_object = translate_expression(expr.attributes['sys_target_object'])
        member_name = expr.attributes['sys_member_name'].concept_name
        result = target_object + ".'" + member_name + "'"
        return result
    if expr.concept_name == 'sys_at':
        target_list = translate_expression(expr.attributes['sys_target_list'])
        element_index = translate_expression(expr.attributes['sys_element_index'])
        result = target_list + '[' + element_index + ']'
        return result
    if expr.concept_name == 'sys_find':
        target_list = translate_expression(expr.attributes['sys_target_list'])
        expression = translate_expression(expr.attributes['sys_expression_for_constraint'])
        result = target_list + '.find(' + expression + ')'
        return result
    if expr.concept_name == 'sys_exist':
        target_list = translate_expression(expr.attributes['sys_target_list'])
        expression = translate_expression(expr.attributes['sys_expression_for_constraint'])
        result = target_list + '.exist(' + expression + ')'
        return result
    if expr.concept_name == 'sys_count':
        target_list = translate_expression(expr.attributes['sys_target_list'])
        expression = translate_expression(expr.attributes['sys_expression_for_constraint'])
        result = target_list + '.count(' + expression + ')'
        return result
    if expr.concept_name == 'sys_target':
        return 'target'
    if expr.concept_name == 'sys_constexpr':
        value = expr.attributes['sys_value']
        special_concepts = ['sys_True', 'sys_False', 'sys_None', 'sys_Fail']
        if value.concept_name == 'sys_integer':
            return str(to_int(value))
        elif value.concept_name in special_concepts:
            return value.concept_name[4:]
        else:
            assert False
    if expr.concept_name == 'sys_and':
        result = '('
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' and '
        return result[:-5] + ')'
    if expr.concept_name == 'sys_or':
        result = '('
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' or '
        return result[:-4] + ')'
    if expr.concept_name == 'sys_not':
        return 'not ' + translate_expression(expr.attributes['sys_param'])
    if expr.concept_name == 'sys_same_concept':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' == '
        return result[:-4]
    if expr.concept_name == 'sys_not_same_concept':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' != '
        return result[:-4]
    if expr.concept_name == 'sys_math_equal':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' === '
        return result[:-5]
    if expr.concept_name == 'sys_not_math_equal':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' =!= '
        return result[:-5]
    if expr.concept_name == 'sys_greater_than':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' > '
        return result[:-3]
    if expr.concept_name == 'sys_less_than':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' < '
        return result[:-3]
    if expr.concept_name == 'sys_greater_than_or_equal_to':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' >= '
        return result[:-4]
    if expr.concept_name == 'sys_less_than_or_equal_to':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' <= '
        return result[:-4]
    if expr.concept_name == 'sys_plus':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' + '
        return result[:-3]
    if expr.concept_name == 'sys_minus':
        result = str()
        params = expr.attributes['sys_params'].value
        assert len(params) >= 2
        for param in params:
            result += translate_expression(param) + ' - '
        return result[:-4]
    if expr.concept_name == 'sys_negative':
        return '-' + translate_expression(expr.attributes['sys_param'])
    print(expr.concept_name)
    assert False


def translate_line(line: AGIObject) -> list:
    if line.concept_name == 'sys_elif_module':
        result = 'elif' + translate_expression(line.attributes['sys_expression_for_judging']) + ':'
    elif line.concept_name == 'sys_assign':
        result = translate_expression(line.attributes['sys_left_value']) + ' = ' \
               + translate_expression(line.attributes['sys_right_value'])
    elif line.concept_name == 'sys_assign_as_reference':
        result = translate_expression(line.attributes['sys_left_value']) + ' &= ' \
               + translate_expression(line.attributes['sys_right_value'])
    elif line.concept_name == 'sys_return':
        result = 'return ' + translate_expression(line.attributes['sys_return_value'])
    elif line.concept_name == 'sys_assert':
        result = 'assert ' + translate_expression(line.attributes['sys_assert_expression'])
    elif line.concept_name == 'sys_for':
        iter_index = to_int(line.attributes['sys_iterator_index'])
        if iter_index in number_to_letter.keys():
            iterator_name = number_to_letter[iter_index]
        else:
            iterator_name = 'iter' + str(iter_index)
        end_value = translate_expression(line.attributes['sys_end_value'])
        result = 'for ' + iterator_name + ' in range(' + end_value + '):'
    elif line.concept_name == 'sys_while':
        expression_for_judging = translate_expression(line.attributes['sys_expression_for_judging'])
        result = 'while ' + expression_for_judging + ':'
    elif line.concept_name == 'sys_break':
        result = 'break'
    elif line.concept_name == 'sys_if':
        expression_for_judging = translate_expression(line.attributes['sys_expression_for_judging'])
        result = 'if ' + expression_for_judging + ':'
    elif line.concept_name == 'sys_append':
        target_list = translate_expression(line.attributes['sys_target_list'])
        element = translate_expression(line.attributes['sys_element'])
        result = target_list + '.append(' + element + ')'
    elif line.concept_name == 'sys_remove':
        target_list = translate_expression(line.attributes['sys_target_list'])
        element = translate_expression(line.attributes['sys_expression_for_constraint'])
        result = target_list + '.remove(' + element + ')'
    elif line.concept_name == 'sys_request':
        result = 'request '
        assert type(line.attributes['sys_requested_registers']) == AGIList
        for reg_id in line.attributes['sys_requested_registers'].value:
            result += 'reg' + str(to_int(reg_id)) + ', '
        result += 's.t.{'
        result += translate_expression(line.attributes['sys_expression_for_constraint'])
        result += '}'
        if line.attributes['sys_provided_block'].agi_list().size() > 0:
            result += ', provided:'
    elif line.concept_name == 'sys_call_none_return_func':
        result = "'" + line.attributes['sys_function_name'].concept_name + "'("
        function_params = line.attributes['sys_function_params'].value
        for function_param in function_params:
            result += translate_expression(function_param) + ', '
        if function_params:
            result = result[:-2]
        result += ')'
    else:
        print(line.concept_name)
        assert False
    return [result]


def decode_function(directory, function_name) -> list:
    file = open(directory + '/Functions/FunctionCode/' + function_name + '.txt', 'rb')
    code_object = pickle.load(file)
    file.close()
    return slice_code(code_object, 0)


def print_code_default(directory, function_name):
    sliced_code = decode_function(directory, function_name)
    for single_line in sliced_code:
        for i, line in enumerate(single_line.lines):
            line_str = str()
            if i == 0:
                if single_line.line_index == 0:
                    line_str += '        '
                else:
                    line_str += str(single_line.line_index).ljust(8, ' ')
            else:
                line_str += '        '
            for j in range(single_line.indentation):
                line_str += '    '
            if i != 0:
                line_str += '        '
            line_str += line
            print(line_str)
