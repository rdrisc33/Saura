# LIs have no electrical connectivity, & include silkscreen, courtyard, mask & do not go in rtree

from utils import * 
from LayersItem import LayersItem 

class NonConnectivityItem(LayersItem): 
    """Items which have no connectivity. Do not go in rtree."""
    def __init__(self, layers, net = None, *args, **kwargs): 
        super().__init__( *args, **kwargs)
    
        self.setLayers(layers)
        # self._net = net
    
    def showLayer(self, layer): 
        print('SHOWLAYER')
        if self.layer() == layer: 
            
            self.show()
            self.setZValue(1)
        else: 
            self.setZValue(0)

    def hideLayer(self, layer):
        print('HIDELAYER')
        if self.layer() == layer: 
            self.hide() 
            self.setZValue(0)

    def layer(self):
        return self._layer
    def setLayer(self, layer):
        self._layer = layer
        self._color = Utils.layerColors[layer]
        
    # def sceneBounds(self):

    #     rect =self.mapToScene(self.boundingRect()).boundingRect()
    #     return ( rect.left() , rect.top() , rect.right() , rect.bottom() )

    # def sceneBufferedBounds(self): 
    #     # rect =self.mapToScene(self.boundingRect()).adjusted(-)
    #     pass
        
    # def connectedNets(self): 
    #     self._connectedNets = [self.net()] 
    #     # r = proposedShape.boundingRect()
    #     # proposedBounds = (r.left() , r.top() , r.right() , r.bottom())
    #     hitIds = self.scene().rtrees[self.layer()].intersection(self.sceneBounds())
    #     # hitIds = self.scene().rtrees[self.layer()].intersection(proposedBounds)
    #     hitItems = [self.scene().ids[hitId] for hitId in hitIds]
    #     for hitItem in hitItems: 
    #         if self.collidesWithItem(hitItem):
    #             self._connectedNets.append(hitItem.net())
        
    #     return self._connectedNets
            
    # def insertIntoRtree(self): 
    #     self.scene().rtrees[self.layer()].insert(self.id() , self.sceneBufferedBounds())

    # def net(self):
    #     return self._net 
    # def setNet(self, net): 
    #     self._net = net 
        

# # QGraphcisItems that have no connectivity, yet is on a layer, example shapes on the 'edge cuts' or 'Fab' layers. Note distinction between LayersRectItem, which DOES have connectivity
# class NonConnectivityRectItem(NonConnectivityItem, QGraphicsRectItem ): 
#     def __init__(self, layer, *args, **kwargs):
#         super().__init__(layer, *args, **kwargs)
#         self.setLayer(layer)
#         self.setPen(QPen(self._color, 0))

# class NonConnectivityEllipseItem(NonConnectivityItem, QGraphicsEllipseItem): 
#     def __init__(self, layer, *args, **kwargs):
#         super().__init__(layer, *args, **kwargs)
#         self.setLayer(layer)
#         self.setPen(QPen(self._color, 0))

# class NonConnectivityLineItem(NonConnectivityItem, QGraphicsLineItem): 
#     def __init__(self, layer, *args, **kwargs):
#         super().__init__( layer, *args, **kwargs )
#         self.setLayer(layer)
#         self.setPen(QPen(self._color, 0))
        
# class NonConnectivitySimpleTextItem(NonConnectivityItem, QGraphicsSimpleTextItem): 
#     def __init__(self, layer, text=None, *args, **kwargs):
#         super().__init__(layer, *args, **kwargs)
#         self.setLayer(layer)
#         self.setText(text)
#         self.setBrush(self._color)
        

# class LayerPathItem(LayerItem, QGraphicsPathItem): 
#     def __init__(self, layer, *args, **kwargs):
#         super().__init__(layer, *args, **kwargs)
#         self.setLayer(layer)
        # self.setPen(QPen(self._color, 0))
        
# class LayerPixmapItem(LayerItem, QGraphicsPixmapItem): 
#     def __init__(self, layer, *args, **kwargs):
#         super().__init__(layer, *args, **kwargs)
#         self.setLayer(layer)
        # self.setPen(QPen(self._color, 0))

# class LayerPolygonItem(LayerItem, QGraphicsPolygonItem): 
#     def __init__(self, layer, *args, **kwargs):
#         super().__init__(layer, *args, **kwargs)
#         self.setLayer(layer)
        # self.setPen(QPen(self._color, 0))



class NonConnectivityItem(LayersItem): # Drawn items are drawn by the user, Ex a rectangle, a line, a text box. DrawnItems are selectable.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    
class NonConnectivityLineItem(NonConnectivityItem , QGraphicsLineItem): # Note understanding of Inheritance needed here. Cant inherit QGraphicsItem twice, thus it has to come from LayerLineItem, which means LayerLineItem must go LAST else when .setFlags called, QGI hasn't been init'd yet and will get error
    def __init__(self, layers, *args, **kwargs):
        super().__init__( layers, *args, **kwargs )

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

