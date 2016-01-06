import csv
import io

from .fields import (BaseField, ReadField, StandardField, RegexField, StringField, WriteField, 
                    FieldParseError, FieldError,  )


class BaseModel(object):
    '''Base type for all model types'''
    _FIELD_TYPE = BaseField

    def __init__(self):
        _named_fields = [ (k, v)  for k, v in self.__class__.__dict__.items() if isinstance(v, BaseField) ]
        _named_fields.sort(key=lambda x: x[1])

        for name, field in _named_fields:
            if not isinstance(field, self._FIELD_TYPE):
                raise JobConfigError( 'model %s only accept %s as field type, %s is recognized as %s' 
                             % (self.__class__.__name__, self._FIELD_TYPE.__name__, name, field.__class__.__name__))

        self._named_fields = _named_fields


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
        for name, field in self._named_fields:
            try:
                field_content, cost_length = field.extract(rest)
            except FieldParseError as e:
                reason, = e.args
                raise FieldError(name, rest, reason)

            d[name] = field_content
            rest = rest[cost_length: ]

        if not self.OPEN_ENDING and rest != '' :
            raise FieldError('$', rest, 'line is not fully matched')

        return d


class CsvReadModel(ReadModel):
    _FIELD_TYPE = StandardField

    def _parse(self, line):
        row = next(csv.reader([line]))

        if len(row) != len(self._named_fields):
            raise FieldError('-', line, 'field number is not fully matched')

        d = { name: content for content, (name, filed) in zip(row, self._named_fields) }
        return d


class WriteModel(BaseModel):
    '''Base type for all write models '''
    _FIELD_TYPE = WriteField

    def _form_contents(self, d):
        contents = []
        for name, field in self._named_fields:
            try:
                contents.append(field.dump(d[name]))
            except FieldParseError as e:
                reason, = e.args
                raise FieldError(name, str(d[name]), reason)
        return contents

    def _parse(self, d):
        raise NotImplementedError()


class TextWriteModel(WriteModel):
    '''Text Write Model'''
    DELIMITER = '\x01'

    def _parse(self, d):
        return self.DELIMITER.join(self._form_contents(d)) + '\n'

class CsvWriteModel(WriteModel):
    '''Csv Write Model'''

    def _parse(self, d):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(self._form_contents(d))
        return buffer.getvalue()
    




