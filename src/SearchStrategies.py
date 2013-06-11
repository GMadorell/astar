# encoding: UTF-8
import pprint
import copy
from OrderedList import OrderedList

class NotFoundException(Exception): pass

class SearchStrategies:
    """
    Provides a way to run various search strategies.

    AStar usage:
        create instance: search = SearchStrategies()
        set the costs matrix: search.setCosts()
        set the euristics matrix: search.setHeuristic()
        (optional) set the ignore value: search.setIgnore(value)
        run algorithm: search.run(from, where)

     BFS usage:
        create instance: search = SearchStrategies()
        set cost matrix: search.setCosts
        (optional) set the ignore value: search.setIgnore(value)
        run algorithm: search.BFS(from, where)
    """
    def __init__(self):
        self.costs = None
        self.heuristic = None
        self.ignore = None
        self.way_list = OrderedList()
        self.parcial_cost_table = {}

    def setCosts(self, costs):
        """
        @costs: 2x2 matrix consisting in a list of lists
        """
        self.costs = costs

    def setHeuristic(self, heuristic):
        """
        @heuristic: 2x2 matrix consisting in a list of lists
        """
        self.heuristic = heuristic

    def setIgnore(self, value):
        """
        Value which represents 'unpassable' or 'invalid' ways.
        Will be compared against each value in the cost matrix and if the
        comparison is True, that cost will be ignored.
        """
        self.ignore = value
    
    def aStar(self, from_, where, start_at = 1):
        """
        Executes the aStar algorithm.
        Fins a way from 'from_' to 'where' and returns it or raises
        NotFoundException if no way has been found.
        @from_: index of the item we are going from
        @where: index of the item we desire to get as destination
        @start_at: which is the first number in the enumeration?
        """
        # fer funció que from i where existeixi (fora d'aquesta classe)
        # Move from and where values to start from zero
        from_, where = from_ - start_at, where - start_at

        self.parcial_cost_table = {}        
        self.way_list = OrderedList()

        self.way_list.add([from_], 0)
        # n = 1
        while self.way_list[0][0] != where and self.way_list:
            # print(n)
            # n+=1
            head = self.way_list[0]
            expanded = self.expand(head)
            expanded = self.cleanCycles(expanded)

            father_cost = self.way_list.get(0)[1] # get cost
            # Remove head as we already explored it
            self.way_list.remove(head)
            # Remove all the ways that aren't optimized
            self.removeRedundantWays(expanded, father_cost)
            # Add all the ways that we found out in this iteration
            for way in expanded:
                cost = self.findCost(way, father_cost)
                self.way_list.add(way, cost)

        if self.way_list:
            return self.way_list[0]
        else:
            raise NotFoundException()

    def BFS(self, from_, where, start_at = 1):
        """
        Executes the Breath First Search algorithm.
        Fins a way from 'from_' to 'where' and returns it or raises
        NotFoundException if no way has been found.
        @from_: index of the item we are going from
        @where: index of the item we desire to get as destination
        @start_at: which is the first number in the enumeration?
        """
        from_, where = from_ - start_at, where - start_at

        self.way_list = []

        self.way_list.append([from_])
        while self.way_list[0][0] != where and self.way_list:
            head = self.way_list[0]
            expanded = self.expand(head)
            expanded = self.cleanCycles(expanded)
            # Remove head as we already explored it
            self.way_list.remove(head)
            # Add all the ways that we found out in this iteration
            for way in expanded:
                self.way_list.append(way)

        if self.way_list:
            return self.way_list[0]
        else:
            raise NotFoundException()

    def expand(self, way):
        """
        Returns a list of all the possible ways that we can produce from the given
        way.
        @way: list containing a way (list of nodes).
        """
        head = way[0] # CARE
        return_list = []

        # Traverse the matrix by row
        for i, cost in enumerate(self.costs[head]):
            if cost != self.ignore:
                copied_list = copy.copy(way)
                copied_list.insert(0, i)
                return_list.append(copied_list)
                return_list.append(copied_list)

        # Traverse the matrix by column (this way we can give only half the table
        # when we make the costs).
        i, j = head, head
        length = len(self.costs)
        while j < length:
            cost = self.costs[j][i]
            assert isinstance(cost, int) or isinstance(cost, float)
            if cost != self.ignore:
                copied_list = copy.copy(way)
                copied_list.insert(0, j)
                return_list.append(copied_list)
            j += 1

        return return_list

    def cleanCycles(self, ways):
        """
        Checks the given ways and returns a list of those ways that have no cycles.
        @ways: list of lists consisting of ways.
        """
        return_list = []
        for way in ways:
            if way[0] in way[1:]:
                continue
            return_list.append(way)
        return return_list

    def findCost(self, way, father_cost):
        """
        Returns the cost of the given way.
        @way: list containing a way (list of nodes).
        @father_cost: acumulated cost in previous steps.
        Example:
            [10,9,7,6,4]
            cost [9,7,6,4] = father_cost
            return cost[9->10] + father_cost
        """
        # Get indexes which will be used for searching the cost
        i = way[0]
        j = way[1]
        # If j is bigger than i, we just invert them, that way we can make sure
        # that the program will work even if we just provide half the
        # cost table (which can save a lot of space).
        if i > j:
            i, j = j, i

        cost = self.costs[j][i]
        return cost + father_cost

    def removeRedundantWays(self, expanded, father_cost):
        """
        Checks every way in the expanded list against the value in the parcial cost
        table.
        If that way isn't optimum, we remove it in order to make the algorithm faster.
        @expanded: 2x2 matrix of possible ways we can go from the actual head.
        @father_cost: cost of the way from origin to the previous father node.
        """
        # Traverse list from last to first as we may need to remove items
        # as we are iterating through it.
        for i in range(len(expanded)-1,-1,-1):
            way = expanded[i]
            head = way[0]
            parcial_cost = self.parcial_cost_table.get(way[0], 'NotFound')
            way_cost = self.findCost(way, father_cost)
            if way_cost < parcial_cost or parcial_cost == 'NotFound':
                # Update the table with the new cost
                self.parcial_cost_table[head] = way_cost
                # Remove ways in the way_list that have the same cost as the parcial cost
                to_remove = []
                for item, cost in self.way_list.iterWithValues():
                    if cost == parcial_cost and item[0] == head:
                        to_remove.append(item)
                for removable in to_remove:
                    self.way_list.remove(removable)
            else:
                expanded.pop(i)







