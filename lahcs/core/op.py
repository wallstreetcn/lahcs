from queue import Queue
from collections import OrderedDict

from lahcs import utils
from lahcs.xfr import DefaultXfr, 
from lahcs.models.fields import (FieldError, )


def transform(read_model, write_model, xfr, src_path, tar_path, err_path, logger):
    '''return err_cnt'''

    err_record = OrderedDict()
    def err_put(err_key, err_desc, linum):
        if err_key in err_record:
            err_record[err_key][0] += 1
        else:
            err_record[err_key] = (1, err_desc, linum)

    logger.info('''transform starting ...
        source file: %s
        target file: %s
        error  file: %s
        ''' % (src_path, tar_path, err_path))

    with open(src_path, 'r') as src_file, \
         open(tar_path, 'w') as tar_file, \
         open(err_path, 'w') as err_file :

        out = Queue()
        for linum, line in enumerate(src_file):

            try:
                d = read_model._parse(line)
            except FieldError as e:
                fieldname, restline, reason = e.args
                err_key = '%s - %s' % (fieldname, reason)
                err_desc = '%s - %s : %s' % (fieldname, reason, repr(restline))
                err_put(err_key, err_desc, linum +1)

                err_file.write(line)
                # out = Queue()
                continue

            try:
                xfr.transform(d, out)
            except XfrError as e:
                err_put(repr(e), repr(e), linum +1)

                err_file.write(line)
                out = Queue()
                continue

            outlines = []
            try:
                while not out.empty():
                    w = out.get()
                    outlines.append(write_model._parse(w))
            except FieldError as e:
                fieldname, restline, reason = e.args
                err_key = '%s - %s' % (fieldname, reason)
                err_desc = '%s - %s : %s' % (fieldname, reason, repr(restline))
                err_put(err_key, err_desc, linum +1)

                err_file.write(line)
                out = Queue()
                continue

            tar_file.writelines(outlines)

    err_cnt = sum(cnt for err_key, (cnt, err_desc, linum) in err_record)
    err_explains = '\n'.join('count: %-4d linum: %-4d  %s' % (cnt, linum, err_desc) 
                                for err_key, (cnt, err_desc, linum) in err_record.items())

    logger.info('transform end, error count %d \n%s' % (err_cnt, err_explains))
    return err_cnt








