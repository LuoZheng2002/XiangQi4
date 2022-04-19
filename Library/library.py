from Library.concepts import concepts
import os
import pickle


class Library:
    def __init__(self, library_directory):
        self.concepts = concepts
        self.functions = dict()
        for function_name in os.listdir(library_directory + '/Functions'):
            assert function_name[-4:] == '.txt'
            file = open(library_directory + '/Functions/' + function_name, 'rb')
            function_code = pickle.load(file)
            file.close()
            self.functions.update({function_name[:-4]: function_code})

    def get_code(self, function_name):
        return self.functions[function_name]
