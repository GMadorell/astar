import abc

class BaseParser(object):
    """
    Defines a common interface for parse objects.
    """
    def __init__(self):
        self.file = None

    def loadFile(self, path, mode='r'):
        """
        Opens a file descriptor pointing to the given path.
        @path: string
        @mode: how the file will be opened (can be 'r', 'w', 'a'...)
        """
        assert isinstance(path, str)
        if self.file is not None:
            self.closeFile()
        self.file = open(path, mode)

    def closeFile(self):
        """ Closes the actual file descriptor."""
        if self.file is not None:
            self.file.close()

    @abc.abstractmethod
    def parse(self):
        """ Where the parsing happens, must be implemented."""
        raise NotImplementedError()