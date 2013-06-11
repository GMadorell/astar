import pprint
import math
import BaseParser

class CityInfoParser(BaseParser.BaseParser):
    """
    Defines a way to parse a appropiate text file into a map structure.
    Structure must be:
        id_of_the_row   name    type    x   y
    Also provides a method that fills a 2x2 matrix with the distances between
    all the points, useful when computing an heuristic.
    """
    def __init__(self):
        super(CityInfoParser, self).__init__()
        self.info = {}
        self.distances = []

    def parse(self):
        """
        Uses the already opened file to parse the information into the info
        variable.
        Data structure will be a dictionary of dictionaries of the form:
            dic[id] = {name, type, x, y}
        """
        assert self.file is not None
        self.info = {}
        for text_line in self.file.readlines():
            # Split text in tabulations
            splitted = text_line.split('\t')
            # The last part is special, we must check for negative numbers and
            # also remove the last \n.
            last = splitted[-1]
            number = ''
            i = 0
            while last[i].isdigit() or last[i] == '-':
                number += last[i]
                i += 1
            splitted[-1] = number

            # Put the parsed info into the dict
            station_id = int(splitted.pop(0))
            name = splitted.pop(0)
            station_type = splitted.pop(0)
            x = int(splitted.pop(0))
            y = int(splitted.pop(0))

            self.info[station_id] = {}
            self.info[station_id]['name'] = name
            self.info[station_id]['type'] = station_type
            self.info[station_id]['x'] = x
            self.info[station_id]['y'] = y

        # print(pprint.pformat(self.info))

    def setDistances(self):
        """
        Parses the actual information we have about the file into a 2x2 matrix
        represented as a list of lists.
        Assumes the parse() method is already used.
        Formula used is:
            xd = x2-x1
            yd = y2-y1
            Distance = SquareRoot(xd*xd + yd*yd) 
        """
        assert self.info is not None
        self.distances = []

        for actual_station_dict in self.info.values():
            actual_station_x = actual_station_dict['x']
            actual_station_y = actual_station_dict['y']

            distance_list = []
            for destination_station_dict in self.info.values():
                destination_station_x = destination_station_dict['x']
                destination_station_y = destination_station_dict['y']

                # Get distance
                xd = destination_station_x - actual_station_x
                yd = destination_station_y - actual_station_y
                d = math.sqrt(xd*xd + yd*yd)

                distance_list.append(d)

            self.distances.append(distance_list)

        # print(pprint.pformat(self.distances))
        

