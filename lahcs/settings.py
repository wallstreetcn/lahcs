import logging
import os


# 日志等级
LOG_LEVEL = logging.DEBUG


# 路径
DW_DIR = '/dw/etl/prod'
DW_EXTRACT = os.path.join(DW_DIR, 'extract')
DW_TMP = os.path.join(DW_DIR, 'tmp')
DW_LAND = os.path.join(DW_DIR, 'land')
DW_HD1 = os.path.join(DW_DIR, 'hd1')

DW_ENV = {
    'DW_DIR': DW_DIR,
    'DW_EXTRACT': DW_EXTRACT,
    'DW_TMP': DW_TMP,
    'DW_HD1': DW_HD1,
}
