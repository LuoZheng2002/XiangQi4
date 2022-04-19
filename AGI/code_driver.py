from AGI.struct import AGIObject, AGIList
from AGI.runtime_memory import RuntimeMemory, Input
from copy import deepcopy
from Exception.dynamic_code_exception import DynamicCodeException, LineException, DynamicExceptionInfo, \
    HardcodedExceptionInfo, ExpressionException
from Exception.hardcoded_code_exception import HardcodedCodeException
from AGI.dynamic_code_debugger import Debugger, global_given_line, global_given_function
from debug import debug_dynamic_code
from SystemFunction.system_function_dict import system_function_dict
from SystemConcept.common_concepts import to_int, int_obj, bool_obj
from Exception.structure_exception import StructureException
from SystemConcept.system_concepts import system_concepts
from Decode.decode_functions import translate_expression

def run_system_function(function_name, input_params: AGIList):
    return system_function_dict[function_name](input_params)


class LineSignal:
    def __init__(self, signal_type, signal_value=None):
        self.signal_type = signal_type
        if signal_type == 'return':
            assert signal_value is not None
        self.signal_value = signal_value


def find_element(target_list: AGIList, expr, runtime_memory, lib, debugger) -> int:
    assert type(target_list) == AGIList
    for i, element in enumerate(target_list.value):
        if solve_expression(expr, runtime_memory, lib, debugger, element).concept_name == 'sys_True':
            return i
    return -1


def solve_expression(expr: AGIObject, runtime_memory: RuntimeMemory, lib, debugger,
                     target=None) -> AGIObject or AGIList:
    if expr.concept_name == 'sys_input':
        index = to_int(expr.attributes['sys_index'])
        assert runtime_memory.has_input(index)
        return runtime_memory.get_input_value(index)
    if expr.concept_name == 'sys_reg':
        index = to_int(expr.attributes['sys_index'])
        if not runtime_memory.has_reg(index):
            raise ExpressionException('Register not created.')
        return runtime_memory.get_reg_value(index)
    if expr.concept_name == 'sys_iterator':
        index = to_int(expr.attributes['sys_index'])
        assert runtime_memory.has_iterator(index)
        return int_obj(runtime_memory.get_iterator_value(index))
    if expr.concept_name == 'sys_call':
        function_name = expr.attributes['sys_function_name'].concept_name
        function_params = list()
        for param in expr.attributes['sys_function_params'].value:
            function_params.append(solve_expression(param, runtime_memory, lib, debugger, target))
        function_params = AGIList(False, function_params)
        if function_name not in system_function_dict.keys():
            try:
                if type(debugger.debug_signal) == int or debugger.debug_signal == 'step_over' or debugger.debug_signal == 'step_out':
                    nDebug = True
                else:
                    nDebug = False
                result = run_dynamic_function(function_name, function_params, lib, nDebug)
            except DynamicCodeException as d:
                raise
        else:
            try:
                if function_name == 'sys_func_test_dynamic_function':
                    function_object = function_params.get_element(0)
                    test_function_params = function_params.get_element(1)
                    if type(test_function_params) == AGIObject:
                        test_function_params = test_function_params.agi_list()
                    result = run_dynamic_function(function_object, test_function_params, lib)
                else:
                    result = run_system_function(function_name, function_params)
            except HardcodedCodeException as h:
                raise
            except DynamicCodeException as d:
                raise
        return result
    if expr.concept_name == 'sys_concept_instance':
        attributes = dict()
        concept_name = expr.attributes['sys_concept_name'].concept_name
        if concept_name in system_concepts:
            if concept_name == 'sys_list':
                return AGIObject('sys_list', True, {'sys_value': None})
            return AGIObject(concept_name, True)
        if concept_name not in lib.concepts.keys():
            assert False, concept_name
        for attribute_name in lib.concepts[concept_name].instance_attributes:
            attributes.update({attribute_name: None})
        return AGIObject(concept_name, True, attributes)
    if expr.concept_name == 'sys_size':
        target_list = solve_expression(expr.attributes['sys_target_list'],
                                       runtime_memory, lib, debugger, target)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        return int_obj(target_list.size())
    if expr.concept_name == 'sys_get_member':
        target_object = solve_expression(expr.attributes['sys_target_object'],
                                         runtime_memory, lib, debugger, target)
        member_id = expr.attributes['sys_member_name'].concept_name
        if member_id not in target_object.attributes.keys():
            raise ExpressionException('Can not get target object\'s member!')
        return target_object.attributes[member_id]
    if expr.concept_name == 'sys_at':
        target_list = solve_expression(expr.attributes['sys_target_list'],
                                       runtime_memory, lib, debugger, target)
        index = to_int(solve_expression(expr.attributes['sys_element_index'],
                                        runtime_memory, lib, debugger, target))
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        return target_list.get_element(index)
    if expr.concept_name == 'sys_find' or \
            expr.concept_name == 'sys_exist' or expr.concept_name == 'sys_count':
        target_list = solve_expression(expr.attributes['sys_target_list'],
                                       runtime_memory, lib, debugger, target)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        count = 0
        for element in target_list.value:
            if solve_expression(expr.attributes['sys_expression_for_constraint'],
                                runtime_memory, lib, debugger, element).concept_name == 'sys_True':
                if expr.concept_name == 'sys_find':
                    return element
                if expr.concept_name == 'sys_exist':
                    return AGIObject('sys_True')
                count += 1
        if expr.concept_name == 'sys_find':
            raise ExpressionException('Can not find the target element!')
        if expr.concept_name == 'sys_exist':
            return bool_obj(False)
        return int_obj(count)
    if expr.concept_name == 'sys_target':
        assert target is not None
        return target
    if expr.concept_name == 'sys_constexpr':
        return expr.attributes['sys_value']
    if expr.concept_name == 'sys_and':
        params = expr.attributes['sys_params'].value
        param_results = list()
        found_false = False
        for param in params:
            result = solve_expression(param, runtime_memory, lib, debugger, target)
            if result.concept_name != 'sys_True' and result.concept_name != 'sys_False':
                print(result.concept_name)
                raise ExpressionException('The params in and operation is not boolean.')
            if result.concept_name == 'sys_False':
                found_false = True
        if found_false:
            # print(translate_expression(expr) + ' is False.')
            return bool_obj(False)
        # print(translate_expression(expr) + ' is True.')
        return bool_obj(True)

    if expr.concept_name == 'sys_or':
        params = expr.attributes['sys_params'].value
        for param in params:
            result = solve_expression(param, runtime_memory, lib, debugger, target)
            if result.concept_name != 'sys_True' and result.concept_name != 'sys_False':
                raise ExpressionException('The params in or operation is not boolean.')
            if result.concept_name == 'sys_True':
                return bool_obj(True)
        return bool_obj(False)
    if expr.concept_name == 'sys_not':
        param = solve_expression(expr.attributes['sys_param'], runtime_memory, lib, debugger, target)
        if param.concept_name != 'sys_True' and param.concept_name != 'sys_False':
            raise ExpressionException('The params in not operation is not boolean.')
        if param.concept_name == 'sys_True':
            return bool_obj(False)
        return bool_obj(True)
    if expr.concept_name == 'sys_same_concept':
        params = expr.attributes['sys_params'].value
        concept_name = None
        for param in params:
            result = solve_expression(param, runtime_memory, lib, debugger, target)
            if type(result) == AGIList:
                return bool_obj(False)
            if concept_name is None:
                concept_name = result.concept_name
            else:
                if concept_name != result.concept_name:
                    return bool_obj(False)
        return bool_obj(True)
    if expr.concept_name == 'sys_not_same_concept':
        params = expr.attributes['sys_params'].value
        assert len(params) == 2
        param1 = solve_expression(params[0], runtime_memory, lib, debugger, target)
        param2 = solve_expression(params[1], runtime_memory, lib, debugger, target)
        if param1.concept_name == param2.concept_name:
            return bool_obj(False)
        return bool_obj(True)
    if expr.concept_name == 'sys_math_equal':
        params = expr.attributes['sys_params'].value
        number = None
        for param in params:
            result = solve_expression(param, runtime_memory, lib, debugger, target)
            assert type(result) == AGIObject
            assert result.concept_name == 'sys_integer'
            if number is None:
                number = result.sys_value
            else:
                if number != result.sys_value:
                    return bool_obj(False)
        return bool_obj(True)
    if expr.concept_name == 'sys_not_math_equal':
        params = expr.attributes['sys_params'].value
        assert len(params) == 2
        param1 = solve_expression(params[0], runtime_memory, lib, debugger, target)
        param2 = solve_expression(params[1], runtime_memory, lib, debugger, target)
        assert param1.concept_name == 'sys_integer' and param2.concept_name == 'sys_integer'
        if param1.sys_value == param2.sys_value:
            return bool_obj(False)
        return bool_obj(True)
    if expr.concept_name == 'sys_greater_than':
        params = expr.attributes['sys_params'].value
        assert len(params) == 2
        param1 = solve_expression(params[0], runtime_memory, lib, debugger, target)
        param2 = solve_expression(params[1], runtime_memory, lib, debugger, target)
        assert param1.concept_name == 'sys_integer' and param2.concept_name == 'sys_integer'
        if param1.sys_value > param2.sys_value:
            return bool_obj(True)
        return bool_obj(False)
    if expr.concept_name == 'sys_greater_than_or_equal_to':
        params = expr.attributes['sys_params'].value
        assert len(params) == 2
        param1 = solve_expression(params[0], runtime_memory, lib, debugger, target)
        param2 = solve_expression(params[1], runtime_memory, lib, debugger, target)
        assert param1.concept_name == 'sys_integer' and param2.concept_name == 'sys_integer'
        if param1.sys_value >= param2.sys_value:
            return bool_obj(True)
        return bool_obj(False)
    if expr.concept_name == 'sys_less_than':
        params = expr.attributes['sys_params'].value
        assert len(params) == 2
        param1 = solve_expression(params[0], runtime_memory, lib, debugger, target)
        param2 = solve_expression(params[1], runtime_memory, lib, debugger, target)
        assert param1.concept_name == 'sys_integer' and param2.concept_name == 'sys_integer'
        if param1.sys_value < param2.sys_value:
            return bool_obj(True)
        return bool_obj(False)
    if expr.concept_name == 'sys_less_than_or_equal_to':
        params = expr.attributes['sys_params'].value
        assert len(params) == 2
        param1 = solve_expression(params[0], runtime_memory, lib, debugger, target)
        param2 = solve_expression(params[1], runtime_memory, lib, debugger, target)
        assert param1.concept_name == 'sys_integer' and param2.concept_name == 'sys_integer'
        if param1.sys_value <= param2.sys_value:
            return bool_obj(True)
        return bool_obj(False)
    if expr.concept_name == 'sys_plus':
        params = expr.attributes['sys_params'].value
        number = 0
        for param in params:
            result = solve_expression(param, runtime_memory, lib, debugger, target)
            assert type(result) == AGIObject
            assert result.concept_name == 'sys_integer'
            number += result.sys_value
        return int_obj(number)
    if expr.concept_name == 'sys_minus':
        params = expr.attributes['sys_params'].value
        assert len(params) == 2
        param1 = solve_expression(params[0], runtime_memory, lib, debugger, target)
        param2 = solve_expression(params[1], runtime_memory, lib, debugger, target)
        assert param1.concept_name == 'sys_integer' and param2.concept_name == 'sys_integer'
        number = param1.sys_value - param2.sys_value
        return int_obj(number)
    if expr.concept_name == 'sys_max':
        params = expr.attributes['sys_params'].value
        number = None
        for param in params:
            result = solve_expression(param, runtime_memory, lib, debugger, target)
            assert type(result) == AGIObject
            assert result.concept_name == 'sys_integer'
            if number is None:
                number = result.sys_value
            else:
                if result.sys_value > number:
                    number = result.sys_value
        return int_obj(number)
    if expr.concept_name == 'sys_min':
        params = expr.attributes['sys_params'].value
        number = None
        for param in params:
            result = solve_expression(param, runtime_memory, lib, debugger, target)
            assert type(result) == AGIObject
            assert result.concept_name == 'sys_integer'
            if number is None:
                number = result.sys_value
            else:
                if result.sys_value < number:
                    number = result.sys_value
        return int_obj(number)
    print(expr.concept_name)
    raise ExpressionException('Unknown head of expression!')


def process_line(line: AGIObject, runtime_memory: RuntimeMemory, lib, debugger: Debugger) -> LineSignal:
    try:
        if (debug_dynamic_code and debugger.debug_signal != 'step_out') \
                or global_given_function[0] == debugger.function_name:
            line_index = to_int(line.attributes['sys_line_index'])
            if (type(debugger.debug_signal) != int and debugger.debug_signal != 'step_out') \
                    or debugger.debug_signal == line_index \
                    or (global_given_function[0] == debugger.function_name and global_given_line[0] == line_index):
                print('Current function: \'' + debugger.function_name + '\'')
                debugger.print_lines(line_index, 5)
                debugger.get_debug_input()
        if line.concept_name == 'sys_assign' or line.concept_name == 'sys_assign_as_reference':
            rhs_value = solve_expression(line.attributes['sys_right_value'], runtime_memory,
                                         lib, debugger)
            lhs = line.attributes['sys_left_value']
            if lhs.concept_name == 'sys_reg':
                reg_index = to_int(lhs.attributes['sys_index'])
                if not runtime_memory.has_reg(reg_index):
                    if line.concept_name == 'sys_assign':
                        runtime_memory.create_reg(reg_index, deepcopy(rhs_value))
                    else:
                        runtime_memory.create_reg(reg_index, rhs_value)
                else:
                    if line.concept_name == 'sys_assign':
                        runtime_memory.set_reg(reg_index, deepcopy(rhs_value))
                    else:
                        runtime_memory.set_reg(reg_index, rhs_value)
            elif lhs.concept_name == 'sys_at':
                target_list = solve_expression(lhs.attributes['sys_target_list'],
                                               runtime_memory, lib, debugger)
                element_index = solve_expression(lhs.attributes['sys_element_index'],
                                                 runtime_memory, lib, debugger)
                if type(target_list) == AGIObject:
                    target_list = target_list.agi_list()
                else:
                    assert type(target_list) == AGIList
                if line.concept_name == 'sys_assign':
                    target_list.set_value(to_int(element_index), deepcopy(rhs_value))
                else:
                    target_list.set_value(to_int(element_index), rhs_value)
            elif lhs.concept_name == 'sys_get_member':
                target_object = solve_expression(lhs.attributes['sys_target_object'],
                                                 runtime_memory, lib, debugger)
                assert type(target_object) == AGIObject
                member_id = lhs.attributes['sys_member_name'].concept_name
                assert member_id in target_object.attributes.keys()
                if line.concept_name == 'sys_assign':
                    target_object.attributes[member_id] = deepcopy(rhs_value)
                else:
                    target_object.attributes[member_id] = rhs_value
            return LineSignal('normal')
        if line.concept_name == 'sys_return':
            return_value = solve_expression(line.attributes['sys_return_value'],
                                            runtime_memory, lib, debugger)
            return LineSignal('return', return_value)
        if line.concept_name == 'sys_assert':
            assert_expression = solve_expression(line.attributes['sys_assert_expression'],
                                                 runtime_memory, lib, debugger)
            if assert_expression.concept_name != 'sys_True':
                raise LineException(to_int(line.attributes['sys_line_index']),
                                    'Assertion Failed in Dynamic Code.')
            return LineSignal('normal')
        if line.concept_name == 'sys_for':
            iter_id = to_int(line.attributes['sys_iterator_index'])
            if runtime_memory.has_iterator(iter_id):
                iterator = runtime_memory.get_iterator(iter_id)
                iterator.value = 0
            else:
                iterator = runtime_memory.create_iterator(iter_id, 0)
            end_value = to_int(solve_expression(line.attributes['sys_end_value'],
                                                runtime_memory, lib, debugger))
            for i in range(end_value):
                for for_line in line.attributes['sys_for_block'].agi_list().value:
                    try:
                        line_signal = process_line(for_line, runtime_memory, lib, debugger)
                    except DynamicCodeException as d:
                        d.line_cache = to_int(for_line.attributes['sys_line_index'])
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('normal')
                    if line_signal.signal_type == 'return':
                        return line_signal
                assert iterator.value == i
                iterator.value = iterator.value + 1
            return LineSignal('normal')
        if line.concept_name == 'sys_while':
            loop_count = 0
            while solve_expression(line.attributes['sys_expression_for_judging'],
                                   runtime_memory, lib, debugger).concept_name == 'sys_True':
                loop_count += 1
                for while_line in line.attributes['sys_while_block'].agi_list().value:
                    try:
                        line_signal = process_line(while_line, runtime_memory, lib, debugger)
                    except DynamicCodeException as d:
                        d.line_cache = to_int(while_line.attributes['sys_line_index'])
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('normal')
                    if line_signal.signal_type == 'return':
                        return line_signal
                if loop_count == 1000:
                    raise LineException(to_int(line.attributes['sys_line_index']),
                                        'While loop does not stop.')
            return LineSignal('normal')
        if line.concept_name == 'sys_break':
            return LineSignal('break')
        if line.concept_name == 'sys_if':
            expression_for_judging = solve_expression(line.attributes['sys_expression_for_judging'],
                                                      runtime_memory, lib, debugger)
            if expression_for_judging.concept_name == 'sys_True':
                for if_line in line.attributes['sys_if_block'].agi_list().value:
                    try:
                        line_signal = process_line(if_line, runtime_memory, lib, debugger)
                    except DynamicCodeException as d:
                        d.line_cache = to_int(if_line.attributes['sys_line_index'])
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('break')
                    if line_signal.signal_type == 'return':
                        return line_signal
            else:
                elif_executed = False
                for elif_module in line.attributes['sys_elif_modules'].value:
                    elif_expression = solve_expression(elif_module.attributes['sys_expression_for_judging'],
                                                       runtime_memory, lib, debugger)
                    if elif_expression.concept_name == 'sys_True':
                        for elif_line in elif_module.attributes['sys_elif_block'].agi_list().value:
                            try:
                                line_signal = process_line(elif_line, runtime_memory, lib,
                                                           debugger)
                            except DynamicCodeException as d:
                                d.line_cache = to_int(elif_line.attributes['sys_line_index'])
                                raise
                            except LineException:
                                raise
                            if line_signal.signal_type == 'break':
                                return LineSignal('break')
                            if line_signal.signal_type == 'return':
                                return line_signal
                        elif_executed = True
                        break
                if not elif_executed:
                    for else_line in line.attributes['sys_else_block'].agi_list().value:
                        try:
                            line_signal = process_line(else_line, runtime_memory, lib, debugger)
                        except DynamicCodeException as d:
                            d.line_cache = to_int(else_line.attributes['sys_line_index'])
                            raise
                        except LineException:
                            raise
                        if line_signal.signal_type == 'break':
                            return LineSignal('break')
                        if line_signal.signal_type == 'return':
                            return line_signal
            return LineSignal('normal')
        if line.concept_name == 'sys_append':
            target_list = solve_expression(line.attributes['sys_target_list'], runtime_memory,
                                           lib, debugger)
            element = solve_expression(line.attributes['sys_element'], runtime_memory, lib,
                                       debugger)
            if type(target_list) == AGIObject:
                target_list = target_list.agi_list()
            else:
                assert type(target_list) == AGIList
            target_list.append(element)
            return LineSignal('normal')
        if line.concept_name == 'sys_remove':
            target_list = solve_expression(line.attributes['sys_target_list'], runtime_memory,
                                           lib, debugger)
            if type(target_list) == AGIObject:
                target_list = target_list.agi_list()
            else:
                assert type(target_list) == AGIList
            while True:
                element_pos = find_element(target_list, line.attributes['sys_expression_for_constraint'],
                                           runtime_memory, lib, debugger)
                if element_pos == -1:
                    break
                target_list.remove(element_pos)
            return LineSignal('normal')
        if line.concept_name == 'sys_request':
            for reg_id in line.attributes['sys_requested_registers'].value:
                reg_id_int = to_int(reg_id)
                raw_input = input('Dynamic code asks you to fill in reg' + str(reg_id_int) + '!\n')
                if raw_input.isdigit():
                    input_object = int_obj(int(raw_input))
                else:
                    assert False
                if not runtime_memory.has_reg(reg_id_int):
                    runtime_memory.create_reg(reg_id_int, input_object)
                else:
                    runtime_memory.set_reg(reg_id_int, input_object)
            for provided_line in line.attributes['sys_provided_block'].agi_list().value:
                try:
                    line_signal = process_line(provided_line, runtime_memory, lib, debugger)
                except DynamicCodeException as d:
                    d.line_cache = to_int(provided_line.attributes['sys_line_index'])
                    raise
                except LineException:
                    raise
                assert line_signal.signal_type != 'break'
                if line_signal.signal_type == 'return':
                    return line_signal
            bool_result = solve_expression(line.attributes['sys_expression_for_constraint'],
                                      runtime_memory, lib, debugger).concept_name
            if bool_result != 'sys_True':
                assert bool_result == 'sys_False'
                raise LineException(to_int(line.attributes['sys_line_index']),
                                'Your inputs do not satisfy the constraints.')
            return LineSignal('normal')
        if line.concept_name == 'sys_call_none_return_func':
            function_name = line.attributes['sys_function_name'].concept_name
            function_params = list()
            for param in line.attributes['sys_function_params'].value:
                function_params.append(solve_expression(param, runtime_memory, lib, debugger))
            function_params = AGIList(False, function_params)
            if function_name not in system_function_dict.keys():
                try:
                    if type(debugger.debug_signal) == int or debugger.debug_signal == 'step_over' or debugger.debug_signal == 'step_out':
                        nDebug = True
                    else:
                        nDebug = False
                    result = run_dynamic_function(function_name, function_params, lib, nDebug)
                except DynamicCodeException as d:
                    d.line_cache = to_int(line.attributes['sys_line_index'])
                    raise
            else:
                try:
                    if function_name == 'sys_func_run_function_object':
                        function_object = function_params.get_element(0)
                        test_function_params = function_params.get_element(1)
                        if type(test_function_params) == AGIObject:
                            test_function_params = test_function_params.agi_list()
                        result = run_dynamic_function(function_object, test_function_params, lib)
                    else:
                        result = run_system_function(function_name, function_params)
                except HardcodedCodeException as h:
                    h.line = to_int(line.attributes['sys_line_index'])
                    raise
                except DynamicCodeException as d:
                    raise
            assert result.concept_name == 'None'
            return LineSignal('normal')
        print(line.concept_name)
        assert False
    except ExpressionException as e:
        raise LineException(to_int(line.attributes['sys_line_index']), e.description)
    except StructureException as s:
        raise LineException(to_int(line.attributes['sys_line_index']), s.description)
    except DynamicCodeException as d:
        if d.line_cache is None:
            d.line_cache = to_int(line.attributes['sys_line_index'])
        raise
    except HardcodedCodeException as h:
        h.line = to_int(line.attributes['sys_line_index'])
        raise
    except LineException:
        raise


def run_dynamic_function(function_name_or_object: str or AGIObject, input_params: AGIList, lib,
                         nDebug=False) -> AGIObject:
    if type(function_name_or_object) == str:
        function_object = lib.get_code(function_name_or_object)
    else:
        function_object = function_name_or_object
    runtime_memory = RuntimeMemory()
    for i, input_param in enumerate(input_params.value):
        runtime_memory.inputs.append(Input(i, input_param))
    debugger = Debugger(function_name_or_object, function_object, runtime_memory)
    if nDebug:
        debugger.debug_signal = 'step_out'
    for line in function_object.agi_list().value:
        try:
            line_signal = process_line(line, runtime_memory, lib, debugger)
        except LineException as l:
            raise DynamicCodeException(DynamicExceptionInfo(function_name_or_object,
                                                            input_params.value, l.line, runtime_memory), l.description)
        except DynamicCodeException as d:
            d.call_stacks.append(
                DynamicExceptionInfo(function_name_or_object, input_params.value, d.line_cache, runtime_memory))
            d.line_cache = None
            raise
        except HardcodedCodeException as h:
            d = DynamicCodeException(HardcodedExceptionInfo(h.function_name), h.description)
            d.call_stacks.append(
                DynamicExceptionInfo(function_name_or_object, input_params.value, h.line, runtime_memory))
            raise d
        assert line_signal.signal_type != 'break'
        if line_signal.signal_type == 'return':
            return line_signal.signal_value
    return AGIObject('sys_None', True)

