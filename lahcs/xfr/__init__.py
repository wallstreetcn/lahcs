
class BaseXfr(Object):
    def transform(d, out):
        raise NotImplementedError()



class DefaultXfr(BaseXfr):
    def transform(d, out):
        out.put(d)

