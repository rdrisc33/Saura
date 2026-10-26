from utils import *
from TerminalItem import TerminalItem

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
        # self.lineItem = QGraphicsLineItem(x1, y1, x2, y2, parent )  # Create each pin as a QGraphicsself.lineItem under parent=parent. (While this is OK, if we parent under PinItem, we can take advantage of that for our .shape())
        self.lineItem = QGraphicsLineItem(x1, y1, x2, y2, self )  # Create each pin as a QGraphicsself.lineItem under parent=self.Note most others are parented under parent=parent. This is because we want PinItem objects which are NOT to be included in our .shape, to be housed under PinItem, while 
        self.lineItem.setPen(QPen(Qt.blue, 0))
            
        # TERMINAL
        r = self.terminalRadius
        # self._terminalItem = TerminalItem(QRectF(-r,-r, 2*r, 2*r) , parent) # Could parent=line_item but a flat hierarchy is more useful. Sign. But then again, no, 
        self._terminalItem = TerminalItem(QRectF(-r,-r, 2*r, 2*r) , self) # Could parent=line_item but a flat hierarchy is more useful. Sign. But then again, no, 
        self._terminalItem.setPos(x1,y1) # Note that (pin (at xy) ) according to kicad standard defines connection point (terminal) of the pin: https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_graphic_items
        # self._terminals[(x1,y1)] = {'priority': Utils.NetPriority.Pin, 'number':number} # Track position of all terminals 
        self._terminalItem.setPen(QPen(Qt.red, 0)) # keep the left& right topmost pins @same location
        # if self.offset is None:  # We want to offset this item, so that a MyTerminalItem appears at origin, so that this item can line up with the grid.
        #     self.offset = terminal_item.pos()
        #     # print()
        #     # print('SELF.OFFSET:', self.offset)
        # NAME 
        self._nameItem.setFont(self.font)
        # self._nameItem.setBrush(QBrush(Qt.black)) Default brush is solid black. Text brush is text color. Text 'pen' is an outline around text((not needed nor wanted; visually cocnfusing)

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
    
