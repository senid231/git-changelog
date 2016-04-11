class Constants:
    class ConstError(TypeError):
        pass

    def __init__(self, constants=None):
        if constants is not None:
            for name, value in constants.iteritems():
                self.__dict__[name] = value

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError("Can't rebind const(%s)" % name)
        self.__dict__[name] = value

    def constants(self):
        return self.__dict__.keys()


EXIT_CODES = Constants({
    "CONTROL_C": 130,
    "UNKNOWN_ARGUMENT": 3,
    "PROJECT_NOT_FOUND": 4,
    "GIT_NOT_FOUND": 5,
    "CHANGELOG_PATH_INVALID": 6,
    "GIT_NO_COMMITS": 7
})

LOG_LEVELS = Constants({
    "ALL": frozenset([0, 1, 2]),
    "DEBUG": 0,
    "INFO": 1,
    "ERROR": 2
})
