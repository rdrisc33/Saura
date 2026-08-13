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
from ViaItem import * 
from ZoneItem import * 
from LayersItem import LayersEllipseItem

class Ffline: 
    # Angles in radians. If angles in degrees, _degrees should be attached to variable name 
    def __init__(self, here, there, scene):  # here,there: draw this ffline from here, to there. scene: need a reference to the scene, for scene.tracewidth, and scene.ids, and scene.rtrees( but we don't want to add fflines to the scene, until we know them and their connecteds are valid, so ffline is not a QGraphicsItem)
        # print('ADDING FFLINE')
        self.is_valid = False 
        
        self._scene = scene
        
        self._lineA = QLineF() # QLineF is used to do all maths, before it is set as Traces line 
        self._lineB = QLineF()

        layers = [ self.scene().activeLayer() ]
        self._traceA = Trace.fromLine(self._lineA, self.scene().traceWidth(), layers )
        # self._traceA.setPen(QPen(Qt.green, self.scene().traceWidth(), c=Qt.PenCapStyle.RoundCap)) # c is for cap;pencap
        # self._traceA.setColor(Qt.green)
        # self._traceA.setTraceWidth(self.scene().traceWidth()) 
        # self.scene().addItem(self._traceA)
        
        self._traceB = Trace.fromLine( self._lineB, self.scene().traceWidth() , layers) 
        # self._traceB.setPen(QPen(Qt.darkGreen, self.scene().traceWidth(), c=Qt.PenCapStyle.RoundCap)) # c is for cap;pencap
        self.scene().addItem(self._traceB)
        
        self.traces = [self._traceA , self._traceB]
        self.scene().addItem(self._traceA)
        self.scene().addItem(self._traceB)
        
        # self.add_line_items_to_scene() # # Put standin QGraphicsLineItems onto the scene, until user double click indicates lines are acceptable, and traces can be added to scene.
        self.setPoints(here, there)
        

    def setPoints(self, here , there): # Draw ffline from here to there, if no collisions. 
        # print('SETTING FFLINE POINTS:')

        if here == there: 
            # print('HERE==THERE; RETURNING')
            return # Both self.linea/b will be null

        if isinstance(here, tuple):
            here = QPointF(*here)
            there = QPointF(*there)

        self.here = here
        self.there = there 

        self.dy = there.y() - here.y()
        self.dx = there.x() - here.x()
        # print('SELF.SCENE.STARTANGLE:', self.scene().startAngle *180/math.pi)
        self.startAngle = self.scene().startAngle # Relies on MyBoardScene().startAngle , as determined in MyBoardScene.addTraceModeMouseMoveEvent

        self._lineA.setP1(self.here)
        self._lineA.setP2(self.there) # This is gonna be overwritten; just need to ensure line is not null
        
        # self._traceA.setLine(self._lineA)
        # self._traceB.setLine(self._lineB)
        
        self._lineA.setAngle(self.startAngle * 180/math.pi ) # better be in degrees
        # Depending on whether trace a is at an angle, or hor/vert, the distance varies:
        if self._lineA.angle() % 90 == 0: # If the angle is hor/vert, 
            self._lineA.setLength( abs(abs(self.dx) - abs(self.dy)) )
        else:
            self._lineA.setLength( math.sqrt(2) * abs(min(abs(self.dx) , abs(self.dy))) ) # This is the fortyfivedegree distance component of our ffline. see ffline distance.

        self._lineB.setPoints( self._lineA.p2() , self.there )  # better be QPoints
        
        self._traceA.setLine(self._lineA)
        self._traceB.setLine(self._lineB)
        
        if self.isColliding():
            self.altAttempt() # Try an alternate attempt: change the startAngle. If this one don't work, ffline.is_valid = False
            if self.isColliding():
                print("This ffline is colliding")
                return False  # The ffline we drew from here to there collided with something

        # print('UPDATING RTREE')
        self._traceA.updateRtree() # If no collisions, update rtree
        self._traceB.updateRtree()
        # self._traceA.setBufferedBounds() 
        # self._traceB.setBufferedBounds()
        # print('Updating line item a and b: ')
 
        # self._traceA.setLine(self.line_a) # If we reached here, set new points, update the scene if no collisions
        # self._traceB.setLine(self.line_b)
        # print('all done')
        # print('SET FFLINE POINTS')
        return True 
            
        
    # def add_line_items_to_scene(self): # Note that this is done once, when the ffline is instantiated, if self.is_valid. They can't be added a bajillion times 
    #     self._traceA = QGraphicsLineItem() # A line item allows us to preview Traces on the scene: lineItems are not given ids/not added to the rtree by scene.addItem, so use LineItems, until we know what we want our Traces to be 
    #     self._traceB = QGraphicsLineItem() 
    #     self._traceA.setPen(QPen(Qt.black, self.scene().traceWidth())) 
    #     self._traceB.setPen(QPen(Qt.black, self.scene().traceWidth()))
        
    #     self.scene().addItem(self._traceA)
    #     self.scene().addItem(self._traceB)
        

        
    def fflineDistance(self):
        return ( math.sqrt(2) * min(self.dx , self.dy) ) + abs(self.dy-self.dx) 
        
    def isColliding(self): # Returns 2-tuple (is_colliding , (test_traceA , test_trace_b) ). If is_colliding, test traces will both be None, else they will be set to their non-colliding traces 
        # test_traceA = None 
        # test_trace_b = None  
                      
        self._lineA.setAngle(self.startAngle * 180/math.pi ) # better be in degrees
        # Depending on whether trace a is at an angle, or hor/vert, the distance varies:
        if self._lineA.angle() % 90 == 0: # If the angle is hor/vert, 
            self._lineA.setLength( abs(abs(self.dx) - abs(self.dy)) )
        else:
            self._lineA.setLength( math.sqrt(2) * abs(min(abs(self.dx) , abs(self.dy))) ) # This is the fortyfivedegree distance component of our ffline. see ffline distance.

        # # print('CreatingTrace')
        # test_traceA = Trace(self._lineA, self.scene().traceWidth() , self.scene().activeLayer()) # Note this trace is created BUT NOT PUT ON THE SCENE we just need it for its .bufferedBounds() so we can query the rtree
        # test_traceA = self.create_trace_item(self.line_a) # Note this trace is created BUT NOT PUT ON THE SCENE we just need it for its .bufferedBounds() so we can query the rtree
        # print('Checking test_traceA collides:')
        if self.traceCollides(self._traceA):
        # if self._traceA.netCollision():
        # if self.trace_collides(test_traceA): # If traceA collides, we are done, return (True ( _ , None) ) 
            return True
        
        # self._lineB.setPoints( self._lineA.p2() , self.there )  # better be QPoints
        # test_trace_b = self.create_trace_item(self.line_b)
        # test_trace_b = Trace(self._lineB , self.scene().traceWidth() , self.scene().activeLayer())
        # self.trace_b = self.create_trace_item(self.line_b)
        # if self.line_collides(self.line_b):
        # print('Checking test_trace_b collides ')
        # if self.trace_collides(test_trace_b):
        # if self.trace_collides(self._traceB):
        # if self._traceB.netCollision(): 
        if self.traceCollides(self._traceB): 
            return True
        
        return False # If we made it here, test traces did not collide
        
    # def create_trace_item(self, line): # Creates a Trace from a QLineF. 
    #     # print('Creating Trace_item: ')
    #     # trace = Trace(self.scene().activeLayer(), line) # Not parented on anything, Traces will just go on the scene as top-level items 
    #     trace = Trace(line, self.scene().traceWidth(), self.scene().activeLayer()) # Not parented on anything, Traces will just go on the scene as top-level items 
    #     # print('TRACE:', trace)
    #     # print('SELF.SCENE.traceWidth():', self.scene().traceWidth())
    #     trace._bufferDistance = self.scene().traceWidth()

    #     # trace.setBufferedBounds(self.scene().traceWidth()) # Item needs a scene to know its bufferedBounds 
    #     trace.setBufferedBounds() # Needed to do hits on rtree
    #     return trace

    def connecteds(self, item):
        pass
            
    def traceCollides(self, trace):
        # print('SELF.SCENE().ITEMS:', len(self.scene().items()), self.scene().items())
        hitItems = trace.queryRtrees()
        for hitItem in hitItems:
            # print('HITITEM:', hitItem)
            if hitItem == self:
                continue
            if hitItem.net() == trace.net(): # Traces on the same net are not collisions; these are joinable
                continue
            # elif hitItem.collidesWithItem(trace.sceneBufferedBounds()): # Can this be used if trace is not on the scene? Also: cWI needs item but gave bounds. Try cWP:
            # elif hitItem.collidesWithPath(trace.bufferedSceneShape()):
            elif hitItem.collidesWithItem(trace): # Think needs to be bufferedShape
                if hitItem.net() == None and trace.net() != None:
                    hitItem.setNet(trace.net())
                elif hitItem.net() != None and trace.net() == None:
                    trace.setNet(hitItem.net)
                else: 
                    return True # Item collides w/ another item
            
        return False # Item does not collide
        
    def netCollision(self):
        pass
        

    # MyBoardScene.trace_collides(self, trace):

    def altAttempt(self): # Change the start angle and 
        pi = math.pi
        
        if self.theta < self.startAngle : 
            self.startAngle = BoardScene.getStartAngle(self.theta - pi/4 ) 
        elif self.theta > self.startAngle: 
            self.startAngle = BoardScene.getStartAngle(self.theta + pi/4 )
        # Note that if self.theta == self.startAngle, the fflines only viable startAngle is startAngle_degreess current value, & startAngle will NOT change, will get tested again, and again be found to collide-- no compute hit bc so rarely happens 
        
    def finalize(self): # creates & adds to scene  self.trace_(a,b), based off line_item_(a,b)'s line, them removes line_item_n Should happen once, in BoardScene.addTraceModeDoubleClickEvent,  when our traces are finalized;not colliding; ready to be id'd and go into rtree.
        
        if self._traceA.line().isNull(): # null aka line of 0 length
            print('TRACEA IS NULL')
            self.scene().removeItem(self._traceA) # standin QGLi no longer needed

        if self._traceB.line().isNull():
            self.scene().removeItem(self._traceB)
        
    def scene(self): # B/c this class takes a reference to a scene, 
        return self._scene
    
    def remove_line_items_from_scene(self):
        self.scene().removeItem(self._traceA)
        self.scene().removeItem(self._traceB)
    
class BoardScene(QGraphicsScene):
    normalMode, addTraceMode, addViaMode, deleteTraceMode = range(4)

    dpi = qApp.screens()[0].physicalDotsPerInch()
    dpmm = dpi / 25.4
    # * 1 bc IDK what the boardScene grid step should be, and * 1 makes for a 1mm grid step.
    grid_spacing_pixels=  dpi * Utils.gridPt1mm # the spacing at which to snap to. 
    grid_spacing_mm = 1 # as in 1mm
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
        self.seekerRect = QRectF(-seeker_radius,-seeker_radius, seeker_radius*2 , seeker_radius*2)
        # self.seeker   = QGraphicsEllipseItem(self.seekerRect)
        self.seeker = LayersEllipseItem(None, self.seekerRect) # Scene has a item, to detect important points/items/to highlight/snap to points of interest on mouse over # Note that do not add it to scene until needed.
        self._mode = self.normalMode 
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
        
        # layer_items_button = QPushButton('Print scene.copperItems() & .layerItems()')
        # layer_items_button.clicked.connect(self.copperItems)
        # layer_items_button.clicked.connect(self.layerItems)
        # self.addWidget(layer_items_button)
        
        # print('BOARDSCENE:')
        # print('.TRACEWIDTH():', self.traceWidth())
        # print('.ACTIVELAYER():', self.activeLayer())
        # print()
        # print('Drawing Board Dots')
        # print(self.tick_spacing)
        # print(self.sceneRect())
        

    # def mirror(self, footprint): # Flips footprints from front-to-back and vv. Updates all affected items too 
    #     if footprint.layer() == 'F.Cu': 
    #         footprint.setLayer('B.Cu')
    #     elif footprint.layer() == 'B.Cu':
    #         footprint.setLayer('F.Cu')
            
    #     # middle_layer = 
    #     # self.layers
    #     for item in footprint.childItems(): 
    #         item.mirror()
        

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
        # if self.mode() == MyBoardScene.addTraceMode:
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
                item.showLayer(layer)
                
    def hideLayer(self, layer):
        print('BOARDSCENE.HIDELAYER()')
        for item in self.items(): 
            item.hideLayer(layer)
   
        
    def normalModeMouseMoveEvent(self, event): # Detect underlying items with .seeker. Move seeker accordingly; seeker ends up snapped to point of interest POI or grid.
        # print('normalModeMouseMoveEvent')

        self.seeker.setPos(event.scenePos()) # Move the seeker to mouse event at first. seeker will move from here, snapping either to point of interest, or to the grid. Note this step is important when grid_step is huge
        
        items = self.items(self.seeker.mapToScene(self.seeker.shape())) # pass SCENE COORDS of seeker.shape(), a path, to items. Will return all visible items that intersect with path
        self.seeker.setPos(self.snapToGrid(event.scenePos())) # after checking if any items beneath seeker @scenePos, we may now snap to grid, tho we may still decide to snap to point of interest 
        
        # for item in items:  # IDK what this is needed for
        #     # if isinstance(item, CopperItem):
        #     if isinstance(item, CopperItemContainer):
        #         if isinstance(item, FootprintItem):
        #             continue
        #         print()
        #         print("ITEM:", item) # ITEM: <FootprintItem.PadItem(0x28d6a794d40, parent=0x28d6a793640, pos=0,0, z=1) at 0x0000028D68F5E7C0>
        #         print("ITEM.TERMINALS:", item.terminals())
        #         for terminal in item.terminals():
        #             terminalXY = terminal[0:2] # Just the x,y part of the full (x,y, layer) terminal
        #             layer      = terminal[2] 
        #             if layer != self.activeLayer():
        #                 return 
        #             if self.seeker.contains(self.seeker.mapFromScene(terminalXY)): 
        #                 print('SEEKER CONTAINS TERMINAL')
        #                 self.seeker.setPos(terminalXY)
        #                 return
                        
                            
                # if isinstance(item, Trace):
                #     # print()
                #     # print('Trace BENEATH MOVE')
                #     # if self.seeker.contains(item.line().p1()): NO BAD (but why exactly)
                #     if self.seeker.contains(self.seeker.mapFromScene(item.line().p1())): 
                #         print('SEEKER CONTAINS P1')
                #         self.seeker.setPos(item.line().p1())
                #     elif self.seeker.contains(self.seeker.mapFromScene(item.line().p2())):
                #         self.seeker.setPos(item.line().p2())
                #         # item.grabMouse() If we are in moveEvent, item would already have become mouseGrabbber in PressEvent
                #         print('SEEKER CONTAINS P2')

                            
    def normalModeMousePressEvent(self, event):
        print('normalModeMousePressEvent')

      
    def addItem(self, item): # QGraphicsScene.addItem reimplementation: Add (Trace,Via,Zone,Footprint) items to: the scene, scene.ids, scene.idx. If Footprint, +1 to reference_values. 
        super().addItem(item) # Add Item normally, which adds all childItems. We still have to add copperItems to their rtree.
        
        if not isinstance(item, LayersItem):
            # print(f'NONBOARDITEM {item}  ADDED TO BOARDSCENE')
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
            self.set_mode(self.normalMode)
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
        # print('MyBoardScene.addTraceModeMousePressEvent')
        if self.ffline is not None: # If there is an existing ffline, we are done with it, add it to scene
            self.ffline.finalize() # Remove traces from scene if any are of 0 length

        self.startPosition = self.snapToGrid(self.seeker.scenePos()) # ffline begins wherever seeker(not mouse) is 
        self.ffline = Ffline(QPointF(0,0), QPointF(0,0) , self) # Note 00 gets overwritten w/every mouseMove # This line is causing kernel crash
        
 # A line drawn from position of click to current mouse position. 
        self._line =  LayersLineItem(['F.Cu'], QLineF(self.seeker.scenePos(), self.seeker.scenePos()))
        self._line.setPen(QPen(Qt.GlobalColor.black , 0, s = Qt.PenStyle.DashLine))
        self.addItem(self._line)      

        self.octant = None 
        self.quadrant = None 
        self.startAngle = None # Traces can be hor, vert, or at 45 degrees. Mouse movement hints at initial direction trace should travel in
        self.startAngleThreshold = self.grid_spacing_mm * self.dpi/25.4 # Conversion of mm to pixels # intial_direction may be set while within this circular threshold
    
    #             item.setPen(QPen(item.pen().color() , traceWidth)) # Preserve pen_color ( Due to qt quirks;cosmetic pen cannot change to non-zero width), we have to replace entire qpen)
    def queryRtrees(self, bounds, layer):
        """Query the rtree at 'layer' for 'bounds'."""
        hitIds = self.rtrees[layer].intersection(bounds)
        hitItems = [self.ids[id] for id in hitIds]
        return hitItems 
    
    
    def addTraceModeMouseMoveEvent(self, event):
        # print('ADDTRACEMODEMOUSEMOVEEVENT')
# CAN WE MOVE SEEKER HERE? Query rtree

        scenePos = event.scenePos()

        self.seeker.setPos(self.snapToGrid(scenePos)) # snap seeker to grid to begin with. We'll move seeker elsewhere if we need to.

        # seekerBounds =  ( self.seeker.boundingRect().left(), self.seeker.boundingRect().top() , self.seeker.boundingRect().right() , self.seeker.boundingRect().bottom() ) NO BAD this gives bounds based on .bR(), which is in local coords; does not reflect any set scene Position
        r = self.seeker.mapToScene(self.seeker.boundingRect()).boundingRect()
        seekerBounds = ( r.left(), r.top(), r.right() , r.bottom())
        # print('SEEKER BOUNDS:', seekerBounds)
        # rtrees = getRtrees()
        hitItems = self.queryRtrees(seekerBounds , self.activeLayer())
        # print('HITITEMS:', hitItems)
        
        for hitItem in hitItems: 
            # print('HITITEM.NET():', hitItem.net())
            if hitItem.net() == self.activeNet() or hitItem.net() == None : 
                nearestSceneSnap = hitItem.nearestSceneSnap(self.seeker.scenePos())
                self.seeker.setPos(nearestSceneSnap)
                break
            
        # print('SELF.STARTPOSITION:', self.startPosition)
        if self.startPosition is not None : # If we previously pressed mouse, we are drawing a trace. Use the mouse position to sense startAngle. Note is not None used because QPoint(0,0) evaluates False while QPoint(1,1) evaluates True; QPoint if testing shouldn't be used, so we compare against None.
            dx = scenePos.x() - self.startPosition.x() # 
            dy = scenePos.y() - self.startPosition.y() 
            theta = BoardScene.normalize_angle( math.atan2( -dy, dx ) ) # Note y is flipped because in QT, positiveY is downwards while atan2 positiveY is upwards. Also, atan2 returns from -pi to 0 to pi, so normalize that angle 
            
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
            # self.ffline.setPoints(self.startPosition , scenePos) # NO BAD do not update to there: scenePos, rather use there: seeker.pos()
            
            # currentPosition = (self.ffline.here , self.ffline.there) # save cP in case revert needed 
            self.ffline.setPoints(self.startPosition, self.seeker.pos()) # This will update the ffline from here to there, as long as no collisions are found, inwhich case the old ffline will persist
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

    def addTraceModeMouseReleaseEvent(self, event):
        print('AddTraceModeMouseReleaseEvent')
        self.removeItem(self._line)
        if self.ffline.here == self.ffline.there: 
            self.removeItem(self.ffline) 
          
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

    def mousePressEvent(self, event): # ToDo: Only allow lines to move hor/vertically from their start point
        # print()
        # print('MyBoardScene.MOUSEPRESSEVENT')
        if self.mode() == BoardScene.addTraceMode: 
            self.addTraceModeMousePressEvent(event)
        if self._mode == BoardScene.normalMode:
            self.normalModeMousePressEvent(event)
        super().mousePressEvent(event) # Call base implementation to: fwd event to mousegrabber if there's a mousegrabber, OR fwd event to topmost item, if no mousegrabber, OR reset selections, then remove focus from any focused items, then ignore the event, if no item below event position. TLDR; Call base implementation to forward event to any items beneath the press.  
               
    def mouseMoveEvent(self, event):
        # print('BOARDSCENE.MOUSEMOVEEVENT')
        # self.seeker.setPos(self.snap_to_grid(event.scenePos())) # This could probably be moved here...?
            
        if self._line : 
            self._line.setLine(QLineF(self._line.line().p1() , event.scenePos())) # _line is drawn from SEEKER position of last click to current MOUSE position
            
        # set the scene's net (TODO AND activeLayer), based off the item currently beneath seeker pos. This is later used in pressEvent, 

        itemsBeneathSeeker = self.items(self.seeker.scenePos())
        netsBeneath = set()
        for item in itemsBeneathSeeker: 
            if isinstance(item, CopperItemContainer):
                if not isinstance(item, FootprintItem): # FPs make sense to have a net
                    netsBeneath.add(item.net())
        if len(netsBeneath) > 1 : 
            self.setActiveNet('error')
            print('ERROR: THERE ARE OVERLAPPING BOARD ITEMS WITH THE SAME NET. THIS NOT SUPPOSED TO HAPPEN')
        elif len(netsBeneath) == 1:
            self.setActiveNet(netsBeneath.pop()) # sets can't be indexed so pop
        elif len(netsBeneath) == 0: 
            self.setActiveNet(None)
        # print()
        # print('BOARDSCENE.ACTIVENET():', self.activeNet())
            

        if self.mode() == BoardScene.normalMode:
            self.normalModeMouseMoveEvent(event)
        elif self.mode() == BoardScene.addTraceMode:
            self.addTraceModeMouseMoveEvent(event)
        super().mouseMoveEvent(event)
        
        # print()
        # print('MOUSEGRABBERITEM:', self.mouseGrabberItem())
        if self.mouseGrabberItem(): 
            
            if isinstance(self.mouseGrabberItem(), FootprintItem):
                self.footprintMoved.emit(self.mouseGrabberItem()) # MW.board.scene().footprintMoved.connect(updateRatsnest)
            

    def mouseDoubleClickEvent(self, event):
        # print('MyBoardScene MOUSEDOUBLECLICKEVENT')
        if self._mode == BoardScene.addTraceMode: # Exit addTraceMode 
           self.addTraceModeMouseDoubleClickEvent(event)
        elif self._mode == BoardScene.deleteTraceMode:
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
    

    def exitAddTraceMode(self):
        print()
        print('MYBOARDSCENE.exitAddTraceMode')
        
#         if self.old_layer: 
#             setlayercomboSignal.emit(self.old_layer)
            

# # in Board: 
#     @Slot(str)
#     def setLayerComboSlot(self, text)
#         self.layer_combo.setCurrentText(text)
#     self.board.scene.setLayerComboSignal.connect(self.setLayerComboSlot)

#########################################

        self.views()[0].setMouseTracking(False) # disable mouseMoveEvent from firing while no mouse button pressed down, which is default setting.    
        self.setMode(BoardScene.normalMode) # restore default mode. But for real app, should stay in wiring_mode
        self.removeItem(self._line) 
        # self._traceA = None 
        # self._traceB = None 
        self.ffline = None 
        self.startPosition = None 
        self.goal_position = None
        # self.seeker.setVisible(False)
        # print("self.views()[0].parentWidget().", self.views()[0].parentWidget()) 
        # print("self.views()[0].parentWidget().parentWidget()",self.views()[0].parentWidget().parentWidget())
        # print("self.views()[0].parentWidget().parentWidget().parentWidget", self.views()[0].parentWidget().parentWidget().parentWidget()) 
        # main_window = self.views()[0].parentWidget().parentWidget().parentWidget()# Get the main_window.( we need to uncheck add_traceAction). The view's parent is the schematic, schematic's parent is a stackedWidget, stackedWidget's parent is the QMainWindow. # This is bad practice bc so brittle but what way is better? HEY this is a good example of when we should start using SIGNALS/SLOTS rather than digging through parent objects 
        # print('IS THIS THE MAIN WINDOW:', main_window)
        # main_window.add_traceAction.setChecked(False) # uncheck add_traceAction
        
    def setMode(self, mode):
        self._mode = mode
# Set seeker color depending on mode TODO should actually change seeker shape 
        if self._mode == self.normalMode: 
            self.seeker.setPen(QPen(Qt.green , 0))
            # self.setCursor(Qt.CursorShape.ArrowCursor)
        if self._mode == self.addTraceMode:
            self.seeker.setPen(QPen(Qt.red , 0))

        print()
        print(f"SET MODE TO {mode}")

    def mode(self):
        return self._mode
                
    def snapToGrid(self, point: QPointF | QPoint):
        # print('SnapToBoardGrid')
        grid_spacing_pixels = self.grid_spacing_mm * self.dpi/25.4 # Conversion of Xmm to pixels
        pt = QPointF( round(point.x()/grid_spacing_pixels)*grid_spacing_pixels , round(point.y()/grid_spacing_pixels)*grid_spacing_pixels ) 
        # print('SNAP POINT:', pt)
        return pt
        
    def set_grid_spacing_mm(self, grid_spacing_mm):
        print('GRID_SPACING_MM:', type(grid_spacing_mm), grid_spacing_mm)
        if isinstance(grid_spacing_mm , str):
            self.grid_spacing_mm = float(grid_spacing_mm)
        elif  isinstance(grid_spacing_mm, (float, int)):
            self.grid_spacing_mm = grid_spacing_mm
        else:
            raise TypeError(f'grid_spacing_mm is type: {type(grid_spacing_mm)} but expected str | int | float')
        # self.update_tick_marks() 
        
            
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

