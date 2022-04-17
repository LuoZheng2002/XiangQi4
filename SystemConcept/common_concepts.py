from AGI.struct import AGIObject, AGIList


def int_obj(integer: int) -> AGIObject:
    return AGIObject('sys_integer', False, sys_value=integer)


def to_int(int_object: AGIObject) -> int:
    assert int_object.concept_name == 'sys_integer'
    return int_object.sys_value


def bool_obj(boolean: bool, mutable=True) -> AGIObject:
    if boolean:
        return AGIObject('sys_True', mutable)
    return AGIObject('sys_False', mutable)


def tag_obj(concept_name, mutable=True):
    return AGIObject(concept_name, mutable)
