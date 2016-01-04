from functools import total_ordering

from lahcs.core.exceptions import FieldError



class BaseField(object):
    '''Base class for all field types'''

    # These track each time a Field instance is created. Used to retain order
    creation_counter = 0

    def __init__(self):
        BaseField.creation_counter += 1
        self.creation_counter = BaseField.creation_counter



class BaseReadField(BaseField):
    '''
        Base class for all read field types.
        This is an abstract class
        abstract members:
            field_reg_str
            field_reg_compiled
            field_reg_index

    '''

    def __str__(self):
        return 'fields.read.%s(%s)' % (self.__class__.__name__, self.field_reg_str)


    def extract(self, rest):
        '''extract this field from the rest of line
           return: content, length
                   where content is the extracted string, 
                   length is the length of the matched string

        '''
        m = field_reg_compiled.match(rest)
        if not m:
            raise FieldError()

        return m.group(self.field_reg_index), m.end()


class Field(BaseReadField):
    '''Standerd read field.
    '''
    
    




