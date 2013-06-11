#encoding: UTF-8
from CityInfoParser import CityInfoParser
from AdjacencyMatrixParser import AdjacencyMatrixParser
from SearchStrategies import SearchStrategies
from CostsManager import CostsManager

import sys
import pprint
import copy

CITY_INFO_PATH = './data/MetroLyon.txt'
MA_PATH = './data/MatriuAdjacencia.txt'

TROLEI_BUS_MA_PATH = './data/TroleiBusMA.txt'
TROLEI_BUS_INFO_PATH = './data/TroleiBusTest.txt'

WALK_MULTIPLIER = 6

def main():
    """
    Method used for testing the performance and the correctness of the implemented
    A* and BFS algorithms along with the parsers.
    Comment / Uncomment code to test different features of the software.
    """

    # Load the information of the city
    train_parser = CityInfoParser()
    train_parser.loadFile(CITY_INFO_PATH)
    train_parser.parse()
    train_parser.setDistances()
    train_info = train_parser.info
    distances = train_parser.distances

    # Load the information of the troleibus (distances are the same as the train)
    bus_parser = CityInfoParser()
    bus_parser.loadFile(TROLEI_BUS_INFO_PATH)
    bus_parser.parse()
    bus_info = bus_parser.info

    # Load the information of the train costs
    matrix_parser = AdjacencyMatrixParser()
    matrix_parser.loadFile(MA_PATH)
    matrix_parser.parse()
    train_costs = matrix_parser.values
    matrix_parser.closeFile()

    # Load info of the troleibus costs
    matrix_parser.loadFile(TROLEI_BUS_MA_PATH)
    matrix_parser.parse()
    bus_costs = matrix_parser.values
    matrix_parser.closeFile()

    
    # Open an instance of cost manager to provide custom results
    # in some cases.
    costs_manager = CostsManager()
    
    
    ########################################
    # Add both the bus and the train info on the same matrix
    # costs_aux = copy.deepcopy(train_costs)
    # for x in enumerate(costs_aux):
    #     print(x)
    costs = costs_manager.combineCosts(train_info, bus_info, train_costs, bus_costs)
    # print(pprint.pformat(enumerate(costs)))
    # for x in enumerate(costs):
    #     print(x)
    # print(costs == costs_aux)

    # # Count differences (debug)
    # count = 0
    # for i in range(len(costs)):
    #     for j in range(len(costs[i])):
    #         if (costs[i][j] != costs_aux[i][j]):
    #             count += 1
    # print("Count: ", count) 
    # return
    # Set transfer costs really high so they are ignored
    # costs_manager.setTransferCost(info_parser.info, costs, 999)
    #########################################

    # Walking costs
    costs = costs_manager.setWalkingCostsWithDistances(
                                               costs,
                                               distances,
                                               multiplier = WALK_MULTIPLIER
                                          )


    # Set up the A* algorithm
    search = SearchStrategies()
    search.setCosts(costs)
    search.setHeuristic(distances)
    search.setIgnore(0)

    # Run the algorithm
    # way = search.aStar(1, 24, start_at=1)
    way = search.BFS(1, 24, start_at=1)
    print 'Result:', way

if __name__ == '__main__':
    main()
