from AGI.struct import AGIObject, AGIList
from AGI.objects import obj
from AGI.code_getter_fundamental import is_code_dynamic


# input0: code_id
def is_code_dynamic_func(params: AGIList, cid_of, dir_list):
    assert type(params.get_element(0)) == AGIObject
    code_id = params.get_element(0).concept_id
    if is_code_dynamic(code_id, dir_list, cid_of):
        return obj('True', cid_of)
    return obj('False', cid_of)

