from utils import * 
from FootprintItem import FootprintItem
import UtilsAfterApp
from ComponentSymbol import ComponentSymbol
from FootprintItem import * 
from PySide6.QtWidgets import QGraphicsSceneDragDropEvent
from FootprintItem import *
import heapq 
import numpy as np
from MyAStar import *
from Trace import * 
from ZoneItem import * 
from LayersItem import LayersEllipseItem, LayersLineItem
from Via import Via
from Ffline import Ffline
    
class BoardScene(QGraphicsScene):
    # normalMode, addTraceMode, addViaMode, deleteTraceMode = range(4)

    dpi = qApp.screens()[0].physicalDotsPerInch()
    dpmm = dpi / 25.4
    # * 1 bc IDK what the boardScene grid step should be, and * 1 makes for a 1mm grid step.
    grid_spacing_pixels=  dpi * Utils.gridPt1mm # the spacing at which to snap to. 
    gridSpacingMm = 1 # as in 1mm
    # print('MYBOARDSCENE.grid_spacing:', grid_spacing)
    tick_spacing = dpi / 25.4 # The spacing at which to draw tick marks 
    # filegrid_spacing = 1.27 # kicad symbols are designed on.05inche grid,  with metric mm measurements. .05inches = 1.27mm 
    # dpi = app.instance().screens()[0].physicalDotsPerInch()  # app.instance() -> a global pointer to the application instance. Equivalent to 'qApp'. Must go AFTER app instance instantiation. 
    # scenegrid_spacing = ( ( dpi/25.4 ) * 4 ) # equals approx 17.8 on my laptop; a 17.8 pixel wide grid_spacing corresponds to 4mm    
    # kicad_symbol_scale_factor = 1/filegrid_spacing * scenegrid_spacing # scale_factor = 1/1.27 * 50 
    # grid_spacing = ( ( dpi/25.4 ) * 1 ) # The default grid for the board should be ? mm 
    # dropped_part = Signal(dict)
    # added_footprint = Signal(dict, int) # (part, value) value as in reference_value as in "C3" "R1" "L2" etc. Note app crashed when Signal(MyFootprintItem)-- signals/slots Demand correct typing
    droppedPart = Signal(dict, QGraphicsSceneDragDropEvent, int) # part, event, source_widget
    deletePart = Signal(str , int) # reference, value . As in reference_value which was deleted. 
    
    tracingLaid = Signal(str) # (net) net of the newly laid tracingTracing as in new traces were added to board

    footprintMoved = Signal(QGraphicsItem) # Emits moved item
    
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs) 
        self._layers = Utils.layers
        self.rtrees = defaultdict(rectangletree.index.Index) # {'F.Cu': rtree}
        # self.footprints = defaultdict(defaultdict) Not used for anything so commented  defaultdict of default dict  { 'C':{1: item , 2: item , 5: item} , 'R': {1:item , 2:item}}}Note Entries/Deletions to this dict managed by MainWindow, bc, parts, with reference_value, go on both schematic AND board, but cant  reach both schematic and board from here, so we pass up to MW.
        self.topmost_layer = 'F.Cu' # The layer which is drawn on top of all other layers. Selected via layerVisibilityControlWidget. Most of the time, will be same value as activeLayer. Default F.Cu
        self._activeLayer = 'F.Cu' # The currently selected layer; the layer the user is currently working on. F_Cu, Inr.3, B_Silk, etc # The layer to which Traces will be added. Selected via layerVisibilityControlWidget. Most of the time, will be same value as topmost_layer. Default F.Cu
        self._activeNet = None  # The currently selected net. gnd, Vcc, 3v3, signal_gnd, etc

        self.showing_layers = set(Utils.layers) # A set containing currently showing layers. Default show all layers 
        self.hidden_layers = []
        
        # self.design_items = set() # a set to hold all 'design items'. DIs are traces, footprints, pads, vias, zones. DI's must have .is_design_item set to True. DIs are QGraphicsItem subclasses. DIs are what make up the PCB design. Compare against grid dots, or the seeker, which are QGraphicsItems, on the scene , yet are not to be in the pcb design. These non design items must have .is_design_item set to the default value None
        
        self.ids = dict() # a dict to hold id:Item key value pairs. Note items also know their own ids. 
        # self.reference_values       = defaultdict(int) # Moved to MW reference_values as in R0 C10 L1 LED2 U0; the reference_values of components on the board. A dictionary, of (reference):(num of components on board with that reference) Ex a board with 10 'C' and 2 'R' and 0 'U' would be {'C': 10 , 'R':2 , 'U': 0} . Defaultdict is a dictionary, with the bonus that if you try to access a key which DNE, instead of throwing KeyError, it will create an entry, of specified type(here 'int', so 0 ), for you. defaultdict (Note  plain dict.get() -> None if key dne) is part of the builtin python module 'collections' (from collections import defaultdict)
        self.count = 1 # counter from which items dropped on scene derive their id. not 0indexed starts at 1
        # self.setSceneRect(-50,-50, 450,450) # I think sceneRect is infinite default. Units are pixels
        # rect = QGraphicsRectItem(QRectF(-10,-10,20,20))
        # rect.setPen(QPen(Qt.yellow, 1))
        # self.addItem(rect)
        # print()
        # print(self.sceneRect())# a empty rect 0000
        
        # print()
        # print("DPI:", self.dpi)
        self.seekerRect = QRectF(-seekerRadius,-seekerRadius, seekerRadius*2 , seekerRadius*2)
        # self.seeker   = QGraphicsEllipseItem(self.seekerRect)
        # self.seeker = LayersEllipseItem(None, self.seekerRect) # Scene has a item, to detect important points/items/to highlight/snap to points of interest on mouse over # Note that do not add it to scene until needed.
        self.seeker = QGraphicsEllipseItem(self.seekerRect) # Scene has a item, to detect important points/items/to highlight/snap to points of interest on mouse over # Note that do not add it to scene until needed.
        self._mode = Utils.BoardSceneMode.NormalMode 
        self.ffline                     = None                      # ffline representing traces currently being drawn.
        self._line                      = None                      # Line from mouse position to position of last click. Usually not displayed but for debugging
        self.trace                      = None                      # Representing the trace user is currently adding to scene. May have many segments
        self.startPosition             = None                      # Representing the start of the trace currently being drawn; the scenePos of a mouse click while in addTraceMode.
        self.goal_position              = None                      # Representing the end of the trace currently being drawn, the scenePos of the seeker
        self.startAngle                = None                      # Representing the direction user wishes hor vert or 45 degree trace to go, as user indicates w/mouse. Is float value for radians indicating angle
        self._traceWidth                = 0.2                       # The currently selected traceWidth(). Default .2mm. When user draws new traces, they are drawn with this traceWidth().
        self._graph                     = np.zeros( ( 10, 10) ) 
        self._copperItems               = defaultdict(list)
        self._layerItems                = defaultdict(list) 
        
        self.seeker.setPen(QPen(Qt.GlobalColor.green, 0)) 
        self.addItem(self.seeker)                     # Add seeker to scene.
        
        origin_item  = LayersEllipseItem(['F.Cu'], -5,-5,10,10)
        origin_item.setPen(QPen(Qt.magenta, 1))
        origin_item.setBrush(Qt.NoBrush) 
        self.addItem(origin_item)
        self.setMode(Utils.BoardSceneMode.NormalMode)

    def collidingNets(self,layers, path=None , point = None): # Returns list of nets colliding with path, or empty list if no nets colliding with path 
        
        collidingNets = set() 
        hitIds = [] 
        hitItems = [] 
        
        if path: 
            r = path.boundingRect()
            bounds = (r.left() , r.top() , r.right() , r.bottom())

        elif point: 
            bounds = (point.x() , point.y() , point.x() , point.y()) 
            
            
        for layer in layers: 
            hitIds = self.rtrees[layer].intersection(bounds)
            hitItems.extend( self.ids[hitId] for hitId in hitIds )
            
        for hitItem in hitItems: 
            if hitItem.collidesWithPath(path):
                print('HIT ITEM COLLIDES WITH PATH. NET:', hitItem.net() )
                collidingNets.add(hitItem.net())
        return collidingNets
            
    def layers(self):
        return self._layers
        
    def traceWidth(self):
        return self._traceWidth
    def setTraceWidth(self,traceWidth):
        self._traceWidth = float(traceWidth)
        
    def addTraceModeMouseDoubleClickEvent(self, event):
        # self.tracing_laid.emit() # When new traces are added, need to update MW.ratsnest & MW.nets@ BoardItems, which is done @ MW level, so we emit a signal.
        self.tracingLaid.emit(self.activeNet()) 
        self.exitAddTraceMode()
        # print('addTraceModeMouseDoubleClickEvent')
        # if self.mode() == MyUtils.BoardSceneMode.AddTraceMode:
        #     self.exitAddTraceMode()
        # elif self.mode() == MyBoardScene.normalMode:
        #     pass


    def activeNet(self): # The net of the currently selected item. Is used to setActiveNet of None-net items and prevent items with unlike nets from connecting
        return self._activeNet 
    
    def setActiveNet(self, activeNet):
        self._activeNet = activeNet
        
    def activeLayer(self): 
        return self._activeLayer
    def setActiveLayer(self, activeLayer):
        self._activeLayer = activeLayer
        
        
    def layerItems(self):
        # print()
        # print('SCENE.LAYERITEMS:')
        # for layer, layerItems in self._layerItems.items():
            # print('LAYER:', layer)
            # print('\t', layerItems)
        return self._layerItems
    
    def addLayerItem(self, layerItem):
        self.layerItems()[layerItem.layer()].append(layerItem)
        
    def removeLayerItem(self, layerItem):
        self.layerItems()[layerItem.layer()].remove(layerItem)
        
    def copperItems(self):
        # print()
        # print('BOARDSCENE.COPPERITEMS():', self._copperItems)
        return self._copperItems
    
    def addCopperItem(self, copperItem):
        self.copperItems()[copperItem.layer()].append(copperItem)
        
    def removeCopperItem(self, copperItem):
        self.copperItems()[copperItem.layer()].remove(copperItem)
        
    def setTopmostLayer(self, layer): # First, return the previous topmostLayer z value to zero, then, set new topmostLayer zValue to 1, bringing that layer above all other items.
        for item in self.copperItems()[self.topmost_layer]: 
            item.setZValue(0)
        for item in self.layerItems()[self.topmost_layer]:
            item.setZValue(0)
            
        self.topmost_layer = layer 
        for item in self.copperItems()[self.topmost_layer]: 
            item.setZValue(1)
        for item in self.layerItems()[self.topmost_layer]:
            item.setZValue(1)
            
    def onlyShowCopperLayers(self):
        for layer in Utils.layers: 
            if layer in Utils.CopperLayers:
                self.showLayer(layer)
            else: 
                self.hideLayer(layer)
        
    def hideLayers(self, layers):
        for layer in layers: 
            self.hideLayer(layer)
            
    def showLayers(self, layers):
        for layer in layers: 
            self.showLayer(layer)
    
    def showLayer(self, layer):
            print('BOARDSCENE.SHOWLAYER()')
            for item in self.items(): 
                if not isinstance(item, LayersItem):
                    continue 
                item.showLayer(layer)
                
    def hideLayer(self, layer):
        print('BOARDSCENE.HIDELAYER()')
        for item in self.items(): 
            if not isinstance(item, LayersItem):
                continue 
            item.hideLayer(layer)
   
        
    def normalModeMouseMoveEvent(self, event): # Detect underlying items with .seeker. Move seeker accordingly; seeker ends up snapped to point of interest POI or grid.
        # print('normalModeMouseMoveEvent')

        # self.seeker.setPos(event.scenePos()) # Move the seeker to mouse event at first. seeker will move from here, snapping either to point of interest, or to the grid. Note this step is important when grid_step is huge
        # items = self.items(self.seeker.mapToScene(self.seeker.shape())) # pass SCENE COORDS of seeker.shape(), a path, to items. Will return all visible items that intersect with path

        # set the scene's net (TODO AND activeLayer), based off the item currently beneath seeker pos. This is later used in pressEvent, 
        self.setActiveNet()
        
        self.seeker.setPos(self.snapToGrid(event.scenePos())) # after checking if any items beneath seeker @scenePos, we may now snap to grid, tho we may still decide to snap to point of interest 
        super().mouseMoveEvent(event) 

    def normalModeMousePressEvent(self, event):
        print('normalModeMousePressEvent')
        super().mousePressEvent(event) # Call base implementation to forward event to any items beneath the press. Call base implementation to: fwd event to mousegrabber if there's a mousegrabber, OR fwd event to topmost item, if no mousegrabber, OR reset selections, then remove focus from any focused items, then ignore the event, if no item below event position. 
      
    def addItem(self, item): # QGraphicsScene.addItem reimplementation: Add (Trace,Via,Zone,Footprint) items to: the scene, scene.ids, scene.idx. If Footprint, +1 to reference_values. 
        super().addItem(item) # Add Item normally, which adds all childItems. We still have to add copperItems to their rtree.
        print('ADDING ITEM OF TYPE:',type(item))
        
        if not isinstance(item, LayersItem):
            print(f'NONLAYERSITEM {item}  ADDED TO BOARDSCENE')
            return         
        
        if isinstance( item, FootprintItem): # Footprint pads go in rtree, so call addItem again for each pad 
            # self.footprints[item.referenceDesignator()][item.referenceNumber()] = item
            for pad in item.pads(): 
                self.addItem(pad)
            
        
        if isinstance(item, CopperItemContainer): # Footprint, TraceViaZonePad, are all copperItemContainers: they track copperItems with their .copperItems() method. CopperItems include Trace, ViaItem, ZoneItem, PadItem. CopperItems support connectivity, and go in the rtree. CopperItems are also .childItems(). There are also layerItems. Think silkscreen doodles, user notes, and ratsnest lines. Layer items do not support connectivity. layerItems are tracked in .layerItems().
            
            # print()
            # print('ITEM.COPPERITEMS():', item.copperItems())
            # self.copperItems().update(item.copperItems()) NO BAD if we .update an existing key, it'll overwrite that existing key
            # for layer, items in item.copperItems().items(): # add item.copperItems() to scene.copperItems() CuItems dont have copperItems

            item.setId(self.count)        # Count may differ between brd and sch
            self.count  += 1 
            self.ids[item.id()] = item
            item.setSceneTerminals() # Note that because Traces have TWO terminals, we will use .setSceneTerminals, plural, which will .setTerminal singular for applicable copperItemContainers
            item.setSceneBounds()
            
            item.setBufferDistance(self.traceWidth()) # Calls setBuffer & setSceneBuffer & setBufferedBounds & setSceneBufferedBounds
            item.insertIntoRtree()



            # for copperItems in item.copperItems().values(): # The copperItems are CuItems with rtree stuff 
        #         # print('COPPERITEMS:', item.copperItems().values())
        #         for copperItem in copperItems: 
                    
        #             copperItem.setId(self.count)        # Count may differ between brd and sch
        #             self.count  += 1 
        #             # print('ASSIGNING ID:', copperItem.id())
        #             self.ids[copperItem.id()] = copperItem

        #             # copperItem.setBounds()
        #             copperItem.setSceneTerminal()
                    
        #             copperItem.setSceneTerminals()
        #             copperItem.setSceneBounds()
        #             copperItem.setBufferDistance(self.traceWidth()) # Calls setBuffer & setSceneBuffer & setBufferedBounds & setSceneBufferedBounds
        #             copperItem.insertIntoRtree()
                    
        #     for layerItems in item.layerItems().values(): # The layerItems are courtyards, silkscreen(for footprints), & pad names&numbers. 
        #         for layerItem in layerItems: 
        #             # print()
        #             # print('LAYERITEM:', layerItem)
        #             self.addLayerItem(layerItem)
                    
        # elif isinstance(item, LayerItem): # If user straight adds a Line to the boardScene, unpackaged by a parentItem
        #     # print()
        #     # print('LAYER ITEM ADDED')
        #     self.addLayerItem(item)
            
    def removeItem(self, item): # QGraphicsScene.removeItem reimplementation : Remove item from rtree self.idx as well
            
        # print('BOARDSCENE.REMOVEITEM', item)
        super().removeItem(item) # invoke super to remove from scene 
        
        if isinstance(item, CopperItemContainer):
            self.ids.pop(item.id()) # Remove from ids 
            for layer in item.layers(): 
                self.rtrees[layer].delete(item.id(), item.sceneBufferedBounds()) # Remove from idx. Index().delete(id, bounds) : Deletes an item from the index by id and coordinates. Note Index id uniqueness is up to the user to implement
                

            # for layer, items in item.copperItems().items():  # remove from copperItems() 
            #     for i in items: 
            #         self.copperItems()[layer].remove(i)
        
        if isinstance(item, FootprintItem):
            for pad in item.pads():
                self.removeItem(pad)
                
            # self.footprints[item.referenceDesignator()].pop(item.referenceNumber())
            # for layer, items in item.copperItems().items():  # remove from copperItems() 
            #     for i in items: 
                    
                    # self.copperItems()[layer].remove(i) # Scene dont need to know all copperItems...
                    # self.removeItem(i) # recusrively call removeItem to wipe i from rtrees
            

# https://rtree.readthedocs.io/en/stable/tutorial.html
# [n.object for n in idx.intersection((left, bottom, right, top), objects=True)]
# [None, None, 42]
        
# But what if the item is edited -- what if zone border changes, what if a Trace is shortened? A: delete old item from scene, add new item to scene.
        
    def chainHits(self, bounds): # bounds: 4-tuple (xmin , ymin , xmax, ymax) aka left top right bottom. Most often,this function used with buffered; expanded;inflated,  bounds, buffered by the scene's currently set traceWidth(). This is for rtree hit detection to determine which items(Footprint, Zone, Trace, Via) are in the way of a trace, such that we may construct a graph of those items, to route traces around them. See traceChainHits to search for traces only. 
            
        print()
        print('CHAINHITS:')
        print('BRDSCENE.IDS:', self.ids)
        print('BRDSCENE.IDX', self.rtree)
        # if self.idx.isempty
        visited = set() # A set, holds ids of rectangles 
        queue = [bounds] # A list, holds bounds 4-tuples to explore
        
        while queue:
            print()
            
            bounds = queue.pop()
            # hit_ids = self.idx.intersection(bounds) # EVIL generator object returned by rtree.index.Index().intersection is garbage collected silently. avoid this by casting to list 
            hit_ids = list(self.rtree.intersection(bounds))  
            print('HIT_IDS:', list(hit_ids))
            for hit_id in hit_ids:
                print('hit_id in hit_ids')
                if hit_id in visited:
                    continue 
                print('adding visited')
                visited.add(hit_id)
                # queue.append(self.ids[hit_id].Rect())  This is not good enough-- .bR takes not into account any .setPos, so we can't use .bR alone 
                item = self.ids[hit_id]
                queue.append(item.sceneBufferedBounds())
                # polygon = item.mapToScene(item.boundingRect()) # Sadly, .mapToScene(rect) does return a QPolygonF. Happily, QPolygonF does implement .boundingRect 
                # queue.append(polygon.boundingRect())
            print('QUEUE:', queue)
            print('VISITED:', visited)
                
        print('DONE: VISITED: ', visited)
        for item in self.items():
            if isinstance(item, Trace):
                print('TRACE.bR():', item.mapToScene(item.boundingRect()).boundingRect())
        return visited
    
    def chainHitsTrace(self, bounds): # Return rtree chain hits, of Traces, that are near enough to given trace that might belong in the trace_vein. Note still need to check if hits exactly connect; need to run result of this function thru further processing. Note that we use self.scene().idx, which is full of buffered rects, which are not needed here, but we can repurpose the rtree here instead of creating a new one. Wait this is senseless bc it saves no time, the traceVein knows exactly where to look don't need rect hitboxes to narrow it down...
        visited = set()
        queue = [bounds]
        
        while queue: 
            hit_ids = self.rtree.intersection(queue.pop())
            for hit_id in hit_ids: 
                if hit_id in visited: 
                    continue 
                visited.add(hit_id) 
                item = self.ids[hit_id]
                if isinstance(item, Trace): # Ignore any non-trace items ( so Zone Footprint Via)
                    # visited.add(hit_id)
                    queue.append( item.sceneBufferedBounds() )

        return visited 

    # def traceVein(self, point): # Return trace vein, if any,for a given point in scene coordinates.
        
    #     visited = set() # items we visited 
    #     # visited_terminals # Think implementing this will save compute. optimization...
    #     nets = defaultdict(list) # Track accrued nets, by priority,to know if any net errors { 0:[ 'C1-1' , 'U3-1 ] , 1:['gnd', 'vcc'] } # We know there's a net error bc 'gnd' is connected to 'vcc', this would be a short
    #     queue = []
    #     vein = []
    #     count = 0
        
    #     rect=  QRectF(point.x() , point.y(), point.x(), point.y()).adjusted(-.5, -.5, .5,.5) 
    #     items= self.items(rect, Qt.ItemSelectionMode.IntersectsItemShape) # Null rect? No intersection, so make rect teeny tiny instead. 
        
    #     for item in items: 
    #         if isinstance(item, QGraphicsProxyWidget):
    #             pass
    #         elif point in item.terminals: 
    #             queue.append(item)
    #             vein.append(item)
                
                
    #     while queue: 
    #         count +=1
    #         item = queue.pop()
    #         visited.add(item)
    #         for terminalXY in item.terminals(): 
    #             bounds = (terminalXY.x() , terminalXY.y() , terminalXY.x() , terminalXY.y()) # Construct a Shapely.bounds (xmin ymin xmax ymax) object for querying rtree 
    #             for other_item in [ self.ids( id ) for id in self.idx.intersection(bounds) ] :
    #                 if other_item not in visited and other_item not in queue: 
    #                     if terminalXY in other_item.terminals(): 
    #                         # queue.append(item)
    #                         vein.append(other_item)  # We now know other_item is in this vein
    #                         queue.append(other_item) # We want to investigate other_item, 
    #                         accrue_nets()
            
    #     print('LEN(VEIN):', len(vein))
    #     # print('NETS:', nets)
    #     print('COUNT:', count)
        
    #     def accrue_nets():
    #         priority = item.terminals()[terminalXY]['priority']
    #         nets[priority].extend(item.terminals[terminalXY]['net'])
        
    def keyPressEvent(self, event):
        print()
        print('MySCHEMATICSCENE.KEYPRESSEVENT')
        if event.key() == Qt.Key.Key_Escape: 
            self.set_mode(Utils.BoardSceneMode.NormalMode)
            self.exitAddTraceMode()
            print('ESCAPE KEY PRESSED. SET MODE TO NORMAL')
            
        if event.key() == Qt.Key.Key_Delete:
            print('DELETE KEY PRESSED')
            for item in self.selectedItems(): 
                
                # # if item.copperItems(): # Moved to removeItems
                # for layer, items in item.copperItems().items(): # Remove all copperItems()
                #     for item in items: 
                #         print('ITEM:', item)
                #         self.copperItems()[layer].remove(item)

#     self.copperItems()[layer].remove(item)
# ValueError: list.remove(x): x not in list
 
                if item.reference(): # Then we are a footprint item, we should ALSO delete the SYMBOL w/ corresponding reference_value. Because we have to reach into schematic & delete that symbol, or board & delete footprint, mmw handles deletion of refVal items on both scene and sch, but trace zone via items can be removed wo/ MMW. Be sure to remove from: the scene, scene.ids, subtract one from reference_values, and remove from the scene.idx, & remove from scene.copperItems() 
                    print(f'ITEM: {item} IS A FOOTPRINT, deleting from both sch and brd')
                    self.deletePart.emit(item.referenceDesignator(), item.referenceNumber()) # Let mmw handle footprint deletion: deleted_item.emit(reference, value).connect(MMW.delete_part) 
                else: 
                    self.removeItem(item)
                    item = None # What this do? 
                                        
        return super().keyPressEvent(event) # This event handler, for event keyEvent, can be reimplemented in a subclass to receive keypress events. The default implementation forwards the event to current focus item.( FOCUS != SELECTION ) 

    def set_mode(self, mode):
        self._mode = mode
        print()
        print(f"SET MODE TO {mode}")

    def addTraceModeMousePressEvent(self, event):
        print()
        print('ADDTRACEMODEMOUSEPRESSEVENT')
        if self.ffline is not None: # If there is an existing ffline, we are done with it, add it to scene
            self.ffline.finalize() # Remove traces from scene if any are of 0 length
        if self._line : 
            self.removeItem(self._line)
            
        # self.startPosition = self.snapToGrid(self.seeker.scenePos()) # ffline begins wherever seeker(not mouse) is 
        self.startPosition = self.seeker.scenePos() # ffline begins wherever seeker(not mouse) is 
        print()
        print('SELF.STARTPOSIITON:', self.startPosition) 
        # self.ffline = Ffline(QPointF(0,0), QPointF(0,0) , self) 
        self.ffline = Ffline(self.seeker.scenePos(), self.seeker.scenePos() , self)
        
 # A line drawn from position of click to current mouse position. 
        # self._line =  LayersLineItem(['F.Cu'], QLineF(self.seeker.scenePos(), self.seeker.scenePos()))
        self._line =  QGraphicsLineItem( QLineF(self.seeker.scenePos(), self.seeker.scenePos()))
        self._line.setPen(QPen(Qt.GlobalColor.black , 0, s = Qt.PenStyle.DashLine))
        self.addItem(self._line)      

        self.octant = None 
        self.quadrant = None 
        self.startAngle = None # Traces can be hor, vert, or at 45 degrees. Mouse movement hints at initial direction trace should travel in
        self.startAngleThreshold = self.gridSpacingMm * self.dpi/25.4 # Conversion of mm to pixels # intial_direction may be set while within this circular threshold
    
    #             item.setPen(QPen(item.pen().color() , traceWidth)) # Preserve pen_color ( Due to qt quirks;cosmetic pen cannot change to non-zero width), we have to replace entire qpen)
    def queryRtrees(self, bounds, layer):
        """Query the rtree at 'layer' for 'bounds'."""
        hitIds = self.rtrees[layer].intersection(bounds)
        hitItems = [self.ids[id] for id in hitIds]
        return hitItems 
    
    
    def addTraceModeMouseMoveEvent(self, event):
        print() 
        print('ADDTRACEMODEMOUSEMOVEEVENT')
        if self._line : 
            self._line.setLine(QLineF(self._line.line().p1() , event.scenePos())) # _line is drawn from SEEKER position of last click to current MOUSE position
        # scenePos = event.scenePos() # EVIL EVIL BAD BAD HOURS OF BUGS BECAUSE THIS RETURNS A QPOINTF, OF AN INTEGERRRRRRR THIS IS WHERE IM GOING WRONG surely. probably.
        print('ATMMMEVENT.SCENEPOS:', event.scenePos())
            
        # self.seeker.setPos(self.snapToGrid(scenePos)) 
        self.seeker.setPos(self.snapToGrid(event.scenePos())) # snap seeker to grid to begin with. We'll move seeker elsewhere if we need to.
        print('SEEKER.SCENEPOS', self.seeker.scenePos())
        # # seekerBounds =  ( self.seeker.boundingRect().left(), self.seeker.boundingRect().top() , self.seeker.boundingRect().right() , self.seeker.boundingRect().bottom() ) NO BAD this gives bounds based on .bR(), which is in local coords; does not reflect any set scene Position
        # r = self.seeker.mapToScene(self.seeker.boundingRect()).boundingRect()
        # seekerBounds = ( r.left(), r.top(), r.right() , r.bottom())
        # # print('SEEKER BOUNDS:', seekerBounds)
        # # rtrees = getRtrees()
        # hitItems = self.queryRtrees(seekerBounds , self.activeLayer())
        # # print('HITITEMS:', hitItems)
        
        # for hitItem in hitItems:  
        #     for terminal in hitItem.terminalsWithin(sceneBounds= seekerBounds):
        #         # print('HITITEM.NET():', hitItem.net())
        #             if hitItem.net() == self.activeNet() or hitItem.net() == None : 
        #                 nearestSceneSnap = hitItem.nearestSceneSnap(self.seeker.scenePos())
        #                 self.seeker.setPos(nearestSceneSnap)
        #                 break
            
        print('SELF.STARTPOSITION:', self.startPosition)
        if self.startPosition is not None : # If we previously pressed mouse, we are drawing a trace. Use the mouse position to sense startAngle. Note is not None used because QPoint(0,0) evaluates False while QPoint(1,1) evaluates True; QPoint if testing shouldn't be used, so we compare against None.
            # dx = scenePos.x() - self.startPosition.x() # NO BAD usage of event.scenePos() is an integer... want to use 
            # dy = scenePos.y() - self.startPosition.y() 
            dx = self.seeker.scenePos().x() - self.startPosition.x() # NO BAD usage of event.scenePos() is an integer... want to use 
            dy = self.seeker.scenePos().y() - self.startPosition.y() 
            # theta = BoardScene.normalize_angle( math.atan2( -dy, dx ) ) # Note y is flipped because in QT, positiveY is downwards while atan2 positiveY is upwards. Also, atan2 returns from -pi to 0 to pi, so normalize that angle 
            theta = math.atan2( -dy, dx ) # Note y is flipped because in QT, positiveY is downwards while atan2 positiveY is upwards. Also, atan2 returns from -pi to 0 to pi, so normalize that angle 
            
            # print('THETA:', theta)
            startAngle= self.getStartAngle(theta) # 
            # print('startAngle:', startAngle)
            octant = self.getOctant(theta)
            # print('OCTANT:', octant)
            
            if math.sqrt(dx**2 + dy**2) < self.startAngleThreshold: # if we are within threshold, assign startAngle
                # print('WE ARE WITHIN THRESHOLD')
                self.startAngle = startAngle 
            
            elif octant != self.octant: # If we are in a new octant, assign startAngle
                # print('WE ARE IN A NEW OCTANT')
                self.octant = octant
                self.startAngle = startAngle

            # print('SELF.startAngle:', self.startAngle)
            # print('SELF.OCTANT:', self.octant)
            
            # ffline = Ffline((20,20) , (150, 200), scene) 
            
            # currentPosition = (self.ffline.here , self.ffline.there) # save cP in case revert needed 
            # self.ffline.setPoints(self.startPosition , scenePos) # NO BAD do not update to there: scenePos, rather use there: seeker.pos()
            print('SELF.SEEKER.SCENEPOS():', self.seeker.scenePos())
            self.ffline.setPoints(self.startPosition, self.seeker.scenePos()) # This will update the ffline from here to there, as long as no collisions are found, inwhich case the old ffline will persist
            # self.ffline.setPoints(self.startPosition, event.scenePos()) # Testing
            # self.ffline.setPoints(self.startPosition, self.seeker.pos()) # NO BAD use sceenPos(even tho should be same bc seeker has no parent item)
            # self.ffline.setConnectedNets()
            # if len(self.ffline.nonNoneNets ) > 1 : 
            #     self.ffline.
            # print()
            # print('SET FFLINE POINTS')

    # Acceptable goals for a_star includes blank space, including blank space within the coutyard of a footprint, and the center of MyPadItems, of the same net.
        # pad = self.is_occluded(self.seeker.scenePos(), [item for item in self.items() if isinstance(item, MyFootprintItem)]) # 
        # if pad: 
        #     if self.net() == pad.net():
        #         print('Pad is of same net as trace')

        #         self.seeker.setPos(pad.center()) # snap seeker to pad center if pad is of same net

        # if self._line: # If user is currently drawing _line, we are drawing a trace, use the aStar algorithm to pathfind trace
        #     self.a_star()

    def mouseReleaseEvent(self, event): 
        if self.mode() == Utils.BoardSceneMode.NormalMode: 
            super().mouseReleaseEvent(event)
        elif self.mode() == Utils.BoardSceneMode.AddTraceMode: 
            # if self.ffline.here == self.ffline.there: 
            #     self.removeItem(self.ffline) 
            pass
        elif self.mode() == Utils.BoardSceneMode.AddViaMode: 
            pass 
          
    def a_star(self): # A* pathfinding: 
        pass

    # @Slot(dict, str)
    # def add_part(self, part:dict, value = None):
    #     item = MyFootprintItem(part)
    #     item.setPos(100,100) # For now just get it away from the topLeft corner
    #     self.addItem(item)
    #     print()
    #     print('ADDED SYMBOL TO SCHEMATIC')
         
    @Slot(dict) # (part) The name of the sql table which was changed
    def reload_part(self, part):
        print()
        print('MYBOARDSCENE.RELOADPART')
        for item in self.items():
            if isinstance(item, FootprintItem):
                
                new_item = FootprintItem(part, item.value(), item.id(), item.reference()) # Create new part symbol. Officially, this is overkill since we only NEED a new item if we set a new symbol, but brute force here makes for simple code  
                
                new_item.setPos(item.scenePos())
                self.removeItem(item) # or is it item.setParent(None) 
                self.addItem(new_item)

    def mousePressEvent(self, event): 
        # print()
        # print('MyBoardScene.MOUSEPRESSEVENT')
        if self._mode == Utils.BoardSceneMode.NormalMode:
            self.normalModeMousePressEvent(event) # this involves adjusting TraceItems & more
        elif self.mode() == Utils.BoardSceneMode.AddTraceMode: 
            self.addTraceModeMousePressEvent(event)
        elif self.mode() == Utils.BoardSceneMode.AddViaMode: # In Scene.addViaModemousePressEvent, have the via take on nets below if appropriate 
            if ( self.via.net() == None ) and (self.via.resolvedNet != 'unresolved'): # None nets take on other nets upon mouseRelease
                self.via.setNet(self.via.resolvedNet)
            self.setMode(Utils.BoardSceneMode.NormalMode)

               
    def mouseMoveEvent(self, event):
        # print('BOARDSCENE.MOUSEMOVEEVENT')

        if self.mode() == Utils.BoardSceneMode.NormalMode:
           self.normalModeMouseMoveEvent(event)
        elif self.mode() == Utils.BoardSceneMode.AddTraceMode:
            self.addTraceModeMouseMoveEvent(event)
        elif self.mode() == Utils.BoardSceneMode.AddViaMode:
            self.addViaModeMouseMoveEvent(event)
        # super().mouseMoveEvent(event)
        
        # print()
        # print('MOUSEGRABBERITEM:', self.mouseGrabberItem())
        if self.mouseGrabberItem(): 
            
            if isinstance(self.mouseGrabberItem(), FootprintItem):
                self.footprintMoved.emit(self.mouseGrabberItem()) # MW.board.scene().footprintMoved.connect(updateRatsnest)
                
    def addViaModeMouseMoveEvent(self, event): 
        print('MOUSEMOVEEVENT')
        self.via.tentativeMove( Utils.snapToGrid(event.scenePos(), 20) )# MOve here, as long as no conflicts
       
    def setActiveNet(self):
        itemsBeneathSeeker = self.items(self.seeker.scenePos())
        netsBeneath = set()
        for item in itemsBeneathSeeker: 
            if isinstance(item, CopperItemContainer):
                if not isinstance(item, FootprintItem): # FPs make sense to have a net
                    netsBeneath.add(item.net())
                    
        if len(netsBeneath) == 0: 
            self._activeNet = None 
            
        elif len(netsBeneath) > 1 : 
            print('NETSBENEATH:', netsBeneath)
            self_activeNet = 'unresolved'
            
        elif len(netsBeneath) == 1:
            self._activeNet = netsBeneath.pop() # sets can't be indexed so pop
            
        # print('BOARDSCENE.ACTIVENET():', self.activeNet())
            


    def mouseDoubleClickEvent(self, event):
        # print('MyBoardScene MOUSEDOUBLECLICKEVENT')
        if self._mode == Utils.BoardSceneMode.AddTraceMode: # Exit addTraceMode 
           self.addTraceModeMouseDoubleClickEvent(event)
        elif self._mode == Utils.BoardSceneMode.DeleteMode:
            pass # 
        # super().mouseDoubleClickEvent(event) # The base implementation calls mousepressEvent. We don't need that here 
            
    def dragMoveEvent(self, event):
        print('MyBoardScene.DRAGMOVEEVENT')
        
    def dropEvent(self, event):   
        print() 
        print('MyBoardScene.DROPEVENT')
        part = json.loads(event.mimeData().text()) # part will be in mimeData().text() as a json string representing a python dictionary
        if part:
            source_widget = MyWidgets.Board.value
            self.droppedPart.emit(part, event, source_widget) # We will .addItem from MyMainWindow, because we ALSO need to add corresponding part to sch. 
        # self.add_footprint(part,  event.scenePos()

    def exitAddTraceMode(self):
        print()
        print('MYBOARDSCENE.exitAddTraceMode')
        self.views()[0].setMouseTracking(False) # disable mouseMoveEvent from firing while no mouse button pressed down, which is default setting.    
        self.setMode(Utils.BoardSceneMode.NormalMode) # restore default mode. But for real app, should stay in wiring_mode
        self.removeItem(self._line) 
        # self._traceA = None 
        # self._traceB = None 
        self.ffline = None 
        self.startPosition = None 
        # main_window = self.views()[0].parentWidget().parentWidget().parentWidget()# Get the main_window.( we need to uncheck add_traceAction). The view's parent is the schematic, schematic's parent is a stackedWidget, stackedWidget's parent is the QMainWindow. # This is bad practice bc so brittle but what way is better? HEY this is a good example of when we should start using SIGNALS/SLOTS rather than digging through parent objects (?)

        
    def setMode(self, mode):
        self._mode = mode
# Set seeker color depending on mode TODO should actually change seeker shape 
        if self._mode == Utils.BoardSceneMode.NormalMode: 
            self.seeker.setPen(QPen(Qt.green , 0))
            # self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self._mode == Utils.BoardSceneMode.AddTraceMode:
            self.seeker.setPen(QPen(Qt.red , 0))
        elif mode == Utils.BoardSceneMode.AddViaMode: 
            print('ENTERED ADD VIA MODE')
            self.via = Via(60,30 , 10, ['F.Cu'])
            self.addItem(self.via) 
            self.via.setPos(-1e9,-1e9)
            self.views()[0].setMouseTracking(True) # mouseMoveEvent fires while no mouse button pressed down 
        print()
        print(f"SET MODE TO {mode}")

    def mode(self):
        return self._mode
                
    def snapToGrid(self, point: QPointF ):
        gridSpacing = self.gridSpacingMm * self.dpi/25.4 # Conversion of Xmm to pixels
        return Utils.snapToGrid(point, gridSpacing)
        
    def setGridSpacingMm(self, gridSpacingMm):
        print('GRIDSPACINGMM:', type(gridSpacingMm), gridSpacingMm)
        if isinstance(gridSpacingMm , str): # Will be str coming from SpinBox widget
            self.gridSpacingMm = float(gridSpacingMm)
        elif  isinstance(gridSpacingMm, (float, int)):
            self.gridSpacingMm = gridSpacingMm
        else:
            raise TypeError(f'grid_spacing_mm is type: {type(gridSpacingMm)} but expected str | int | float')
        # self.update_tick_marks() 
        
            
        
    @staticmethod 
    def get_quadrant(theta):
        pi = math.pi 
        if 0*pi/4 <= theta <= 2*pi/4:
            return 1 # as in quadrant 1
        if 2*pi/4 <  theta <= 4*pi/4:
            return 2 # as in quadrant 2 
        if 4*pi/4 <  theta <= 6*pi/4:
            return 3
        if 6*pi/4 <  theta <= 8*pi/4:
            return 4
 
                
    @staticmethod
    def getOctant(theta): # return 1-8 representing the octant we are in ( like a quadrant but there's eight sections )
        pi = math.pi
        if 0*pi/4 <= theta <= 1*pi/4:
            return 1 # as in octant 1
        if 1*pi/4 <  theta <= 2*pi/4:
            return 2 # as in octant 2 
        if 2*pi/4 <  theta <= 3*pi/4:
            return 3
        if 3*pi/4 <  theta <= 4*pi/4:
            return 4
        if 4*pi/4 <  theta <= 5*pi/4:
            return 5
        if 5*pi/4 <  theta <= 6*pi/4:
            return 6
        if 6*pi/4 <  theta <= 7*pi/4:
            return 7
        if 7*pi/4 <  theta <= 8*pi/4:
            return 8
            
    @staticmethod
    def getStartAngle(theta): 
        pi = math.pi
        theta = BoardScene.normalize_angle(theta) # atan2 returns -pi<theta<=pi , so, you'll want to normalize the angle first 
        if 0 <= theta <= pi/8 or 15*pi/8 < theta <= 2*pi: #  To determine which direction the user is trying to draw the line at initially, look in octants rotated 22.5 degrees ( pi/ 16) ( draw a picture to better understand)
            return 0 # as in 0 degrees 
        elif pi/8 < theta <= 3*pi/8: # 
            return 2*pi/8 # as in 45 degrees 
        elif 3*pi/8 < theta <= 5*pi/8:
            return 4*pi/8
        elif 5*pi/8 < theta <= 7*pi/8:
            return 6*pi/8
        elif 7*pi/8 < theta <= 9*pi/8:
            return 8*pi/8
        elif 9*pi/8 < theta <= 11*pi/8:
            return 10*pi/8
        elif 11*pi/8 < theta <= 13*pi/8:
            return 12*pi/8
        elif 13*pi/8 < theta <= 15*pi/8:
            return 14*pi/8
        

    @staticmethod
    def normalize_angle(theta): # Return an angle between 0 and 2 pi
        pi = math.pi 
        while theta > 2*pi : # as long as theta is out of bounds
            theta -= 2*pi
        while theta < 0: 
            theta += 2*pi
        # print('NORMALIZED THETA:', theta)
        return theta 
    
    # def update_tick_marks(self, tick_spacing = None ): # default:  dpi * grid_1mm
    #     if tick_spacing: 
    #         self.tick_spacing = tick_spacing 
    #     print('SELF.TICK_SPACING:', self.tick_spacing)
    #     if self.tick_marks: 
    #         for tick_mark in self.tick_marks: 
    #             self.removeItem(tick_mark) # This took 30s 

    #         print('CLEARED OLD TICK_MARKS')
            
    #     for x in range(0 , int( self.sceneRect().width() / self.tick_spacing) ): 
    #         for y in range(0 , int(self.sceneRect().height() / self.tick_spacing)):
    #             tick_mark = QGraphicsEllipseItem(QRectF(-.1, -.1, .2 , .2)) 
    #             tick_mark.setBrush(Qt.gray)
    #             tick_mark.setPen(Qt.NoPen)
    #             tick_mark.setPos(x*self.tick_spacing , y*self.tick_spacing)
    #             self.addItem(tick_mark)
    #             self.tick_marks.append(tick_mark)
    #     print('LEN(SELF.TICK_MARKS:', len(self.tick_marks))# 359809

    
        

        
    # def traceWidth()(self):
    #     return self._traceWidth()
    # traceWidth()()(self, traceWidth()):
    #     return self._traceWidth()
    
        

##TESTING###
# from utils import * 
# from MyView import MyView
# app = QApplication(sys.argv)
# # print("Qapp:", qApp)

# board_scene = MyBoardScene()
# view = MyView()
# view.setScene(board_scene)
# view.show()

# sys.exit(app.exec())

        



#.POSITION ()
# -> item position, in parent coordinates. This function is the same as item.mapToParent(0, 0).
#.SCENEPOSITION()
# -> item position, in scene coordinates. Same as item.mapToScene(0,0)
#.GLOBALPOSITION()
#->item position, in global(screen), coordinates 

