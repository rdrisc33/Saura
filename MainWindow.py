from utils import * 

from PySide6.QtCore import QModelIndex
from SchematicScene import SchematicScene
from Schematic import Schematic
from Board import Board
from PySide6.QtWidgets import QFileDialog
from Spreadsheet import Spreadsheet
from MyCreatePartDialog import CreatePartDialog
from DigikeyParser import DigikeyParser
from DigikeyAPI import DigikeyAPI
from CentralWidget import CentralWidget
from MyCreateDialog import MyCreateDialog
from ComponentSymbol import ComponentSymbol
from FootprintItem import FootprintItem
from Database import database 
from MyGraphicAssign import MyGraphicAssign
from MyGraphicAssign import MyGraphicsAssign
from PySide6.QtWidgets import *
from Symbol import Symbol 
from Label import Label
from Label import Label
from Label import LocalLabel
from Label import HierarchyLabel
from Label import GlobalLabel
from Symbol import Symbol
# from 

from WireItem import WireItem
from utils import Utils
# from Label import Label 
from NetSymbol import NetSymbol
from Component import Component

import numpy as np
from scipy.sparse import coo_array
from scipy.spatial.distance import squareform, pdist
import matplotlib.pyplot as plt
        

class MainWindow(QMainWindow):
    # wiring_action_signal = Signal(int) # This signal emits when the wiring action is triggered ( user presses 'wiring mode' button) ( Signals aren't designed to be reimplemented-- so don't reimplement builtin signals. Instead, create your own Signals)
    on_graphic_assign_all_done = Signal()

    def __init__(self):
        super().__init__()        
        self.veins = {0:None}                   # 'veins' after veins of ore, 
        self.nets = defaultdict(dict)                          # 
        self.connectedVeins = set()               # Track any veins connected to the vein currently being drawn
        self.ratsnests = defaultdict(list)                     # {'3V3': [QGraphicsLineItem1, ...], 'GND':[...], ... }
        # self.ratsnestGraphs = defaultdict(list)
        G = []
        self.mst = None

        defaultdictInfinite = lambda: defaultdict(defaultdictInfinite) # see infinite default dict
        # self.components = defaultdict(defaultdict) # Not deep enough defaultdict 
        # self.components = defaultdictInfinite() # {"R": {1:<Component>, '5':<Component> } , "U": {4:<Component>} } # Note netSymbols go in schematic.scene.netSymbols 
        # self.netSymbols = defaultdictInfinite() # { 'GND': {1: <NetSymbol>} , '3V3': {1:<NetSymbol , 2: {NetSymbol}}}}
        # self.labels     = defaultdictInfinite() # { 'HI_A', {1 :<Label>}}
        
        self.components = defaultdict(defaultdict) # {"R": {1:<Component>, '5':<Component> } , "U": {4:<Component>} } # Note netSymbols go in schematic.scene.netSymbols 
        self.netSymbols = defaultdict(defaultdict) # { 'GND': {1: <NetSymbol>} , '3V3': {1:<NetSymbol , 2: {NetSymbol}}}}
        self.labels     = defaultdict(defaultdict) # { 'HI_A', {1 :<Label>}}
        
        self.setAcceptDrops(True)
        self.schematic= Schematic() #Shown on start. part of stacked_widget
        self.board = Board() # hidden on start. part of stacked widget 
        self.spreadsheet = Spreadsheet() # MySchematic has self.spreadsheet and its visible while editing .brd and .sch
        
        self.spreadsheet.table.clicked.connect(self.onTableClicked)
        self.create_actions()
        self.create_menus()
        self.create_schematic_toolbar()
        self.create_board_toolbar()
        
        
        database.changed.connect(self.reloadPart) # When the database changes, reload all parts on all scenes
        
### Had many issues adding part to both brdScene & schScene @same time-- I ended up creating a signal, to .emit on a sceneDropEvent, .connecting that symbol at the MainWindow level, below: ### I THINK it'd be better to have a BoardScene & symbolScene subclass...
        
        self.schematic.scene().droppedPart.connect(self.placePart)
        self.board.scene().droppedPart.connect(self.placePart)
        
        
        self.schematic.scene().deletePart.connect(self.deletePart)
        self.board.scene().deletePart.connect(self.deletePart)
        
        self.board.scene().tracingLaid.connect(self.onTracingLaid)
        self.schematic.scene().wiringLaid.connect(self.onWiringLaid)
        
        self.board.scene().footprintMoved.connect(self.onFootprintMoved)
        # self.parts = {}# A dict representing all parts placed on our sch & brd.  keys are reference_value. values are the symbol and  {C1:}
        
        self.setCentralWidget(CentralWidget(self.schematic, self.board)) # Bc QMainWindow deletes old central widgets upon assignment of create central widgets, protect schematic&board from deletion inside a stackedwidget.
        # self._addWireAction.trigger()# The triggered signal is emitted when an action is activated, such as when the user clicks a menu button, or when .trigger() was called
        self.dock_spreadsheet = QDockWidget()
        self.dock_spreadsheet.setWidget(self.spreadsheet)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea , self.dock_spreadsheet)
        self.dock_spreadsheet.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
# I need to be able to talk to the database 
        # database.changed.connect(self.spreadsheet.table.setTableName) TYPING MISMATCH: .changed emits DICT but .setTableName accepts STR # Now every time the database gets an update or insert, the table will refresh, w/ changes 
        # database.changed.connect(self.spreadsheet.reload_part)  #Every time the database gets an update or insert, the table will refresh, based on part.get('table_name')
        # database.changed.connect(self.schematic.scene().reload_part) #This belongs in scene() constructor # Refresh all the symbols belonging to 'table_name' when we update the db (Bc the symbols hold their own part record) This may not make any visiblie changes, unless you change the 'symbol' attribute 
        # database.changed.connect(self.board.scene().reload_part)  # This belongs in scene()'s constructor # Refresh all the footprints belonging to 'table_name' when we update the db( Bc the footprints also hold heir own part record) This may not make any visible changes, unless you change the 'footprint' attribute...
        
    def onFootprintMoved(self, footprint):
        footprint.setNets()

        print('FOOTPRINT:', footprint)
        print('FOOTPRINT.NETS():', footprint.nets())
        for net in footprint.nets():
            self.updateRatsnest(net)

    def setVeinNets(self, vein): # TODO more robust drc
        print()
        print('setVeinNets')
        
        highestPriority = max(vein)# ValueError: max() iterable argument is empty
        print('VEIN:', vein)
        print('HIGHESTPRIORITY:', highestPriority)
        
        if highestPriority == Utils.SchematicItemKinds.Wire.value: # .value!!
            # vein['nets'].append(None)
            print()
            print('DRC NOTIFICATION: WIRES FLOATING IN SPACE') 
            
        elif highestPriority == Utils.SchematicItemKinds.Pin.value: 
            
            pins = vein[Utils.SchematicItemKinds.Pin.value]
            if len(pins) == 1: 
                print()
                print('DRC NOTIFICATION: PIN IS NOT CONNECTED') 
            
            pins = sorted(pins, key = lambda pin: pin.name()+str(pin.number())) # pin.id is unique integer assigned during brdScene.addItem. TODO: confirm pin.id is deterministic way for sorting pins. Could also sort by pin name ('C3-1') since we need it for the net anyway
            pin = pins[0]
            net = pin.parentItem().reference() + '_' + pin.number()
            vein['nets'].append(net)

        elif highestPriority == Utils.SchematicItemKinds.LocalLabel.value: 
            print()
            print('NET ASSIGNMENTS VIA LABELS NOT YET IMPLEMENTED')
            
        elif highestPriority == Utils.SchematicItemKinds.NetSymbol.value: 
            netSymbols = vein[Utils.SchematicItemKinds.NetSymbol.value]
            print('HIGHEST PRIO 3: NET SYMBOL')
            print('NETSYMBOLS:', len(netSymbols), netSymbols)
            nets = [netSymbol.net() for netSymbol in netSymbols]
            vein['nets'].extend( nets )
            
            if len(nets) > 1: 
                print()
                print('NETS:', nets)
                print('DRC ERROR: CONFLICTING NET SYMBOLS')

        else: 
            print()
            print('NET ASSIGMENT VIA HIGHEST PRIORITY SCHEMATICITEM NOT YET IMPLEMENTED')
            
        # Note use of nets rather than net. This is because its possible user conencted two nets to same vein, in which case, we want to raise a DRC error 
        # Note that if HP is Global label, most prios below must also be checked for conflicts 
        
    def onWiringLaid(self, pos): # This slot runs when schematic.scene emits wiring_laid. pos: the position of any terminal of laid wiring. If user added wire, pos equals mouseDoubleClickEvent.event.scenePos(). 
        # We need to:
            # update MW.veins
            # update MW.nets
            # update the ratsnest for this net
            # All of which updateVeins does
        print()
        print('WIRING LAID', pos.toPoint())
        self.updateVeins(pos)

    def onTracingLaid(self, net): # Slot runs when board.scene emits tracing_laid
        #We need to 
        # update ( nets@BIs, ratsnest )
        # First, update nets@BI's, because, ratsnest will use padTerminals=nets[BI.Pad]  
        self.updateRatsnest(net)

    def propagations(self, xYLayer, net): # xYLayer is a 3-tuple (x,y,layer). pos already taken to refer to 2-tuple|QPointF(x,y)
        startxYLayer = xYLayer

        xYLayerQueue = [xYLayer]
        visitedItems = set()
        visitedxYLayers = set()
        while xYLayerQueue: 
            xYLayer = xYLayerQueue.pop(0)
            visitedxYLayers.add(xYLayer)
            for hitItem in self.queryRtrees(xYLayer):
                if hitItem in visitedItems: continue 
                visitedItems.add(hitItem)
                # item = hitItem):
                for hitItem2 in self.queryRtrees(item=hitItem, layer=xYLayer[2]):
                    if hitItem2 in visitedItems: continue 
                    elif hitItem2 == hitItem: continue 
                    if hitItem2.connectsTo(hitItem):
                        # xYLayerQueue.extend(hitItem2.sceneTerminals()) # not enough
                        for layer in hitItem2.copperLayers():
                            for terminal in hitItem2.sceneTerminals():
                                
                                xYLayerQueue.append( (*terminal.toTuple(), layer) )
                # if not isinstance(hitItem ,FootprintItem):
                #     if hitItem.net() != None and  hitItem.net() != net: 
                #         raise ValueError(f'HITITEM.NET(): {hitItem.net()} AND TRACE NET: {net} DO NOT MATCH')
                #     hitItem.setNet(net) # Set net on every BoardItem, (but not here-- done before) so that brdScene knows net info w/o relying on MW.nets, which it cannot ez access.  
        print(f'xYLayer {startxYLayer} PROPAGATED TO { len(visitedxYLayers) } POINTS:', list(visitedxYLayers)) 
        return list(visitedxYLayers) 
        
    def queryRtrees(self, xYLayer=None , item=None, bounds=None, layer=None ): 
        """Query rtree for either pos, item&layer, or bounds&layer.
        pos: 3-tuple (x,y,layer) 
        item: a PadTraceViaZone item
        bounds: 4-tuple 
        layer: str representing which rtree layer to query
        """
        if xYLayer: 
            x, y, layer = xYLayer
            bounds = ( x, y , x , y )
        elif item: 
            bounds = item.sceneBounds()
            
        hitIds = self.board.scene().rtrees[layer].intersection(bounds)
        hitItems = [self.board.scene().ids[id] for id in hitIds]
        return hitItems 
        
    def updateRatsnest(self, net): # Modified Kruskal Minimum Spanning Tree https://www.w3schools.com/dsa/dsa_algo_mst_kruskal.php  https://en.wikipedia.org/wiki/Kruskal's_algorithm#Pseudocode. Note uses indices of vertices as ordered in G, rather than vertices.
        G = [ [ [2,0,'F.Cu'] , [0,0,'F.Cu'],  [1,1,'F.Cu' ] , [1,3,'F.Cu'] ] , [ [3,2,'F.Cu'], [4,2,'F.Cu'] ] ]
        G = self.ratsnestGraph(net) 
        print('G:', G) # G: [[(55.0, 55.0, 'F.Cu')], (55.0, 55.0, 'F.Cu')]
        if not G: 
            print('NO GRAPH WITH WHICH TO UPDATE RATSNEST')
            return

        flat = [] 

        for subgraph in G: 
            for pos in subgraph: 
                flat.append(pos[0:2]) # Flat doesn't have layer part

        print('FLAT:', flat)
        self.addRatsnestToScene(G , flat, net)
        
    def ratsnestGraph(self, net):
        print()
        print('RATSNESTGRAPH')
        G = [] # ratsnest lines arent wanted between connected items. Collect vertices of connected items in G
        # self.subgraphs = [] # ratsnest lines arent wanted between connected items. Collect vertices of connected items in self.subgraphs  
        print('NET:', net)
        print('MW.NETS:')
        for k,v in self.nets.items(): 
            print(k , ':', v)
        print(f'MW.NETS[{net}]:', self.nets[net])

        pads =  self.nets[net].get(Utils.BoardItemKinds.Pad.value, [])
        print('PADS:', len(pads), pads)
        if not pads: 
            return
        # padTerminals = {pad.sceneTerminals(net) for pad in pads}         # padTerminals = [ [0,0, 'F.Cu'] , [2,0,'] , [3,0] , [0,2] ] 
        padTerminals = []
        for pad in pads :
            pad.setSceneTerminal()
            for layer in pad.layers(): 
                if layer in Utils.CopperLayers: 
                    padTerminals.append( (*pad.sceneTerminal().toTuple() , layer) ) # xYLayer form

        print('PADTERMINALS:', len(padTerminals), padTerminals) 
        # padTerminals: 2 [[(-0.9271, 0.0, 'F.Cu'), (-0.9271, 0.0, 'F.Paste'), (-0.9271, 0.0, 'F.Mask')], [(0.9271, 0.0, 'F.Cu'), (0.9271, 0.0, 'F.Paste'), (0.9271, 0.0, 'F.Mask')]]

        # G = set(padTerminals) NO SETS bc cannot iterate over sets 
         # padTerminals is a precursor G, includes pad terminals, but G requires terminals of any connected pads/traces/zones as well # copy padTerminals with set() as they belong in G
        # for pos in padTerminals :
        
        while padTerminals: 
            pos = padTerminals.pop(0)
            
            if any(pos in subgraph for subgraph in G):
                continue
            propagations = self.propagations(pos, net)
            G.append(propagations) #  Accumulate all pad, trace, via, and zone terminals connected to pads. L8r, G used to disallow ratsnest lines intra-subgraph. Bc connected items dont get a ratsnest line.

        return G
 
    def ratsnestMST(self, G, flat ): 
        # Graph Theory: 
            # Tree: a graph. Vertices connected by 1 path. Undirected, acyclic.
            # Forest: a graph. Vertices connected by 0 or 1 path. Undirected, acyclic,  ( so named because a 'forest' can contain many 'trees') 
            # Minimum Spanning Tree MST: A Tree, connecting all nodes in the graph, with minimum weight
            # Kruskal: The most common MST algo. Orders edges by increasing weight, then adds them as long as no cycle is formed. Uses set data structures to detect cycles.
            # graphComponent : as subgraphs is used elsewhere, decided to call mst subgraph graphComponent
        # Modifications: 
            # Kruskal algo insufficient for my use case as-written. The board may have wires, vias, zones, connected to each other. Since we want ratsnest wires to span between unconnected items, we collect connected vertices in self.subgraphs. intra-subgraph connections are not allowed. Inter-subgraph connections only. To this end we have .propagations() method to collect subgraphs; connected vertices. Propagations considers not just pad terminals, but also terminals of connected vias and wires and zones-- these are all viable vertices for the ratsnest to connect to 
            # .propagations method detects vertices connected to a given point; self.subgraphs. Used to prevent intra-subgraph connections
        # G started with padTerminals, then we added all points of propagation. Now, G is a list of points representing possible ratsnest vertices for this net. But that's not enough for a ratsnest-- we need to not draw wires between connected items -- so we also have self.subgraphs, containing sets representing connected items. 
                
        print()
        print('RATSNESTMST')
        
        def findSubgraph(index, G): # find the subgraph of G of the pos represented by index 
            pos  = flat[index] 
            for subgraph in G: 
                for xYLayer in subgraph: 
                    XY = xYLayer[0:2]  # Look at XY not xYLayer
                    if XY == pos:
                        return subgraph
            
        def findSet(index, subsets):
            for subset in subsets: 
                if index in subset: 
                    return subset 
            

        
        # kruskal starts w/ each vertex index its own set 
        
        # sets = [ set([index]) for index in range(len(flat))]
        

        subsets = [] 
        count = 0
        for subgraph in G: 
            subset = set() 
            for _ in subgraph: 
                subset.add(count)
                count +=1 
            subsets.append(subset)
        print('SUBSETS:', subsets)

        # Generate edges 
        coo = coo_array(squareform(pdist(flat)))
        # print(coo)
        edges = list(zip(coo.row, coo.col, coo.data)) 
        for edge in edges:  # Remove redundant edges 
            u, v, dist = edge 
            if (v,u,dist) in edges: 
                edges.remove((v,u,dist))
        edges = sorted(edges, key= lambda x: x[2])
        print('EDGES:', len(edges), edges)
        
        for edge in edges[:]: # Remove intra-subgraph edges. Unlike kruskalMST, ratsnestMST disallows intra-subgraph connections, implemented by removing intra-subgraph edges. 
            u,v,dist = edge
            # print('uPos:', uPos) 
            # print('vPos:', vPos)
            subgraphU, subgraphV = findSubgraph(u, G), findSubgraph(v, G)
            #Modify findSubgraph to find XY and not xYLayer
            print('subgraphU:', subgraphU)
            print('subgraphV:', subgraphV)
            # print('SUBGRAPHU:', subgraphU)
            # print('SUBGRAPHV:', subgraphV)
            if subgraphU == subgraphV: 
                edges.remove(edge)
        print('EDGES:', len(edges), edges)

        forest = set()
        for edge in edges: 
            print()
            print('EDGE:', edge)
            u,v,dist = edge
            
            setU, setV = findSet(u, subsets), findSet(v, subsets)
            print('SETU:', setU)
            print('SETV:', setV)
            if setU != setV: 
                forest = forest.union({ frozenset([u,v]) })
                subsets.append(setU.union(setV))
                subsets.remove(setU)
                subsets.remove(setV)
            
        print('FOREST:', forest)# MST: {frozenset({3, 4}), frozenset({1, 2}), frozenset({2, 6})}
        return forest
    
    # Pretty sure this makes a correct ratsnestMST.
    # def ratsnestMinimumSpanningTree(self, G):

    #     def findSubgraph(index): # index: 
    #         for subgraph in self.subgraphs: 
    #             if index in subgraph: 
    #                 return subgraph
    #     removedLayerCoordinate = list(set([i[0:2] for i in G ])) # Remember in slice [0:2] that 2 is exclusive 
    #     print('REMOVED LAYER COORDINATE:', removedLayerCoordinate) # [(0.9271,)]
    #     pairwiseDistance = pdist( removedLayerCoordinate )
    #     print('PAIRWISEDISTANCE:', pairwiseDistance) 
    #     adjacencyMatrix = squareform( pairwiseDistance ) # pdist as in pairwise distance. Use scipy to form weighted adjacency matrix, a precursor to the minimum spanning tree. See sparse matrices, compressed sparse matrices,  scipy.pdist, scipy.squareform, adjacency matrices, minimum spanning tree(everyone uses KruskalMST including me here). adj matrix aka 'graph' in compSci 
    #     # adjacencyMatrix = squareform( pdist( G )) 
    #     print('ADJACENCYMATRIX:', adjacencyMatrix)
        
    #     coo = coo_array(adjacencyMatrix) # Create a sparse matrix, COOrdinate flavor, so that we can use coo.row & coo.col to make our graph edges-- Note these edges are made of indices of points, corresponding to how they were ordered in 'points'. So edge(0,2) corresponds to points[0] to points[2]
    #     edges = list(zip(coo.row , coo.col, coo.data))      
    #     edges = sorted(edges, key = lambda coo : coo[2] ) # order G edges by weight; Kruskal algo
    #     for edge in edges: # Example: edge:(0,3,3.0) where 0&3 code for indices in G. 3.0 would code for the distance from G[0] to G[3]; edge weight. Thus edge 0-3 is a line from (0,0) to (3,0)            
    #         u = edge[0]
    #         v = edge[1]
    #         setU = findSubgraph(u)
    #         setV = findSubgraph(v)
        
    #         # for subgraph in self.subgraphs: 
    #         #     if (u in subgraph) and (v in subgraph):
    #         #         continue 
                
    #         if setU != setV:
    #             self.mst = self.mst.union( { frozenset(u,v) } ) # {}.union( { (0,3) } ) -> { (0,3) } # Store 2-sets, which preserves the data needed to draw lines. note in python, sets are mutable; unhashable. Unhashable types can't be part of a set. Use tuples or frozenset(which creates an immutable set) instead
    #             setU.union(setV)
                
    #     print()
    #     print('SELF.MST:', type(self.mst))
    #     print(self.mst)
    
    def addRatsnestToScene(self, G, flat, net):

        print()
        print('ADDRATSNESTTOSCENE')
        ratsnest = self.ratsnests[net]
        for line in ratsnest: # Remove from scene each existing line in ratsnest, then, clear ratsnest
            self.board.scene().removeItem(line)
        self.ratsnests[net] = []
        
        for edge in self.ratsnestMST(G, flat): 
            u,v = list(edge)
            print('FLAT[u]:', flat[u])
            line = QLineF(*flat[u], *flat[v])
            # line = QGraphicsLineItem(line)
            line = BoardLineItem(None, line)
            line.setPen(QPen(Qt.blue, 0 ))
            self.board.scene().addItem(line)
            self.ratsnests[net].append(line) # Track ratsnest lines for later removal from scene

    def updateVeins(self, pos): 

        # def merge( pos, wire, otherWire, points, row, col, data ): 
        def merge( pos, wire, otherWire ): 
            """Merge wires adjacent at pos
            Checks to ensure existence of adjacent collinear wires with no Symbol terminals on pos, nor any orthagonal wires on pos, are implemented elsewhere"""

            if len(points <= 2): # Then not enough points to perform a merge
                return
            

            index = points.index(pos) 
            points.pop(index)
            p1 = [wire.p1() , wire.p2()][wire.p2()==pos] 
            p2 = [otherWire.p1() , otherWire.p2()][otherWire.p2()==pos]
            index1 = points.index(p1)
            index2 = points.index(p2)

            upForMerge = {c for c,x in enumerate(row) if (x==index1) or (x==index2) } + { c for c,x in enumerate(col) if (x==index1) or (x==index2) }
            print('UPFORMERGE:', upForMerge)
            reversed = sorted(upForMerge , reverse=True)
            for l in [row, col, data]: 
                for r in reversed:
                    l.pop(r) # This entry is merging; no longer exists 

            dist = Utils.distance(points[index1] , points[index2])
            row.append(index1)
            col.append(index2) 
            data.append( dist)
            
            row.append(index2)
            col.append(index1)
            data.append(dist)

            
            # delete row and column 
            # deleted = G.pop(index)
            
            # indices12 = [] # Know positions adjacent to pos by which two are nonzero. Note if there winds up being more than 2 im screwed 
            # for count, d in enumerate(deleted): 
            #     if d != 0: 
            #         indices12.append(count)
            # index1, index2 = indices12 
                    
            # for row in G: 
            #     row.pop(index)

            # weight = deleted[index1] + deleted[index2]

            # if index1 > index : index1 -= 1 # We did delete a col from G, which affected indices greater than that column by 1
            # if index2 > index : index2 -= 1 
            
            # G[index1] [index2] = weight

### add/remove splits from scene 
            self.schematic.scene().removeItem(wire)
            self.schematic.scene().removeItem(otherWire)

            # p1, p2 = wire.line().toTuple()
            # p3, p4 = otherWire.line().toTuple
            
            # x1, y1 = p1.toTuple()
            # x2, y2 = p2.toTuple()
            # x3, y3 = p3.toTuple()
            # x4, y4 = p4.toTuple()
            
            # xMax = max(x1, x2 , x3 , x4) 
            # yMax = max(y1, y2, y3, y4)
            # xMin = min(x1, x2 , x3 , x4) 
            # yMin = min(y1, y2, y3, y4)
            
            # merged = WireItem(xMin, yMin, xMax, yMax) # Note this works bc previous checks ensure we're working with collinear lines & scene only allows hor/vert lines\
            merged = WireItem(*p1, *p2)
            merged.setPen(QPen(Qt.darkCyan, 1 ))
            merged.setVeinId(wire.veinId())
            self.schematic.scene().addItem(merged)

            return points , row, col, data , merged

        # def split(pos , wire, points, row, col, data ): 
        def split(pos , wire): 

            d1 = Utils.distance(wire.p1() , pos)
            d2 = Utils.distance(pos, wire.p2())

### remove/add split to scene
            split1 = WireItem(QLineF(wire.p1(), pos))
            split2 = WireItem(QLineF(pos, wire.p2()))
            split1.setPen(QPen(Qt.magenta, 1))
            split2.setPen(QPen(Qt.darkMagenta, 1))
            split1.setVeinId(wire.veinId())
            split2.setVeinId(wire.veinId())
            self.schematic.scene().addItem(split1)
            self.schematic.scene().addItem(split2)
            self.schematic.scene().removeItem(wire) 
            
            return split1 , split2
            # return points, row, col, data, split1 , split2

            # index = points.index(pos) 
            # index1 = points.index(wire.p1())
            # index2 = points.index(wire.p2()) 
            
            # upForRemoval = {c for c,x in enumerate(row) if (x==index1) or (x==index2)} + {c for c,x in enumerate(col) if (x==index2) or (x==index2)}
            # upForRemoval = sorted(upForRemoval, reverse=True)
            # for l in [row, col, data]: 
            #     for r in upForRemoval: 
            #         l.pop(r) # These edges no longer exist
            
            # # Add in new edges
            # #from wire.p1 to pos 
            # row.append(index) 
            # col.append(index1)
            # data.append(d1)
            
            # row.append(index1)
            # col.append(index)
            # data.append(d1)
            
            # # from pos to wire.p2 
            # row.append(index)
            # col.append(index2)
            # data.append(d2)

            # row.append(index2)
            # col.append(index)
            # data.append(d2)
            
                    



        def normalizeWiring(pos): 
            """Normalize entire wiring using queues & graph
            graph is of scipy COOrdinate form, where a graph is represented by three arrays: row, col, and data, see scipy.coo_array. 
            COOrdinate form was chosen over adjacency matrix because I couldnt quite figure out how to implement adjacency matrix :/
            See normalizeWiring Tutorial<LINK TUTORIAL> 
            Note usage of break break continue to stop processing a wire which needs to be split/merged.
            Note usage of while loops rather than for loops so as to be able to add split/merged wires as they're created
            
            a 'wiring' is one or more connected wires. 
            a wire is a line segment used to connect things on the schematic. 
            Note difference between 'wires floating in space' and 'wire end' and 'wire terminals'
            'wire(s) floating in space' means wiring never connects to anything, besides other wires. 
            'wire end' is a point where a wire is not connected to anything else
            'wire terminal' is either p1 or p2; its the point where wire can connect to other stuff
            """
            
            # G = [[]] 
            print()
            print('NORMALIZEWIRING')
            # row = []  # row col data as in scipy COOrdinate format 
            # col = [] 
            # data = [] 
            visitedPositions = []
            positionQueue = [pos] 
            points = [pos] # list of points. indices of points correspond to adjacencyMatrix 
            
            while positionQueue: 
                pos = positionQueue.pop(0)
                if pos in visitedPositions: 
                    continue 
                visitedPositions.append(pos)
                
                print('POS:', pos.toPoint())
                _merge = True # flag merge indicates whether there are collinear adjacent wires to merge at pos. Will not merge, if adjacent orthagonal wires, or Symbol terminals, are present at pos
                
                items = self.schematic.scene().items(pos) 
                while items: 
                    item = items.pop(0)
                    if not isinstance(item,( WireItem, Symbol) ):  # Ignore the seeker, which is a QGraphicsEllipseItem
                        continue 
                
                # for item in self.schematic.scene().items(pos): #  Usage of WHILE loops not for loops, so as to be able to add split/merged wires a
                    print('ITEM IS:', type(item))
                    if isinstance(item, Symbol): # Symbol includes ComponentSymbol, NetSymbol, label 
                        # sceneTerminals = item.sceneTerminals() # For ComponentSymbol, sceneTerminals
                        if any(otherTerminal == pos for otherTerminal in item.sceneTerminals()): # If there is a symbol terminal at pos, we do not want to merge adjacent wires
                            _merge = False 
                            # Collect pins and symbols and labels into vein
                            if isinstance(item, ComponentSymbol):
                                for pin in item.pins(): 
                                    if pin.sceneTerminal() == pos: 
                                        print('ADDING PIN')
                                        vein[Utils.SchematicItemKinds.Pin.value].append(pin)
                            # print('VEIN:', vein)
                            if isinstance(item, NetSymbol):
                                vein[Utils.SchematicItemKinds.NetSymbol.value].append(item)
                            if isinstance(item, LocalLabel):
                                vein[Utils.SchematicItemKinds.LocalLabel.value].append(item)

                    if isinstance(item, WireItem): 
                        print('WIRE.SCENETERMINALS():', item.sceneTerminals())
                        if not any(terminal == pos for terminal in item.sceneTerminals()): # Then this wire is not connected to this pos. 
                            print('WIRE NOT TERMINATING ON POS')
                            continue
                        
                        wire = item 
                        wireNormal = True # This flag indicates whether or not the wire is 'normal' -- abnormal wires get either split or merged, and then cease to be processed, while normal wires are processed as part of the vein
                        
                        #for symbols terminating inside wire segment: 
                        for symbol in [item for item in self.schematic.scene().collidingItems(wire) if isinstance(item, Symbol)] :
                            for symbolTerminal in symbol.sceneTerminals(): 

                                if Utils.pointWithinSegment(symbolTerminal, wire.line()):
                                    print('SYMBOL WITHIN WIRE SEGMENT')

                                    if (symbolTerminal not in positionQueue) and (symbolTerminal not in visitedPositions):
                                        positionQueue.append(symbolTerminal)
                                        # points.append(symbolTerminal)
                                        # points, row, col, data, split1, split2 = split(pos, wire, points, row, col, data)
                                        split1, split2 = split(pos, wire)
                                        items.append(split1)
                                        items.append(split2)
                                        wireNormal = False
                                        break # If we split a wire, we need to stop processing this wire, since we took it off the scene.
                            if not wireNormal: # break out of 'for symbol in symbols'
                                break

                        if not wireNormal: # Then we split this wire, and it no longer exists. continue to the next in 'while items' 
                            continue 

                        if _merge == True: # If merge is still True, lets look for wires orthagonal @ pos. If so, _merge=False. 
                            for otherWire in [otherWire for otherWire in self.schematic.scene().collidingItems(wire) if isinstance(otherWire, WireItem)]: # Check for orthagonal wires, no need to merge if any orthagonal wires
                                if any(otherTerminal == pos for otherTerminal in otherWire.sceneTerminals()): # Check wire, otherWire, are adjacent @ pos # TODO: at this point , do a wire-end-check: check that wire @ pos IS connected to another wire @ pos (otherwise wire ends here, and thats a special case )
                                        if Utils.wiresAreOrthagonal(wire, otherWire):  
                                            _merge = False 
                        if _merge == True: #  If merge still True, then there were no Symbols on pos, and no orthagonals on pos, and pos is not a wire end. Thus there are collinear adjacent wires at pos and we need to merge them.

                            if len(points) <= 2: 
                                print(f'MERGE REQUIRES 3+ POINTS BUT LEN(POINTS) = {len(points)})')
                                # continue # to the next item in 'while items'
                                _merge = False 
                                
                            if _merge == True: 
                                # points , row, col, data, merged = merge(pos, wire, otherWire, points , row, col, data)
                                merged = merge(pos, wire, otherWire)
                                items.append(merged)
                                wireNormal = False
                                continue # to the next item in 'while items'
                        
                        # Reaching this point means wireNormal, and we want to add wire to our vein 
                        print('WIRENORMAL')
                        vein[Utils.SchematicItemKinds.Wire.value].append(wire)

                        # if any(terminal == pos for terminal in wire.sceneTerminals()): # Then this wire is connected to this pos. 
                        if wire.veinId() is not None: 
                            self.connectedVeins.add(wire.veinId())

                        p1 = wire.p1()
                        p2 = wire.p2()
                        if pos == p1: 
                            distal = p2 
                        elif pos == p2: 
                            distal = p1 

                        if ( distal not in positionQueue) and (distal not in visitedPositions) : 
                            positionQueue.append(distal)
                            # points.append(distal)
                            print('DISTAL:', distal.toPoint())
                            # print('POINTS:', points)

                            # index = points.index(pos)
                            # indexDistal = points.index(distal)
                            
                            # row.append(index) 
                            # row.append(indexDistal) 
                            
                            # col.append(index) 
                            # col.append(indexDistal) 

                            # dist = Utils.distance(distal, pos) 
                            # data.append(dist)
                            # data.append(dist)
                        
            print('NORMALIZEWIRINGDONE')
            print()
            # return points , row, col, data
            return None
### BEGIN UPDATEVEINS ###
        print()
        print('UPDATEVEINS:')
        vein = defaultdict(list)              
        # points, row, col, data = normalizeWiring(pos)
        normalizeWiring(pos)
        print('VEIN:', vein)

        print('MW.CONNECTEDVEINS:', self.connectedVeins)
        
        if self.connectedVeins: # Kill any veins which were connected to. Remove that vein from vein, nets, & ratsnest. Connected-to veins will become absorbed into the vein we're currently laying
            for id in self.connectedVeins: 
                print('ID:', id)
                print('SELF.VEINS:', self.veins)
                net2Rm = self.veins.pop(id)['net']
                print('NET2RM:', net2Rm)
                self.nets[net2Rm]['veinIds'].remove(id)
                
                ratsnest = self.ratsnests[net2Rm]
                for line in ratsnest:  # Remove from scene each existing line in ratsnest, then, clear ratsnest
                    self.board.scene().removeItem(line)
                self.ratsnests[net2Rm] = [] 


        
        veinId = max(self.veins) + 1 
        print('VEINID:', veinId)
        # Put vein in veins, nets, and ratsnest
        self.veins[veinId] = vein 

        
        self.setVeinNets(vein) 
        
        if len(vein['nets']) == 1: # Then no DRC error; its good this vein has one net.
            print('THIS VEIN HAS ONE NET')
        if len(vein['nets']) > 1: # Then that's bad; DRC error 
            print('THIS VEIN HAS MORE THAN ONE NET. DRC ERROR')
            return 


        nets = vein['nets']
        print('NETS:', nets)
        
        if not nets: 
            net = None 
            
        if len(nets) == 1: 
            net = nets[0]

        if len(nets) > 1: 
            print('DRC ERROR: MORE THAN ONE ASSIGNED NET: ', nets)
            net = nets # Note we still track net chimera as a list rather than a string (?)
            
        if net == None : # Then we're dealing with wires floating in space, and as such, there is no vein to update
            return 
        
        if not self.nets[net]: 
            self.nets[net] = defaultdict(list) 
            
        self.nets[net]['veinIds'].append(veinId)
        
        veinPins =vein[Utils.SchematicItemKinds.Pin.value] 
        print()
        print('VEINPINS:' ,veinPins)
        if not veinPins: 
            print('NO veinPins')
            print('VEIN:', vein)
            for key, value in vein.items(): 
                print('KEY:',key)
                print('VALUE:', value)
            return 

        for pin in veinPins: 
            refDes = pin.parentItem().referenceDesignator()
            refNum = pin.parentItem().referenceNumber() 
            
            symbol = self.schematic.scene().symbols[refDes][refNum]
            if isinstance(symbol, ComponentSymbol): #  CompSyms are the only symbols that have pads. NS and Labels have no pads. 
                component = self.components[refDes][refNum]
                pads = component.footprintItem().pads()

                for pad in pads: 
                    if pad.name() == pin.number():  # Then this pin and pad are linked
                        print('PADNAME MATCHES PINNUMBER', pad, pin)
                        pad.setNet(net) # initial pad net is set in constructor, but pad nets may be overridden
                        vein['pads'].append(pad) 
                        self.nets[net][Utils.BoardItemKinds.Pad.value].append(pad)# update nets with pads whose pad.name() matches the pin.number(). 
                        # veinPins/pads are linked via their padName matching their pinNumber. Based on looking at 2 kicad files.
                # self.nets[vein['net']][Utils.BoardItemKinds.Pad.value].extend(pinPads) NO BAD fetches all pads 

        # print('VEIN:', vein)
        for key, value in vein.items(): 
            print('KEY:',key)
            print('VALUE:', value)
            
        self.updateRatsnest(net)
        
































#         def wire1SplitBySymbolOrLabel(): # Split wire1 if a symbol or label terminal is on wire1  
#             symbolsAndLabels    = [ item for item in self.schematic.scene().collidingItems(wire1) if isinstance(item, (ComponentSymbol, NetSymbol, Label) ) ]  # All symbols and labels intersecting wire1
#             print('SYMBOLSANDLABELS:', symbolsAndLabels)
#             # print('P1:', p1.toPoint()) 
#             # print('P2:', p2.toPoint())
#             for symbolOrLabel in symbolsAndLabels: # If symbolOrLabel terminal is ON wire1, then, split wire @ terminal, ignore cases where terminals exactly match; adjacency needs no split

#                 print('SYMBOLORLABEL:', symbolOrLabel)
#                 print('SOL.SCENETERMINALS:', symbolOrLabel.sceneTerminals())

#                 for otherTerminalPos in symbolOrLabel.sceneTerminals():
#                     # otherTerminalPos = QPointF(*otherTerminalPos)

#                     if wire1.contains(otherTerminalPos): #Just bc schematicItem intersects wire, dont mean its terminals do. Check which schematicItem terminals intersect, ignoring terminals coincident with wire terminals #TODO change this to inbound collinear test? in-segment intersection test?

#                         if otherTerminalPos == p1 or otherTerminalPos == p2: 
#                             continue # if symbol or label terminates on wire terminal, no need to split
#                         print('OTHERTERMINAL:', otherTerminalPos.toPoint()) # OTHERTERMINAL: (PySide6.QtCore.QPointF(232.186047, 482.232558), <SchematicSymbolItem.PinItem(0x171a1651980, parent=0x171a16513c0, pos=0,0) at 0x00000171A07C0080>)

#                         orient = Utils.threePointOrientation(p1, p2, otherTerminalPos)        
#                         if orient == 0: # Then pos collinear with p1p2 . Check if otherTerminalPos within segment p1p2
#                             xOverlap = (p1.x(), p2.x(), otherTerminalPos.x(), otherTerminalPos.x())
#                             yOverlap = (p1.y() , p2.y(), otherTerminalPos.y(), otherTerminalPos.y()) 
#                             if xOverlap and yOverlap: # then split this wire 
#                                 split1 = WireItem(QLineF(p1, otherTerminalPos))
#                                 split2 = WireItem(QLineF(otherTerminalPos, p2))
#                                 self.schematic.scene().removeItem(wire1)
#                                 self.schematic.scene().addItem(split1)
#                                 self.schematic.scene().addItem(split2)
#                                 wires.append(split1)
#                                 # wires.append(split2) Note we do NOT add split2 to wires when splitting by symbolOrLabel otherTerminalPos, bc split2 does not touch pos. split2 is on the scene, so it will be visited, but not 
#                                 print('WIRE1 SPLIT BY SYMBOL OR LABEL')

#                                 return True
#             return False   

#         def normalizeWires(): 
    
#             def rangesOverlap(a1,a2 , b1,b2) : 
#                 # First, make sure that ranges are 'well ordered':  n1 < n2 
#                 if a1 > a2: 
#                     a1, a2 = a2, a1 # Switch 1&2
#                 if b1 > b2: 
#                     b1, b2 = b2, b1
#                 # Its a mindfuck, but ranges overlap if the start of one range is <= end of the other AND vice versa
#                 return a1 <= b2 and b1 <= a2
            
#             def junction(wire1, wire2): 
#                 """Returns a tuple which differs depending on junction type between wire1 and wire2. 
#                 Zeroeth index is junctionType, a Utils.JunctionType. 
#                 If junctionType is Utils.JunctionType.Tee, this function will return a 2-tuple (junctionType, zero) where zero is orient1, orient2, orient3, or orient4, whichever one was zero. See three point orientation tutorial.
#                 If junctionType is any other Utils.JunctionType, this function will return a 1-tuple (junctionType)
#                 Note (5) is an int while (5,) is a tuple. This used in this functions return statements """
                
#                 orient1 = Utils.threePointOrientation(p1,p2,p3) 
#                 orient2 = Utils.threePointOrientation(p1,p2,p4)
#                 orient3 = Utils.threePointOrientation(p3,p4,p1)
#                 orient4 = Utils.threePointOrientation(p3,p4,p2)
                
#                 numZeroes = [orient1, orient2, orient3, orient4].count(0)
                
#                 if numZeroes == 1: # Then this is a Tee intersection. Will split, if no 'L' @ split point 
#                     zero = [orient1, orient2, orient3, orient4].index(0) # Find the index of the single zero. We can tell how we should split based on which orient is 0.
#                     return ( Utils.JunctionType.Tee , zero )
                
#                 elif numZeroes == 2: # Then this is a L intersection. No action.
#                     return ( Utils.JunctionType.L , ) 
                
#                 elif numZeroes == 4: #Then these lines are collinear. Check if they are adjacent collinear, or overlapping collinear, or nonintersecting
#                     if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4: # Then these are adjacent collinear. 
#                         return ( Utils.JunctionType.CollinearAdjacent , )
#                     else: 
#                         x1, y1 = p1.toTuple() 
#                         x2, y2 = p2.toTuple()
#                         x3, y3 = p3.toTuple()
#                         x4, y4 = p4.toTuple()
                
#                         # Test if X range overlaps: 
#                         xOverlap = rangesOverlap(x1, x2 , x3 , x4)
#                         yOverlap =  rangesOverlap(y1,y2 , y3, y4) 
#                         if xOverlap or yOverlap: # If x-rangesoverlap OR y-ranges overlap, these lines overlap
#                             return ( Utils.JunctionType.CollinearOverlap ,)
                        
#                 elif orient1 != orient2 and orient3 != orient4: # Then these lines are intersecting. Note no action needed here(no split. intersecting lines in EDA SW are supposed to not connect
#                     return ( Utils.JunctionType.Intersecting , )
                
#                 return ( Utils.JunctionType.NonIntersecting , )
            
#             def merge(): # merge does not take self as merge is a local function within normalizeWires
#                 print('MERGE')
#                 self.schematic.scene().removeItem(wire1)
#                 self.schematic.scene().removeItem(wire2)
                
#                 x1, y1 = p1.toTuple() 
#                 x2, y2 = p2.toTuple()
#                 x3, y3 = p3.toTuple()
#                 x4, y4 = p4.toTuple()
                
#                 xMax = max(x1, x2 , x3 , x4) 
#                 yMax = max(y1, y2, y3, y4)
#                 xMin = min(x1, x2 , x3 , x4) 
#                 yMin = min(y1, y2, y3, y4)
                
#                 merged = WireItem(xMin, yMin, xMax, yMax) # Note this works bc previous checks ensure we're working with collinear lines & scene only allows hor/vert lines\
#                 merged.setPen(QPen(Qt.darkCyan, 1 ))
                
#                 self.schematic.scene().addItem(merged)
#                 wires.append(merged)
#                 # There are already no mentions of wire1/2 anywhere, either already popped or not yet added(?)
#                 if not merged.line().p1()  in visitedPositions:
#                     positionQueue.append(merged.line().p1())
#                 if not merged.line().p2()  in visitedPositions:
#                     positionQueue.append(merged.line().p2())

#             def split(junction):
#                 print('SPLIT')
#                 # pass # Know how to split wire by which orient1234 is 0. 
#                 junctionId = junction[1]
#                 if junctionId == 0: # Split line(p1,p2) @ p3. Remove wire1 from scene
#                     split1 = (p1, p3) 
#                     split2 = (p3, p2)
#                     self.schematic.scene().removeItem(wire1)
                    
#                 elif junctionId == 1: # Split line(p1,p2) @ p4 
#                     split1= (p1, p4) 
#                     split2 = (p4, p2) 
#                     self.schematic.scene().removeItem(wire1)
#                 elif junctionId == 2: # Split line(p3, p4) @ p1 
#                     split1 = (p3, p1) 
#                     split2 = (p1, p4) 
#                     self.schematic.scene().removeItem(wire2)
#                 elif junctionId == 3: # Split line(p3, p4) @ p2
#                     split1 = (p3, p2) 
#                     split2 = (p2, p4)
#                     self.schematic.scene().removeItem(wire2)

#                 split1 = QLineF(*split1)
#                 split2 = QLineF(*split2)
                
#                 # if not split1.p1() in visitedPositions: # Dont think this good
#                 #     visitedPositions.append(split1.p1())
                    
#                 # if not split2.p2() in visitedPositions: 
#                 #     visitedPositions.append(split2.p2())
                    
#                 split1 = WireItem(split1)
#                 split2 = WireItem(split2)
                
#                 # Colors for debugging
#                 split1.setPen(QPen(Qt.magenta, 1))
#                 split2.setPen(QPen(Qt.darkMagenta, 1))

#                 # self.schematic.scene().removeItem(wire1) 
#                 self.schematic.scene().addItem(split1)
#                 self.schematic.scene().addItem(split2)
                

            
#             # def checkLs(pos): # Deprecated for checkOtherTerminals
#             #     hitWires = [ hitWire for hitWire in self.schematic.scene().items(pos) if isinstance(hitWire, WireItem) ] 
                
#             #     for hitWire in hitWires: 
#             #         if hitWire == wire1 or hitWire == wire2: 
#             #             continue 
#             #         if junction(wire1, hitWire)[0] == Utils.JunctionType.L:
#             #             return True
#             #     return False 
            
#             def checkOtherTerminals(pos): # Check if there is either an L-junction or a non-Wire terminal, like a label or ComponentSymbol terminal, at pos. If there is, then we would not want to merge collinear adjacent wires at pos. 
#                 hitItems = [item for item in self.schematic.scene().items(pos) if isinstance(item, (WireItem, Symbol))]
#                 for hitItem in hitItems: 
#                     if hitItem == wire1 or hitItem == wire2: 
#                         continue 
#                     if isinstance(hitItem, WireItem):
#                         if junction(wire1, hitItem)[0] == Utils.JunctionType.L:
#                             return True 
#                     for otherTerminalPos in hitItem.sceneTerminals(): 
#                         if otherTerminalPos == pos:
#                             return True
                            
#                 # hitWires = [ hitItem for hitItem in hitItems if isinstance(hitItem, WireItem) ]
#                 # hitSymbolsAndLabels = [ hitItem for hitItem in hitItems if isinstance(hitItem, )]
            
#             def processJunction(junction):
#                 wire1Normal = True
                
#                 junctionType = junction[0] 
                
#                 if  junctionType == Utils.JunctionType.Tee: 
#                     split(junction)
#                     wire1Normal = False
#                 elif junctionType == Utils.JunctionType.CollinearOverlap: 
#                     merge()
#                     wire1Normal = False 
#                 elif junctionType == Utils.JunctionType.CollinearAdjacent:# Check for L intersections @adjacent point. if None, merge 
#                     if p1 == p3 or p1 == p4:
#                         adjacentPoint = p1
#                     if p2==p3 or p2==p4: 
#                         adjacentPoint = p2 
                
#                     # if not checkLs(adjacentPoint) and not checkTerminals(adjacentPoint):
#                     if not checkOtherTerminals(adjacentPoint):
#                         merge()
#                         wire1Normal = False 
#                 return wire1Normal   
                
#             print('NORMALIZEWIRES')
#             junc = Utils.junction(wire1.line() , wire2.line())
#             print('JUNC:', junc)
#             wire1Normal = processJunction(junc)
#             return wire1Normal

#         # def wirePropagations(pos): 
#         visitedPositions = [] 
#         visitedWires = []     
#         visitedSymbolsAndLabels = []
#         positionQueue = [pos] # To start, we know we want to look at pos. As we go, we'll add the distal coordinate of connected wires, expanding the vein
#         self.connectedVeins = {}       
#         vein = defaultdict(list)              

#         while positionQueue: 
#             pos = positionQueue.pop(0)
#             if pos in visitedPositions: continue
#             visitedPositions.append(pos) 
#             print()
#             print('POS:', pos.toPoint())
#             # items = self.queryRtrees(pos)
#             wires = [ item for item in self.schematic.scene().items(pos) if isinstance(item,  WireItem                 ) ]  # All wires intersecting pos
#             print('WIRES:', wires)
#             while wires: # inf refursion when lay wire over existing wire
#                 print('WHILE WIRES')
#                 print('WIRES:', wires)
#                 wire1 = wires.pop(0) 
#                 wire1Normal = True 
#                 if wire1 in visitedWires: 
#                     continue
#                 p1 = wire1.p1()
#                 p2 = wire1.p2()
#                 if pos == p1: 
#                     distal = p2 
#                 elif pos == p2: 
#                     distal = p1 
#                 print('DISTAL:', distal.toPoint())
#                 # wire1: may be split by a connecting symbol or label
#                 if wire1SplitBySymbolOrLabel(): 
#                     continue # wire was split, no longer exists, move on
#                 hitWires = [item for item in self.schematic.scene().collidingItems(wire1) if isinstance(item, WireItem)]

#                 print('HITWIRES:', len(hitWires), hitWires)
                
#                 while hitWires: 
#                     print('WHILE HITWIRES')
#                     wire2 = hitWires.pop(0)
#                     if wire2 in visitedWires : 
#                         continue
#                     if wire2 == wire1:
#                         continue 

#                     p3 = wire2.p1()
#                     p4 = wire2.p2()   
                    
#                     wire1Normal = normalizeWires() # 'Normalize' wire1 and wire2: merge or split, if needed. If wire1 was abnormal -> False. If wire1 was normal -> True
                    
#                     if not wire1Normal: 
                        
#                         break # If wire1 was split or merged; abnormal, wire1 was no good for thevein, ditch all hitWires w/ break, and move to the next wire1 w/ continue
        
#                 if not wire1Normal: 
#                     print('ONTOTHENEXTWIRE1')
#                     continue # IF wire1 is abnormal, then it no longer exists, so stop processing it
                
#                 if wire1Normal:
                    
#                     vein[Utils.SchematicItemKinds.Wire.value].append(wire1) # wire was checked and was neither splittable nor mergeable; normal. Lets add it to the vein
#                     positionQueue.append(distal)
#                     visitedWires.append(wire1) 

#                     # print('POSQ:', positionQueue)
#                     if wire1.veinId is not None:
#                         self.connectedVeins.add(wire1.veinId)
# # collect pins/labels of normalized wires
#                     symbolsAndLabels    = [ item for item in self.schematic.scene().collidingItems(wire1) if isinstance(item, (ComponentSymbol, NetSymbol, Label) ) ]  # All symbols and labels intersecting wire1
#                     print('SYMBOLSANDLABELS:', symbolsAndLabels)
#                     for symbolOrLabel in symbolsAndLabels: 
#                         # for otherTerminalPos, pin in symbolOrLabel.sceneTerminals().items():
#                         # for otherTerminalPos in symbolOrLabel.sceneTerminals():
#                         for pin in symbolOrLabel.pins(): 
                            
#                             otherTerminalPos = pin.sceneTerminal()
                        
#                             # otherTerminalPos = QPointF(*otherTerminalPos) # QPoint is unhashable; cannot be dict keys, so I have to manually convert back to QPoint. Which I hate. TODO: change everything to tuple points? idk
#                             if wire1.contains(otherTerminalPos): #Just bc schematicItem intersects wire, dont mean its terminals do. Check which terminals are contained by wire1,before checking which exactly match up #TODO change this to inbound collinear test? in-segment intersection test?

#                                 if otherTerminalPos == p1 or otherTerminalPos == p2:  # Collect pins and symbols and labels into vein
#                                     print('ADDING PINS')
#                                     vein[Utils.SchematicItemKinds.Pin.value].append(pin)
                                    
#                                     print('VEIN:', vein)
#                                     if isinstance(symbolOrLabel, NetSymbol):
#                                         vein[Utils.SchematicItemKinds.NetSymbol.value].append(symbolOrLabel)
#                                     if isinstance(symbolOrLabel, ComponentSymbol):
#                                         vein[Utils.SchematicItemKinds.ComponentSymbol.value].append(symbolOrLabel)
                
#         print()
#         print('PROPAGATEWIRESDONE')
#         print('VEIN:', vein)
#         if self.connectedVeins: # Kill any veins which were connected to. Remove that vein from vein, nets, & ratsnest. Connected-to veins will become absorbed into the vein we're currently laying
#             for id in self.connectedVeins: 
#                 net2Rm = self.veins.pop(id)['net']
                
#                 self.nets[net2Rm]['veinIds'].remove(id)
                
#                 ratsnest = self.ratsnests[net2Rm]
#                 for line in ratsnest:  # Remove from scene each existing line in ratsnest, then, clear ratsnest
#                     self.board.scene().removeItem(line)
#                 self.ratsnests[net2Rm] = [] 


#         net = self.setVeinNets(vein) 
#         print('NET', net)
        
#         veinId = max(self.veins) + 1 
#         print('VEINID:', veinId)
#         # Put vein in veins, nets, and ratsnest
#         self.veins[veinId] = vein 
        
#         if not self.nets[net]: 
#             self.nets[net] = defaultdict(list) 
            
#         self.nets[net]['veinIds'].append(veinId)
        
#         veinPins =vein[Utils.SchematicItemKinds.Pin.value] 
#         print()
#         print('VEINPINS:' ,veinPins)
#         if not veinPins: 
#             print('NO veinPins')
#             print('VEIN:', vein)
#             for key, value in vein.items(): 
#                 print('KEY:',key)
#                 print('VALUE:', value)
#             return 
# # self.components holds caps, res, leds; ComponentSymbols, not NetSymbols. 
# # but veinPins holds any pin, from a ComponentSymbol o NetSymbol or Label. 
# # So 'for pin in veinPins' includes NetSymbol veinPins, but, these veinPins' reference DNE in components. 
# # consistent api across NS, Label, CompSym... they don't really 
# # implement SchScene.symbols
# # for pin in veinPins: 
# #     pads = self.schematic.scene().symbols[refDes][refNum].footprintItem()
#         # print('SELF.COMPONENTS:', self.components)
#         # for pin in veinPins :
#         #     print('PIN.PARENTITEM():', pin.parentItem())
#         #     print('PARENTITEM().REFERENCEDESIGNATOR()', pin.parentItem().referenceDesignator())
#         #     print('PARENTITEM().REFERENCENUMBER()', pin.parentItem().referenceNumber())
#         #     pads = self.components[pin.parentItem().referenceDesignator()][pin.parentItem().referenceNumber()].footprintItem().pads()
#         #     print('PADS:', pads)
#         #     # set net on every pad. So that brdScene knows net info of its own pads, w/o needing MW.nets, which brdScene cannot ez access. 

#         for pin in veinPins: 
#             refDes = pin.parentItem().referenceDesignator()
#             refNum = pin.parentItem().referenceNumber() 
            
#             symbol = self.schematic.scene().symbols[refDes][refNum]
#             if isinstance(symbol, ComponentSymbol): # CompSyms are the only symbols that have pads. NS and Labels have no pads. 
#                 component = self.components[refDes][refNum]
#                 pads = component.footprintItem().pads()

#                 for pad in pads: 
#                     if pad.name() == pin.number():  # Then this pin and pad are linked
#                         print('PADNAME MATCHES PINNUMBER', pad, pin)
#                         vein['pads'].append(pad) 
#                         pad.setNet(net) # initial pad net is set in constructor, but pad nets may be overridden
#                         self.nets[net][Utils.BoardItemKinds.Pad.value].append(pad)# update nets with pads whose pad.name() matches the pin.number(). 
#                         # veinPins/pads are linked via their padName matching their pinNumber. Based on looking at 2 kicad files.
#                 # self.nets[vein['net']][Utils.BoardItemKinds.Pad.value].extend(pinPads) NO BAD fetches all pads 

#         # print('VEIN:', vein)
#         for key, value in vein.items(): 
#             print('KEY:',key)
#             print('VALUE:', value)
            
#         self.updateRatsnest(net)
                    
    def onAddNetSymbolActionTriggered(self):

        path = os.path.join(Utils.SauraPath, Utils.SymbolDirectoryName, Utils.NetSymbolDirectoryName)
        print(path)

        filePath, fileFilters = QFileDialog.getOpenFileName(self, 'Select Net Symbol', path)

        head, tail = os.path.split(filePath)
        netSymbolFile = tail 
        root, ext = os.path.splitext(tail)
        referenceDesignator = root 

        print(netSymbolFile)
        print(referenceDesignator)

        if self.netSymbols[referenceDesignator]: # Give netSymbol a referenceNumber
            referenceNumber = max(self.netSymbols[referenceDesignator]) + 1 
        else: 
            referenceNumber = 1 
        netSymbol = NetSymbol(referenceDesignator, referenceNumber, filePath)
        
        self.schematic.scene().addItem(netSymbol)
        netSymbol.setPos(self.schematic.scene().seeker().scenePos())
        self.netSymbols[referenceDesignator][referenceNumber] = netSymbol 
        
        
    @Slot(dict) # part . The part which was changed.
    def reloadPart(self, part): # part was just updated in db. I need to propogate fresh part to all symbols/footprints. 
        print()
        print('MySCENE.RELOAD_PART')
        for item in self.schematic.scene().items():
            if isinstance(item, ComponentSymbol):
                if item.part.get('mpn') == part.get('mpn'):
                    print('MPNS MATCH ! RELOADING PART:')
                    newItem = ComponentSymbol.fromPart(part, item.referenceNumber() ) # referenceNumber didn't change; Grab item.referenceNumber() for new_item
                    newItem.setPos(item.scenePos())
                    self.schematic.scene().removeItem(item)
                    self.schematic.scene().addItem(newItem)
                # item.setPart(part) # Not enough-- if we changed part's symbol, must update that, as well... 
                # There actually is no reloading of parts-- 

        for item in self.board.scene().items():
            if isinstance(item, FootprintItem):
                newItem = FootprintItem.from_part(part, item.referenceNumber()) # Will be same graphic as old item if we didn't update 'footprint' field
                newItem.setPos(item.scenePos())
                self.board.scene().removeItem(item)
                self.board.scene().addItem(newItem)


        
    # @Slot(str , int)
    # def delete_footprint(self, reference , referenceNumber):
    #     print(f'Deleting Footprint & Symbol: {reference}{referenceNumber}')
        
    #     deleted_symbol = False 
    #     deleted_footprint = False 
    #     for item in self.schematic.scene().items():
    #         if isinstance(item, MySymbolObject):
    #             if (item.reference , item.referenceNumber()) == ( reference , referenceNumber ):
    #                 self.schematic.scene().removeItem(item)
    #                 deleted_symbol = True
    #                 print('DELETED SYMBOL')
    #     for item in self.board.scene().items():
    #         if isinstance(item, FootprintItem):
    #             if (item.reference , item.referenceNumber()) == ( reference , referenceNumber ):
    #                 self.board.scene().removeItem(item)
    #                 deleted_footprint = True
    #                 print('DELETED FOOTPRINT')
    #     if (not deleted_footprint) or(not deleted_symbol): 
    #         print(f'SOMETHING WRONG, COULD NOT DELETE reference_value: {reference}{referenceNumber}')
            
        
    # @Slot( dict , QGraphicsSceneDragDropEvent, int) # event fresh from QGraphicsScene.dropEvent(self, event). part is dict, contained in drop's mimeData. sourceWidget is the widget where event happened, either Widgets.Schematic or Widgets.Board
    @Slot( dict , str, int) 
    def deletePart(self, referenceDesignator , referenceNumber): 
        # print("MW DELETING PART")
        # print('COMPONENTS:', self.components)
        # print('REFERENCEDESIGNATOR:', referenceDesignator)
        # print('REFERENCENUMBER:', referenceNumber)

        # print(self.board.scene().footprints)
        # print(self.schematic.scene().symbols)
        # footprint = self.board.scene().footprints[referenceDesignator].pop(referenceNumber)
        # symbol = self.schematic.scene().symbols[referenceDesignator].pop(referenceNumber)
        footprint = self.components[referenceDesignator][referenceNumber].footprintItem()
        symbol = self.components[referenceDesignator][referenceNumber].symbolItem()
        print('FOOTPRINT:', footprint)
        # # self.board.scene().ids[footprint.id] = None # set value in ids to 'None' 
        # self.board.scene().ids.pop(footprint.id) # Remove from ids 
        # self.board.scene().index.delete(footprint.id, footprint.buffered_bounds()) # Remove from index. Index().delete(id, bounds) : Deletes an item from the index by id and coordinates. Note Index id uniqueness is up to the user to implement

        self.board.scene().removeItem(footprint)
        self.schematic.scene().removeItem(symbol) # Remove reference_value from symbols
        
    def onTableClicked(self, part):
        pass

    def placePart(self, part, event , sourceWidget): # Drop a part onto the board's & schematic's respective scenes ( the board gets a footprint, the schematic gets a symbol ) # Source_widget: a number, representing where this signal came in from
        print()
        print('placePart')
        # print('SOURCE_WIDGET:', sourceWidget)
        # print()
        
        referenceDesignator = part.get('referenceDesignator', '?')
        if self.components[referenceDesignator]:
            referenceNumber = max(self.components[referenceDesignator]) + 1
        else: 
            referenceNumber = 1 # initialize to 1. Don't want 0indexed referenceNumbers
            
        component = Component.fromPart(part, referenceNumber)
        
        self.components[referenceDesignator][referenceNumber] = component # Track the component
        print('ADDED COMPONENT:' , self.components) # Looks good...
        
        
        if sourceWidget == MyWidgets.Schematic.value:
            component.symbolItem().setPos(self.schematic.scene().snapToGrid(event.scenePos())) # Add symbol lined up on the grid 
            component.footprintItem().setPos(55,55)
            
        elif sourceWidget == MyWidgets.Board.value:
            component.symbolItem().setPos(111,111)
            component.footprintItem().setPos(self.board.scene().snapToGrid(event.scenePos()))
        # print('ADDING ITEMS')
        
        self.schematic.scene().addItem(component.symbolItem())
        self.board.scene().addItem(component.footprintItem())
        
        # self.parts.add(part)
        
# Be sure to add to: the scene, scene.ids, add one to components, and add to the scene.index
        

    def dropEvent(self, event): # This event handler is called when the drag is dropped on this widget. The event is passed in the event parameter.      
        print()
        print('MAINWINDOW.DROPEVENT()') # Does not execute when I drop on scene
        super().dropEvent(event)   # Why call this?   

        
    def create_menus(self): 
        self._file_menu = self.menuBar().addMenu("&File") # -> QMenu, so we can add actions to file menu
        # self.menuBar().clear()
        self._file_menu.addAction(self.exit_action)
        self._file_menu.addSeparator() # Aestheic line 
        self._file_menu.addAction(self._addWireAction)
        self._file_menu.addAction(self.delete_wire_action)
        
        self._preferences_menu = self.menuBar().addMenu("&Preferences")
        
        self.create_menu = self.menuBar().addMenu("Create")
        # self.create_menu.addAction(self.create_symbol_action)
        # self.create_menu.addAction(self.create_footprint_action)
        self.create_menu.addAction(self.create_part_action)
        # self._schematic_toolbar.addAction(self.create_footprint_action)
        # self._schematic_toolbar.addAction(self.create_part_action)
        
# Actions are meant to be children of the application's main window, and live in menus, toolbars, and buttons. Actions shoiuld be connected to slots, which will execute the action

    def create_actions(self): # Later, Actions go on toolbar
    # Add Net Symbol
        self.add_net_symbol_action = QAction("Add Net Symbol", self, triggered = self.onAddNetSymbolActionTriggered)
    # Add Wire 
        self._addWireAction = QAction("Add Wire", self, triggered = self.onAddWireActionTriggered) # Hook up this action with  MyScene's slot. Equivalent : self._addWireAction.triggered.connect(MyScene.wiring_action_signal) # specifying triggered = func1 in the action's constructor is equivalent to  action.triggered.connect(func1) 
        self._addWireAction.setCheckable(True)
        # TODO # Pressing the esc key while in add_wire_mode should set scene.mode to default mode
        self._addWireAction.setShortcut(QKeySequence("W")) # Set the shortcut#Question: how can I code for self._addWireAction to emit integer '10' when i click its' button?
    # Delete Wire 
        self.delete_wire_action = QAction("Delete Wire", self, triggered = self.on_delete_wire_action_triggered)
        self.delete_wire_action.setShortcut(QKeySequence('D'))
    # # Create Symbol
    #     self.create_symbol_action = QAction("Create Symbol", self, triggered = self.on_create_symbol_action_triggered)
    #     self.create_symbol_action.setShortcut(QKeySequence('S'))
    # # Create Footprint
    #     self.create_footprint_action = QAction("Create Footprint", self, triggered = self.on_create_footprint_action_triggered)
    #     self.create_footprint_action.setShortcut(QKeySequence('F'))
    # Create Part 
        self.create_part_action = QAction("Create Part", self, triggered = self.on_create_part_action_triggered)
        self.create_part_action.setShortcut(QKeySequence('P'))
    # Show Board 
        self.show_board_action = QAction('Show Board', self, triggered = self. on_show_board_action_triggered)
    # Show Schematic 
        self.show_schematic_action = QAction('Show Schematic', self, triggered = self.on_show_schematic_action_triggered)
    

#Board Actions 
    # Add Trace 
        self.add_trace_action = QAction('Add Trace' , self, triggered = self.add_trace_action_triggered)
    #Create Gerber 
        self.create_gerbers_action = QAction('Create Gerber Files', self, triggered = self.create_gerbers)
    # Exit 
        self.exit_action = QAction("Exit", self, triggered = self.close)
        

# Actions not on any toolbar: 
    # Assign Symbol To Part 
        self.assign_symbol_action = QAction("Assign Symbol To Part", self)
    # Assign Footprint to Part
        self.assign_footprint_action = QAction("Assign Footprint to Part")

    def add_trace_action_triggered(self):
        print('add_trace_action_triggered')
        if self.board.scene().mode() != self.board.scene().addTraceMode:
            self.board.scene().setMode(self.board.scene().addTraceMode)
        else: 
            self.board.scene().setMode(self.board.scene().normalMode)
            self.board.scene().exitAddTraceMode() # Delete currently drawing scene._line & more if exiting

    # def on_create_footprint_action_triggered(self):
    #     print('on_create_footprint_action_triggered')
    #     create_footprint_dialog = MyCreateDialog('footprint', self)
        
    # def on_create_symbol_action_triggered(self):
    #     # self.create_symbol_
    #     print("on_create_symbol_action_triggered")
    #     create_symbol_dialog = MyCreateDialog('symbol', self) #
    #     create_symbol_dialog.show() 
        
    # def on_create_symbol_dialog_finished(self):
    #     QFileDialog.getOpenFileName( self, "Select Symbol", os.path.join(kicad_third_party_path, 'symbols'), filter = "All Files (*)" )

    def on_create_part_action_triggered(self):
        
        #What should I do to create a new part? 1) launch mpn window
        self.create_part_dialog = CreatePartDialog( self )
        self.create_part_dialog.created_part.connect(self.on_created_part) # NOTE could be moved to create_part_dialog.accept(), as long as create_part_dialog is parented on MyMainWindow; as long as create_part_dialog has access to MainWindow.database.insert_into_table... Q: could I miss the dependence  on parentage by sig/slot usage? 
        self.create_part_dialog.open()
        
    @Slot(dict)
    def on_created_part(self, part):
        print()
        # table_name= part.get('table_name', None)
        # print('TABLE_NAME:', table_name)
        # self.created_part.emit(part) ??? in constructor: self.created_part.connect(database.insert_into_table())
        database.insert_into_table(part) # Do a sqlINSERT statement-- database API handles the nittygritty. Spreadsheet owns the database
    #Prompt user to assign this part a symbol &/or footprint # Symbol files don't exist yet, depending. QFileDialog.getOpenFileName(parent=None, caption="SelectFileToOpen", dir=start_dir, filter="All Files (*)")
        self.assign_graphics(part) # self.assign_graphics() is a Slot but here we'll call it directly.(Slots are normal functions if you didn't know)
    # Now refresh the table 
        # self.spreadsheet.setTableName(table_name) This is done within ss.reload_part, which is called later on down this chain
        # self.spreadsheet.reload_combo_box_tables() This also called later down chain
        self.create_part_dialog.deleteLater()

    @Slot(dict)
    def assign_graphics(self, part): # Dialog to assign both symbol and/or footprint to part 
        Graphics_assign = MyGraphicsAssign(part, self)
        Graphics_assign.open()
        
    # @Slot(dict)
    # def assign_graphic(self, graphic, part):
    #     Graphic_assign = MyGraphicAssign(self.parent(), graphic, part)
    #     Graphic_assign.open()
   

    def create_gerbers(self):
        self.board.create_gerbers()
        
    def on_show_schematic_action_triggered(self):    
        self.centralWidget().setCurrentIndex(0) # Schematic is at index 0
        self.board_toolbar.hide()
        self._schematic_toolbar.show()
        # self.central_widget.setCurrentWidget(self.schematic)
        
    def on_show_board_action_triggered(self):
        self.centralWidget().setCurrentIndex(1) # Board is at index 1 
        self.board_toolbar.show()
        self._schematic_toolbar.hide()
        # self.central_widget.setCurrentWidget(self.board)
    
    def create_board_toolbar(self):
        self.board_toolbar = self.addToolBar("Board Toolbar")
        self.board_toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)
        self.board_toolbar.hide() # Hide at start
        
        # print()
        # print('CURRENT TRACE_WIDTH:', self.board.scene().trace_width)
        board_grid_spacing_options = [.1, .2 , .25, .5, 1, 2, 4, 5, 10]
        board_grid_spacing_combo = QComboBox()
        board_grid_spacing_combo.addItems(map(str , board_grid_spacing_options))
        board_grid_spacing_combo.setCurrentText(str(self.board.scene().grid_spacing_mm))
        board_grid_spacing_combo.currentTextChanged.connect(self.board.scene().set_grid_spacing_mm )
        board_grid_spacing_label = QLabel('Grid Spacing')
        board_grid_spacing_widget = QWidget()
        board_grid_spacing_widget.setLayout(QHBoxLayout())
        board_grid_spacing_widget.layout().addWidget(board_grid_spacing_label)
        board_grid_spacing_widget.layout().addWidget(board_grid_spacing_combo)
        
        trace_width_options = [.2,.3,.4,.5,.6,.7,.8,.9,1,1.2,1.4,1.5,1.6,1.8,2,3,4,5,6,7,8,9,10]
        
        self.trace_width_combo = QComboBox()
        self.trace_width_combo.addItems(map( str, trace_width_options))
        self.trace_width_combo.setCurrentText(str(self.board.scene().traceWidth()))
        self.trace_width_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        # print()
        # print(self.trace_width_combo.sizePolicy()) #<PySide6.QtWidgets.QSizePolicy(horizontalPolicy = QSizePolicy::Preferred, verticalPolicy = QSizePolicy::Fixed) at 0x000001791013DCC0>
        #Q: How do I set the sizes of the dropdown of the combobox? 
        # self.trace_width_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        # self.trace_width_combo.setBaseSize(QSize(100,100)) Seems to do nothing
        # self.trace_width_combo.setFixedSize(200,200) Makes a big square
        self.trace_width_combo.currentTextChanged.connect(self.board.scene().setTraceWidth)
        self.trace_width_label = QLabel('Trace Width:')
        self.trace_width_widget = QWidget()
        self.trace_width_widget.setLayout(QHBoxLayout())
        self.trace_width_widget.layout().addWidget(self.trace_width_label)
        self.trace_width_widget.layout().addWidget(self.trace_width_combo)
        
        self.board_toolbar.addAction(self.show_schematic_action)
        self.board_toolbar.addAction(self.create_gerbers_action)
        self.board_toolbar.addAction(self.add_trace_action)
        self.board_toolbar.addWidget(self.trace_width_widget)
        self.board_toolbar.addWidget(board_grid_spacing_widget)
        



    def create_schematic_toolbar(self):        # The signal actionTriggered() emits on toolbar button press 
        
        self._schematic_toolbar = self.addToolBar("Schematic Toolbar")  # toolbars are most often created with QMainWindow.addToolBar()
        
        # self._schematic_toolbar.addAction(self.dk_api_action) 
        self._schematic_toolbar.addAction(self.add_net_symbol_action)
        self._schematic_toolbar.addAction(self._addWireAction)
        self._schematic_toolbar.addAction(self.delete_wire_action)
        self._schematic_toolbar.addSeparator()
        self._schematic_toolbar.addAction(self.show_board_action)# May add toolbar buttons by adding actions 
        # self._schematic_toolbar.addAction(self.create_symbol_action)          # Moved to menuBar
        # self._schematic_toolbar.addAction(self.create_footprint_action)       
        # self._schematic_toolbar.addAction(self.create_part_action)
        # self._schematic_toolbar.addAction(self.show_schematic_action)         #Moved to Board Toolbar
        # self._schematic_toolbar.addAction(self.create_gerbers_action)

        # Set allowed toolbar areas: .allowedAreas()
        self._schematic_toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)
        # self._schematic_toolbar.addWidget(QSpinBox())  May add toolbar buttons by adding widgets, too. # Other suitable actions include QDoubleSpinBox, QComboBox(aka dropdown selection)
        # Fix in place: .setMovable()
        # Toolbar hides overflowing items behind extension button if toolbar shrunk too small, clicking extension button will reveal a popup with hidden items( If QToolBar is not child of QMainWindow, popup doesn't work in all cases-- see docs )

    
    def contextMenuEvent(self, event): # RMB on a window to generate a contextMenuEvent, which is automatically passed to the widget beneath RMB. Default implementation will generates a menu with checkable actions from the DockWidgets & ToolBar(NotMenuBar). Reimplement to run your own code. Here, I make my own context menu for the MyMainWindow
        # context_menu= QMenu(self) # 
        # test_action = context_menu.addAction(QAction('TEST_ACTION', self)) # Add action to this menu. Save reference to action in test_action. 
        # context_menu.exec(event.globalPos()) # Execute menu where the event occurred
        # Or, call the base implementation, to do the default behavior 
        super().contextMenuEvent(event)
        

        
    def on_delete_wire_action_triggered(self):
        print("DELETE WIRE ACTION TRIGGERED")
        # self.schematic.scene().setMode(MyScene.DeleteWireMode)
        self.centralWidget().schematic().scene().setMode(SchematicScene.DeleteWireMode)
            
    def library_id_selector(self, parent=None):
        print( f'LIBRARY_ID {library_id} NOT FOUND IN FILE {self.library}')
        lst_widget = QListWidget(parent)
        for row_index, library_id in enumerate(self.library_ids):
            item = QListWidgetItem()
            item.setText(library_id)
            lst_widget.insertItem(row_index, item)
        lst_widget.show()

    # Q: should this be a slot? 
    def onAddWireActionTriggered(self):
        print()
        print('ACTIVATED ON_WIRING_ACTION_TRIGGERED') 
        # We have to get the scene first-- don't use signals/slots bc we need to access our instance of QGraphicsScene -- which we cannot emit (without fetching, anyway), and 
        # central_widget = self.centralWidget()
        # print()
        # print(type(central_widget))
        
        # scene.setMouseTracking(True) # Don't do this here Enable mouseMoveEvent to fire while no mouse button pressed down mouseMoveEvent. default fire only on mouse move when mouse button pressed down. 

        # .findChildren(QGraphicsView) # QObject.findChildren() -> all children with given name, of given type T. Note that a view's scene is NOT A CHILD WIDGET of the view.
        print()
        print(self.schematic.scene())
        current_mode =self.schematic.scene().mode()
        if current_mode != SchematicScene.AddWireMode:
           self.schematic.scene().setMode(SchematicScene.AddWireMode)
        #    self.schematic.scene().set_cursor(Qt.CursorShape.CrossCursor)
        else: 
           self.schematic.scene().exitAddWireMode() # Note triggered is any time we press the btn, including when we've already pressed it & entered _addWireAction. In this case, we want to exit add_wire_mode
           self.schematic.scene().setMode(SchematicScene.normalMode)
        #    self.schematic.scene().set_cursor(Qt.CursorShape.ArrowCursor)
        print(self.schematic.scene()._mode)

# app = QApplication(sys.argv)
# part = {'ultralibrarian': 'https://ultralibrarian.com' , 'snapmagic': 'https://snapmagic.com'}
# dialog = MySymbolAssign(part=part)
# dialog.open() # Shows the dialog as a window modal dialog, returning immediately. Connect to the 'finished' signal to know when the dialog has been QDialog.Accepted or QDialog.rejected


# sys.exit(app.exec())