import datetime

class Log:
    def _t():
        return datetime.datetime.now().strftime('%H:%M:%S.%f')

class ConsoleLog(Log):
    DEFAULT = '\033[0m'
    BLACK = '\033[30m'
    DARKRED = '\033[31m'
    DARKGREEN = '\033[32m'
    DARKYELLOW = '\033[33m'
    DARKGRAY = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    ERR = RED
    BGERR = BG_RED+BLACK
    WARN = YELLOW
    HIGHLIGHT = BG_YELLOW+BLACK

    def highlight(message):
        try:
            print(f'{ConsoleLog.DARKGRAY}{Log._t()} {ConsoleLog.HIGHLIGHT}{message}', end='')
        finally:
            print(f'{ConsoleLog.DEFAULT}')

    def verbose(message):
        try:
            print(f'{ConsoleLog.DARKGRAY}{Log._t()} VERBOSE: {message}', end='')
        finally:
            print(f'{ConsoleLog.DEFAULT}')

    def info(message):
        try:
            print(f'{ConsoleLog.DARKGRAY}{Log._t()} {ConsoleLog.DEFAULT}INFO: {message}', end='')
        finally:
            print(f'{ConsoleLog.DEFAULT}')

    def warn(message):
        try:
            print(f'{ConsoleLog.DARKGRAY}{Log._t()} {ConsoleLog.WARN}WARNING: {message}', end='')
        finally:
            print(f'{ConsoleLog.DEFAULT}')

    def error(message):
        try:
            print(f'{ConsoleLog.DARKGRAY}{Log._t()} {ConsoleLog.ERR}ERROR: {message}', end='')
        finally:
            print(f'{ConsoleLog.DEFAULT}')
