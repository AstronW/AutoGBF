# import datetime
import logging
import logging.handlers
import os
import sys


def empty_function(*args, **kwargs):
    pass


# cnocr will set root logger in cnocr.utils
# Delete logging.basicConfig to avoid logging the same message twice.
logging.basicConfig = empty_function
logging.raiseExceptions = True  # Set True if wanna see encode errors on console


# Logger init
logger_debug = True

logger = logging.getLogger('autogbf')
logger.setLevel(logging.DEBUG if logger_debug else logging.INFO)
# .%(msecs)03d
file_formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_formatter = logging.Formatter(
    fmt='%(asctime)s │ %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Add console logger
console = logging.StreamHandler(stream=sys.stdout)
console.setLevel(logging.INFO)
console.setFormatter(console_formatter)
console.flush = sys.stdout.flush
logger.addHandler(console)

# Ensure running in Alas root folder
os.chdir(os.path.join(os.path.dirname(__file__), '../'))

# Add file logger
pyw_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]


log_file = './logs/autogbf'
file_hdlr = logging.handlers.TimedRotatingFileHandler(filename=log_file, when='MIDNIGHT', interval=1,
                                                      backupCount=7, encoding='utf-8')
file_hdlr.setLevel(logging.DEBUG)
file_hdlr.setFormatter(file_formatter)
logger.addHandler(file_hdlr)


def hr(title, level=3):
    title = str(title).upper()
    if level == 1:
        logger.info('═')
        logger.info(title)
    if level == 2:
        logger.info('─')
        logger.info(title)
    if level == 3:
        logger.info(title)
    if level == 0:
        logger.info('═')
        logger.info(title)
        logger.info('═')


def attr(name, text):
    logger.info('[%s] %s' % (str(name), str(text)))


def attr_align(name, text, front='', align=22):
    name = str(name).rjust(align)
    if front:
        name = front + name[len(front):]
    logger.info('%s: %s' % (name, str(text)))


def show():
    logger.info('INFO')
    logger.warning('WARNING')
    logger.debug('DEBUG')
    logger.error('ERROR')
    logger.critical('CRITICAL')
    logger.hr('hr0', 0)
    logger.hr('hr1', 1)
    logger.hr('hr2', 2)
    logger.hr('hr3', 3)
    logger.info(r'Brace { [ ( ) ] }')
    logger.info(r'True, False, None')
    logger.info(r'E:/path\\to/alas/alas.exe, /root/alas/, ./relative/path/log.txt')
    # local_var1 = 'This is local variable'
    # Line before exception
    raise Exception("Exception")
    # Line below exception


def error_convert(func):
    def error_wrapper(msg, *args, **kwargs):
        if isinstance(msg, Exception):
            msg = f'{type(msg).__name__}: {msg}'
        return func(msg, *args, **kwargs)

    return error_wrapper


logger.error = error_convert(logger.error)
logger.hr = hr
logger.attr = attr
logger.attr_align = attr_align
logger.print = print
COUNT_CHARS = 43
CENTER_COUNT_CHARS = (COUNT_CHARS - 5)
print("=" * COUNT_CHARS)
print(" " * CENTER_COUNT_CHARS + "START" + " " * CENTER_COUNT_CHARS)
print("=" * COUNT_CHARS)
