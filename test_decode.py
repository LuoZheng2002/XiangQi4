from Decode.decode_functions import print_code_default
from Exception.agi_exception import AGIException

try:
    print_code_default('Workspace/Processed', 'test')
except AGIException as e:
    e.show()