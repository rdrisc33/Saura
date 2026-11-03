from utils import * 

from MyGraphicAssign import MyGraphicAssign
from TerminalItem import TerminalItem
from Reference import Reference
from WireItem import WireItem 
from PinItem import PinItem

# class SchematicSymbolItem(SchematicItem):
class Symbol(Reference, QGraphicsItem):
    font = Utils.symbolFont

    def __init__(self, referenceDesignator, referenceNumber, file, *args, **kwargs):
        super().__init__(referenceDesignator, referenceNumber, *args, **kwargs)
        self._file = None 
        self._pins = [] # A list to store Pin objects
        # self._pins = {} # A dict to store pin.sceneTerminal:Pinobjects pairs
        # self._terminals = [] # idt this ever needed 
        self._sceneTerminals = [] 
        
        self.setFile(file)

        self._nameItem = QGraphicsSimpleTextItem('', self) 
        
        dpi = qApp.screens()[0].physicalDotsPerInch() # dpi relies on the qApp instance; you have to already have instantiated QApplication()
        kicad_symbol_scale_factor = dpi * Utils.grid4mm / Utils.fileGridStep  # scale_factor = 1/1.27 * 50 
        self.setScale(kicad_symbol_scale_factor) # scale item so it fits on the scene's grid
        if self.file() is None or self.file() == "": 
            self.placeholder = QGraphicsSimpleTextItem("Assign Symbol", self) # Indicate this item requires footprint assignment
            self.placeholder.setFont(footprint_placeholder_font)
        else: 
            self.units = [0,1] # Only Draw units 0 and 1 by default.
            # self.offset = None # A value representing the x and y offsets needed to get this item lined up with the grid ( equal to the distance from the origin to a MyTerminalItem. offset is made 'permanent' by implementing .setPos(pos() - offset) in the .paint() reimplementation(?)) # This is all wrong, silly past-me

            self.draw_graphics()

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        
    def terminals(self): 
        self._terminals = [] 
        for pin in self.pins():
            self._terminals.append(pin.terminal())
        return self._terminals
    
    def sceneTerminals(self):
        return self._sceneTerminals # [ ( (0,0) , <pin> ) , ... ]

    def setSceneTerminals(self): # Called by self.mouseMoveEvent
        self._sceneTerminals = []
        for pin in self.pins(): 
            self._sceneTerminals.append( pin.sceneTerminal() )
        # self._sceneTerminals = {}
        # for pin in self.pins(): 
        #     self._sceneTerminals[pin.sceneTerminal().toTuple()] = pin
        
    def boundingRect(self):
        return self.childrenBoundingRect() or QRectF(0,0,0,0) # Note .cBR will include .bR of hidden childrenItems. 

    # the default of returning a rect based on boundingRect dnw bc a Symbol has simple text items, which should not be part of hit area
    def shape(self): #
        path = QPainterPath()
        for child in self.childItems(): # Collect paths of all childItems, except for text. So, pins, and lines & arcs & such
            if not isinstance(child, QGraphicsSimpleTextItem): 
                # print('CHILD:', type(child))
                path.addPath(child.shape())
        r = path.boundingRect()
        # print('R:', r)
        p = QPainterPath()
        p.addRect(r)
        # print('P:', p)
        return p
    
    def moveShape(self): # Return a shape consisting of the boundingRects of 'core' components; components to move by, such as lines and arcs, making up the actual symbol, no pins. This shape is used in mousePressEvent to decide if item will become mouse grabber, thus receiving future mouse events 
        path = QPainterPath()
        for child in self.childItems(): # Collect paths of all childItems, except for pins, and text. So, lines & arcs & such
            if not isinstance(child, (PinItem, QGraphicsSimpleTextItem)): 
                # print('CHILD:', type(child))
                path.addPath(child.shape())
        r = path.boundingRect()
        # print('R:', r)
        p = QPainterPath()
        p.addRect(r)
        # print('P:', p)
        return p

    def paint(self, painter, option, widget):
       pass# Child Items will draw themselves
    
    def mousePressEvent(self, event):  # MOUSEGRABBER: User chooses mousegrabber by clicking on it(and item will stay mousegrabber(?) for ~.3s after the release event, enough time for it to register any incoming double click events. item has to be mouse grabber to process second mousePressEvent as a double click. Item becomes mousegrabber by .accept()ing initial press event. reimplements of QGItem.mouse(press,release,doubleclick)Event()s automatically accept their respective event, so reimplement QGraphicsItem.MusePressEvent() to accept the mousePressEvent, then do what you will with it
        # print("SCHEMATICSYMBOL.MousePressEvent")
        # print('ITEM IS MOUSEGRABBER') if self.scene().mouseGrabberItem() is self else print('ITEM IS NOT MOUSE GRABBER')
        if not self.moveShape().contains(event.pos()) : 
            event.ignore() # Loose the mouse grab, we don't want to receive future mouse press events if click not within move shape. 
            return 
        
        self.offset = self.scenePos() - event.scenePos()  # Could also utilize event.mouseDownPosition(no could not
        self.prepareToMoveConnectedWires()
        super().mousePressEvent(event) 

    def prepareToMoveConnectedWires(self): 
        """Search for wires and symbols connected to this symbol to generate self.connections, a data structure used in mouseMoveEvent to adjust connected wires upon user moving this symbol. 
        A symbol may have wires or other symbols connected to it's terminals. When we move the symbol, we want wires connected to terminals to remain connected to their terminals.
        Locate an 'anchor' point, in scene coordinates, where the terminal eventually connects to. 
        This anchor point is two wires away, one horizontal wire, one vertical wire. 
        If there is just one wire connected to terminal, the anchor point is that wire's distal 
        If there is a symbol connected to terminal, the anchor is right there. 
        If there is a junction of 2+ wires at terminal, the anchor is also right there.
        If there is nothing connected at terminal, the anchor is None 
        
        
        For each terminal in this symbol, look for connected symbols or wires. 
            if there are no connections at terminal, anchor is None 
            if there is a symbol connected at terminal, or 2+ wires connected at terminal, anchor will be that terminal. 
            if there is a single wire connected to terminal, whose distal is not connected to anything, or whose distal is connected to 2+ wires, or whose distal is connected to a symbol, anchor will be that wire's distal. If wire is horizontal, denote initialDirection as 'x', and horWire is wire. If wire is vertical, denote initialDirection as 'y', and vertWire is wire. 
            If there is just one wire connected to terminal, whose distal is connected to one other wire, anchor will be that second wire's distal. If second wire is vertical, vertWire is secondWire. If second wire is horizontal, horWire is second wire 
        Use self.connections is keyed on local position of the terminal, and value stores 4-tuple with relevant info about any connections: (anchor, initialDirection, horWire, vertWire)
        self.connections is used in mouseMoveEvent to know what wires to adjust as symbol moves, with initialDirection maintained.
        """
        
        self.connections = {}
        items = [item for item in self.collidingItems() if isinstance(item, (WireItem, Symbol))]
        
        for t in self.terminals():
            wire                = None 
            wire2               = None 
            anchor              = None 
            anchor2             = None
            initialDirection    = None
            horWire             = None
            vertWire            = None
            connectedWires      = 0 
            
            for item in items: 
                for terminal in item.sceneTerminals():
                    if terminal == self.mapToScene(t): # Then self and item connect
                        if isinstance(item, Symbol):
                            anchor = terminal
                            initialDirection = None 
                            horWire = WireItem()
                            vertWire = WireItem()
                            break

                        elif isinstance(item, WireItem):
                            connectedWires += 1 
                            wire = item
                            if connectedWires == 2: # 
                                wire = None 
                                anchor = terminal
                                initialDirection=None 
                                horWire = WireItem()
                                vertWire = WireItem()
                                break
                if anchor: 
                    break
                
            # if connectedWires == 1: 
            if wire is not None: # Wire is None unless a single wire connected to terminal
                if wire.isHorizontal(): 
                    horWire = wire 
                    vertWire = WireItem()
                    initialDirection = 'x'
                elif wire.isVertical():
                    vertWire = wire 
                    initialDirection = 'y'
                    horWire = WireItem()

                distal = None 
                print()
                print('WIRE.P1()', wire.p1())
                print('WIRE.P2()', wire.p2())
                print('SELF.MAPTOSCENE(T)', self.mapToScene(t))
                if wire.p2() == self.mapToScene(t):
                    distal = wire.p1() 
                if wire.p1() == self.mapToScene(t) : 
                    distal = wire.p2() 
                anchor = distal 
                
                # if there is one other wire connected to wire at distal, that wire is our missing hor/vert wire, anchor is other wire's distal
                # if there is a symbol, or 2+ wires connected to wire at distal,  our missing hor/vert wire is null, anchor is distal
                items2 = [ item2 for item2 in self.scene().items(distal)  if isinstance(item2, (Symbol ,WireItem)) and item2 is not wire]

                connectedWires2 = 0
                for item2 in items2: 
                    for terminal2 in item2.sceneTerminals(): 
                        if terminal2 == distal: # Then wire is connected to item2
                            if isinstance(item2, WireItem):
                                connectedWires2 += 1 
                                wire2 = item2
                                if connectedWires2 == 2: 
                                    wire2 = None 
                                    anchor2 = distal
                                    break 
                            elif isinstance(item2, Symbol):
                                anchor2 = distal
                                break 
                    if anchor2: 
                        break 
                    
                # if connectedWires2 == 1:
                if wire2 is not None:  
                    if wire2.isHorizontal():
                        horWire = wire2
                    elif wire2.isVertical():
                        vertWire = wire2
                        
                    distal2 = None 
                    if wire2.p2() == distal:
                        distal2 = wire2.p1() 
                    if wire2.p1() == distal : 
                        distal2 = wire2.p2() 
                    anchor2 = distal2 
 
            anchor = anchor2 if anchor2 else anchor
            if horWire: 
                if not horWire.scene(): 
                    self.scene().addItem(horWire)
            if vertWire: 
                if not vertWire.scene():
                    self.scene().addItem(vertWire)
                
            self.connections[t.toTuple()] = (anchor, initialDirection, horWire, vertWire)

        print('SELF.CONNECTIONS:', self.connections)
            

    def mouseMoveEvent(self, event): 
        # print("MOUSEMOVEEVENT")
        # print('EVENT.SCENEPOS:', event.scenePos())
        self.setPos(self.scene().snapToGrid(event.scenePos() + self.offset))
        self.setSceneTerminals()
        self.moveConnectedWires()
        # super().mouseMoveEvent(event)
    
    def moveConnectedWires(self):
        """Relies on self.connections, as created in mousePressEvent. Moves wires in self.connections to match up with this symbols new position. """
        for pos, (anchor, initialDirection, horWire, vertWire) in self.connections.items():
            if anchor is None: 
                continue 
            # wireUp(self.mapToScene(pos) , anchor), taking initialDirection and any existing hor/VertWires into account
            startPos    = self.mapToScene(QPointF(*pos))
            endPos      = anchor
            if initialDirection == 'x': 
                horWire.setLine(QLineF( startPos , QPointF(endPos.x(), startPos.y()) )  )
                vertWire.setLine(QLineF( QPointF(endPos.x() , startPos.y()) , endPos) )

            elif initialDirection == 'y': 
                vertWire.setLine(QLineF( startPos , QPointF(startPos.x() , endPos.y())) ) 
                horWire.setLine(QLineF( QPointF(startPos.x() , endPos.y()) , endPos ) )
            
            
    def mouseReleaseEvent(self, event):
        # print("SYMBOLITEM.MOUSERELEASEVENT")
        
        self.setSceneTerminals() # We need to setSceneTerminals() on every reposition. 
        # print('SCENETERMINALS:' ,self.sceneTerminals())
        for terminal in self.sceneTerminals():
            self.scene().wiringLaid.emit(terminal) # We can use the wiringLaid signal

        for pos, (anchor, initialDirection, horWire, vertWire) in self.connections.items():
            if horWire: 
                if horWire.line().isNull(): 
                    self.scene().removeItem(horWire)
            if vertWire: 
                if vertWire.line().isNull():
                    self.scene().removeItem(vertWire)
        self.connections.clear()
        
        super().mouseReleaseEvent(event) # Release's base implementation handles selection and moving, which we want, so call base implementation
        
    def nameItem(self):
        return self._nameItem

    def mouseDoubleClickEvent(self, event): # Base implementation just calls mousePressEvent(). This reimplementation launches a dialog, lets user assign new symbol to this part
        print()
        print('MySymbolItem.mouseDoubleClickEvent:', self)
        # part = self.data(PartData.PART.value)
        # self.assign_graphic()
        

    def assign_graphic(self):
        self.graphic_assign = MyGraphicAssign( self.part() ,'symbol' )
        self.graphic_assign.open()
        
    @staticmethod
    def scale_1pt27_to_4_mm(x):
        return float(x)*4.0/1.27
        
    def draw_graphics(self):
        # print("DRAWNG GRAPHICS")
        root = etree.parse(self.file()).getroot() # etree.ElementTree, made by etree.parse(xml), only has .iter, etree.Elements have an extended iteration API, which includes .findall -- iter includes tthe element itself, while iterD does not include the element itself 
        # print('NAME:', root.attrib.get('name'))
        self._nameItem.setText(root.attrib.get('name', ''))
        self._nameItem.setFont(Utils.symbolFont)

        # print("ROOT:", root)
        # print('root.findall("graphic"):', root.findall("graphic")) # converter is not making 'graphic' elements.
        for graphic_elem in root.findall("graphic"):  # There is no string 'graphic' in .kicad_sym files BUT THERE IS IN .SYM FILES
            u = graphic_elem.get('unit')
            style = int(graphic_elem.get('style'))
            if style > 1: 
                break
            # print("U:", u)
            if not (int(u) in self.units): # Goddam be careful with your boolean assigments
                break  # Stop drawing 
            
            for pin_elem in graphic_elem.findall('pin'):
                pin = PinItem.fromElem(pin_elem , self)
                self.pins().append(pin)
                pin.nameItem().hide() 
                pin.numberItem().hide() # Base symbol hides pin info bc netSymbols should have those hidden TODO move this to netSymbols
                
            self.draw_polylines(graphic_elem)
            self.draw_rectangles(graphic_elem)

    def draw_polylines(self, graphic_elem):
        # print()
        # print('DRAW_POLYLINES')
        polylines = graphic_elem.findall('polyline')
        # print('POLYLINES:', polylines)
        if polylines:
            for polyline_elem in polylines:
                path = QPainterPath()
                
                points = polyline_elem.get('points').split(" ")
                points = [point.split(',') for point in points]
                # print("POINTS:", points)
                first_point = points.pop(0)
                
                path.moveTo(float(first_point[0]) , float(first_point[1])) # path.moveTo( x , y )
                for point in points: 
                    path.lineTo(float(point[0]), float(point[1])) # path.lineTo( x , y )

                pen = QPen(Qt.darkMagenta, 0)
                # pen.setCosmetic(True)
                path_item = QGraphicsPathItem(path, parent=self)
                path_item.setPen(pen)
        return 
    
    def draw_rectangles(self, graphic_elem):
        rectangles= graphic_elem.findall('rectangle')
        for rectangle_elem in rectangles :
            QGraphicsRectItem(QRectF(rectangle_elem.get('topLeft') , rectangle_elem.get('bottomRight')).normalized(), parent=self)# Add a rectangle as a child onto parent item, self. 
    #         # Note: in QT, invalid rectangles are those with negative widths or heights. Their rendering is undefined, so, make them defined with QRectF.normalized().
    
    def file(self):
        return self._file 
    def setFile(self, file):
        self._file = file 
    def pins(self):
        return self._pins

    
    def sceneTerminals(self):
        return self._sceneTerminals
            
