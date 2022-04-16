from Encode.encode_functions import encode_function
from Exception.agi_exception import AGIException

try:
    encode_function('Workspace/Raw', 'test', 'Workspace/Processed')
except AGIException as e:
    e.show()