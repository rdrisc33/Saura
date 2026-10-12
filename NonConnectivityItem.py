# LIs have no electrical connectivity, & include silkscreen, courtyard, mask & do not go in rtree

from utils import * 
from LayersItem import LayersItem 

class NonConnectivityItem(LayersItem): 
    """Items which have no connectivity. Do not go in rtree. Ex a courtyard rectangle, a courtyard path, a textbox."""
    def __init__(self, layers, *args, **kwargs): 
        super().__init__(layers, *args, **kwargs)

        # self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        
    
class NonConnectivityLineItem(NonConnectivityItem , QGraphicsLineItem): # Note understanding of Inheritance needed here. Cant inherit QGraphicsItem twice, thus it has to come from LayerLineItem, which means LayerLineItem must go LAST else when .setFlags called, QGI hasn't been init'd yet and will get error
    def __init__(self, layers, *args, **kwargs):
        super().__init__( layers, *args, **kwargs )
        print(f'NONCONNECTIVITYLINEITEM LAYERS={layers}')

class NonConnectivityRectItem(NonConnectivityItem, QGraphicsRectItem): 
    def __init__(self, layers, lineWidth,*args, **kwargs):
        super().__init__( layers, *args, **kwargs )
        self.lineWidth = lineWidth
        self.setPen(QPen(self._color , self.lineWidth))

    def shape(self): 
        path = QPainterPath() 
        path.addRect(self.boundingRect())
        
        return path
        
class NonConnectivityEllipseItem(NonConnectivityItem, QGraphicsEllipseItem): 
    def __init__(self, layers, *args, **kwargs):
        super().__init__( layers, *args, **kwargs )



