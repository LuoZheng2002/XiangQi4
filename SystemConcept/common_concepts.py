from AGI.struct import AGIObject, AGIList


def int_obj(integer: int) -> AGIObject:
    return AGIObject('sys_integer', False, sys_value=integer)


def to_int(int_object: AGIObject) -> int:
    assert int_object.concept_name == 'sys_integer'
    return int_object.sys_value
