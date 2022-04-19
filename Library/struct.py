
class ConceptInfo:
    def __init__(self, instance_attributes=None):
        if instance_attributes is None:
            self.instance_attributes = list()
        else:
            self.instance_attributes = instance_attributes
