import copy

class CostsManager:
    """
    Allows modifying a costs 2x2 matrix depending on diferent things.
    """
    def __init__(self):
        pass

    def setWalkingCostsWithDistances(self, costs, distances, multiplier):
        """
        Modifies the costs matrix comparing it to a combination of the
        distances matrix and the multiplier value and storing only the 
        lower value.
        Doesn't modify the given cost list.
        Returns a modified copy of the given cost list.
        @costs: 2x2 matrix represented as a list of lists.
        @distances: 2x2 matrix represented as a list of lists.
        @multiplier: number
        """
        assert len(costs) == len(distances)

        copied_costs = copy.deepcopy(costs)
        # We iterate over both matrixes using the same index.
        # That holds true because both matrixes must be of the same size.
        for i in range(len(copied_costs)):
            j = 0
            while j <= i:
                mult_value = multiplier * distances[i][j]
                if mult_value < copied_costs[i][j] or copied_costs[i][j] == 0: # 0 is a special case because we had 0 as the ignorable value
                    copied_costs[i][j] = mult_value
                j += 1
        return copied_costs

    def changeValues(self, matrix, which, to):
        """
        Changes all the values that have 'which' value to value 'to' on the given
        2x2matrix consisting on a list of lists.
        """
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                value = matrix[i][j]
                if value == which:
                    matrix[i][j] = to

    def setTransferCost(self, info, costs, cost):
        """
        Checks every info entry against every other entry for the same x and y coordinates,
        and then sets that cost in the costs 2x2 matrix to the given value.
        @info: dictionary after parsing the city info.
        @costs: 2x2 matrix (list of lists).
        @cost: number assigned to transfer.
        """
        i,j = 0,0
        for value, dic in info.items():
            j = 0
            for value2, dic2 in info.items():
                if j > i:
                    break
                if value == value2:
                    pass
                elif dic['x'] == dic2['x'] and dic['y'] == dic2['y']:
                    costs[i][j-1] = cost
                j += 1
            i += 1

    def combineCosts(self, info1, info2, costs1, costs2):
        """
        Merges the information on the '1' entity with the info on the '2' entity.
        @info1: dict of the first transport
        @info2: dict of the second transport
        @costs1: 2x2 matrix containing the costs info of the first transport
        @costs2: 2x2 matrix containing the costs info of the second transport
        """

        # Sort keys because dicts return keys in an arbitrary order
        list_info = info2.keys()
        list_info.sort()
        # Iterate over the ids of the dict twice and check the info
        # against each other.
        i = 0
        for id in list_info:
            j = 0
            for id2 in list_info:
                # Make the first value the lower one
                k, m = ((i, j) if i < j else (j, i))
                x, y = ((id2, id) if id < id2 else (id, id2))

                # print " x:",x, " y:",y," m:",m," k:",k
                # print "costs1[x-1][y-1]:",costs1[x-1][y-1], " costs2[m][k]:", costs2[m][k]
                
                # 
                if costs1[x-1][y-1] > costs2[m][k] \
                    or (costs1[x-1][y-1] == 0 and costs2[m][k] != 0):
                    # print("Hello")
                    costs1[x-1][y-1] = costs2[m][k]
                    # return costs1
                j += 1
            i += 1
        return costs1