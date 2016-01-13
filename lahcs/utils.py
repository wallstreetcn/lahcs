import logging
import re

from lahcs import settings
from lahcs.core.exceptions import SHEvaluationError


############################################
######   logger setting
############################################

def set_logger(logname, screen=True, logpath=None):
    logger = logging.getLogger(logname)
    logger.setLevel(settings.LOG_LEVEL)
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s')

    if screen:
        ch = logging.StreamHandler()
        ch.setLevel(settings.LOG_LEVEL)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if logpath:
        fh = logging.FileHandler(logpath)
        fh.setLevel(settings.LOG_LEVEL)
        fh.setFormatter(formatter)
        logger.addHandler(fh)


def sh_envaluate(s, *envs, strict=True):
    '''
    replace parameter ${XX} in the string s
    envs: list of dicts
    strict: if True, each parameter will be set, or evaluation will fail
            else, if parameter not set, default will be ''
    '''
    if len(envs) == 1:
        env = envs[0]
    else:
        env = {}
        for e in envs:
            env.update(e)

    reg = re.compile(r'\$\{([a-zA-Z_]\w*)\}')
    v = ''

    while True:
        search = reg.search(s)
        if not search:
            v += s
            break

        start, end = search.span()
        name = search.group(1)

        if name not in env:
            if strict:
                raise SHEvaluationError('parameter ${%s} is invalid' % name)
            else:
                value = ''
        else:
            value = str(env[name])

        v += s[:start] + value
        s = s[end:]

    return v




