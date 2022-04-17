from AGI.struct import AGIObject, AGIList
from AGI.code_browser import translate_expression, number_to_letter
from SystemConcept.common_concepts import to_int
from AGI.runtime_memory import RuntimeMemory
from Decode.decode_functions import slice_code

global_given_line = [0]
global_given_function = ['some string']


def translate_dynamic_code_line(line):
    if line.concept_name == 'dcr::assign' or line.concept_name == 'dcr::assign_as_reference':
        if line.concept_name == 'dcr::assign':
            sign = ' = '
        else:
            sign = ' &= '
        result = translate_expression(line.attributes['dc::left_value']) + sign + translate_expression(
            line.attributes['dc::right_value'])
        return result
    if line.concept_name == 'dcr::return':
        result = 'return ' + translate_expression(line.attributes['dc::return_value'])
        return result
    if line.concept_name == 'dcr::assert':
        result = 'assert ' + translate_expression(line.attributes['dc::assert_expression'])
        return result
    if line.concept_name == 'dcr::for':
        iter_index = to_int(line.attributes['dc::iterator_index'])
        if iter_index in number_to_letter.keys():
            iterator_name = number_to_letter[iter_index]
        else:
            iterator_name = 'iter' + str(iter_index)
        end_value = translate_expression(line.attributes['dc::end_value'],
                                         )
        result = 'for ' + iterator_name + ' in range(' + end_value + '):'
        return result
    if line.concept_name == 'dcr::while':
        expression_for_judging = translate_expression(line.attributes['dc::expression_for_judging'])
        result = 'while ' + expression_for_judging + ':'
        return result
    if line.concept_name == 'dcr::break':
        result = 'break'
        return result
    if line.concept_name == 'dcr::if':
        expression_for_judging = translate_expression(line.attributes['dc::expression_for_judging'])
        result = 'if ' + expression_for_judging + ':'
        return result
    if line.concept_name == 'dcr::append' or line.concept_name == 'dcr::remove':
        target_list = translate_expression(line.attributes['dc::target_list'],
                                           )
        if line.concept_name == 'dcr::append':
            element = translate_expression(line.attributes['dc::element'])
            word = '.append('
        else:
            element = translate_expression(line.attributes['dc::expression_for_constraint'])
            word = '.remove('
        result = target_list + word + element + ')'
        return result
    if line.concept_name == 'dcr::request':
        result = 'request '
        assert type(line.attributes['dc::requested_registers']) == AGIList
        for reg_id in line.attributes['dc::requested_registers'].value:
            result += 'reg' + str(to_int(reg_id)) + ', '
        result += 's.t.{'
        result += translate_expression(line.attributes['dc::expression_for_constraint'])
        result += '}, provided:'
        return result
    if line.concept_name == 'dcr::call_none_return_func':
        result = "'" + line.attributes['dc::function_name'].concept_name + "'("
        function_params = line.attributes['dc::function_params'].value
        for function_param in function_params:
            result += translate_expression(function_param) + ', '
        if function_params:
            result = result[:-2]
        result += ')'
        return result
    if line.concept_name == 'dc::elif_module':
        result = 'elif ' + translate_expression(line.attributes['dc::expression_for_judging']) + ':'
        return result
    assert False


class Line:
    def __init__(self, line_ptr, indentation):
        self.line_ptr = line_ptr
        self.indentation = indentation


class Debugger:
    def __init__(self, function_name, code_object: AGIObject, runtime_memory: RuntimeMemory):
        self.function_name = function_name
        self.debug_signal = None
        self.runtime_memory = runtime_memory
        self.sliced_code = slice_code(code_object, 0)

    def print_lines(self, line_index, radius):
        assert line_index >= 0
        if line_index <= radius:
            start_pos = 1
            end_pos = radius * 2 + 2
        elif line_index + radius > len(self.sliced_code):
            start_pos = len(self.sliced_code) - radius
            end_pos = len(self.sliced_code) + 1
        else:
            start_pos = line_index - radius
            end_pos = line_index + radius + 1
        for i in range(start_pos, end_pos):
            single_line = self.sliced_code[i - 1]
            for j, line in enumerate(single_line.lines):
                line_str = str()
                if j == 0:
                    if i == line_index:
                        line_str += '->'
                    else:
                        line_str += '  '
                    if single_line.line_index == 0:
                        line_str += '        '
                    else:
                        line_str += str(single_line.line_index).ljust(8, ' ')
                else:
                    line_str += '  '
                    line_str += '        '
                for h in range(single_line.indentation):
                    line_str += '    '
                if j != 0:
                    line_str += '        '
                line_str += line
                print(line_str)

    def get_debug_input(self):
        while True:
            debug_input = input('')
            if debug_input == '':
                self.debug_signal = 'step_over'
                break
            elif debug_input == 'si':
                self.debug_signal = 'step_into'
                break
            elif debug_input == 'so':
                self.debug_signal = 'step_out'
                break
            elif debug_input[:3] == 'reg':
                reg_index = int(debug_input[3:])
                target_object = self.runtime_memory.get_reg_value(reg_index)
                print(debug_input + ' is:')
                print_debug_object(target_object)
            elif debug_input[:4] == 'iter':
                iter_index = int(debug_input[4:])
                target_object = self.runtime_memory.get_iterator_value(iter_index)
                print(debug_input + ' is:')
                if type(target_object) == int:
                    print(target_object)
                else:
                    print_debug_object(target_object)
            elif debug_input[:5] == 'input':
                input_index = int(debug_input[5:])
                target_object = self.runtime_memory.get_input_value(input_index)
                print(debug_input + ' is:')
                print_debug_object(target_object)
            elif debug_input.isdigit():
                self.debug_signal = int(debug_input)
                break
            elif debug_input[:4] == 'set ':
                rest = debug_input[4:]
                space_pos = rest.find(' ')
                assert space_pos != -1
                function_name = rest[:space_pos]
                line_number = int(rest[space_pos + 1:])
                global global_given_function, global_given_line
                global_given_function[0] = function_name
                global_given_line[0] = line_number
                print(global_given_line[0])
                print(global_given_function[0])
            else:
                print('Unknown command.')


def translate_debug_AGIList(target: AGIList, indentation, attribute_name):
    result = str()
    for i in range(indentation):
        result += '|   '
    if attribute_name != '':
        result += "'" + attribute_name + "': "
    result += 'AGIList\n'
    if target.size() > 0 and type(target.get_element(0)) == AGIObject \
            and target.get_element(0).concept_name == 'xq::piece':
        result += 'Some xq::piece s.\n'
    else:
        for i in target.value:
            if type(i) == AGIObject:
                result += translate_debug_AGIObject(i, indentation + 1, str())
            elif type(i) == AGIList():
                result += translate_debug_AGIList(i, indentation + 1, str())
            elif type(i) is None:
                for j in range(indentation + 1):
                    result += '    '
                result += 'None\n'
            else:
                assert False
    return result


def translate_debug_AGIObject(target, indentation, attribute_name):
    result = str()
    for i in range(indentation):
        result += '|   '
    if attribute_name != '':
        result += "'" + attribute_name + "': "
    result += "'" + target.concept_name + "'\n"
    line_concepts = ['dcr::assign',
                     'dcr::assign_as_reference',
                     'dcr::return',
                     'dcr::assert',
                     'dcr::for',
                     'dcr::while',
                     'dcr::break',
                     'dcr::if',
                     'dcr::append',
                     'dcr::remove',
                     'dcr::request',
                     'dcr::call_none_return_func']
    if target.concept_name == 'natural_number':
        result += '(natural_number)' + str(to_int(target)) + '\n'
    elif target.concept_name == 'xq::chessboard':
        result += 'A chessboard.\n'
    elif target.concept_name == 'xq::pieces':
        result += 'Some pieces.\n'
    elif target.concept_name in line_concepts:
        result += translate_dynamic_code_line(target) + '\n'
    else:
        for i in target.attributes:
            if type(target.attributes[i]) == AGIObject:
                result += translate_debug_AGIObject(target.attributes[i], indentation + 1, [i])
            elif type(target.attributes[i]) == AGIList:
                result += translate_debug_AGIList(target.attributes[i], indentation + 1, [i])
            elif target.attributes[i] is None:
                for j in range(indentation + 1):
                    result += '|   '
                    result += "'" + i + '\': None\n'
            else:
                print([target.attributes[i]])
                assert False
    return result


def print_debug_object(target):
    if type(target) == AGIObject:
        print(translate_debug_AGIObject(target, 0, str()))
    elif type(target) == AGIList:
        print(translate_debug_AGIList(target, 0, str()))
    else:
        print(type(target))
        assert False
