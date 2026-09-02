from utils import * 
from CopperItemContainer import CopperItemContainer 
from LayersItem import LayersItem
from Net import Net 

class ViaBase():#QGraphicsItem):
    def __init__(self, outerDiameter, innerDiameter, clearance, **kwargs):#,parent=None):
        # print('VIABASE.KWARGS:', kwargs)
        super().__init__(**kwargs)#parent) 
        # super().__init__(parent=parent) TypeError: NO BAD no keywords use positional: LayersContainer.__init__() got an unexpected keyword argument 'parent' # IDK why this happens-- could not replicate in simple example. Something about QGraphicsItem preferring positional args. But sometimes it can take kwargs. I always put classes, which inherit QGI, LAST, in the inheritance, because super() cannot propagate correctly after it hits QGI.
        
        self._pen = Qt.NoPen 
        self._brush = Qt.NoBrush
        self._outerDiameter = outerDiameter 
        self._innerDiameter = innerDiameter 
        self._clearance = clearance

        self._boundingRect = QRectF(-(outerDiameter+clearance)/2 , -(outerDiameter+clearance)/2 , outerDiameter+clearance , outerDiameter+clearance) # Must include clearance in BR so we can redraw the clearance w/o artifacts.

    def boundingRect(self):
        return self._boundingRect 

    # def paint(self, painter, option, widget):
    #     pass 
    
    def shape(self): # Note that shape, .bR, are GOING to be reimplementing QGI.shape,.bR once ViaBase is inherited by Via, ViaItem. (Good, bad) practice? 
        path = QPainterPath()
        path.addEllipse(QPoint(),  self.outerRadius(), self.outerRadius() ) # This doesnt account for clearance, and it doesnt need to, but bR needs to
        return path 
        
    def outerDiameter(self):
        return self._outerDiameter 
    def innerDiameter(self):
        return self._innerDiameter 

    def outerRadius(self):
        return self._outerDiameter/2
    def innerRadius(self):
        return self._innerDiameter/2
    
    def clearance(self):
        return self._clearance
            
# class ViaItem(CopperItem, ViaBase):
class ViaItem(LayerItem, ViaBase, QGraphicsItem):
        # def QGI.__init__(self, parent: PySide6.QtWidgets.QGraphicsItem | None= ...) -> None: ...
    def __init__(self, layer, outerDiameter, innerDiameter, clearance, color , parent):
        # super().__init__(outerDiameter=outerDiameter, innerDiameter=innerDiameter, clearance=clearance, parent=parent)
        super().__init__( layer, outerDiameter=outerDiameter, innerDiameter=innerDiameter, clearance=clearance, parent=parent) # TypeError: ViaBase.__init__() takes 4 positional arguments but 5 were given
        # QGraphicsItem.__init__(self, parent)
        # print('VIAITEM.LAYER:', self.layer())
        self._color = color
        # self._boundingRect = QRectF(-(outerDiameter+clearance)/2 , -(outerDiameter+clearance)/2 , outerDiameter+clearance , outerDiameter+clearance) # Must include clearance in BR so we can redraw the clearance w/o artifacts.

    # def boundingRect(self): # Belive this covered by super
    #     return self._boundingRect
    
    def paint(self, painter, option, widget): # QGraphicsItem.paint reimplementation to draw the aspects of a via: a clearance indicator and some colored circles
        #DrawClearance
        painter.setPen(QPen(self._color, 0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(), self.clearance()/2, self.clearance()/2)
        #DrawVia
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._color, bs=Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(QPoint(0,0), self.outerDiameter()/2 , self.outerDiameter()/2)
        painter.setBrush(QColor(230,230,230)) # Gray
        painter.drawEllipse(QPoint(0,0), self.innerDiameter()/2+Utils.viaPlatingThickness , self.innerDiameter()/2+Utils.viaPlatingThickness)
        painter.setBrush(QColor(255,215,0)) # Gold
        painter.drawEllipse(QPoint(0,0), self.innerDiameter()/2, self.innerDiameter()/2)


# class Via(LayersContainer, ViaBase): # A Via is made up of several childItem viaItems, one viaItem per layer. 
class Via(ViaBase, CopperItemContainer, QGraphicsItem):
    
    def __init__(self,  outerDiameter, innerDiameter, clearance=Utils.viaClearance, layers=Utils.CopperLayers, net=Net()): # layers : A via may exist on all or some layers, default all # clearance: default 1mm
        # print('VIA.MRO:', Via.mro())
        super().__init__(outerDiameter=outerDiameter, innerDiameter=innerDiameter, clearance=clearance, layers = layers)

        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)# | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)  # Cannot set QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges flag in LayersItem, I think bc QGI has not been instantiated by that point 
        
        # print('VIA.LAYERS():', self.layers())
        for layer in self.layers():
            # print('LAYER:', layer)
            ViaItem(layer, outerDiameter, innerDiameter, clearance, Utils.layerColors[layer], self)
            # self.copperItems()[layer].append(item) Phasing out# Track ViaItem as copperItems ( is this necessary? )

        self._netItem = QGraphicsSimpleTextItem(self)
        self._netItem.setZValue(2) # Above 0 and 1 
        self._netItem.setBrush(QColor(0, 0, 0, 100) ) #pale black text
        self.setNet(net)

    def nearestSceneSnap(self, pos): # Via only has one snap; center. But since TraceItem has two snaps, all items need this method to maintain consistent API.
        return self.scenePos()
    
    # def mouseMoveEvent(self, event):
    #     super().mouseMoveEvent(event)
    #     self.setSceneTerminal()
        
    def mouseReleaseEvent(self, event):
        print('VIA.MRE')
        if ( self.net() == None ) and (self.resolvedNet != 'unresolved'): # None nets take on other nets upon mouseRelease
            self.setNet(self.resolvedNet)
        super().mouseReleaseEvent(event) 
        
    def mousePressEvent(self, event): 
        print('VIA.MPE')
        self._offset = event.scenePos() - self.scenePos()
        
    def mouseMoveEvent(self, event): 
        print('VIA.MME')
        pos = Utils.snapToGrid(event.scenePos() - self._offset , 20)
        self.tentativeMove(pos) 

    def tentativeMove(self, pos): # Move here but move back if there are obstructions 
        self._previousPos = self.scenePos()  # Save the previous position 
        self.setPos(pos) # Move to proposed position
        nets = self.netsBeneath()  # Accumulate list of all nets beneath this item. # Are there net conflicts, if so, we do NOT want to move here. Did a None net collide with another net? If so, None net joins to other net 
        self.resolvedNet = self.resolveNets(nets) # resolve nets into one net if possible, ex 'GND' or None. Else set net 'unresolved'
        print('RESOLVEDNET:', self.resolvedNet)
        print('SELF.NET:', self.net())
        
        if (self.resolvedNet == 'unresolved'): # Then revert
            self.setPos(self._previousPos) 
        
        elif ( (self.net() is not None) and (self.net() != self.resolvedNet ) ) : # If nets do not match, then revert
            self.setPos(self._previousPos)

        else: # If we're staying here:
            self.setSceneTerminal()
            

    def netsBeneath(self): # Return list of all nets beneath this item 
        netsBeneath = set([self.net()])
        for item in self.scene().items(): 
            if not isinstance(item, LayersItem): 
                continue 
            if self.collidesWithItem(item): 
                netsBeneath.add(item.net())
        return netsBeneath
    
    def resolveNets(self, nets): # Return True if a net is resolvable from given list of nets 
        nonNoneNets = [net for net in nets if net != None] 
        
        if len(nonNoneNets) == 0: # Then net was None, which is allowed
            return None 
              
        elif len(nonNoneNets) == 1: 
            if (self.net() is not None) and (self.net() != nonNoneNets[0]): # 
                return 'unresolved'
            else: 
                return nonNoneNets[0] 
            
        elif len(nonNoneNets) >1 : 
            return 'unresolved'

    def net(self):
        return self._net 
    def setNet(self, net):
        # Note pad net is determined by the schematic connections. Via,Trace, net is determined by pads
        self._net = net
        self._netItem.setText(str(self._net)) # str(None) -> None 
    def sceneTerminal(self): 
        return self.scenePos()
    def setSceneTerminal(self):
        self._sceneTerminal = self.scenePos()
        
    def sceneTerminals(self):
        return self._sceneTerminals
    def setSceneTerminals(self):
        self.setSceneTerminal()
        self._sceneTerminals = [self.sceneTerminal()]
    def boundingRect(self):
        return self.childrenBoundingRect() or QRectF()
    def paint(self, painter, option, widget):
        pass# ChildrenItems will paint themselves