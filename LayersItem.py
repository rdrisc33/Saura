from PySide6.QtWidgets import * 
from PySide6.QtCore import *
from PySide6.QtGui import * 

from utils import LayerItem

class LayersItem(): 
    def __init__(self, layers, *args, **kwargs):
        # print('BOARDITEM.KWARGS:', kwargs)
        # print('BOARDITEM.ARGS:', args)
        super().__init__(*args, **kwargs) 

        
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges) # Must enable to receive item position changes. 
        # self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges) setting this flag in LayersItem has no effect, I think bc QGI comes after in MRO
        self._net                   = None 
        self._layers                = layers
        self._connectedNets         = []
        # print('LAYERS:', layers)
        self._terminals             = None 
        self._nonNoneNets           = None 
        self._sceneTerminal         = None      # 3-Tuple (scenePosX,scenePosY,layer) 
        self._sceneTerminals        = None      # self.terminals are point(s) on a pad, via, which are connectable. Ex TraceItem self.terminals are p1,p1. Via self.terminals are center aka origin, pad self.terminals are pad origin(NOT necessarily pad centroid, think solder bridge pads), and Footprint self.terminals are pads/vias contained in the footprint
        self._buffer                = None      # QGraphicsPolygonItem representing item's shape, buffered by (mostLikely) scene.tracewidth
        self._sceneBuffer           = None      # A QPolygonF(?) representing item's shape, buffered by .bufferDistance(), in scene coordinates 
        self._bounds                = None      # A 4-tuple(left top right bottom). unbuffered. used by ... ?
        self._sceneBounds           = None      # A 4-tuple(left top right bottom), buffered by .bufferDistance(). Used in the rtree
        # self._bufferedBounds        = None    This never used. Only sceneBufferedBounds is used, in rtree  # A 4-tuple(left top right bottom) buffered by .bufferDistance(). local coordinates 
        self._sceneBufferedBounds   = None      # ._bufferedBounds in scene coordinates
        self._id                    = None 
        self._net                   = None 
        
        
    # def connectedNets(self, proposedShape): 
    #     self._connectedNets = [self.net()]
    #     for child in self.childItems(): 
    #         self._connectedNets.extend(child.connectedNets(proposedShape))

    def mousePressEvent(self, event): 
        self._offset = self.scenePos() - event.scenePos()

    def mouseMoveEvent(self, event): 
        if (event.buttons() & Qt.MouseButton.LeftButton ) and (self.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable): # Only move if the item is selectable, and the mouse left button is clicked. https://github.com/qt/qtbase/blob/dev/src/widgets/graphicsview/qgraphicsitem.cpp if ((event->buttons() & Qt::LeftButton) && (flags() & ItemIsMovable)) {
            print('LAYERSITEM.MOUSEMOVEEVENT')
            self._previousPos = self.scenePos()     #Save the previous position
            self._previousNet = self.net()          #Save the previous net 

            self.setPos(self.scene().snapToGrid(event.scenePos() + self._offset))
            nets = self.nets() 
            self.resolveNets(nets)
            if self.net() == 'unresolved': 
                self.setPos(self._previousPos)
                self.setNet(self._previousNet)
        else: 
            event.ignore() # This seems to do nothing 
        

    def nets(self): # collects the net of any items which collide with this item.
        nets = set( [self.net()] ) 
        
        hitIds = [] 
        hitItems = [] 
        print('SELF.SCENEBOUNDS:', self.sceneBounds())
        if not self.sceneBounds(): 
            self.setSceneBounds
        for layer in self.layers(): 
            
            hitIds.extend( self.scene().rtrees[layer].intersection(self.sceneBounds() ) ) 
        hitItems = [self.scene().ids[hitId] for hitId in hitIds]
        
        for item in hitItems: 
            if self.collidesWithItem(item):
                nets.add(item.net())
        return nets 
            

    # def resolveNets(self, nets ): # Given list of nets, return resolved net as a string, or 'unresolved' if unresolvable, or None if there are no nets 
    #     nonNoneNets = [net for net in nets if net is not None ]

    #     if len(nonNoneNets) == 0: 
    #         self.setNet(None) 
    #     if len(nonNoneNets) == 1: 
    #         self.setNet(nonNoneNets[0])
    #     elif len(nonNoneNets) > 1: 
    #         self.setNet('unresolved')

    # def mouseMoveEvent(self, event): 
    #     super().mouseMoveEvent( event)

    # def itemChange(self, change, value): 
    #     # TODO: Confirm that ItemPositionChanges sends changes when sceneChanges
    #     if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange: # If the item position has changed, we will check to see if there is a net conflict, and we will NOT MOVE HERE if there is one
    #         print()
    #         newPos = value # The value arguement is the new position, a QPointF 
    #         delta = newPos - self.pos() 
    #         print('DELTA:', delta) 
            
    #         proposedPath = self.mapToScene(self.shape().translated(delta)) 
    #         print('PROPOSEDPATH:', proposedPath)
    #         collidingNets = self.scene().collidingNets(self.layers(), path = proposedPath) # 
    #         print('COLLIDINGNETS:', collidingNets) 
    #         self.resolveNets(collidingNets)
    #         print('SELF.NET:', self.net())

    #         if self.net() == 'unresolved':
    #             # do NOT move the item here / fill item background red w/alpha.5
    #             print('DO NOT MOVE THE ITEM HERE') # We accomplish this by returning item's current .pos(), rather than the proposed newPos
    #             return super().itemChange(change, self.pos())
                
    #         elif self.net() != 'unresolved' : # None or '3V3' for example.  
    #             # DO move the item here...  ONly not that simple. While a Via may simply move its child Items, a trace complicatedly moves its childITems, and two other lines, in specific ways ... Focus on vias for now        
    #             return super().itemChange(change, newPos)            

    #     return super().itemChange( change, value) # handle all other changes 

    def showLayer(self, layer): 
        for childItem in self.childItems(): 
            if not isinstance(childItem, LayerItem): 
                continue 
            if childItem.layer() == layer: 
                childItem.show()
                childItem.setZValue(1)
                
        return None 
    def showLayers(self, layer):
        return None 
    def hideLayer(self, layer): 
        return None 
    def hideLayers(self, layers):
        return None 

    def insertIntoRtree(self): 
        return None 

    def removeFromRtree(self):
        return None        

    # def connectedNets(self): 
    #     return self._connectedNets 
    def nonNoneNets(self):
        return None 
    def connectsToItem(self, other): # -> True if self is connected to other. Connected as in electrically connected.
        return None 
    def updateRtree(self):
        return None 
    def updateRtrees(self):
        return None 
    def insertIntoRtrees(self):
        return None 
    def removeFromRtrees(self): 
        return None 
    def containsTerminal(self, terminal): 
        return None 
    def setShowingLayers(self, layers): 
        return None 
    
    def net(self):
        return self._net     
    def setNet(self, net):
        self._net = net 
                
    def setBufferDistance(self, bufferDistance):
        self._bufferDistance = bufferDistance
        
    def layer(self): 
        # print('SELF:', self)
        return self._layer
    
    def setLayer(self, layer):
        self._layer = layer        
        
    def layers(self):
        return self._layers
    def setLayers(self, layers):
        self._layers = layers 
        
    def id(self):
        return self._id 
    def setId(self, id):
        self._id = id 
    def bounds(self): 
        return self._bounds 
    def setBounds(self): # UNBUFFERED bounds. Local position. Used for .... ? 
        return None 
    def sceneBounds(self):
        return self._sceneBounds 
    def setSceneBounds(self):
        return None 
        # r = self.boundingRect() mapped to scene 
        
        # return ( r.left(), r.top(), r.right() , r.bottom() ) 
    def buffer(self):
        return self._buffer
    def setBuffer(self):#, bufferDistance = None): 
        return None 
    def sceneBuffer(self):
        return self._sceneBuffer
    def setSceneBuffer(self):
        return None 
    # def bufferedBounds(self):
    #     return self._bufferedBounds  
    def setBufferedBounds(self):#, self._bufferDistance=None): # calulate and set new bounds. Bounds describes a bounding rectangle around a shape, in the form of a 4-tuple (xmin ymin xmax ymax), aka (left top right bottom). Bounds is borrowed from how the the python modules Shapely/rtree use bounds; bounds is not from Qt. calculate_bufferedBounds returns the bounds, buffered by self._bufferDistance(most likely = currently selected scene.traceWidth()). The bounds 4-tuple is used bt the rtree module to describe rectangles. Note that, because Qt considers pen_width in .boundingRect, I have to manually set a 0 width pen away from the default width-of-1 pen, else the buffered bounds will be .5 wider than supposed to.
        return None 
    def sceneBufferedBounds(self):
        return self._sceneBufferedBounds 
    def setSceneBufferedBounds(self):
        return None 
    def setConnectedNets(self):
        return None 
    def addLayer(self, layer):
        return None        
    def removeLayer(self, layer):
        return None          
    # def copperLayers(self):
    #     return None        
    # def copperItems(self):
    #     return None
    # def setCopperItems(self,copperItems):
    #     return None
    # def addCopperItem(self, layer, copperItem):
    #     return None    
    # def removeCopperItem(self, layer, copperItem):
    #     return None       

# Excepting seeker and ratsnest lines, all LayerItems have layers. 

class LayersSimpleTextItem(LayersItem, QGraphicsSimpleTextItem): 
    def __init__(self, layers , text=None, *args, **kwargs):
        super().__init__(layers, *args, **kwargs)
        self.setLayers(layers)
        self.setText(text)
        
class LayersRectItem(LayersItem, QGraphicsRectItem ): 
    def __init__(self, layers, *args, **kwargs):
        super().__init__(layers, *args, **kwargs)
        self.setLayers(layers)

class LayersEllipseItem(LayersItem, QGraphicsEllipseItem): 
    def __init__(self, layers, *args, **kwargs):
        super().__init__(layers, *args, **kwargs)
        self.setLayers(layers)

class LayersPathItem(LayersItem, QGraphicsPathItem): 
    def __init__(self, layers, *args, **kwargs):
        super().__init__(layers, *args, **kwargs)
        self.setLayers(layers)

class LayersLineItem(LayersItem, QGraphicsLineItem): 
    def __init__(self, layers, *args, **kwargs):
        super().__init__( layers, *args, **kwargs )
        self.setLayers(layers)

class LayersPixmapItem(LayersItem, QGraphicsPixmapItem): 
    def __init__(self, layers, *args, **kwargs):
        super().__init__(layers, *args, **kwargs)
        self.setLayers(layers)

class LayersPolygonItem(LayersItem, QGraphicsPolygonItem): 
    def __init__(self, layers, *args, **kwargs):
        super().__init__(layers, *args, **kwargs)
        self.setLayers(layers)

