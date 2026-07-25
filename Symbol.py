from utils import * 

from MyGraphicAssign import MyGraphicAssign
from TerminalItem import TerminalItem
from Reference import Reference
from WireItem import WireItem 

# class SchematicSymbolItem(SchematicItem):
class Symbol(Reference, QGraphicsItem):
    font = Utils.symbolFont

    def __init__(self, referenceDesignator, referenceNumber, file, *args, **kwargs):
        super().__init__(referenceDesignator, referenceNumber, *args, **kwargs)
        self._file = None 
        self._pins = [] # A list to store Pin objects
        # self._terminals = [] # idt this ever needed 
        self._sceneTerminals = [] 
        
        self.setFile(file)

        self._nameItem = QGraphicsSimpleTextItem('', self) 
        dpi = qApp.screens()[0].physicalDotsPerInch() # dpi relies on the qApp instance; you have to already have instantiated QApplication()
        kicad_symbol_scale_factor = dpi * grid_4mm / file_grid_step  # scale_factor = 1/1.27 * 50 
        self.setScale(kicad_symbol_scale_factor) # scale item so it fits on the scene's grid
        if self.file() is None or self.file() == "": 
            self.placeholder = QGraphicsSimpleTextItem("Assign Symbol", self) # Indicate this item requires footprint assignment
            self.placeholder.setFont(footprint_placeholder_font)
        else: 
            self.units = [0,1] # Only Draw units 0 and 1 by default.
            # self.offset = None # A value representing the x and y offsets needed to get this item lined up with the grid ( equal to the distance from the origin to a MyTerminalItem. offset is made 'permanent' by implementing .setPos(pos() - offset) in the .paint() reimplementation(?)) # This is all wrong, silly past-me

            self.draw_graphics()

        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.ItemIsSelectable)


    def boundingRect(self):
        return self.childrenBoundingRect() or QRectF(0,0,0,0)

    def paint(self, painter, option, widget):
       pass# Child Items will draw themselves
    
    def mousePressEvent(self, event):  # MOUSEGRABBER: User chooses mousegrabber by clicking on it(and item will stay mousegrabber(?) for ~.3s after the release event, enough time for it to register any incoming double click events. item has to be mouse grabber to process second mousePressEvent as a double click. Item becomes mousegrabber by .accept()ing initial press event. reimplements of QGItem.mouse(press,release,doubleclick)Event()s automatically accept their respective event, so reimplement QGraphicsItem.MusePressEvent() to accept the mousePressEvent, then do what you will with it
        print("SCHEMATICSYMBOL.MousePressEvent")
        print('ITEM IS MOUSEGRABBER') if self.scene().mouseGrabberItem() is self else print('ITEM IS NOT MOUSE GRABBER')
        self.offset = self.scenePos() - event.scenePos()  # Could also utilize event.mouseDownPosition(no could not
        # self.p1_offset = event.scenePos() - p1
        # self.p2_offset = p2 - event.scenePos() #offsets must be recorded at mouse press location ( Hmm but we don't have p1/p2 here )(Gotta record connected wires upon mousePressEvent)
        wires = [wire for wire in self.scene().items() if isinstance(wire, WireItem)]
        terminals = [ terminal for terminal in self.childItems() if isinstance(terminal, TerminalItem)]
        self.connected_wires = {}
        for wire in wires: 
            p1 = wire.line().p1()
            print()
            p2 = wire.line().p2() 
            for terminal in terminals: 
                # print('TERMINAL.POS():', terminal.scenePos()) # Must specify scenePos, else will use itemPos, relative to items' 0,0.
                if p1 == terminal.scenePos(): #  This works only if terminal has not yet moved which I believe is the case 
                    print('P1 is connected to a terminal')
                    self.connected_wires[wire] = {'point': 'p1' , 'p1_offset': p1 - event.scenePos() }
                    # wire.setLine( QLineF( self.snapToGrid(event.scenePos() + self.p1_offset) , wire.line().p2() ) )
                elif p2 == terminal.scenePos():
                    self.connected_wires[wire] = {'point': 'p2' , 'p2_offset': p2 - event.scenePos() }
                    # wire.setLine( QLineF( wire.line().p1() , self.snapToGrid(event.scenePos() + self.p2_offset)) )
                    
        print('SELF.OFFSET:', self.offset)
        super().mousePressEvent(event) 

    def mouseMoveEvent(self, event): 
        print("MOUSEMOVEEVENT")
        print('EVENT.SCENEPOS:', event.scenePos())

        
        for wire in self.connected_wires: # I have to find offsets of connected_wires, in order to move connected wires when user moves item. Record connected_wire offsets in mousePress, and move the wires in mouseMove
            if self.connected_wires[wire]['point'] == 'p1': 
                p1_offset =  self.connected_wires[wire]['p1_offset']
                wire.setLine( QLineF( self.scene().snapToGrid(event.scenePos() +p1_offset) , wire.line().p2() ) ) # TODO: set line xy componenets # TODO: implement snap_to_graph 
            elif self.connected_wires[wire]['point'] == 'p2':
                p2_offset = self.connected_wires[wire]['p2_offset']
                wire.setLine( QLineF( wire.line().p1() , self.scene().snapToGrid(event.scenePos() + p2_offset) ) )

        self.setPos(self.scene().snapToGrid(event.scenePos() + self.offset))
        
        self.setSceneTerminals() # We need to setSceneTerminals() on every mouseMove
        # print('SCENETERMINALS:' ,self.sceneTerminals())
        
    def mouseReleaseEvent(self, event):
        print("MySymbolItem.MouseReleaseEvent")
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
                pin.numberItem().hide()
                
                
            # self.draw_pins(graphic_elem)
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
            

class PinItem( QGraphicsItem): 
    terminalRadius = 1
    font = Utils.symbolFont
    
    def __init__(self, parent, x1, y1, x2, y2, id, number, name, electrical_type = 'passive' , logic_type='normal' ):
        super().__init__(parent)
        self._id = id 
        self._number = number 
        self._name = name 
        self._electricalType = electrical_type 
        self._logicType = logic_type 
        self._terminal = QPointF(x1, y1)
        # self._terminals = []
        self._nameItem = QGraphicsSimpleTextItem(name, parent) # appears at origin of MySymbolItem-- not line_item-- oh bc line_item uses parent coordinates, &child items are placed at origin of parent

        # LINE
        self.lineItem = QGraphicsLineItem(x1, y1, x2, y2, parent )  # Create each pin as a QGraphicsself.lineItem under parent=self.
        self.lineItem.setPen(QPen(Qt.blue, 0))
            
        # TERMINAL
        r = self.terminalRadius
        self._terminalItem = TerminalItem(QRectF(-r,-r, 2*r, 2*r) , parent) # Could parent=line_item but a flat hierarchy is more useful
        self._terminalItem.setPos(x1,y1) # Note that (pin (at xy) ) according to kicad standard defines connection point (terminal) of the pin: https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_graphic_items
        # self._terminals[(x1,y1)] = {'priority': Utils.NetPriority.Pin, 'number':number} # Track position of all terminals 
        self._terminalItem.setPen(QPen(Qt.red, 0)) # keep the left& right topmost pins @same location
        # if self.offset is None:  # We want to offset this item, so that a MyTerminalItem appears at origin, so that this item can line up with the grid.
        #     self.offset = terminal_item.pos()
        #     # print()
        #     # print('SELF.OFFSET:', self.offset)
        # NAME 
        self._nameItem.setFont(self.font)
        self._nameItem.setBrush(QBrush(Qt.black)) # Text brush is text color. Text 'pen' is an outline around text((not needed nor wanted; visually cocnfusing)

        #NUMBER
        self._numberItem = QGraphicsSimpleTextItem(number, parent)
        self._numberItem.setFont(self.font)
        self._numberItem.setBrush(QBrush(Qt.darkCyan))# Text 'pen' is an outline around text(not needed nor wanted-- just set the brush)
    
        # NAME & NUMBER POSITION varies if pin is on left or right side of symbol
        # if x1 == leftmost: 
        if x1 < x2: 
            # print("LEFTMOST", leftmost)
            textHeight = self._nameItem.boundingRect().height()                                                                              
            self._nameItem.setPos( x1+self.lineItem.line().length() , y1-textHeight/2 )                                                                      
            self._numberItem.setPos( x1-self._numberItem.boundingRect().width()/2+self.lineItem.line().length()/2 , y1-self._numberItem.boundingRect().height()/2 )

        # if x1 == rightmost: 
        if x1 > x2: 
            # print('RIGHTMOST', rightmost)
            line_length = self.lineItem.line().length()
            textHeight = self._nameItem.boundingRect().height()
            text_width =  self._nameItem.boundingRect().width()
            self._nameItem.setPos( x1 - line_length - text_width, y1 - textHeight/2 )
            num_height = self._numberItem.boundingRect().height()
            num_width = self._numberItem.boundingRect().width()
            self._numberItem.setPos( x1 - num_width/2 - self.lineItem.line().length()/2 , y1 - num_height/2 )
        if x1 == x2: #  A vertical pin
            pass # TODO
        
    def boundingRect(self):
        return self.childrenBoundingRect()
    def paint(self, painter, option, widget):
        pass 

    def sceneTerminal(self):
        return self.mapToScene( self.lineItem.line().p1() )
    
    @classmethod
    def fromElem(cls, elem, parent): #     <pin name="C" number="C" PIN_ELECTRICAL_TYPE="passive" PIN_GRAPHIC_STYLE="line" x1="-7.62" y1="0.0" x2="-5.08" y2="0.0"/>
        x1,y1,x2,y2 = map(float , [elem.get('x1') , elem.get('y1') , elem.get('x2') , elem.get('y2')])
        number, name =  elem.get('number') , elem.get('name')
        # print('NUMBER:', number, "NAME:", name)elem
        return cls(parent, 
                   x1,y1,x2,y2, 
                   id = id, 
                   number = number,
                   name = name
        )
    
    def id(self):
        return self._id 
    def setId(self, id):
        self._id = id 
        
    def name(self):
        return self._name 
    def setName(self, name):
        self._name = name 
        self._nameItem.setText(self._name)
        
    def number(self):
        return self._number 
    def setNumber(self, number):
        self._number = number
        self._numberItem.setText(self._number)
        
    def nameItem(self):
        return self._nameItem
    
    def numberItem(self):
        return self._numberItem
    
    def electricalType(self):
        return self._electricalType
    
    def logicType(self):
        return self._logicType 
    
