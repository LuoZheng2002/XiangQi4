class Concepts:
    def __init__(self):
        self.concepts = list()

    def get_concept(self, concept_id):
        for concept in self.concepts:
            if concept.concept_id == concept_id:
                return concept
        assert False
    
    def create_concept(self, concept_name):
        if concept_name[:4] == 'sys_':
            print('SystemConcept name can not start with \'sys_\'!')
            return
        for concept in self.concepts:
            if concept.concept_name == concept_name:
                print('SystemConcept already created!')
                return
        self.concepts.append(Concept(concept_name))
            
    def delete_concept(self, concept_name):
        for i, concept in enumerate(self.concepts):
            if concept.concept_name == concept_name:
                if concept.usages:
                    print('The concept is used by ', end='')
                    for usage in concept.usages:
                        print(usage + ', ', end='')
                    print('and is not safe to delete.')
                    return
                # 去除在其它概念中的使用记录
                for references_concept in concept.references:
                    assert concept.concept_name in references_concept.usages
                    references_concept.usages.remove(concept.concept_name)
                self.concepts.pop(i)
                print('Successfully deleted a concept!')
                return
        print('Can not find target concept.')


class Concept:
    def __init__(self, concept_name):
        self.concept_name = concept_name
        self.references = list()  # 使用的其它的概念
        self.usages = list()  # 被哪些概念使用
        self.attributes = None
        self.function = None


class Attribute:
    def __init__(self, concept_instance_attributes):
        self.concept_instance_attributes = concept_instance_attributes
        self.references = list()
        for attribute in concept_instance_attributes:
            self.references.append(attribute)


class Function:
    def __init__(self, input_param_count, function_code, input_inspection_code, input_declaration, input_roles, output_role, references):
        self.input_param_count = input_param_count
        self.function_code = function_code
        self.input_inspection_code = input_inspection_code
        self.input_declaration = input_declaration
        self.input_roles = input_roles
        self.output_role = output_role
        self.references = references


class InputFeature:
    def __init__(self, is_mutable):
        self.is_mutable = is_mutable
        
