'''
Global Django exception and warning classes.
'''

class FieldError(Exception):
    '''Some kind of problem with a model field.'''
    pass