from utils import *
from PySide6.QtCore import Qt 

class WireItem(QGraphicsLineItem):
    
    def __init__(self, *args, **kwargs):

        super().__init__( *args, **kwargs )
        self.setPen(QPen(wireItemColor, 1))
        self.veinId = None # Wire will know the id of the vein which they belong to.  
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setPen(QPen(Qt.magenta, 1)) # 
        self.li1 = None 
        self.li2 = None 
                    
    def mousePressEvent(self, event):
        self._dragStart = event.scenePos()
        self.connectedWiresP1 = dict() # stores wire:anchor key-value pairs. wire:WireItem, anchor: QPointF
        self.connectedWiresP2 = dict()
        
        p1 = self.line().p1()
        p2 = self.line().p2() 
        for wire in [item for item in self.scene().items() if isinstance(item, WireItem) and self.isOrthagonalTo(item) ]: 
                
            # if wire.line().p1() == p1 or wire.line().p2() == p1:
            #     self.connectedWiresP1[wire] = anchor
            if wire.line().p1() == p1:
                anchor = wire.line().p2()
                self.connectedWiresP1[wire] = anchor
                
            elif wire.line().p2() == p1:
                anchor = wire.line().p1()
                self.connectedWiresP1[wire] = anchor
                
            elif wire.line().p1() == p2:
                anchor = wire.line().p2()
                self.connectedWiresP2[wire] = anchor
                
            elif wire.line().p2() == p2:
                anchor = wire.line().p1()
                self.connectedWiresP2[wire] = anchor
            
        print('CONNECTEDWIRESP1:', self.connectedWiresP1)
        print('CONNECTEDWIRESP2:', self.connectedWiresP2)

            
        if len(self.connectedWiresP1) == 0: # Then there are no wires connected to p1. Create one 
            newWire = WireItem(QLineF(p1,p1))
            self.connectedWiresP1[newWire] = p1 # zero length WireItem anchored on p1
            self.scene().addItem(newWire)
        if len(self.connectedWiresP2) == 0: 
            newWire = WireItem(QLineF(p2,p2))
            self.connectedWiresP2[newWire] = p2 
            self.scene().addItem(newWire)

            
        # p1 = self.line().p1()
        # p2 = self.line().p2() 
        # for wire in [item for item in self.scene().items() if isinstance(item, WireItem) ]: 
        #     if wire.line().p1() == p1 or wire.line().p1() == p2:
        #         p3 = wire.line().p2()
        #     elif wire.line().p2() == p1 or wire.line().p2() == p2:
        #         p3 = wire.line().p1()

        #     orientation = Utils.threePointOrientation(p1, p2, p3) 
            
        #     self.connectedWires[wire]['orientation'] = orientation
        #     self.connectedWires[wire]['anchor'] = p3
            
        #     print('CONNECTED WIRES:', self.connectedWires)
            
        # seekerSide = Utils.threePointOrientation(p1, p2, self.scene().seeker().scenePos())
        # for wire, wireInfo in self.connectedWires.items():
        #     if wireInfo['orientation'] == seekerSide: # If this connectedWire is on same side of self  as seeker: 
        #         wire.setLine(wireInfo['anchor'] , p1.x() if self.isHorizontal() else p1.y(), event.scenePos().y() if self.isHorizontal() else event.scenePos().x())
                
    def mouseMoveEvent(self, event):
        # dragVector = QLineF(event.scenePos() , self._dragStart)
        # if dragVector.length() < 4:
        #     return  
        
        p1 = self.line().p1()
        p2 = self.line().p2() 
        snapPos = self.scene().snapToGrid(event.scenePos())
        snapY = snapPos.y()
        
        if self.isHorizontal(): 
# Move self 
            self.setLine(QLineF(QPointF(p1.x(), snapY) , QPointF(p2.x(), snapY)))
# Move connectedWires
            for wire, anchor in self.connectedWiresP1.items():
                    wire.setLine(QLineF(anchor, QPointF(p1.x() , snapY)))
            
            for wire, anchor in self.connectedWiresP2.items():
                    wire.setLine(QLineF(anchor, QPointF(p2.x() , snapY)))
            

        
    def mouseReleaseEvent(self, event):
        for wire, anchor in self.connectedWiresP1.items(): 
            if wire.line().length() == 0: 
                self.scene().removeItem(wire)
                
        for wire,anchor in self.connectedWiresP2.items(): 
            if wire.line().length() == 0: 
                self.scene().removeItem(wire)
                
        self.scene().wiringLaid.emit(self.line().p1())
        #Remove any items which are of 0 length 
        
        
            
    def isOrthagonalTo(self, wire):
        if Utils.junction(self, wire)[0] == Utils.JunctionType.L:
            return True 
        return False 
    
    def terminatesOnWire(self, wire):
        for terminal in self.sceneTerminals():
            for otherTerminal in wire.terminals: 
                if terminal == otherTerminal: 
                    return True 
        return False 
            

            
    def isHorizontal(self):
        if self.line().dx() and self.line().dy(): 
            return False 
        if self.line().dx(): 
            return True 
        
    def isVertical(self):
        if self.line().dx() and self.line().dy():
            return False
        if self.line().dy():
            return True 
            
            

    def p1(self): # Any reason to not do this? 
        return self.line().p1()
    
    def p2(self):
        return self.line().p2()
    
    def terminals(self):
        pass
    def sceneTerminals(self):
        return self._sceneTerminals 
    def setSceneTerminals(self):
        self._sceneTerminals = [ self.mapToScene(self.line().p1()) , self.mapToScene( self.line().p2()) ]
    


#WireItem is NOT a copperItem; connects things on the schematic not board. 
