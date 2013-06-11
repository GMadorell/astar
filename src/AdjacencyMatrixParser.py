import pprint
import BaseParser


class AdjacencyMatrixParser(BaseParser.BaseParser):
    """
    Represents a way to parse a given adjacency matrix into a python list.
    Usage:
      - Use openFile(path) to load the file
      - Use parse to populate self.values with a 2x2 matrix
    """
    def __init__(self):
        super(AdjacencyMatrixParser, self).__init__()
        self.values = []

    def parse(self):
        """
        Populates the self.values list using the already opened file.
        """
        assert self.file is not None
        self.values = []
        for line in self.file.readlines():
            # Split string into tabulations
            dirty_str = line.split('\t')
            # Remove all None values and the last value which is a '\n'
            # Also parse it into a list and transform the characters into numbers.
            clean_sublist = []
            for char in dirty_str:
                if char in ('', '\n'):
                    continue
                clean_sublist.append(int(char))
            self.values.append(clean_sublist)
            
        # print(pprint.pformat(clean_list, depth=50))
