# encoding: UTF-8
# Preliminars
# import wxversion
# wxversion.select('2.8')
import wx
import copy
# ---------------------
from BaseParser import BaseParser
from CityInfoParser import CityInfoParser
from AdjacencyMatrixParser import AdjacencyMatrixParser
from CostsManager import CostsManager
from SearchStrategies import SearchStrategies


## Some links
## http://www.java2s.com/Tutorial/Python/0380__wxPython/Catalog0380__wxPython.htm
## http://www.blog.pythonlibrary.org/2008/05/18/a-wxpython-sizers-tutorial/

MAP_IMG_PATH = "./img/Mapa.png"
BUTTON_IMG_PATH = "./img/go_button4.png"

CITY_INFO_PATH = './data/metroLyon.txt'
MA_PATH = './data/MatriuAdjacencia.txt'

TROLEI_BUS_MA_PATH = './data/trolleibusMA.txt'
TROLEI_BUS_INFO_PATH = './data/trolleibusTest.txt'

WALK_MULTIPLIER = 10

# Frame = window 
class GuiAstar(wx.Frame): 
    def __init__(self, parent, id):
        self.size = (720,640)
        wx.Frame.__init__(self, parent, id, 'Astar', size=self.size)
        self.SetMinSize(self.size)

        # Create a base panel
        self.panel = wx.Panel(self)

        # Create sizers
        self.top_level_sizer = wx.BoxSizer(wx.VERTICAL) # Sizer which will include everything in the GUI
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL) # Sizer which will include the map and the options
        self.map_sizer = wx.BoxSizer(wx.VERTICAL) # Will include the map
        self.options_sizer = wx.BoxSizer(wx.VERTICAL) # Will include the options
        self.options_grid_sizer = wx.GridSizer(rows=3, cols=2, vgap=5, hgap=5)

        # Create the map and add it to it's sizer
        self.map_img = wx.Image(MAP_IMG_PATH)
        self.static_bitmap_map = wx.StaticBitmap(self.panel, -1, wx.BitmapFromImage(self.map_img))
        self.map_sizer.Add(self.static_bitmap_map, proportion=0, flag = wx.ALL|wx.ALIGN_CENTER, border = 3)

        # Create checkboxes for the options
        self.walking_cb = wx.CheckBox(self.panel, -1, "Walking")
        self.subway_cb = wx.CheckBox(self.panel, -1, "Subway")
        self.trolleybus_cb = wx.CheckBox(self.panel, -1, "Trolleybus")

        # Create some radio buttons for letting the user select in which way to optimize the pathfinding.
        self.stations_rb = wx.RadioButton(self.panel, -1, "Minimize stops", style = wx.RB_GROUP)
        self.transfers_rb = wx.RadioButton(self.panel, -1, "Minimize transfers")
        self.costs_rb = wx.RadioButton(self.panel, -1, "Minimize cost")

        # Add the checkboxes and the radio buttons to the respective sizer
        self.options_grid_sizer.Add(self.walking_cb)
        self.options_grid_sizer.Add(self.stations_rb)
        self.options_grid_sizer.Add(self.subway_cb)
        self.options_grid_sizer.Add(self.transfers_rb)
        self.options_grid_sizer.Add(self.trolleybus_cb)
        self.options_grid_sizer.Add(self.costs_rb)

        # Add the grid sizer of the customizable options to it's father sizer
        self.options_sizer.Add(self.options_grid_sizer, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER, border = 3)

        # Create choices so the user can select destiny and origin
        # Also create some text so the user can know what is destiny and what origin
        self.list_destiny = self.fetchStations()
        self.list_origin = self.fetchStations()
        self.choice_destiny = wx.Choice(self.panel, -1, choices = self.list_destiny)
        self.choice_origin = wx.Choice(self.panel, -1, choices = self.list_origin)
        self.text_origin = wx.StaticText(self.panel, -1, "Origin: ")
        self.text_destiny = wx.StaticText(self.panel, -1, "Destiny: ")

        # Add the choices and their text to their sizer
        self.options_sizer.Add(self.text_origin, proportion=0, flag=wx.ALL|wx.ALIGN_LEFT, border = 3)        
        self.options_sizer.Add(self.choice_origin, proportion=0, flag=wx.ALL|wx.ALIGN_LEFT, border = 3)
        self.options_sizer.Add(self.text_destiny, proportion=0, flag=wx.ALL|wx.ALIGN_LEFT, border = 3)
        self.options_sizer.Add(self.choice_destiny, proportion=0, flag=wx.ALL|wx.ALIGN_LEFT, border = 3)

        # Create a button so the user can run the algorithm
        self.button_img = wx.Bitmap(BUTTON_IMG_PATH, wx.BITMAP_TYPE_ANY)
        width, height = self.button_img.GetWidth(), self.button_img.GetHeight()
        self.go_button = wx.BitmapButton(self.panel, -1, self.button_img, (width, height))

        # Bind a function to the button - will be executed whenever the user clicks the button        
        self.Bind(wx.EVT_BUTTON, self.onButtonClick, self.go_button) 

        # Add the button to the sizer
        self.options_sizer.Add(self.go_button, proportion=0, flag = wx.ALL|wx.ALIGN_CENTER, border = 5)        

        # Add the options to the main sizer - a horizontal one             
        self.main_sizer.Add(self.map_sizer, proportion=0, flag = wx.ALL|wx.ALIGN_CENTER, border = 5)
        self.main_sizer.Add(self.options_sizer, proportion=0, flag = wx.ALIGN_CENTER|wx.ALL, border = 10)

        # Add the main sizer to the top_level_sizer - that way we have the map and the options sorted out
        self.top_level_sizer.Add(self.main_sizer, proportion=0, flag=wx.ALL|wx.ALIGN_TOP|wx.ALIGN_CENTER, border = 0)

        # Create the text for ouput
        self.output_text_font = wx.Font(15, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.output_text = wx.TextCtrl(self.panel, -1, "Output", size=(640, 150), style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.output_text.SetFont(self.output_text_font)

        # Add the text output rectangle to the top_level_sizer
        self.top_level_sizer.Add(self.output_text, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER, border = 10)

        # Set the panel's sizer to the top_level_sizer
        self.panel.SetSizer(self.top_level_sizer)
        self.top_level_sizer.Fit(self)

    def onButtonClick(self, event):
        """
        This function will be activated whenever the user presses the go button.
        Will call the function to run the algorithm according to the selected
        options.
        """
        self.run()       

    def run(self):
        """
        Takes the options (input from the user) and processes it in order to
        give a customizable output, which is later on moved to a textctrl
        widget.
        """
        # Get the state of the check boxes
        walking_selected = self.walking_cb.GetValue()
        subway_selected = self.subway_cb.GetValue()
        trolleybus_selected = self.trolleybus_cb.GetValue()

        # Get the state of the radio boxes
        minimize_stations = self.stations_rb.GetValue()
        minimize_transfers = self.transfers_rb.GetValue()        
        minimize_cost = self.costs_rb.GetValue()

        # Get the origin selected - if no origin selected -> error
        selected = self.choice_origin.GetCurrentSelection()
        if selected == -1:
            return self.error("No origin selected.")
        origin = self.list_origin[selected]
        origin_id = self.stationStringToId(origin)

        # Get the destiny selected - if no destination is selected -> error
        selected = self.choice_destiny.GetCurrentSelection()
        if selected == -1:
            return self.error("No destiny selected.")
        destiny = self.list_destiny[selected]
        destiny_id = self.stationStringToId(destiny)

        #### Use the logic obtained to run the algorithm
        ## Error checking
        # Check if the user selected at least one of the check boxes
        if not (walking_selected or subway_selected or trolleybus_selected):
            return self.error("Please select some vehicle.")

        # If we selected trolleybus, check for a valid destiny and origin
        if trolleybus_selected and not subway_selected and not walking_selected:
            trolleybus_ids = self.gettrolleybusIdList()
            found = False
            for id in origin_id:
                if id in trolleybus_ids:
                    found = True
            if not found:
                return self.error("This origin isn't possible when we use trolleybus.")
            found = False
            for id in destiny_id:
                if id in trolleybus_ids:
                    found = True
            if not found:
                return self.error("Unreachable destiny via trolleybus.")

        # Check if the user selected the same origin and destiny
        if origin_id == destiny_id:
            return self.output_text.ChangeValue("You are already there.")
        ## /Error checking

        ## Use selected options to manage the data to run the algorithm
        # Load the information of the city
        train_parser = CityInfoParser()
        train_parser.loadFile(CITY_INFO_PATH)
        train_parser.parse() 
        train_parser.setDistances()
        train_info = train_parser.info
        distances = train_parser.distances

        # Load the information of the trolleybus (distances are the same as the train)
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

        # Load info of the trolleybus costs
        matrix_parser.loadFile(TROLEI_BUS_MA_PATH)
        matrix_parser.parse()
        bus_costs = matrix_parser.values
        matrix_parser.closeFile()

        # Open an instance of cost manager to provide custom results
        # in some cases.
        costs_manager = CostsManager()

        if subway_selected and trolleybus_selected:
            costs = costs_manager.combineCosts(train_info, bus_info, train_costs, bus_costs)
        elif subway_selected:
            costs = train_costs
        elif walking_selected and not subway_selected and not trolleybus_selected:
            costs = self.makeWalkingMatrix(distances)
        elif walking_selected and trolleybus_selected:
            costs = self.expandBusMatrix()
        else:
            costs = bus_costs

        if walking_selected and (subway_selected or trolleybus_selected):
            costs = costs_manager.setWalkingCostsWithDistances(
                                               costs,
                                               distances,
                                               multiplier = WALK_MULTIPLIER
                                          )

        if minimize_transfers:
            if subway_selected:
                costs_manager.setTransferCost(train_parser.info, costs, 999)
            elif trolleybus_selected:
                costs_manager.setTransferCost(bus_parser.info, costs, 999)


        # Set up the algorithm
        search = SearchStrategies()
        search.setCosts(costs)
        search.setHeuristic(distances)
        search.setIgnore(0)

        # Run the algorithm
        # If we only selected walking option, let the user go directly to their destination
        if walking_selected and not trolleybus_selected and not subway_selected:
            result = [destiny_id[0] - 1, origin_id[0] - 1] # substract -1 to normalize, enumeration starts with n=1
        # Select the optimum way in case we have stations with same name (multiple IDs station)
        elif minimize_stations:
            result_list = []
            for id in origin_id:
                for id2 in destiny_id:
                    result_list.append(search.BFS(id, id2, start_at = 1))
            bird = len
            result_list.sort(key=bird) # The key is the bird
            result = result_list[0]
        else:
            result_list = []
            for id in origin_id:
                for id2 in destiny_id:
                    print(id, id2)
                    result_list.append(search.aStar(id, id2, start_at = 1))
            bird = len
            result_list.sort(key=bird)
            result = result_list[0]
        
        # We process the result in order to display a nice output to the user
        # We do that because the algorithms return a boring list of numbers.
        self.output_text.Clear()
        walking_costs = self.makeWalkingMatrix(distances)

        # Helper method to calculate the optimum way of traversing from two
        # stations id given the actual options.
        def wayCheck(id1, id2):
            """
            Helper function.
            Returns 1, 2 or 3 depending on whether the optimum way of going from
            id1 to id2 is by train (subway), bus or walking.
            @id1 (int): station_id1
            @id2 (int): station_id2
            """
            # id1, id2 = id1-1, id2-1
            patata = False
            if id2>id1:
                id1,id2=id2,id1            
            if walking_selected:
                costCaminant = walking_costs[id1-1][id2-1]
            if trolleybus_selected:
                ola=False
                busList = self.gettrolleybusIdList()
                if id2==18:
                    ola=True
                    id2,id1=id1,38
                print busList
                print id1 , id2 ,id1 in busList and id2 in busList
                if id1 in busList and id2 in busList:
                    patata = True
                    sorted_dict_keys = bus_parser.info.keys()
                    sorted_dict_keys.sort()
                    for n, i in enumerate(sorted_dict_keys):
                        if id1 == i:
                            break
                    for n2, j in enumerate(sorted_dict_keys):
                        if id2 == j:
                            break
                    if n2>n:
                        n2,n = n,n2
                    costBus = bus_costs[n][n2]
                if ola:
                    id1,id2=id2,18
            if subway_selected:
                if id1==38:
                    xx,yy=17,id2-1
                    if xx<yy:
                        xx,yy=yy,xx
                    if train_costs[xx][yy]!=0 and train_costs[37][id2-1]==0:
                        id1=18
                if id1<id2:
                    id2,id1=id1,id2
                costsubway = train_costs[id1-1][id2-1]
            if subway_selected and not trolleybus_selected and not walking_selected:
                #100
                return 1
            elif not subway_selected and trolleybus_selected and not walking_selected:
                #010
                return 2
            elif not subway_selected and not trolleybus_selected and walking_selected:
                #001
                return 3
            elif subway_selected and not trolleybus_selected and walking_selected:
                #101
                if costsubway==0:
                    return 3
                x = min(costsubway,costCaminant)
                if x==costsubway:
                    return 1
                elif x==costCaminant:
                    return 3
                else:
                    raise ValueError()
            elif subway_selected and trolleybus_selected and not walking_selected and patata:
                #110
                if costsubway==0:
                    return 2
                elif costBus==0:
                    return 1
                else:
                    x = min(costsubway,costBus)
                    if x==costsubway:
                        return 1
                    elif x==costBus:
                        return 2
                    else:
                        raise ValueError()
            elif subway_selected and trolleybus_selected and not walking_selected and not patata:
                return 1
            elif not subway_selected and trolleybus_selected and walking_selected and patata:
                #011
                if costBus==0:
                    return 3
                x = min(costBus,costCaminant)
                if x==costBus:
                    return 2
                elif x==costCaminant:
                    return 3
                else:
                    raise ValueError()
            elif not subway_selected and trolleybus_selected and walking_selected and not patata:
                return 3
            elif subway_selected and trolleybus_selected and walking_selected and patata:
                #111
                if costsubway==0 and costBus==0:
                    return 3
                elif costsubway==0:
                    x = min(costBus,costCaminant)
                    if x==costBus:
                        return 2
                    elif x==costCaminant:
                        return 3
                    else:
                        raise ValueError()
                elif costBus==0:
                    x = min(costsubway,costCaminant)
                    if x==costsubway:
                        return 1
                    elif x==costCaminant:
                        return 3
                    else:
                        raise ValueError()
                else:
                    x = min(costsubway,costCaminant,costBus)
                    if x==costsubway:
                        return 1
                    elif x==costCaminant:
                        return 3
                    elif x==costBus:
                        return 2
                    else:
                        raise ValueError()
            elif subway_selected and trolleybus_selected and walking_selected and not patata:
                if costsubway==0:
                    return 3
                x = min(costsubway,costCaminant)
                if x==costsubway:
                    return 1
                elif x==costCaminant:
                    return 3
                else:
                    raise ValueError()
            else:
                raise ValueError()
        result.reverse()

        ###### Parse 2 per arreglar error
        matrix_parser = AdjacencyMatrixParser()
        matrix_parser.loadFile(MA_PATH)
        matrix_parser.parse()
        train_costs = matrix_parser.values
        matrix_parser.closeFile()

        print "result", result
        result = map(lambda num: num+1, result) # Increment each result by one
        print "result",result
        station_id1=result[0]       
        for n, station_id2 in enumerate(result[1:], start=1):
            number = wayCheck(station_id1,station_id2)
            print "station ids: ", station_id1, station_id2

            origen_station = self.stationIdToString(station_id1)
            destiny_station = self.stationIdToString(station_id2)

            station_id1=station_id2
            
            self.output_text.AppendText(str(n) + ") " + origen_station + " -> " + destiny_station +": ")            
            if number == 1:
                self.output_text.AppendText("Subway")
            elif number == 2:
                self.output_text.AppendText("Trolleybus")
            elif number == 3:
                self.output_text.AppendText("Walking")
            else:
                raise ValueError()

            if origen_station == destiny_station:
                self.output_text.AppendText(" (transfer)")
            self.output_text.AppendText("\n")

        # Move selection of text ctrl to topleft    
        self.output_text.ShowPosition(0)

    ##### HELPER FUNCTIONS
    def fetchStations(self):
        """
        Returns a list with the names of every single possible station formatted 
        in TitleCase, with the _ stripped off and sorted by alfabetical order.
        """
        list=[]
        list2=[]
        parsedInfo=CityInfoParser()
        parsedInfo.loadFile(CITY_INFO_PATH)
        parsedInfo.parse()
        for id in parsedInfo.info.keys():
            if not parsedInfo.info[id]["name"] in list:
                list.append(parsedInfo.info[id]["name"])
        list.sort()
        for obj in list:
            obj=obj.replace("_",' ')
            obj=obj.title()
            list2.append(obj)
        parsedInfo.closeFile()
        return list2

    def stationStringToId(self, string):
        """
        Takes the string selected from the choice and returns a list of all the possible ids.
        Raises value error if not found.
        """
        return_list = []
        string=string.replace(' ','_')
        string=string.upper()
        parsedInfo=CityInfoParser()
        parsedInfo.loadFile(CITY_INFO_PATH)
        parsedInfo.parse()
        for id in parsedInfo.info.keys():
            if string==parsedInfo.info[id]["name"]:
                return_list.append(id)
        if len(return_list) == 0:
            raise ValueError()
        else:
            return return_list

    def stationIdToString(self,id1):
        """
        For a given id returns the name of the station
        """
        parsedInfo=CityInfoParser()
        parsedInfo.loadFile(CITY_INFO_PATH)
        parsedInfo.parse()
        parsedInfo.closeFile()
        for id in parsedInfo.info.keys():
            if id1==id:
                obj = parsedInfo.info[id]["name"]
                obj = obj.replace('_',' ')
                obj = obj.title()
                return obj

    def gettrolleybusIdList(self):
        """
        Returns a list with every ID avaiable when travelling by trolleybus
        """
        list=[]
        parsedInfo=CityInfoParser()
        parsedInfo.loadFile(TROLEI_BUS_INFO_PATH)
        parsedInfo.parse()
        for id in parsedInfo.info.keys():
            list.append(id)
        parsedInfo.closeFile()
        return list

    def makeWalkingMatrix(self, distances):
        """
        Returns the given matrix multiplied by walking_costs.
        """
        return_list = copy.deepcopy(distances)
        for i in range(len(return_list)):
            for j in range(len(return_list[i])):
                return_list[i][j] *= WALK_MULTIPLIER
        return return_list

    def expandBusMatrix(self):
        """
        """
        # Do a matrix the size of the train info matrix full of zeros
        matrix_parser = AdjacencyMatrixParser()
        matrix_parser.loadFile(MA_PATH)
        matrix_parser.parse()
        train_costs = matrix_parser.values
        matrix_parser.closeFile()
        zero_list = []
        for element in train_costs:
            sub_list = []
            for element2 in element:
                sub_list.append(0)
            zero_list.append(sub_list)

        # Load info of the trolleybus costs
        matrix_parser.loadFile(TROLEI_BUS_MA_PATH)
        matrix_parser.parse()
        bus_costs = matrix_parser.values
        matrix_parser.closeFile()

        # Load the information of the trolleybus
        bus_parser = CityInfoParser()
        bus_parser.loadFile(TROLEI_BUS_INFO_PATH)
        bus_parser.parse()
        bus_info = bus_parser.info

        # Iterate twice over the bus_info dictionary and move the values in it's
        # adjacency matrix to the zero_list
        i = 0
        bus_info_keys = bus_info.keys()
        bus_info_keys.sort()
        for id in bus_info_keys:
            j = 0
            bus_info_keys_2 = bus_info.keys()
            bus_info_keys_2.sort()
            for id2 in bus_info_keys_2:
                m, n = ((id2, id) if id < id2 else (id, id2))
                x, y = ((j, i) if i < j else (i, j))
                zero_list[m-1][n-1] = bus_costs[x][y] 
                j += 1
            i += 1
        return zero_list

    def error(self, error_msg):
        """
        Creates and shows an error dialog.
        """
        assert isinstance(error_msg, str)
        error = wx.MessageDialog(self.panel, error_msg, 'Error', style=wx.ICON_ERROR|wx.OK )
        error.ShowModal()    

if __name__ == '__main__':
    app = wx.PySimpleApp() #runs program (inner working)
    frame = GuiAstar(parent = None, id = -1) #displays program 
    frame.Show()
    app.MainLoop()