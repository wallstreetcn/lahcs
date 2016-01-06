
class BaseXfr(object):
    def transform(self, d, out):
        raise NotImplementedError()


class DefaultXfr(BaseXfr):
    def transform(self, d, out):
        out.put(d)

