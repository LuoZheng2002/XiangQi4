from SystemConcept.struct import SystemConcept


system_concepts = [
    SystemConcept('sys_None'),
    SystemConcept('sys_True'),
    SystemConcept('sys_False'),
    SystemConcept('sys_Fail'),
    SystemConcept('sys_integer'),
    SystemConcept('sys_string'),
    SystemConcept('sys_')
]

system_concept_list = list()
for system_concept in system_concepts:
    system_concept_list.append(system_concept.concept_name)

