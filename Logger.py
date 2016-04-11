from Constants import LOG_LEVELS
from sys import stderr


class Logger:
    def __init__(self, log_level):
        self.validate_log_level(log_level)
        self.log_level = log_level

    @staticmethod
    def validate_log_level(log_level):
        if log_level not in LOG_LEVELS.ALL:
            raise TypeError("Can't find %s in LOG_LEVELS" % log_level)

    def write_log(self, log_level, message):
        if log_level >= self.log_level:
            if log_level != LOG_LEVELS.ERROR:
                print message
            else:
                stderr.write(message)

    def info(self, message):
        self.write_log(LOG_LEVELS.INFO, message)

    def debug(self, message):
        self.write_log(LOG_LEVELS.DEBUG, message)

    def error(self, message):
        self.write_log(LOG_LEVELS.ERROR, message)
