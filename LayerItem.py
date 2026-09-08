# LIs have no electrical connectivity, & include silkscreen, courtyard, mask & do not go in rtree

from utils import * 

class LayerItem(): 
    """Items which have just one layer. Always childItems of Via, Trace, Zone, Pad, Footprint"""
    def __init__(self, layer, net = None, *args, **kwargs): 
        super().__init__( *args, **kwargs)
    
        self.setLayer(layer)
        self._net = net
        
    def sceneBounds(self):

        rect =self.mapToScene(self.boundingRect()).boundingRect()
        return ( rect.left() , rect.top() , rect.right() , rect.bottom() )


    def sceneBufferedBounds(self): 
        # rect =self.mapToScene(self.boundingRect()).adjusted(-)
        pass
        
    def connectedNets(self): 
        self._connectedNets = [self.net()] 
        # r = proposedShape.boundingRect()
        # proposedBounds = (r.left() , r.top() , r.right() , r.bottom())
        hitIds = self.scene().rtrees[self.layer()].intersection(self.sceneBounds())
        # hitIds = self.scene().rtrees[self.layer()].intersection(proposedBounds)
        hitItems = [self.scene().ids[hitId] for hitId in hitIds]
        for hitItem in hitItems: 
            if self.collidesWithItem(hitItem):
                self._connectedNets.append(hitItem.net())
        
        return self._connectedNets
            

    def insertIntoRtree(self): 
        self.scene().rtrees[self.layer()].insert(self.id() , self.sceneBufferedBounds())

            

    def net(self):
        return self._net 
    def setNet(self, net): 
        self._net = net 
        
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


class LayerSimpleTextItem(LayerItem, QGraphicsSimpleTextItem): 
    def __init__(self, layer, text=None, *args, **kwargs):
        super().__init__(layer, *args, **kwargs)
        self.setLayer(layer)
        self.setText(text)
        self.setBrush(self._color)
        
class LayerRectItem(LayerItem, QGraphicsRectItem ): 
    def __init__(self, layer, *args, **kwargs):
        super().__init__(layer, *args, **kwargs)
        self.setLayer(layer)
        self.setPen(QPen(self._color, 0))

class LayerEllipseItem(LayerItem, QGraphicsEllipseItem): 
    def __init__(self, layer, *args, **kwargs):
        super().__init__(layer, *args, **kwargs)
        self.setLayer(layer)
        self.setPen(QPen(self._color, 0))

# class LayerPathItem(LayerItem, QGraphicsPathItem): 
#     def __init__(self, layer, *args, **kwargs):
#         super().__init__(layer, *args, **kwargs)
#         self.setLayer(layer)
        # self.setPen(QPen(self._color, 0))

class LayerLineItem(LayerItem, QGraphicsLineItem): 
    def __init__(self, layer, *args, **kwargs):
        super().__init__( layer, *args, **kwargs )
        self.setLayer(layer)
        self.setPen(QPen(self._color, 0))
        
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

