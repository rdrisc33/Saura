from utils import * 
from ConnectivityItem import ConnectivityItem 
from NonConnectivityItem import NonConnectivityItem
from LayersItem import LayersItem

from Net import Net 
# When using painter.drawEllipse(), there is an int overload, and a float overload, and Qt will choose which one to use based on whether its passed a QPoint or a QPointF so be sure to use QPointF! 
class Via(ConnectivityItem, QGraphicsItem):
    def __init__(self, outerDiameter, innerDiameter, clearance=Utils.viaClearance, layers=Utils.copperLayers, net=Net(),parent=None):# layers : A via may exist on all or some layers, default all # clearance: default 1mm
        
        super().__init__(layers = layers)
        
        self._pen = Qt.NoPen
        self._brush = Qt.NoBrush
        self._color = Qt.black # Won't know color until add to scene, & see what activeLayer is set 
        self._color = Utils.layerColors[self.layers()[0]]
        
        
        self._outerDiameter = outerDiameter
        self._innerDiameter = innerDiameter
        self._clearance = clearance

        self._boundingRect = QRectF(-(self.outerRadius()+clearance), -(self.outerRadius()+clearance) , self.outerDiameter()+clearance*2 , self.outerDiameter()+clearance*2) # Must include clearance in BR so we can redraw the clearance w/o artifacts.


        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)# | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)  # Cannot set QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges flag in LayersItem, I think bc QGI has not been instantiated by that point 

        self._netItem = QGraphicsSimpleTextItem(self)
        self._netItem.setZValue(2) # Above 0 and 1 
        self._netItem.setBrush(QColor(0, 0, 0, 100) ) #pale black text
        self.setNet(net)

    def boundingRect(self):
        print('VIA.BOUNDINGRECT:', self._boundingRect)
        return self._boundingRect 
        
    def paint(self, painter, option, widget): # QGraphicsItem.paint reimplementation to draw the aspects of a via: a clearance indicator and some colored circles. Be sure to use QRectFs, or, all values will be cast to int
        #DrawClearance
        painter.setPen(QPen(QColor(self._color).lighter(150), 0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0,0), self.outerRadius()+ self.clearance(), self.outerRadius()+self.clearance())
        #DrawOuter
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._color, bs=Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(QPointF(0,0), self.outerRadius() , self.outerRadius())
        # DrawAesthetic
        painter.setBrush(QColor(230,230,230)) # Gray
        painter.drawEllipse(QPointF(0,0), self.innerRadius()+Utils.viaPlatingThickness , self.innerRadius()+Utils.viaPlatingThickness)
        # DrawInner
        painter.setBrush(QColor(255,215,0)) # Gold
        painter.drawEllipse(QPointF(0,0), self.innerRadius(), self.innerRadius())
        
    def shape(self): 
        path = QPainterPath()
        path.addEllipse(QPointF(),  self.outerRadius()+ self.clearance(), self.outerRadius() + self.clearance() ) 
        return path 

    def setColor(self, color): 
        self._color = color
        self.update() # Schedules a redraw of the area covered by rect in this item. You can call this function whenever your item needs to be redrawn, such as if it changes appearance or size.

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

    def nearestSceneSnap(self, pos): # Via only has one snap; center. But since TraceItem has two snaps, all items need this method to maintain consistent API.
        return self.scenePos()

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