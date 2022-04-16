import pickle


def encode_concepts(raw_directory, processed_directory):
    file = open(raw_directory, 'r')
    content = file.read()
    file.close()
    concept_names = list()
    while content.find('\n') != -1:
        return_pos = content.find('\n')
        concept_name = content[:return_pos]
        if concept_name != '':
            concept_names.append(concept_name)
        content = content[return_pos + 1:]
    file = open(processed_directory, 'wb')
    pickle.dump(concept_names, file)
    file.close()
    print('Successfully encoded concepts!')

