import pickle
from Workspace.Raw.attributes import attributes


def encode_attributes(processed_directory):
    file = open(processed_directory, 'wb')
    pickle.dump(attributes, file)
    file.close()
    print('Successfully encoded attributes!')
