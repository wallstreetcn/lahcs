import re
from functools import total_ordering


class FieldParseError(Exception):
    '''Exception type for Field Inner'''
    def __init__(self, reason):
        super().__init__(reason)


class FieldError(Exception):
    '''Some kind of problem with a model field.'''
    def __init__(self, fieldname, restline, reason):
        super().__init__(fieldname, restline, reason)



@total_ordering
class BaseField(object):
    '''Base class for all field types'''

    # These track each time a Field instance is created. Used to retain order
    creation_counter = 0

    def __init__(self):
        BaseField.creation_counter += 1
        self.creation_counter = BaseField.creation_counter

    def __eq__(self, other):
        # Needed for @total_ordering
        if isinstance(other, BaseField):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, BaseField):
            return self.creation_counter < other.creation_counter
        return NotImplemented





class ReadField(BaseField):
    '''Base class for all read field types'''
    pass


class StandardField(ReadField):
    '''Field type for Standard data format like csv ...'''
    pass


class RegexField(ReadField):
    '''Field with a regex to define the border and content of it. '''

    def __init__(self, regex, index=1):
        '''
            regex: the regex express to define the border of the field
            index: the index of content in the matched groups
        '''
        super().__init__()

        self.reg_str = regex
        self.reg_compiled = re.compile(regex)
        self.reg_index = index

    def __str__(self):
        return 'read.%s(/%s/)' % (self.__class__.__name__, self.reg_str)


    def extract(self, rest):
        '''extract this field from the rest of line
           return: content, length
                   where content is the extracted string, 
                   length is the length of the matched string

        '''
        m = self.reg_compiled.match(rest)
        if not m:
            raise FieldParseError('Rest of line do not match with field regex')

        try:
            content = m.group(self.reg_index)
        except IndexError:
            raise FieldParseError('Group index is invalid for field regex')

        return content, m.end()



class StringField(RegexField):
    '''Field of String, with split char for front and end. '''

    def __init__(self, end, front=''):
        '''
            end: spliter at the end of the field
            front: string at the begging of the field
        '''

        if end:
            regex = '%s([^%s]*)%s' % ( re.escape(front), re.escape(end[0]), re.escape(end) )
        else:
            regex = '%s(.*)' % ( re.escape(front), )

        super().__init__(regex)






class WriteField(BaseField):
    '''Base class for all write field types'''
    pass


