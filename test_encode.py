from Encode.encode_functions import encode_function
from Exception.agi_exception import AGIException
import os
try:
    for function_name in os.listdir('Workspace'):
        encode_function('Workspace', function_name[:-4], 'Library/Functions')
except AGIException as e:
    e.show()
