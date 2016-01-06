import re
import decimal
import datetime
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
    _creation_counter = 0

    def __init__(self):
        BaseField._creation_counter += 1
        self.creation_counter = BaseField._creation_counter

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
    
    def dump(self, content):
        raise NotImplementedError()


class String(WriteField):
    '''String Write Field. '''

    def __init__(self, max_length=-1, null=True, regex=None, check=None):
        super().__init__()

        self.max_length = max_length
        self.null = null
        self.regex_str = regex
        self.regex_compiled = re.compile(regex) if regex else None
        self.check = check

    def dump(self, content):
        if isinstance(content, str):
            if self.max_length >= 0 and len(content) > self.max_length:
                raise FieldParseError('content length exceed the max_length of String field')
            if not self.null and not content:
                raise FieldParseError('content is null while String field is not allowed')
            if self.regex_compiled and not self.regex_compiled.match(content):
                raise FieldParseError('content not match with regex of String field')
            if self.check and not self.check(number):
                raise FieldParseError('content do not accepted by user defined function' )
            return content

        elif self.null and content is None:
            return ''

        raise FieldParseError('content type %s for String field' % content.__class__.__name__)


class BaseIntegerWriteField(WriteField):
    '''Base type for all integer write filed'''
    SIGNED_INTEGER_RANGE = (0, 0)
    UNSIGNED_INTEGER_RANGE = (0, 0)

    def __init__(self, null=True, unsigned=False, check=None):
        super().__init__()

        self.null = null
        self.unsigned = unsigned
        self.check = check

    def dump(self, content):
        if isinstance(content, str):
            if not content:
                if self.null:
                    number = None
                else:
                    raise FieldParseError('content is null while null is not allowed')
            else:
                try: 
                    number = int(content)
                except ValueError:
                    raise FieldParseError('content is not a valid integer')

        elif isinstance(content, int):
            number = content

        elif content is None:
            if self.null:
                number = content
            else:
                raise FieldParseError('content is null while null is not allowed')

        else:
            raise FieldParseError('content type %s for Integer Field' % content.__class__.__name__)

        if self.check and not self.check(number):
            raise FieldParseError('content do not accepted by user defined function' )

        if number is None:
            return ''

        if self.unsigned:
            if not( self.UNSIGNED_INTEGER_RANGE[0] <= number <= self.UNSIGNED_INTEGER_RANGE[1] ): 
               raise FieldParseError('number exceed range of unsigned %s' % self.__class__.__name__ )
        else:
            if not( self.SIGNED_INTEGER_RANGE[0] <= number <= self.SIGNED_INTEGER_RANGE[1] ): 
               raise FieldParseError('number exceed range of %s' % self.__class__.__name__ )

        return str(number)


class TinyInt(BaseIntegerWriteField):
    '''tinyint'''
    SIGNED_INTEGER_RANGE = (-2**7, 2**7-1)
    UNSIGNED_INTEGER_RANGE = (0, 2**8)


class SmallInt(BaseIntegerWriteField):
    '''smallint'''
    SIGNED_INTEGER_RANGE = (-2**15, 2**15-1)
    UNSIGNED_INTEGER_RANGE = (0, 2**16)

class Int(BaseIntegerWriteField):
    '''Int, Integer'''
    SIGNED_INTEGER_RANGE = (-2**31, 2**31-1)
    UNSIGNED_INTEGER_RANGE = (0, 2**32)   

class BigInt(BaseIntegerWriteField):
    SIGNED_INTEGER_RANGE = (-2**63, 2**63-1)
    UNSIGNED_INTEGER_RANGE = (0, 2**64)


class BaseFloatWriteField(WriteField):
    '''Base type for all float write filed'''
    SIGNED_Float_RANGE = (0.0, 0.0)
    UNSIGNED_Float_RANGE = (0.0, 0.0)

    def __init__(self, null=True, unsigned=False, check=None):
        super().__init__()

        self.null = null
        self.unsigned = unsigned
        self.check = check

    def dump(self, content):
        if isinstance(content, str):
            if not content:
                if self.null:
                    number = None
                else:
                    raise FieldParseError('content is null while null is not allowed')
            else:
                try: 
                    number = float(content)
                except ValueError:
                    raise FieldParseError('content is not a valid float')

        elif isinstance(content, float):
            number = content

        elif isinstance(content, int):
            number = content

        elif content is None:
            if self.null:
                number = content
            else:
                raise FieldParseError('content is null while null is not allowed')

        else:
            raise FieldParseError('content type %s for Float Field' % content.__class__.__name__)

        if self.check and not self.check(number):
            raise FieldParseError('content do not accepted by user defined function' )

        if number is None:
            return ''

        if self.unsigned:
            if not( self.UNSIGNED_Float_RANGE[0] <= number <= self.UNSIGNED_Float_RANGE[1] ): 
               raise FieldParseError('number exceed range of unsigned %s' % self.__class__.__name__ )
        else:
            if not( self.SIGNED_Float_RANGE[0] <= number <= self.SIGNED_Float_RANGE[1] ): 
               raise FieldParseError('number exceed range of %s' % self.__class__.__name__ )

        return str(number)

class Float(BaseFloatWriteField):
    '''Float'''
    SIGNED_Float_RANGE   = (-3.402823466e+38, 3.402823466e+38)
    UNSIGNED_Float_RANGE = (0.0, 3.402823466e+38)

class Double(BaseFloatWriteField):
    '''Double'''
    SIGNED_Float_RANGE   = (-1.7976931348623157e+308, 1.7976931348623157e+308)
    UNSIGNED_Float_RANGE = (0.0, 1.7976931348623157e+308)


class Decimal(WriteField):
    '''Decimal'''
    def __init__(self, m, d, null=True, unsigned=False, check=None):
        super().__init__()

        assert m >= d
        self.m = m
        self.d = d
        self.null = null
        self.unsigned = unsigned
        self.check = check

    def dump(self, content):
        if isinstance(content, str):
            if not content:
                if self.null:
                    number = None
                else:
                    raise FieldParseError('content is null while null is not allowed')
            else:
                try: 
                    number = decimal.Decimal(content)
                except decimal.InvalidOperation:
                    raise FieldParseError('content is not a valid decimal')

        elif isinstance(content, float):
            number = content

        elif isinstance(content, int):
            number = content

        elif content is None:
            if self.null:
                number = content
            else:
                raise FieldParseError('content is null while null is not allowed')

        else:
            raise FieldParseError('content type %s for Decimal Field' % content.__class__.__name__)

        if self.check and not self.check(number):
            raise FieldParseError('content do not accepted by user defined function' )

        if number is None:
            return ''

        if self.unsigned and number < 0:
            raise FieldParseError('number exceed range of unsigned %s' % self.__class__.__name__ )

        if abs(int(number)) >= 10**(m-d):
            raise FieldParseError('number exceed range of %s' % self.__class__.__name__ )

        return str(number)


class Date(WriteField):
    '''Date'''
    def __init__(self, null=True, format='%Y-%m-%d', check=None):
        super().__init__()

        self.null = null
        self.format = format
        self.check = check

    def dump(self, content):
        if isinstance(content, str):
            if not content:
                if self.null:
                    dt = None
                else:
                    raise FieldParseError('content is null while null is not allowed')
            else:
                try:
                    dt = datetime.datetime.strptime(content, self.format).date()
                except ValueError:
                    raise FieldParseError('content is not a valid date')

        elif isinstance(content, datetime.date):
            dt = content

        elif content is None:
            if self.null:
                dt = content
            else:
                raise FieldParseError('content is null while null is not allowed')

        else:
            raise FieldParseError('content type %s for Date Field' % content.__class__.__name__)

        if self.check and not self.check(dt):
            raise FieldParseError('content do not accepted by user defined function' )

        if dt is None:
            return ''

        return dt.strftime('%Y-%m-%d')


class Timestamp(WriteField):
    '''Timestamp'''
    def __init__(self, null=True, format='%Y-%m-%d %H:%M:%S', check=None):
        super().__init__()

        self.null = null
        self.format = format
        self.check = check

    def dump(self, content):
        if isinstance(content, str):
            if not content:
                if self.null:
                    ts = None
                else:
                    raise FieldParseError('content is null while null is not allowed')
            else:
                try:
                    ts = datetime.datetime.strptime(content, self.format)
                except ValueError:
                    raise FieldParseError('content is not a valid timestamp')

        elif isinstance(content, datetime.datetime):
            ts = content

        elif content is None:
            if self.null:
                ts = content
            else:
                raise FieldParseError('content is null while null is not allowed')

        else:
            raise FieldParseError('content type %s for Timestamp Field' % content.__class__.__name__)

        if self.check and not self.check(ts):
            raise FieldParseError('content do not accepted by user defined function' )

        if ts is None:
            return ''

        return ts.strftime('%Y-%m-%d %H:%M:%S')



