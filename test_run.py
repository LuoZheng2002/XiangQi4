from Exception.dynamic_code_exception import DynamicCodeException, show_dynamic_code_exception
from SystemConcept.concept_manager import summon_concepts
from AGI.code_driver import run_dynamic_function
from AGI.struct import AGIObject, AGIList
from AGI.objects import obj, num_obj
from AGI.translate_struct import print_obj
cid_of, cid_reverse = summon_concepts('SystemConcept/concepts.txt')
try:
    result = run_dynamic_function(cid_of['func::test'],
                                  AGIList([num_obj(100, cid_of), num_obj(100, cid_of)]), cid_of, 'Formatted')
    print('result is:')
    print_obj(result, cid_reverse)
except DynamicCodeException as d:
    show_dynamic_code_exception(d, cid_of, cid_reverse)
