import logging
import os
import sys
import datetime
import ctypes
from logging.handlers import TimedRotatingFileHandler
from configuration import *
from PySide6.QtCore import QObject, Signal, Slot

MODULE_NAME = "ingenuity"
DEBUG_MODE = True


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", ctypes.c_uint), ("dwHighDateTime", ctypes.c_uint)]


def precise_time_now():
    """
    Accurate version of time.time() for windows
    """
    # Between Jan 1, 1601 and Jan 1, 1970 there are 11644473600 seconds, so we will just subtract that value
    adjust = int(11644473600 * 1e7)
    file_time = FILETIME()
    ctypes.windll.kernel32.GetSystemTimePreciseAsFileTime(ctypes.byref(file_time))
    quad = (file_time.dwHighDateTime << 32) + file_time.dwLowDateTime
    # remove the diff between 1970 and 1601
    unix = quad - adjust
    # convert back from 100-nanoseconds to seconds
    return unix / 1e7


class TimestampFilter (logging.Filter):
    """
    This is a logging filter which will check for a `timestamp` attribute on a
    given LogRecord, and if present it will override the LogRecord creation time
    to be that of the timestamp (specified as a time.time()-style value).
    This allows one to override the date/time output for log entries by specifying
    `timestamp` in the `extra` option to the logging call.
    """
    def filter(self, record):
        if hasattr(record, 'timestamp'):
            record.created = record.timestamp
        return True


class ConsoleLogger(QObject):

    consoleLog = Signal(str)

    def __init__(self):
        super().__init__()
        self._last_log = ""

    @Slot(str)
    def forward_log(self, log: str):
        self._last_log = log
        self.consoleLog.emit(self._last_log)


console_logger = ConsoleLogger()


class CustomLogger(metaclass=Singleton):

    log = Signal(str)

    def __init__(self, module: str = MODULE_NAME, show_trace: bool = DEBUG_MODE):
        """
        Logger constructor.
        """
        super().__init__()
        # log_formatter = '%(asctime)s.%(msecs)03d %(name)s %(message)s'
        log_formatter = '%(asctime)s.%(msecs)03d %(message)s'
        console_formatter = '%(message)s'
        time_formatter = '%Y-%m-%d %H:%M:%S'

        self.module = module
        self.show_trace = show_trace
        if self.show_trace:
            level = logging.DEBUG
        else:
            level = logging.INFO

        self.max_entries = 5000000
        self.current_entries = 0

        # create file handler
        # RotatingFileHandler
        self._current_log_filename = CustomLogger.namer("")
        self.file_handler = logging.handlers.TimedRotatingFileHandler(self._current_log_filename, when='midnight',
                                                                      interval=1, backupCount=0, encoding="utf-8")
        # create file formatter and add it to the handler
        file_formatter = logging.Formatter(fmt=log_formatter, datefmt=time_formatter)
        self.file_handler.setFormatter(file_formatter)
        self.file_handler.namer = CustomLogger.namer
        self.file_handler.rotator = self.rotator

        # create console handler with a higher log level
        self.console_handler = logging.StreamHandler(stream=sys.stdout)
        # create console formatter and add it to the handler
        console_formatter = logging.Formatter(fmt=console_formatter)
        self.console_handler.setFormatter(console_formatter)

        # get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.WARN)
        # attach handler to root logger and allow logging propagate mechanism to handle all messages
        # otherwise the same event will be logged multiple times
        root_logger.addHandler(self.file_handler)
        root_logger.addHandler(self.console_handler)

        # get simulation child logger, other Python modules will have the default root logger level
        self.logger = logging.getLogger(self.module)  # application
        # set the child logger level, the root logger is created with default level WARNING
        self.logger.setLevel(level)
        time_filter = TimestampFilter()
        self.logger.addFilter(time_filter)
        self.trace("Open log")

    @staticmethod
    def namer(name):
        """
        Returns a filename for the log based on date and time when called.
        :return: the log file name to use
        """
        log_filename = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S_') + LOG_FILENAME

        if not os.path.exists(PATH_LOGS):
            os.makedirs(PATH_LOGS)

        return os.path.join(os.path.abspath(PATH_LOGS), log_filename)

    def rotator(self, source, dest):
        """
        When rotating, rotate the current log.
        If the attribute isn't callable (the default is None), the source
        is simply renamed to the destination.
        :param source: The source filename.
        :param dest:   The destination filename.
        """
        # source is untouched and closed, current file name set to dest.
        self.file_handler.baseFilename = dest
        self.current_entries = 0

    def split_log(self):
        """
        Close the current file and create a new one
        :return:
        """
        self.file_handler.doRollover()

    def close_file(self):
        self.file_handler.close()

    def get_filename(self):
        return self._current_log_filename

    @Slot()
    def log(self, level, msg):
        """
        Log message with defined level
        :param level: event log level
        :param msg: event message
        :return:
        """
        str_level = ""
        timestamp = precise_time_now()
        if level == logging.DEBUG:
            str_level = "Trace"
            self.logger.debug("[{}]: {}".format(str_level, msg), extra={'timestamp': timestamp})
        elif level == logging.INFO:
            str_level = "Info"
            self.logger.info("[{}]: {}".format(str_level, msg), extra={'timestamp': timestamp})
        elif level == logging.WARNING:
            str_level = "Warn"
            self.logger.warning("[{}]: {}".format(str_level, msg), extra={'timestamp': timestamp})
        elif level == logging.ERROR:
            str_level = "Error"
            self.logger.error("[{}]: {}".format(str_level, msg), extra={'timestamp': timestamp})
        elif level == logging.CRITICAL:
            str_level = "SeriousError"
            self.logger.critical("[{}]: {}".format(str_level, msg), extra={'timestamp': timestamp})
        elif level == logging.NOTSET:
            self.logger.critical("{}".format(msg), extra={'timestamp': timestamp})

        from datetime import datetime
        time_formatter = '%Y-%m-%d %H:%M:%S.%f'
        formatted_time = datetime.fromtimestamp(timestamp).strftime(time_formatter)[:-3]
        console_logger.forward_log(f"{formatted_time}: [{str_level}]: {msg}")

        self.current_entries += 1
        if self.current_entries >= self.max_entries:
            self.current_entries = 0
            self.split_log()

    def log_exception(self, exception):
        """
        Log an exception
        :param exception:
        :return:
        """
        self.log(logging.CRITICAL, "An exception has occurred: " + str(exception))
        self.logger.exception(exception, exc_info=True)

    def error(self, msg):
        """
        Log an error
        :param msg: The error message
        :return:
        """
        self.log(logging.ERROR, msg)

    def warn(self, msg):
        """
        Log a warning
        :param msg: the warning message
        :return:
        """
        self.log(logging.WARNING, msg)

    def info(self, msg):
        """
        Log an info
        :param msg: informational message
        :return:
        """
        self.log(logging.INFO, msg)

    def trace(self, msg):
        """
        Log a Debug / Trace event
        :param msg: the trace message
        :return:
        """
        if self.show_trace:
            self.log(logging.DEBUG, msg)

    def get_logger(self):
        """
        Gets the current logger instance.
        :return: The current logger instance.
        """
        return self.logger


sim_logger = CustomLogger()
