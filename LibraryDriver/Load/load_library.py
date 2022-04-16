import pickle
import os
from LibraryDriver.struct import Concepts


class Library:
    def __init__(self, directory):
        self.directory = directory
        self.concepts = self.load_concepts()
        functions = self.load_functions()
        attributes = self.load_attributes()
        for concept_name in functions.keys():
            self.concepts.get_concept(concept_name).attributes = functions[concept_name]
        for concept_name in attributes.keys():
            self.concepts.get_concept(concept_name).attributes = attributes[concept_name]

    def load_concepts(self):
        file = open(self.directory + '/concepts.txt', 'rb')
        concepts = pickle.load(file)
        assert type(concepts) == Concepts
        file.close()
        return concepts

    def load_attributes(self):
        file = open(self.directory + '/attributes.txt', 'rb')
        attributes = pickle.load(file)
        file.close()
        return attributes

    def load_functions(self):
        file_names = os.listdir(self.directory + '/Functions')
        functions = dict()
        for file_name in file_names:
            assert file_name[-4:] == '.txt'
            file = open(self.directory + '/Functions/' + file_name, 'rb')
            functions.update({file_name[:-4]: pickle.load(file)})
            file.close()
        return functions
