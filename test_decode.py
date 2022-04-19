from Decode.decode_functions import print_code_default
from Exception.agi_exception import AGIException

try:
    function_name = input('Please input function name.\n')
    print_code_default('Library/Functions', function_name)
except AGIException as e:
    e.show()