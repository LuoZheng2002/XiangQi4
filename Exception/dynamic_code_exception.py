from AGI.struct import AGIObject, AGIList
import traceback
from Decode.decode_functions import print_code_default

class HardcodedExceptionInfo:
    def __init__(self, function_name):
        self.function_name = function_name


class DynamicExceptionInfo:
    def __init__(self, function_name, input_params, line, runtime_memory):
        self.function_name = function_name
        self.input_params = input_params
        self.line = line
        self.runtime_memory = runtime_memory


class ExpressionException(BaseException):
    def __init__(self, description):
        self.description = description


class LineException(BaseException):
    def __init__(self, line, description):
        self.line = line
        self.description = description


class DynamicCodeException(BaseException):
    def __init__(self, process_exception_info, description):
        self.call_stacks = [process_exception_info]
        self.description = description
        self.line_cache = None


def translate_exception_AGIList(agi_list: AGIList, cid_of, cid_reverse, indentation, attribute_name):
    result = str()
    for i in range(indentation):
        result += '|   '
    if attribute_name != '':
        result += "'" + attribute_name + "': "
    result += 'AGIList\n'
    if agi_list.size() > 0 and type(agi_list.get_element(0)) == AGIObject and agi_list.get_element(0).concept_name == cid_of['xq_piece']:
        result += 'Some xq_piece s.\n'
    else:
        for i in agi_list.value:
            if type(i) == AGIObject:
                result += translate_exception_AGIObject(i, cid_of, cid_reverse, indentation + 1, str())
            elif type(i) == AGIList():
                result += translate_exception_AGIList(i, cid_of, cid_reverse, indentation + 1, str())
            elif type(i) is None:
                for j in range(indentation + 1):
                    result += '    '
                result += 'None\n'
            else:
                assert False
    return result


def translate_exception_AGIObject(agi_object: AGIObject, cid_of, cid_reverse, indentation,  attribute_name):
    result = str()
    for i in range(indentation):
        result += '|   '
    if attribute_name != '':
        result += "'" + attribute_name + "': "
    result += "'" + cid_reverse[agi_object.concept_name] + "'\n"
    if agi_object.concept_name == cid_of['xq_chessboard']:
        result += 'A chessboard.\n'
    elif agi_object.concept_name == cid_of['xq_pieces']:
        result += 'Some pieces.\n'
    elif agi_object.concept_name == cid_of['dynamic_code']:
        result += 'A dynamic code.\n'
    else:
        for i in agi_object.attributes:
            if type(agi_object.attributes[i]) == AGIObject:
                result += translate_exception_AGIObject(agi_object.attributes[i], cid_of, cid_reverse, indentation + 1, cid_reverse[i])
            elif type(agi_object.attributes[i]) == AGIList:
                result += translate_exception_AGIList(agi_object.attributes[i], cid_of, cid_reverse, indentation + 1, cid_reverse[i])
            elif agi_object.attributes[i] is None:
                for j in range(indentation + 1):
                    result += '|   '
                result += "'" + cid_reverse[i] + '\': None\n'
            else:
                print(cid_reverse[agi_object.attributes[i]])
                assert False
    return result


def print_exception_obj(target: AGIObject or AGIList, cid_of, cid_reverse):
    if type(target) == AGIObject:
        print(translate_exception_AGIObject(target, cid_of, cid_reverse, 0, str()))
    elif type(target) == AGIList:
        print(translate_exception_AGIList(target, cid_of, cid_reverse, 0, str()))
    else:
        print(type(target))
        assert False


def show_dynamic_code_exception(dce: DynamicCodeException, function_directory):
    print('Dynamic Code Exception Triggered!')
    print(dce.description)
    for process in dce.call_stacks:
        if type(process) == DynamicExceptionInfo:
            print('Process: \'' + process.function_name + "'")
            print('The problematic line is: ' + str(process.line))
            print('The code is:')
            print_code_default(function_directory, process.function_name)
            print()
        elif type(process) == HardcodedExceptionInfo:
            print('Hardcoded Process: ' + process.function_name)
            print()
        else:
            assert False
    traceback.print_exc()
