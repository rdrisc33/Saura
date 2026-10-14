from utils import * 

# class CourtyardItem(QGraphicsPathItem):
#     def __init__(self, layer, parent, path=None,  *args, **kwargs ):
#         super().__init__( path, parent, *args, **kwargs )
#         self._layer = layer
#         # self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        
#     def paint(self, painter, option, widget):
#         redAlpha = QColor(255, 0, 0, 65) # transparent red 
#         painter.setPen(QPen(Qt.black, 0))
#         if self.parentItem():
#             painter.setBrush(redAlpha if self.collidingCourtyardItems() else Qt.NoBrush)
#         super().paint(painter,option,widget)

class CourtyardItem(QGraphicsPathItem):
    def __init__(self, layer, parent, path=None,  *args, **kwargs ):
        super().__init__( path, parent, *args, **kwargs )
        self.setPen(QPen(Qt.black, 0))
        