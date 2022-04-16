from AGI.struct import AGIObject, AGIList
from AGI.hardcoded_code_getter import get_hardcoded_code
from AGI.code_getter_fundamental import is_code_dynamic
from AGI.runtime_memory import RuntimeMemory, Input
from copy import deepcopy
from Exception.dynamic_code_exception import DynamicCodeException, LineException, DynamicExceptionInfo, \
    HardcodedExceptionInfo, ExpressionException
from Exception.hardcoded_code_exception import HardcodedCodeException
from Exception.structure_exception import StructureException
from AGI.concept_instance_creator import create_concept_instance
from AGI.translate_struct import print_obj
from Hardcoded.is_code_dynamic_func import is_code_dynamic_func
from Hardcoded.run_hardcoded_code_func import run_hardcoded_code_func
from Hardcoded.code_simulator import get_dynamic_code_object
from AGI.dynamic_code_debugger import Debugger, global_given_line, global_given_function
from debug import debug_dynamic_code


def run_hardcoded_code(code_id, input_params: AGIList, dcd):
    if code_id == 'func::is_code_dynamic']:
        result = is_code_dynamic_func(input_params, dcd)
    elif code_id == 'func::run_hardcoded_code']:
        result = run_hardcoded_code_func(input_params, dcd)
    elif code_id == 'func::get_dynamic_code_object']:
        result = get_dynamic_code_object(input_params, dcd)
    else:
        result = get_hardcoded_code(code_id, cid_of)(input_params, cid_of)
    if result is None:
        result = AGIObject('None'])
    return result


class LineSignal:
    def __init__(self, signal_type, signal_value=None):
        self.signal_type = signal_type
        if signal_type == 'return':
            assert signal_value is not None
        self.signal_value = signal_value


def find_element(target_list: AGIList, expr, runtime_memory, dcd, debugger) -> int:
    assert type(target_list) == AGIList
    for i, element in enumerate(target_list.value):
        if solve_expression(expr, runtime_memory, dcd, debugger, element).concept_id == 
                'True']:
            return i
    return -1


def solve_expression(expr: AGIObject, runtime_memory: RuntimeMemory, dcd, debugger,
                     target=None) -> AGIObject or AGIList:
    if expr.concept_id == 'dcr::input']:
        index = to_integer(expr.attributes['dc::index']], cid_of)
        assert runtime_memory.has_input(index)
        return runtime_memory.get_input_value(index)
    if expr.concept_id == 'dcr::reg']:
        index = to_integer(expr.attributes['dc::index']], cid_of)
        if not runtime_memory.has_reg(index):
            raise ExpressionException('Register not created.')
        return runtime_memory.get_reg_value(index)
    if expr.concept_id == 'dcr::iterator']:
        index = to_integer(expr.attributes['dc::index']], cid_of)
        assert runtime_memory.has_iterator(index)
        return num_obj(runtime_memory.get_iterator_value(index), cid_of)
    if expr.concept_id == 'dcr::call']:
        code_id = expr.attributes['dc::function_name']].concept_id
        function_params = list()
        for param in expr.attributes['dc::function_params']].value:
            function_params.append(solve_expression(param, runtime_memory, dcd, debugger, target))
        function_params = AGIList(function_params)
        if is_code_dynamic(code_id, dcd, cid_of):
            try:
                if type(debugger.debug_signal) == int or debugger.debug_signal == 'step_over' or debugger.debug_signal == 'step_out':
                    nDebug = True
                else:
                    nDebug = False
                result = run_dynamic_code(code_id, function_params, dcd, nDebug)
            except DynamicCodeException as d:
                raise
        else:
            try:
                result = run_hardcoded_code(code_id, function_params, dcd)
            except HardcodedCodeException as h:
                raise
        return result
    if expr.concept_id == 'dcr::concept_instance']:
        return create_concept_instance(expr.attributes['dc::concept_name']].concept_id, cid_of)
    if expr.concept_id == 'dcr::size']:
        target_list = solve_expression(expr.attributes['dc::target_list']],
                                       runtime_memory, dcd, debugger, target)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        return num_obj(target_list.size(), cid_of)
    if expr.concept_id == 'dcr::get_member']:
        target_object = solve_expression(expr.attributes['dc::target_object']],
                                         runtime_memory, dcd, debugger, target)
        member_id = expr.attributes['dc::member_name']].concept_id
        if member_id not in target_object.attributes.keys():
            raise ExpressionException('Can not get target object\'s member!')
        return target_object.attributes[member_id]
    if expr.concept_id == 'dcr::at']:
        target_list = solve_expression(expr.attributes['dc::target_list']],
                                       runtime_memory, dcd, debugger, target)
        index = to_integer(solve_expression(expr.attributes['dc::element_index']],
                                            runtime_memory, dcd, debugger, target), cid_of)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        return target_list.get_element(index)
    if expr.concept_id == 'dcr::find'] or \
            expr.concept_id == 'dcr::exist'] or expr.concept_id == 'dcr::count']:
        target_list = solve_expression(expr.attributes['dc::target_list']],
                                       runtime_memory, dcd, debugger, target)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        count = 0
        for element in target_list.value:
            if solve_expression(expr.attributes['dc::expression_for_constraint']],
                                runtime_memory, dcd, debugger, element).concept_id == 
                'True']:
                if expr.concept_id == 'dcr::find']:
                    return element
                if expr.concept_id == 'dcr::exist']:
                    return AGIObject('True'])
                count += 1
        if expr.concept_id == 'dcr::find']:
            raise ExpressionException('Can not find the target element!')
        if expr.concept_id == 'dcr::exist']:
            return AGIObject('False'])
        return num_obj(count, cid_of)
    if expr.concept_id == 'dcr::target']:
        assert target is not None
        return target
    if expr.concept_id == 'dcr::constexpr']:
        return expr.attributes['value']]
    print(expr.concept_id)
    raise ExpressionException('Unknown head of expression!')


def process_line(line: AGIObject, runtime_memory: RuntimeMemory, dcd, debugger) -> LineSignal:
    try:
        if (debug_dynamic_code and debugger.debug_signal != 'step_out') or global_given_function[0] == debugger.code_id:
            line_index = to_integer(line.attributes['dc::line_index']], cid_of)
            if (type(debugger.debug_signal) != int and debugger.debug_signal != 'step_out') \
                    or debugger.debug_signal == line_index \
                    or (global_given_function[0] == debugger.code_id and global_given_line[0] == line_index):
                print('Current function: \'' + debugger.code_id] + '\'')
                for i in range(line_index - 4, line_index + 5):
                    if 1 <= i <= len(debugger.lines):
                        if i == line_index:
                            debugger.print_single_line(i, True)
                        else:
                            debugger.print_single_line(i, False)
                debugger.get_debug_input()
        if line.concept_id == 'dcr::assign'] or line.concept_id == 'dcr::assign_as_reference']:
            rhs_value = solve_expression(line.attributes['dc::right_value']], runtime_memory, cid_of,
                                         dcd, debugger)
            lhs = line.attributes['dc::left_value']]
            if lhs.concept_id == 'dcr::reg']:
                reg_index = to_integer(lhs.attributes['dc::index']], cid_of)
                if not runtime_memory.has_reg(reg_index):
                    if line.concept_id == 'dcr::assign']:
                        runtime_memory.create_reg(reg_index, deepcopy(rhs_value))
                    else:
                        runtime_memory.create_reg(reg_index, rhs_value)
                else:
                    if line.concept_id == 'dcr::assign']:
                        runtime_memory.set_reg(reg_index, deepcopy(rhs_value))
                    else:
                        runtime_memory.set_reg(reg_index, rhs_value)
            elif lhs.concept_id == 'dcr::at']:
                target_list = solve_expression(lhs.attributes['dc::target_list']],
                                               runtime_memory, dcd, debugger)
                element_index = solve_expression(lhs.attributes['dc::element_index']],
                                                 runtime_memory, dcd, debugger)
                if type(target_list) == AGIObject:
                    target_list = target_list.agi_list()
                else:
                    assert type(target_list) == AGIList
                if line.concept_id == 'dcr::assign']:
                    target_list.set_value(to_integer(element_index, cid_of), deepcopy(rhs_value))
                else:
                    target_list.set_value(to_integer(element_index, cid_of), rhs_value)
            elif lhs.concept_id == 'dcr::get_member']:
                target_object = solve_expression(lhs.attributes['dc::target_object']],
                                                 runtime_memory, dcd, debugger)
                assert type(target_object) == AGIObject
                member_id = lhs.attributes['dc::member_name']].concept_id
                assert member_id in target_object.attributes.keys()
                if line.concept_id == 'dcr::assign']:
                    target_object.attributes[member_id] = deepcopy(rhs_value)
                else:
                    target_object.attributes[member_id] = rhs_value
            return LineSignal('normal')
        if line.concept_id == 'dcr::return']:
            return_value = solve_expression(line.attributes['dc::return_value']],
                                            runtime_memory, dcd, debugger)
            return LineSignal('return', return_value)
        if line.concept_id == 'dcr::assert']:
            assert_expression = solve_expression(line.attributes['dc::assert_expression']],
                                                 runtime_memory, dcd, debugger)
            if assert_expression.concept_id != 'True']:
                raise LineException(to_integer(line.attributes['dc::line_index']], cid_of),
                                    'Assertion Failed in Dynamic Code.')
            return LineSignal('normal')
        if line.concept_id == 'dcr::for']:
            iter_id = to_integer(line.attributes['dc::iterator_index']], cid_of)
            if runtime_memory.has_iterator(iter_id):
                iterator = runtime_memory.get_iterator(iter_id)
                iterator.value = 0
            else:
                iterator = runtime_memory.create_iterator(iter_id, 0)
            end_value = to_integer(solve_expression(line.attributes['dc::end_value']],
                                                    runtime_memory, dcd, debugger), cid_of)
            for i in range(end_value):
                for for_line in line.attributes['dc::for_block']].agi_list().value:
                    try:
                        line_signal = process_line(for_line, runtime_memory, dcd, debugger)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(for_line.attributes['dc::line_index']], cid_of)
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
        if line.concept_id == 'dcr::while']:
            loop_count = 0
            while solve_expression(line.attributes['dc::expression_for_judging']],
                                   runtime_memory, dcd, debugger).concept_id == 'True']:
                loop_count += 1
                for while_line in line.attributes['dc::while_block']].agi_list().value:
                    try:
                        line_signal = process_line(while_line, runtime_memory, dcd, debugger)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(while_line.attributes['dc::line_index']], cid_of)
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('normal')
                    if line_signal.signal_type == 'return':
                        return line_signal
                if loop_count == 1000:
                    raise LineException(to_integer(line.attributes['dc::line_index']], cid_of),
                                        'While loop does not stop.')
            return LineSignal('normal')
        if line.concept_id == 'dcr::break']:
            return LineSignal('break')
        if line.concept_id == 'dcr::if']:
            expression_for_judging = solve_expression(line.attributes['dc::expression_for_judging']],
                                                      runtime_memory, dcd, debugger)
            if expression_for_judging.concept_id == 'True']:
                for if_line in line.attributes['dc::if_block']].agi_list().value:
                    try:
                        line_signal = process_line(if_line, runtime_memory, dcd, debugger)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(if_line.attributes['dc::line_index']], cid_of)
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('break')
                    if line_signal.signal_type == 'return':
                        return line_signal
            else:
                elif_executed = False
                for elif_module in line.attributes['dc::elif_modules']].value:
                    elif_expression = solve_expression(elif_module.attributes['dc::expression_for_judging']],
                                                       runtime_memory, dcd, debugger)
                    if elif_expression.concept_id == 'True']:
                        for elif_line in elif_module.attributes['dc::elif_block']].agi_list().value:
                            try:
                                line_signal = process_line(elif_line, runtime_memory, dcd,
                                                           debugger)
                            except DynamicCodeException as d:
                                d.line_cache = to_integer(elif_line.attributes['dc::line_index']], cid_of)
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
                    for else_line in line.attributes['dc::else_block']].agi_list().value:
                        try:
                            line_signal = process_line(else_line, runtime_memory, dcd, debugger)
                        except DynamicCodeException as d:
                            d.line_cache = to_integer(else_line.attributes['dc::line_index']], cid_of)
                            raise
                        except LineException:
                            raise
                        if line_signal.signal_type == 'break':
                            return LineSignal('break')
                        if line_signal.signal_type == 'return':
                            return line_signal
            return LineSignal('normal')
        if line.concept_id == 'dcr::append']:
            target_list = solve_expression(line.attributes['dc::target_list']], runtime_memory, cid_of,
                                           dcd, debugger)
            element = solve_expression(line.attributes['dc::element']], runtime_memory, dcd,
                                       debugger)
            if type(target_list) == AGIObject:
                target_list = target_list.agi_list()
            else:
                assert type(target_list) == AGIList
            target_list.append(element)
            return LineSignal('normal')
        if line.concept_id == 'dcr::remove']:
            target_list = solve_expression(line.attributes['dc::target_list']], runtime_memory, cid_of,
                                           dcd, debugger)
            if type(target_list) == AGIObject:
                target_list = target_list.agi_list()
            else:
                assert type(target_list) == AGIList
            while True:
                element_pos = find_element(target_list, line.attributes['dc::expression_for_constraint']],
                                           runtime_memory, dcd, debugger)
                if element_pos == -1:
                    break
                target_list.remove(element_pos)
            return LineSignal('normal')
        if line.concept_id == 'dcr::request']:
            for reg_id in line.attributes['dc::requested_registers']].value:
                reg_id_int = to_integer(reg_id, cid_of)
                raw_input = input('Dynamic code asks you to fill in reg' + str(reg_id_int) + '!\n')
                if raw_input.isdigit():
                    input_object = num_obj(int(raw_input), cid_of)
                else:
                    assert False
                if not runtime_memory.has_reg(reg_id_int):
                    runtime_memory.create_reg(reg_id_int, input_object)
                else:
                    runtime_memory.set_reg(reg_id_int, input_object)
            for provided_line in line.attributes['dc::provided_block']].agi_list().value:
                try:
                    line_signal = process_line(provided_line, runtime_memory, dcd, debugger)
                except DynamicCodeException as d:
                    d.line_cache = to_integer(provided_line.attributes['dc::line_index']], cid_of)
                    raise
                except LineException:
                    raise
                assert line_signal.signal_type != 'break'
                if line_signal.signal_type == 'return':
                    return line_signal
            if solve_expression(line.attributes['dc::expression_for_constraint']],
                                runtime_memory, dcd, debugger).concept_id != 'True']:
                raise LineException(to_integer(line.attributes['dc::line_index']], cid_of),
                                    'Your inputs do not satisfy the constraints.')
            return LineSignal('normal')
        if line.concept_id == 'dcr::call_none_return_func']:
            code_id = line.attributes['dc::function_name']].concept_id
            function_params = list()
            for param in line.attributes['dc::function_params']].value:
                function_params.append(solve_expression(param, runtime_memory, dcd, debugger))
            function_params = AGIList(function_params)
            if is_code_dynamic(code_id, dcd, cid_of):
                try:
                    if type(debugger.debug_signal) == int or debugger.debug_signal == 'step_over' or debugger.debug_signal == 'step_out':
                        nDebug = True
                    else:
                        nDebug = False
                    result = run_dynamic_code(code_id, function_params, dcd, nDebug)
                except DynamicCodeException as d:
                    d.line_cache = to_integer(line.attributes['dc::line_index']], cid_of)
                    raise

            else:
                try:
                    result = run_hardcoded_code(code_id, function_params, dcd)
                except HardcodedCodeException as h:
                    h.line = to_integer(line.attributes['dc::line_index']], cid_of)
                    raise
            assert result.concept_id == 'None']
            return LineSignal('normal')
        print(line.concept_id)
        assert False
    except ExpressionException as e:
        raise LineException(to_integer(line.attributes['dc::line_index']], cid_of), e.description)
    except StructureException as s:
        raise LineException(to_integer(line.attributes['dc::line_index']], cid_of), s.description)
    except DynamicCodeException as d:
        if d.line_cache is None:
            d.line_cache = to_integer(line.attributes['dc::line_index']], cid_of)
        raise
    except HardcodedCodeException as h:
        h.line = to_integer(line.attributes['dc::line_index']], cid_of)
        raise
    except LineException:
        raise


def run_dynamic_code(code_id: int, input_params: AGIList, dcd, nDebug=False) -> AGIObject:
    code_object = dcd.get_code(code_id)
    runtime_memory = RuntimeMemory()
    for i, input_param in enumerate(input_params.value):
        runtime_memory.inputs.append(Input(i, input_param))
    debugger = Debugger(code_id, code_object, runtime_memory)
    if nDebug:
        debugger.debug_signal = 'step_out'
    for line in code_object.agi_list().value:
        try:
            line_signal = process_line(line, runtime_memory, dcd, debugger)
        except LineException as l:
            raise DynamicCodeException(DynamicExceptionInfo(code_id,
                                                            input_params.value, l.line, runtime_memory), l.description)
        except DynamicCodeException as d:
            d.call_stacks.append(DynamicExceptionInfo(code_id, input_params.value, d.line_cache, runtime_memory))
            d.line_cache = None
            raise
        except HardcodedCodeException as h:
            d = DynamicCodeException(HardcodedExceptionInfo(h.function_name), h.description)
            d.call_stacks.append(DynamicExceptionInfo(code_id, input_params.value, h.line, runtime_memory))
            raise d
        assert line_signal.signal_type != 'break'
        if line_signal.signal_type == 'return':
            return line_signal.signal_value
    return AGIObject('None'])
