class SystemConcept:
    def __init__(self, concept_name, concept_instance_attributes=None):
        self.concept_name = concept_name
        if concept_instance_attributes is not None:
            self.concept_instance_attributes = concept_instance_attributes
        else:
            self.concept_instance_attributes = list()

