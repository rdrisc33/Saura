from utils import * 
from TerminalItem import TerminalItem
from WireItem import WireItem
from MyNode import MyNode # Node as in little circle indicating wire connects to other wire 
# from UtilsAfterApp import UtilsAfterApp 
from ComponentSymbol import ComponentSymbol
from NetSymbol import NetSymbol
from Symbol import Symbol
from PySide6.QtGui import QDropEvent
from Database import database 
from PySide6.QtWidgets import QGraphicsSceneDragDropEvent
from SchematicItem import SchematicItem

class SchematicScene(QGraphicsScene):
    NormalMode, AddWireMode, DeleteWireMode, AddSymbolMode = range(4)

    grid_step = qApp.screens()[0].physicalDotsPerInch() * grid_4mm # SchematicScene grid_step is 4mm aka 17.86046511627907 pixels
    # print()
    # print('GRID_STEP: ', grid_step)
    droppedPart = Signal(dict , QGraphicsSceneDragDropEvent, int) # part, event , source_widget . Where part is a dict representing a part, event is QGraphicsScene.dropEvent(event), source_widget is a Widget enum representing schematic or board.  event is needed to set QGrapicsItem.setPos(event.scenePos) Note when I add a part on the schematic's scene, I ALSO want to add a part on the board's scene -- the latter can't be done at schScene's level, so we have to do it at MW level. Plus, I have to assign the same value (for reference_value) to the symbol AND footprint -- may as well generate that once not twice. Plus, I have to support part deletion, and thus value reassignment, all of which may as well be done at a level where schScene AND brdScene are accessible( atm level is MyMainWindow)
    deletePart = Signal(str , int) # reference, value . As in reference_value to be deleted 
    wiringLaid = Signal(QPointF) # Wiring as in new wires were just laid. pos: any terminal position in the wiring, choose first laid wire.p1() as pos. Emitted when: 1) User adds new wire 2) User edits existing wire 
    
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs) 
                
        self.symbols = defaultdict(defaultdict) # Track symbols. Symbols include ComponentSymbol , Label, and NetSymbol 
        
        # self._netSymbols = defaultdict(dict)
        # self._labels = defaultdict(dict) 


        self.seeker_rect = QRectF(-seeker_radius,-seeker_radius, seeker_radius*2 , seeker_radius*2)
        self._seeker  = QGraphicsEllipseItem(self.seeker_rect) # Scene has a item, to detect important points/items/to highlight/snap to points of interest on mouse over # Note that do not add it to scene until needed.
        # self.addItem(QGraphicsRectItem(self.sceneRect())) # draw the sceneRect
        # self.addItem(QGraphicsEllipseItem(Geometry.small_rect))# draw the origin 
        self._mode = self.NormalMode 
        # self._currentlyAddingSymbolItem     = None # the symbolItem currently being added by user, if any
        self.moused_over_wire               = None # Representing any wire currently being moused over 
        self.terminal                       = None # Representing any terminal currently being moused over 
        self._line                          = None # Line from mouse position to position of last click. Not snapped to grid. A QGraphicsLineItem. Only use is to establish self.initial_direction.
        self._wire                          = None # Representing the wire user is currently adding to scene. Snapped to grid. A QGraphicsLineItem
        self._horWire                       = None # Representing X componenet of self.moused_over_wire. A QGraphicsWireItem
        self._vertWire                      = None # Representing Y componenet of self.moused_over_wire. A GraphicsWireItem
        self._initial_direction             = 'x' # Representing the direction user wishes hor or vert line to initially go, as user indicates w/mouse, left,right, down, or up. Can take values 'x' or 'y'
        self._wiringPos                      = None # Any point on wiring, so that may backfollow wiring
        self._pinId                         = 0    # Id pinItems such that they are always sortable
        # database.changed.connect(self.reload_part ) # In MyBoardScene, too. Moved to stackedWidget
        self.setSceneRect(0,0,1000,1000) # I think sceneRect is infinite default? 2000 might seem too big, but remember that these units are pixels
        scene_rect = self.sceneRect()
        self.addItem(QGraphicsRectItem(scene_rect))
        
        self._seeker.setPen(QPen(Qt.GlobalColor.green, 0)) 
        # self._seeker.setVisible(False)                 # Make invisible
        self.addItem(self._seeker)                     # Add seeker to scene, hidden to start
        
        origin_item  = QGraphicsEllipseItem(-5,-5,10,10)
        origin_item.setPen(QPen(Qt.GlobalColor.magenta, 1)) 
        calibation_square = QGraphicsRectItem(0,0,10,10)
        self.addItem(calibation_square)
        self.addItem(origin_item)
        
        # "qApp" is not defined: The qApp object exists only after you create a QApplication instance as in: app = QApplication(sys.argv) # qApp is a global pointer to the application instance. qApp keeps info on things like properties, palette, fonts, and settings. # qApp detects the OS it is running in and try to 'blend in' by matching palettes, etc. QApplication or QGuiApplication creates qApp. # Fetch DPI, aka the number of pixels per inch, of your screen with : qApp.screens()[0].physicalDotsPerInch()
        
        #How do i draw a grid every 17.84456 pixels? Like so: Use not the scene.sceneRect, but the view.viewport().rect(), so we lay dots over the whole viewport (But this needs to happen when we expand the viewport, how do i do that)
        for x in range(0, int(self.sceneRect().width()/self.grid_step) ): 
            for y in range(0, int(self.sceneRect().height()/self.grid_step) ):
                dot = QGraphicsEllipseItem(QRectF(-1,-1,2,2))
                dot.setBrush(Qt.gray)
                dot.setPen(Qt.NoPen)
                # dot.setFlags(QGraphicsItem.GraphicsItemFlag.)
                dot.setPos(x*self.grid_step,y*(self.grid_step))
                self.addItem(dot)
        # self.addItem(QGraphicsLineItem(QLineF(30,30,30,30))) # Test to see what a line of no length looks like : A: a dot when zoomed out, a line when zoomed in
     
    def seeker(self):
        return self._seeker
    def setSeeker(self, seeker):
        self._seeker = seeker
        
    def addItem(self, item):
        print('SCHEMATICSCENE.ADDITEM')
        super().addItem(item)

        if isinstance(item , Symbol) :
            self.symbols[item.referenceDesignator()][item.referenceNumber()] = item
            
        if isinstance(item, (WireItem, Symbol)):
            item.setSceneTerminals()

               
        
    def wireVein(self, pos): # Return the vein of wire, a dict including wire and other interconnected wires, pins, NetSymbols, and labels, and more.
        pass  # Implemented in MainWindow
                
                        
    @Slot(dict) # (table_name) The name of the sql table which was changed
    def reload_part(self, part): # part was just updated in db. I need to propogate fresh part to all symbols/footprints
        print()
        print('SCHEMATICSCENE.RELOAD_PART')
        for item in self.items():
            if isinstance(item, ComponentSymbol):

                item.setPart(part) # 
                # new_item = MySymbolObject(part) # Create new part symbol. Officially, this is overkill since we only NEED a new item if we set a new symbol, but brute force here makes for simple code  
                # new_item.setPos(item.scenePos())
                # self.removeItem(item) # or is it item.setParent(None) 
                # self.addItem(new_item)

    def keyPressEvent(self, event):
        print()
        print('SCHEMATICSCENE.KEYPRESSEVENT')
        if event.key() == Qt.Key.Key_Escape: 
            self.exitCurrentMode()
            print('ESCAPE KEY PRESSED')
        if event.key() == Qt.Key.Key_Delete:
            print('DELETE KEY PRESSED')
            for item in self.selectedItems():

                if item.reference(): # Then we are a item, we should ALSO delete the SYMBOL w/ corresponding reference_value. 
                    print(f'ITEM: {item} IS A SYMBOL, deleting from both sch and brd')
                    self.deletePart.emit(item.referenceDesignator(), item.referenceNumber()) # Let MMW handle SymbolItem removal, bc we need to remove corresponding footprint too, and we can only reach boardScene through mmw. deleted_item.emit(reference, value).connect(MMW.delete_part) 
                else: 
                    self.removeItem(item)
                    item = None
                        
        return super().keyPressEvent(event) # This event handler, for event keyEvent, can be reimplemented in a subclass to receive keypress events. The default implementation forwards the event to current focus item.( FOCUS != SELECTION ) 
    
    def exitCurrentMode(self):
        if self.mode() == self.AddWireMode:
            self.exitAddWireMode()
        elif self.mode() == self.AddSymbolMode:
            self.symbol = None 
        self.setMode(self.NormalMode)
            
            

            
        self.setMode(self.NormalMode)
            
    def removeItem(self, item): 
        super().removeItem(item)


    ##CODE FOR DRAGNDROP DROPS
    # def dragEnterEvent(self, event): # dragEnterEvent default does what we want: accepts event, & allows scene to receive future dragMoves 
    #     print("MYSCENE.DRAGENTEREVENT")
    #     super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event): #Note this reimplementation IS REQUIRED to get QDrag to work, even if it only passes
        # print('SCHEMATICSCENE.DRAGMOVEEVENT')
        pass
        

    def dropEvent(self, event):
        print() 
        print('MySCENE.DROPEVENT')
        part = json.loads(event.mimeData().text()) # part will be in mimeData().text() as a json string representing a python dictionary
        source_widget = MyWidgets.Schematic.value 
        # print('SOURCEWIDGET:', source_widget)
        self.droppedPart.emit(part, event, source_widget)
        # item = MySymbolObject(part)
        
        # # Assign a value to this item for reference_value
        # value = 1 # I don't want a "R0", begin at 1. # Q: Any standards say otherwise? (TODO: Should be user-configurable)
        # # for i in self.views()[0].parent().parent()
        # for i in self.items(): 
        #     if isinstance(i, MySymbolObject):
        #         if item.part().get('reference') == i.part().get('reference'):
        #             value += 1 # 
        # item.setValue(value)        
                
        # # symbol.doubleClicked.connect()
        # item.setPos(self.snap_to_grid(event.scenePos())) # Add symbol lined up on the grid 
        # self.addItem(item)
        # print("ADDED PART TO SCHEMATIC")
        # self.added_symbol.emit(part) # Let the world know that a part was added to a scene. In MyMainWindow: mw.schematic.scene.added_symbol.connect(mw.board.scene.add_part) & vv.
        
    def AddWireModeMousePressEvent(self, event): 
        # print("AddWireModeMOUSEPRESSEVENT")
        
        if self._wire: # If we already clicked, and click again near the same spot, don't do anything. 
            if  self._wire.line().length() == 0: 
                return None 
            
# _line and _wire are only for creating hor_wire and vert_wire & debugging; remove _line and _wire, do not remove hor_wire or vert_wire.
        if self._line: 
            self.removeItem(self._line) # finish the _line, aka remove it from the scene, ._line & ._wire are just for debugging, hor_wire & vert_wire are staying on scene 
        if self._wire: 
            self.removeItem(self._wire)
            if not self._wiringPos: # Store one point for wirePropagations()
                self._wiringPos = self._wire.line().p1()
                # print()
                # print('SCHSCENE.WIRINGPOS:', self._wiringPos)


        if self._horWire: # If we have a _horWire, and we click again, but _horWire is of 0 length, we should take it off the scene. (This case happens when user draws all-vertical wiring)(Otherwise, it will be an invisible, but 0 length line on the scene. We just don't need it.)
            if self._horWire.line().length() == 0: 
                self.removeItem(self._horWire)
        if self._vertWire: # If we have a _horWire, and we click again, but _horWire is of 0 length, we should take it off the scene. (This case happens when user draws all-vertical wiring)(Otherwise, it will be an invisible, but 0 length line on the scene. We just don't need it.)
            if self._vertWire.line().length() == 0: 
                self.removeItem(self._vertWire)
            
# Create new items when we click
        self._wire = QGraphicsLineItem(QLineF(self._seeker.scenePos(),self._seeker.scenePos())) # Begin a wire when we click. This wire will represent the wire 'as the crow flies'. Helps create hor_wire and vert_wire.  
        self._line = QGraphicsLineItem(QLineF(self._seeker.scenePos(),self._seeker.scenePos()))
        self._horWire = WireItem(QLineF(self._seeker.scenePos(),self._seeker.scenePos()))
        self._vertWire = WireItem(QLineF(self._seeker.scenePos(),self._seeker.scenePos()))
        
# Avoid artifact where line of 0 length looks like a line when zoomed in
        self._wire.setVisible(False)
        self._line.setVisible(False) 
        self._horWire.setVisible(False)
        self._vertWire.setVisible(False)
        
# Make lines have different pen colors so we can see them easier
        self._wire.setPen(QPen(Qt.red, 1 , Qt.PenStyle.DotLine))
        self._line.setPen(QPen(Qt.yellow, 1 , Qt.PenStyle.DotLine )) 
        self._horWire.setPen(QPen(Qt.blue, 1))
        self._vertWire.setPen(QPen(Qt.cyan, 1))

# Add new items to scene. Then every time we mouseMove, we may update these items 
        self.addItem(self._wire) 
        self.addItem(self._line)
        self.addItem(self._horWire)
        self.addItem(self._vertWire)   
        
    def mouseMoveEvent(self, event): # Collect info about what we mouse over. save as instance variables, such that mousePressEvent can use them.
        # print("MYSCENE MOUSEMOVEEVENT")
### seeker snaps to grid default
        grid_pos = self.snapToGrid(event.scenePos())
        self._seeker.setPos(grid_pos)         # wire gridding implemeneted by snapping seeker to grid_step in moveEvent, then creating wires at seeker pos. Mousing over a TerminalItem overrides gridding, so you can connect to any TerminalItem, even if it isn't matched up to the grid_step( EVEN THO SYMBOL GRAPHICS SHOULD BE DESIGNED WITH TERMINAL ITEMS ON GRID)
        # if self._mode == SchematicScene.AddSymbolMode: 
        #     self._seeker.hide()
        #     self._currentlyAddingSymbolItem.setPos(grid_pos) # Add symbol lined up on the grid 
        
        if (self._mode == SchematicScene.AddWireMode): 
            self.terminal = None # Need to reset any references to terminals/wires when we mouse away from them 
            self.moused_over_wire = None # 
            self.symbol = None 
            self._seeker.show()
            
### seeker snap to points of interest if applicable
            detected_items = self._seeker.collidingItems() # List all items beneath seeker  # Qt.ItemSelectionMode.ContainsItemBoundingRect) 
            if detected_items: 
                for item in detected_items:  # These for loops are written such that we only bother processing a single item
                    if isinstance(item, TerminalItem):
                        self.terminal = item 
                        # print('DETECTED TERMINAL:', self.terminal)
                        self._seeker.setPos(self.terminal.scenePos()) # Snap seeker to terminal item
                        break
                    elif isinstance(item, WireItem) and not item==self._horWire and not item==self._vertWire and not item==self._wire:#  Find wires in enlarged area under mouse press(enlarge bc skinny wires are hard to click on). Disregard currently drawing wire items, tho.
                        self.moused_over_wire = item 
                        # print('DETECTED WIRE:', self.moused_over_wire)
                    # wires= [item for item in items if isinstance(item, MyGraphicsWireItem) and not item==self.hor_wire and not item== self.vert_wire and not item==self._wire] #  Find wires in enlarged area under mouse press(enlarge bc skinny wires are hard to click on). Disregard currently drawing wire items, tho.

                        if self.moused_over_wire.line().dy(): # If this wire is vertical:
                            seeker_snap = QPointF(self.moused_over_wire.line().x1(), grid_pos.y()) # Snap wires to the grid_step, as well
                        elif self.moused_over_wire.line().dx(): # If this wire is horizontal: 
                            seeker_snap = QPointF(grid_pos.x(), self.moused_over_wire.line().y1())  # 
                        self._seeker.setPos(seeker_snap) # Update seeker pos
                        break
### Drawing _line. _line Does NOT snap
            if self._line:
                self._line.setLine( QLineF(self._line.line().p1() , event.scenePos()) ) # Update _line with current pos of mouse. Line does NOT snap
### Drawing Wire. _wire snaps, to seeker
            if self._wire and self._line: # self._wire is created in mousePressEvent. Check if we have one. self.line draws straightest path between start point and mouse,(which is necessary to have but we also want user to draw ONLY horizontal & vertical wires on the schematic)
                self.updateWireComponents()# Update x/y componenets to match self._wire. 
            # We saved self.terminal and self.moused_over_wire as an instance variable for mousePressEvent to use 

        elif self._mode == SchematicScene.NormalMode: 
            pass
        super().mouseMoveEvent(event)

    def updateWireComponents(self): # self.hor_wire and self.vert_wire depend on self.line()
        if (not self._line) or (not self._wire): 
            print('We need _wire and _line to calculate wire componenets')
            return None 
        
        dx = self._line.line().dx() 
        dy = self._line.line().dy()
        threshold = 30 # set to anything less than grid_step 
        if abs(dx) < threshold and abs(dy) < threshold: # If we are below a threshold, let initial_direction be changed
            
            self._initial_direction = 'x' if abs(dx) >= abs(dy) else 'y' # if we have more x than y , we want to draw horizontal line attached to the start point # if more y than x, we want to draw vertical line attached to the start point
            
        self._wire.setLine(QLineF(self._wire.line().p1(), self._seeker.scenePos())) # Update _wire's p2 to seeker's scenePos. 
        if self._initial_direction == 'x': 
            self._horWire.setLine(QLineF(self._wire.line().p1() , QPointF(self._wire.line().p2().x() , self._wire.line().p1().y())))
            self._vertWire.setLine(QLineF(self._horWire.line().p2() , self._wire.line().p2()))
            
        elif self._initial_direction == 'y':
            self._vertWire.setLine(QLineF(self._wire.line().p1() , QPointF(self._wire.line().p1().x() , self._wire.line().p2().y())))
            self._horWire.setLine(QLineF(self._vertWire.line().p2() , self._wire.line().p2()))

        self._horWire.setSceneTerminals() # Set scene Terminals every time the _hor/_vertWire moves
        self._vertWire.setSceneTerminals()
        
        # _WIRE and HOR_WIRE and VERT_WIRE only VISIBLE IF length is nonzero
        self._horWire.setVisible(False)
        self._vertWire.setVisible(False)
        self._wire.setVisible(False)
        
        if self._wire.line().length() > 0: # _wire is snapped to grid: only show, if its of nonzero length.
            self._wire.setVisible(True)
        if self._vertWire.line().length() > 0:  
            self._vertWire.setVisible(True)
        if self._horWire.line().length() > 0:
            self._horWire.setVisible(True)
        if self._line.line().length() > 0: 
            self._line.setVisible(True)
            
    def exitAddWireMode(self):

        print('MYSCENE.exitAddWireMode')
        self.views()[0].setMouseTracking(False) # disable mouseMoveEvent from firing while no mouse button pressed down. this is default setting.    
        self.setMode(SchematicScene.NormalMode) # restore default mode. But for real app, should stay in wiring_mode
        mainWindow = self.views()[0].parentWidget().parentWidget().parentWidget()# Get the main_window.( we need to uncheck addWireAction). The view's parent is the schematic, schematic's parent is a stackedWidget, stackedWidget's parent is the QMainWindow. HEY this is a good example of when we should start using SIGNALS/SLOTS rather than digging through parent objects 
        # print('IS THIS THE MAIN WINDOW:', main_window) # Yes
        mainWindow._addWireAction.setChecked(False) # uncheck addWireAction
        self.removeItem(self._line) 
        self.removeItem(self._wire) # Need to remove the current _wire from the scene( bc, on the first click of our doubleclick, press event finishes the current line and makes a new line -- this new line is what we want to delete.) 
        self.removeItem(self._horWire)
        self.removeItem(self._vertWire)
        self._line = None 
        self._wire = None           # Note also can destroy existing ._wire so it isn't sticking around when next addWireMode comes around
        self._horWire = None 
        self._vertWire = None 
        # self._seeker.setVisible(False)
        self.wiringLaid.emit(self._wiringPos)
        self._wiringPos = None 
        # self.hor_wire = None  Don't just set to none. mousePress creates new ._line, .hor_wire and .vert_wire, so remove actually remove them from the scene
        # self.vert_wire = None# We are done drawing lines. # Note: Empty MyGraphicsWireItem()s are allowed. They evaluate to True. 
                
    def mousePressEvent(self, event): # ToDo: Only allow lines to move hor/vertically from their start point
        # print('MYSCENE MOUSEPRESSEVENT')
        
        if self._mode == SchematicScene.AddWireMode: # Add a new MyGraphicsWireItem() to the scene, with every click.
            self.AddWireModeMousePressEvent( event)
        elif self._mode == SchematicScene.DeleteWireMode:
            self.DeleteWireModeMousePressEvent(event)
        elif self._mode == SchematicScene.NormalMode:
            self.NormalModeMousePressEvent(event)
        elif self._mode == SchematicScene.AddSymbolMode: 
            self.exitCurrentMode()
            
            # self.AddSymbolModeMousePressEvent(event)
        # if self._mode == SchematicScene.addSymbolMode: 
        #     self._seeker.hide()
        #     self.symbol.setPos(grid_pos)
        super().mousePressEvent(event) # Call base implementation to: fwd event to mousegrabber if there's a mousegrabber, OR fwd event to topmost item, if no mousegrabber, OR reset selections, then remove focus from any focused items, then ignore the event, if no item below event position. TLDR; Call base implementation to forward event to any items beneath the press.         

    # def addSymbolModeMousePressEvent(self, event):
    #     self.
    def DeleteWireModeMousePressEvent(self, event):
        items = self.items(self._seeker.scenePos()) 
        for item in items: 
            if isinstance(item, WireItem):
                self.removeItem(item)
                print('REMOVED ITEM: ', item)
                
    def NormalModeMousePressEvent(self, event):
                # if self.symbol: # if we moused over a symbol: 
        pass
        
    def mouseReleaseEvent(self, event):
        print("MYSCENE MOUSERELEASEEVENT")
        super().mouseReleaseEvent(event) # 

    def mouseDoubleClickEvent(self, event):
        print('MYSCENE MOUSEDOUBLECLICKEVENT')
        if self._mode == SchematicScene.AddWireMode: # Exit AddWireMode. normalizeWiring. 
            self.exitAddWireMode()
        elif self._mode == SchematicScene.DeleteWireMode:
            pass # 
        else: 
            super().mouseDoubleClickEvent(event) # Call base implementation to forward event to items beneath the event            
            

    def setMode(self, mode):
        self._mode = mode
        print()
        print(f"SET MODE TO {mode}")

    def mode(self):
        return self._mode
                
    def snapToGrid(self, point: QPointF | QPoint):
        return QPointF( round(point.x()/self.grid_step)*self.grid_step , round(point.y()/self.grid_step)*self.grid_step ) 


        



#.POSITION ()
# -> item position, in parent coordinates. This function is the same as item.mapToParent(0, 0).
#.SCENEPOSITION()
# -> item position, in scene coordinates. Same as item.mapToScene(0,0)
#.GLOBALPOSITION()
#->item position, in global(screen), coordinates 

