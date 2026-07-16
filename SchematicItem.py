from utils import * 
from TerminalItem import TerminalItem
from WireItem import WireItem
from Reference import Reference

# ToDo: make class BaseSymbol, lives behind both netSymbol & Symbol
class SchematicItem(Reference, QGraphicsItem): # PLACE QT CLASSES LAST IN INHERITANCE bc they are coded in C++, they cannot use super().__init__. If they can't call super().__init__(), They cannot get back on the MRO chain; cannot make sense of *args nor **kwargs. If you place Qt classes last, by the time you get to them, *kw/args have already been eaten up. : # NOTE QGraphicsOBJECT IS a QGraphicsITEM   which inherits QObject, such that QGraphicsObject can use signals and slots; QGraphicsITEM is not a QObject. BUT idn qobject yet at least

    font = Utils.symbolFont

    def __init__(self, referenceDesignator, referenceNumber, *args, **kwargs):
        super().__init__(referenceDesignator, referenceNumber, *args, **kwargs)

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
        super().mousePressEvent(event) # The default implementation handles basic item interaction, such as selection and moving. If you want to keep the base implementation when reimplementing this function, call QGraphicsItem::mousePressEvent() in your reimplementation.

    def mouseMoveEvent(self, event): # I want to do something custom when I clickNDdrag. I can do that in mouseMoveEvent(). "Reimplement this event handler to receive mouse move events for this item. If you do receive this event, you can be certain that this item also received a mouse press event, and that this item is the current mouse grabber." Q: Can I also be certain we are dragging this item? 
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
        
        
        # super().mouseMoveEvent(event) # We want to call the base implementation to handle moving the item. # self.setPos( self.snapToGrid(event.pos() + self.offset  ) ) # The base implementation handles moving # Except we want to snap to grid, so we can't use base implementation: Complicatedly, we need to snap, acounting for t between item origin and location of mouse grab. (Note the item's terminals must line up with grid, not necessarily item center  Note that item center should ALSO be on grid, and this demands items have been created ON GRID, which indeed they are, for all EDA softwares.)


        # print("EMITTING PART:", part)
        # self.doubleClicked.emit(part) # MySymbolItem().doubleClicked.connect(MyMainWindow().assign_graphic) ? 
        # self.doubleClicked.connect(self.assign_graphic('symbol',part)) Can I launch a assign symbol dialog from here? 
        


        
        # super().mouseMoveEvent(event)
# QWidget.hide() effectively removes the widget from it's layout until QWidget.show()    
# Nonselectable or nonmovable items Do not receive single or double click events 

        # super().mouseDoubleClickEvent(event) No need to call double click's base implementation, the base implementation just calls mousePressEvent 

    def mouseReleaseEvent(self, event):
        print("MySymbolItem.MouseReleaseEvent")
        super().mouseReleaseEvent(event) # Release's base implementation handles selection and moving, which we want, so call base implementation
        
