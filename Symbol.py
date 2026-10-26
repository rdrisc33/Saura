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
        # self.p1_offset = event.scenePos() - p1
        # self.p2_offset = p2 - event.scenePos() #offsets must be recorded at mouse press location ( Hmm but we don't have p1/p2 here )(Gotta record connected wires upon mousePressEvent)
        # wires = [wire for wire in self.scene().items() if isinstance(wire, WireItem)]
        # terminals = [ terminal for terminal in self.childItems() if isinstance(terminal, TerminalItem)]
        # self.connected_wires = {}
        # for wire in wires: 
        #     p1 = wire.line().p1()
        #     print()
        #     p2 = wire.line().p2() 
        #     for terminal in terminals: 
        #         # print('TERMINAL.POS():', terminal.scenePos()) # Must specify scenePos, else will use itemPos, relative to items' 0,0.
        #         if p1 == terminal.scenePos(): #  This works only if terminal has not yet moved which I believe is the case 
        #             # print('P1 is connected to a terminal')
        #             self.connected_wires[wire] = {'point': 'p1' , 'p1_offset': p1 - event.scenePos() }
        #             # wire.setLine( QLineF( self.snapToGrid(event.scenePos() + self.p1_offset) , wire.line().p2() ) )
        #         elif p2 == terminal.scenePos():
        #             self.connected_wires[wire] = {'point': 'p2' , 'p2_offset': p2 - event.scenePos() }
        #             # wire.setLine( QLineF( wire.line().p1() , self.snapToGrid(event.scenePos() + self.p2_offset)) )
                    
        # print('SELF.OFFSET:', self.offset)
        super().mousePressEvent(event) 

    def mouseMoveEvent(self, event): 
        # print("MOUSEMOVEEVENT")
        # print('EVENT.SCENEPOS:', event.scenePos())
        
        # for wire in self.connected_wires: # I have to find offsets of connected_wires, in order to move connected wires when user moves item. Record connected_wire offsets in mousePress, and move the wires in mouseMove
        #     if self.connected_wires[wire]['point'] == 'p1': 
        #         p1_offset =  self.connected_wires[wire]['p1_offset']
        #         wire.setLine( QLineF( self.scene().snapToGrid(event.scenePos() +p1_offset) , wire.line().p2() ) ) # TODO: set line xy componenets # TODO: implement snap_to_graph 
        #     elif self.connected_wires[wire]['point'] == 'p2':
        #         p2_offset = self.connected_wires[wire]['p2_offset']
        #         wire.setLine( QLineF( wire.line().p1() , self.scene().snapToGrid(event.scenePos() + p2_offset) ) )

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
            
