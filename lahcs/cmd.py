'''
linux like command 
'''

import os
import shutil
from glob import glob


class CmdError(Error):
    pass


def ls(s):
    files = glob(s)
    if not files:
        raise CmdError('No such file or directory: %s' % s)

    return files


