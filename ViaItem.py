# from utils import * 


# class ViaItem(CopperItemContainer, QGraphicsItem):
#     def __init__(self, outerDiameter, innerDiameter, layer, parent=None):
#         super().__init__(layer=layer , parent=parent) 
    
#         self._boundingRect = QRectF(-outerDiameter/2 , -outerDiameter/2, outerDiameter , outerDiameter) 
#         self._outerDiameter = outerDiameter 
#         self._innerDiameter = innerDiameter 
        
        
#     def terminal(self): # Via has only one terminal, its origin # Center must be at origin; shape must be symmetric about origin. While that is the case, .scenePos() will be the center
#         return self.scenePos()
    
#     def setTerminals(self):
#         self._terminals = [self.scenePos()]

#     def boundingRect(self): 
#         return self._boundingRect

#     def paint(self, painter, option, widget):
#         painter.setPen(Qt.NoPen)
#         painter.setBrush(self._color)
#         painter.drawEllipse(QPoint(0,0), self.outerDiameter()/2 , self.outerDiameter()/2)
#         painter.setBrush(QColor(230,230,230)) # Gray
#         painter.drawEllipse(QPoint(0,0), self.innerDiameter()/2+Utils.viaPlatingThickness , self.innerDiameter()/2+Utils.viaPlatingThickness)
#         painter.setBrush(QColor(255,215,0)) # Gold
#         painter.drawEllipse(QPoint(0,0), self.innerDiameter()/2, self.innerDiameter()/2)

#     def outerDiameter(self):
#         return self._outerDiameter 
#     def innerDiameter(self):
#         return self._innerDiameter 

#     def shape(self):
#         path = QPainterPath()
#         path.addEllipse(QPoint(),  self.outerRadius, self.outerRadius )
#         return path 
    
#     def snap(self, seeker, net):
#         # if (self.net == None) and (net == None): 
#         print('VIAITEM.SNAP')
            
#         if self.net == net or (self.net == None) or (net == None):
#             if self.collidesWithItem(seeker): 
#                 seeker.setPos(self.via_item.scenePos())
#             if self.net == None: 
#                 self.net = net 
#             elif net == None: 
#                 net = self.net
                



    
#     # def calculate_buffer(self): 
#     #     stroker = QPainterPathStroker()
#     #     stroker.setWidth(self.scene().trace_width)
#     #     stroker.setJoinStyle(Qt.BevelJoin) 
#     #     stroker.setCapStyle(Qt.FlatCap)
        
#     #     path = self.to_path() # self.item better be a QGraphicsPathItem to use .path()
#     #     strokerPath = stroker.createStroke(path)
#     #     expandedPath = path.united(strokerPath) #Unite the fillable areas of the paths into one consolidated path
#     #     self.buffer = QGraphicsPolygonItem( expandedPath.toFillPolygon() ) # convert to a QPolygonF then to a QGPolygonItem.
    
    
