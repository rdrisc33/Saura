from utils import * 

from shapely.ops import polylabel # polylabel aka pointOfInaccessibility aka centroid of freaky polygons 
from shapely.geometry import Polygon

class ZoneItem( CopperItemContainer, QGraphicsPathItem):
    def __init__(self, layer, *args, **kwargs ):
        super().__init__(layer, *args, **kwargs)
        self.setPen(QPen(self._color, 0))
        self.setBrush(QBrush(self._color, bs=Qt.BrushStyle.FDiagPattern))

        self._centroid = None
        self._layer = None 
        
    def layer(self):
        return self._layer
    def setLayer(self, layer):
        self._layer = layer
        
    def setCentroid(self): # Freaky shaped polygons may have traditional centroid outside themselves. What I want is the 'Point of Inaccessibility', the point inside the pgon furthest from any boundary. On a map, the POI is a good place to anchor a label, and the algo for POI is called 'polylabel' as in polygon label. 
        self._centroid = self.pointOfInaccessibility()
        
    def pointOfInaccessibility(self):
        polygon = Polygon( [ [point.x() , point.y()] for point in self])
        self._centroid = polylabel(Polygon(polygon))


    def terminals(self):
        # terminal = Centroid of zone which is within the part ?
        return [self.centroid()]
    
    def terminal(self):
        return self.centroid()
    
    def shape(self):
        print('ZONEITEM.SHAPE nyi')
        # pass
        # path = QPainterPath()
        # path.moveTo(self.item)
        # for point in self.polygon:
            

# A Qt plugin for node editing pollygons? 


from PySide6.QtGui import * 
# from PySide6.QtCore import * 
# from PySide6.QtWidgets import * 
# import sys 
# app = QApplication(sys.argv)
# x = QGraphicsPolygonItem([QPointF(0,0), QPointF(100,200)]) # PolygonItem can be a line # in Qt, one polygon cannot hold multiple polygons, 'holes', which most mapping softwares do. Technically Qt is right, a polygon is not two+ polygons...

# print(x.polygon().value(0))
# print(x.polygon().pop_back())
# print(x.polygon().push_back(QPoint(50,200)))
# print(x.polygon().toList())
# print(x.polygon().isEmpty())
# print(x.polygon().last())
# print(x.polygon().isClosed())
# scene = QGraphicsScene() 
# scene.addItem(x)
# view=  QGraphicsView()
# view.setScene(scene)
# view.show()
# sys.exit(app.exec())