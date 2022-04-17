from AGI.struct import AGIObject, AGIList
from Exception.hardcoded_code_exception import HardcodedCodeException
from AGI.objects import obj, num_obj, to_integer


def get_dynamic_code_object(params: AGIList, cid_of, dcd):
    code_id = params.get_element(0).concept_id
    return dcd.get_code(code_id)


def remove_element_by_index(params: AGIList, cid_of):
    target_list = params.get_element(0)
    index = params.get_element(1)
    if type(target_list) == AGIObject:
        target_list = target_list.agi_list()
    assert type(target_list) == AGIList
    if target_list.size() == 0:
        raise HardcodedCodeException('empty list', 'func::remove_element_by_index')
    target_list.remove(to_integer(index, cid_of))


# params.get_element(0): object, params.get_element(1): member object
def get_object_member_func(params: AGIList, cid_of) -> AGIObject:
    target_object = params.get_element(0)
    member_object = params.get_element(1)
    assert type(target_object) == AGIObject and type(member_object) == AGIObject
    if not member_object.concept_id in target_object.attributes.keys():
        raise HardcodedCodeException('Can not find target object\'s member!', 'func::get_object_member')
    return target_object.attributes[member_object.concept_id]


# params.get_element(0): object, params.get_element(1): member object, params[2]: value
def set_object_member_func(params: AGIList, cid_of):
    target_object = params.get_element(0)
    member_object = params.get_element(1)
    value = params.get_element(2)
    assert type(target_object) == AGIObject and type(member_object) == AGIObject
    assert member_object.concept_id in target_object.attributes.keys()
    target_object.attributes[member_object.concept_id] = value


#
def remove_element_by_index(params: AGIList, cid_of):
    target_list = params.get_element(0)
    index = params.get_element(1)
    if type(target_list) == AGIObject:
        target_list = target_list.agi_list()
    assert type(target_list) == AGIList
    if target_list.size() == 0:
        raise AGIException('empty list', special_name='index', special_str=str(to_integer(index, cid_of)))
    target_list.remove(to_integer(index, cid_of))


def get_input_object(params: AGIList, cid_of):
    if dynamic_simulator_inputs:
        print('Obtained an input from cache!')
        input_object = num_obj(dynamic_simulator_inputs.pop(0), cid_of)
    else:
        input_object = num_obj(int(input('Dynamic code simulator asks you to input one param.\n')), cid_of)
    return input_object


def create_concept_instance_func(params: AGIList, cid_of):
    assert type(params.get_element(0)) == AGIObject
    concept_id = params.get_element(0).concept_id
    return create_concept_instance(concept_id, cid_of)



# input0: code_id
def is_code_dynamic_func(params: AGIList):
    if params.get_element(0).concept_name in system_function_list:
        return AGIObject('sys_False', False)
    return AGIObject('sys_True', False)