import re
import shutil
from glob import glob

from settings import (DW_ENV, DW_EXTRACT, )
from lahcs.core.exceptions import JobConfigError, ExcutingError, SHEvaluationError
from lahcs import utils

class Terminal(object):
    def __init__(self, sa_id, tbl_id):
        self.sa_id = sa_id
        self.tbl_id = tbl_id


class SourceTerminal(Terminal):
    def _split_src_list(self, src_list):
        return re.split(r'\s+', src_list.strip())

    def extract(self, **kwargs):
        raise NotImplementedError() 


class TargetTerminal(Terminal):
    def load(self, **kwargs):
        raise NotImplementedError() 


class DatabaseTerminal(SourceTerminal, TargetTerminal):
    def execute(self, sql):
        raise NotImplementedError()


class MysqlTerminal(DatabaseTerminal):
    pass


class HiveTerminal(DatabaseTerminal):
    pass


class FileTerminal(SourceTerminal):
    def extract(self, src_lists, seq_num):
        '''
        src_list is a line like this:
        ---
        1 ${DW_LAND}/sa_id/files*.dat
        '''
        logger = logging.getLogger('lahcs.core.terminal.file')

        src_files = []
        tar_files = []

        for src_list in src_lists:
            src_params = self._split_src_list(src_list)
            if len(src_params) < 2:
                raise JobConfigError('sources.lis error: %s' % src_list)

            try:
                filepath = utils.sh_envaluate(src_params[1], DW_ENV)
            except SHEvaluationError as e:
                raise ExcutingError('sources.lis error: %s' % str(e)

            fileglobs = glob(filepath)
            if not fileglobs:
                raise ExcutingError('sources.lis error: %s , item not match with any files' % src_list)

            for fg in fileglobs:
                if not os.path.isfile(fg):
                    raise ExcutingError('sources.lis error: %s is not valid file' % fg)
                if fg not in files:
                    src_files.append(fg)

        try:
            for i, src_file in enumerate(src_files):
                tar_file = os.path.join(DW_EXTRACT, self.sa_id, '%s.%d.dat.%d' % (self.tbl_id, i, seq_num))
                if os.path.exists(tar_file):
                    raise ExcutingError('file operation error: %s already exists' % tar_file)

                shutil.move(src_file, tar_file)
                tar_files.append(tar_file)
                logger.info('move file: %s %s' % (src_file, tar_file))

        except Exception as e:
            for src_file, tar_file in reversed(list(zip(src_files, tar_files))):
                if os.path.exists(src_file):
                    raise ExcutingError('rollback error: %s already exists' % src_file)

                shutil.move(tar_file, src_file)
                logger.info('rollback file: %s %s' % (tar_file, src_file))





