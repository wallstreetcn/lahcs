import csv

from fields import (BaseField, ReadField, StandardField, RegexField, StringField, WriteField, 
                    FieldParseError, FieldError,  )


class BaseModel(Object):
    '''Base type for all model types'''
    _FIELD_TYPE = BaseField

    def __init__(self):
        namedfields = [ (k, v)  for k, v in self.__dict__.items() if isinstance(v, BaseField) ]
        namedfields.sort(key=lambda x: x[1])

        for name, field in namedfields):
            if not isinstance(field, self._FIELD_TYPE):
                raise JobConfigError( 'model %s only accept %s as field type, %s is recognized as %s' 
                             % (self.__class__.__name__, self._FIELD_TYPE.__name__, name, field.__class__.__name__))

        self.namedfields = namedfields


class ReadModel(BaseModel):
    '''Base type for all read models '''
    _FIELD_TYPE = ReadField

    def _parse(self, line):
        raise NotImplementedError()


class TextReadModel(ReadModel):
    _FIELD_TYPE = RegexField
    OPEN_ENDING = False

    def _parse(self, line):
        d = {}
        rest = line
        for name, field in self.namedfields:
            try:
                field_content, cost_length = field.extract(rest)
            except FieldParseError as e:
                reason, = e.args
                raise FieldError(name, rest, reason)

            d[name] = field_content
            rest = rest[cost_length: ]

        if not self.OPEN_ENDING and rest != '' and rest != '\n' :
            raise FieldError('$', rest, 'line is not fully matched')

        return d


class CsvReadModel(ReadModel):
    _FIELD_TYPE = StandardField

    def _parse(self, line):
        row = next(csv.reader([line]))
        if len(row) != len(self.namedfields):
            raise FieldError('-', line, 'field number is not fully matched')

        d = { name: content for content, (name, filed) in zip(row, self.namedfields) }
        return d


class WriteModel(BaseModel):
    '''Base type for all write models '''
    _FIELD_TYPE = WriteField

    def _parse(self, row):
        raise NotImplementedError()

    




