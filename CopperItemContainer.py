from utils import * 
from LayersItem import * 

class CopperItemContainer(LayersItem): # Base class of FP TR ZN VA PD classes. Not useful by itself
    def __init__(self, layers, *args, **kwargs):
        # print('CUIC.LAYERS:', layers)
        # print('CUIC.ARGS:', args)
        # print('CUIC.KWARGS:', kwargs)
        super().__init__(layers, *args, **kwargs)
        # print('COPPERITEMCONTAINER.INIT')
        # self._layer                 = None    Moved to BoardItem
        # self._layers                = layers  Moved to BoardItem
        # self._layerItems            = defaultdict(list) # { 'F.Cu': LineItem} Phasing out
        self._terminals             = None 
        self._nonNoneNets           = None 
        self._sceneTerminal         = None      # 3-Tuple (scenePosX,scenePosY,layer) 
        self._sceneTerminals        = None      # self.terminals are point(s) on a pad, via, which are connectable. Ex TraceItem self.terminals are p1,p1. Via self.terminals are center aka origin, pad self.terminals are pad origin(NOT necessarily pad centroid, think solder bridge pads), and Footprint self.terminals are pads/vias contained in the footprint
        self._buffer                = None      # QGraphicsPolygonItem representing item's shape, buffered by (mostLikely) scene.tracewidth
        self._sceneBuffer           = None      # A QPolygonF(?) representing item's shape, buffered by .bufferDistance(), in scene coordinates 
        self._bounds                = None      # A 4-tuple(left top right bottom). unbuffered. used by ... ?
        self._sceneBounds           = None      # A 4-tuple(left top right bottom), buffered by .bufferDistance(). Used in the rtree
        self._bufferedBounds        = None      # A 4-tuple(left top right bottom) buffered by .bufferDistance(). local coordinates 
        self._sceneBufferedBounds   = None      # ._bufferedBounds in scene coordinates
        self._id                    = None 
        self._net                   = None 
        # self._copperItems           = phasing out defaultdict(list) # {'F.Cu': [PadItem , ViaItem] , 'Inr_1': [ZoneItem, ... }


    def queryRtrees(self):
        """query MainWindow.rtrees for self.sceneBufferedBounds() at each layer in self.layers """
        # print('self.SceneBufferedBounds():', self.sceneBufferedBounds())
        hitIds = [] 
        for layer in self.layers(): 
            hitIds.extend( self.scene().rtrees[layer].intersection(self.sceneBufferedBounds()) )
        # print(f'HIT {len(hitIds)} ITEMS')
        hitItems = [self.scene().ids[hitId] for hitId in hitIds]
        return hitItems
    
    def showLayer(self, layer): 
        for childItem in self.childItems(): 
            if not isinstance(childItem, LayerItem):
                continue 
            childItem.showLayer(layer)
            
    def hideLayer(self, layer):
        for childItem in self.childItems():
            if not isinstance(childItem, LayerItem):
                continue 
            if childItem.layer() == layer: 
                childItem.hide()
            # childItem.hideLayer(layer)
            
    def insertIntoRtree(self): 
        for layer in self.layers(): 
            self.scene().rtrees[layer].insert(self.id() , self.sceneBufferedBounds())
        # for child in self.childItems(): 
        #     if isinstance(child, LayerItem): 
        #         child.insertIntoRtree()
                
    def net(self):
        return self._net 
    def setNet(self, net):
        self._net = net
      
    def setBufferDistance(self, bufferDistance): # Upon construction, item may not have a scene, thus it cannot know scene.traceWidth aka bufferDistance, thus we must wait until item is added to scene to implement buffer functions. 
        self._bufferDistance = bufferDistance 
        self.setBuffer()
        # print('BUFFER:', self.buffer())
        self.setSceneBuffer() 
        # print('SETSCENEBUFFER')
        self.setBufferedBounds() # Must have bounds to insert into rtree ( Would do this in constructor, except requires bufferWidth, which is taken from scene)
        self.setSceneBufferedBounds()
        
    # def insertIntoRtree(self):
    #     self.scene().rtrees[self.layer()].insert(self.id() , self.sceneBufferedBounds())
        
    def removeFromRtree(self):
        for layer in self.layers(): 
            self.scene().rtrees[layer].delete(self.id() , self.sceneBufferedBounds())
        
    def updateRtree(self): # Update existing entry in rtree
        self.removeFromRtree() # rtree removal demands (id, bounds). Thus we must remove B4 .setSceneBufferedBounds()
        self.setSceneBufferedBounds()
        self.insertIntoRtree()
        
    # def layer(self): # CuICs won't all have just one layer
    #     return self._layer
    # def setLayer(self, layer):
    #     self._layer = layer
        
    def layers(self):
        return self._layers
    def setLayers(self, layers):
        self._layers = layers
        
    def copperLayers(self):
        return [layer for layer in self.layers() if layer in Utils.CopperLayers]
        
    def id(self):
        return self._id 
    def setId(self, id):
        self._id = id
        
    # def mouseMoveEvent(self, event):
    #     print('CUITEM.MOUSEMOVEEVENT:')
    #     self.updateRtree()
    #     self.setSceneBuffer()
    #     self.setTerminals()
    #     self.setSceneBounds()
    #     super().mouseMoveEvent(event)
    
    def bounds(self): 
        return self._bounds
    def setBounds(self): # UNBUFFERED bounds. Local position. Used for .... ? 
        rect =self.boundingRect()
        self._bounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 

    def sceneBounds(self):
        return self._sceneBounds
    def setSceneBounds(self):
        
        rect =self.mapToScene(self.boundingRect()).boundingRect()
        self._sceneBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 
        print('SET SCENE BOUNDS: ', self._sceneBounds)
        
    def buffer(self):
        return self._buffer
    def setBuffer(self):#, bufferDistance = None): 
            
        stroker = QPainterPathStroker()
        stroker.setWidth(self._bufferDistance)
        stroker.setJoinStyle(Qt.BevelJoin) # ry roundJoin for irl
        stroker.setCapStyle(Qt.FlatCap)
        
        path = self.shape() 
        path.closeSubpath() # Often, .shape() -> an unclosed shape
        strokerPath = stroker.createStroke(path)
        expandedPath = path.united(strokerPath) #Unite the fillable areas of the paths into one consolidated path
        self._buffer = expandedPath.toFillPolygon()  # convert to a QPolygonF then to a QGPolygonItem.

    def sceneBuffer(self):
        return self._sceneBuffer
    def setSceneBuffer(self):
        self._sceneBuffer = self.mapToScene(self.buffer())

    def bufferedBounds(self):
        return self._bufferedBounds
    def setBufferedBounds(self):#, self._bufferDistance=None): # calulate and set new bounds. Bounds describes a bounding rectangle around a shape, in the form of a 4-tuple (xmin ymin xmax ymax), aka (left top right bottom). Bounds is borrowed from how the the python modules Shapely/rtree use bounds; bounds is not from Qt. calculate_bufferedBounds returns the bounds, buffered by self._bufferDistance(most likely = currently selected scene.traceWidth()). The bounds 4-tuple is used bt the rtree module to describe rectangles. Note that, because Qt considers pen_width in .boundingRect, I have to manually set a 0 width pen away from the default width-of-1 pen, else the buffered bounds will be .5 wider than supposed to.
        rect = self.boundingRect().adjusted(-self._bufferDistance,-self._bufferDistance, self._bufferDistance,self._bufferDistance)
        self._bufferedBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 
    
    def sceneBufferedBounds(self):
        return self._sceneBufferedBounds
    def setSceneBufferedBounds(self):
        rect = self.mapToScene(self.boundingRect().adjusted(-self._bufferDistance,-self._bufferDistance, self._bufferDistance,self._bufferDistance)).boundingRect() # 
        self._sceneBufferedBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 
        
    def connectsToItem(self, item): # -> True if self is connected to other. Connected as in electrically connected.

        if  isinstance(item, CopperItemContainer): 
            for t in item.sceneTerminals():  # Try cheap check: do terminal exact positions match 
                print("SELF:", self)
                print('SELF.SCENETERMINALS():', self.sceneTerminals())
                if any(t == t2 for t2 in self.sceneTerminals()): 
                    return True 
            for t in item.sceneTerminals(): # Try cheap-ish check: does shape contain termianal
                if self.contains(t): 
                    return True
            if self.collidesWithItem(item): # Try expensive check: do shapes collide at all
                return True 
            else: 
                return False 
            
        # elif isinstance(other, QPoint): # idt this is used
        #     if any( t == other for t in self.terminals() ): # Initial fast check to see if terminals perfectly align
        #         return True 
        #     elif self.contains(other): # (low cost?) check to see if point is within other
        #         return True 
        #     # elif self.collidesWithItem No such thing as cWI for a point
            
        else: 
            print('MW.connectsTo() SOMETHING WRONG ')

    # def connectedNets(self): 
    #     return self._connectedNets
    def nonNoneNets(self):
        return self._nonNoneNets

    def connectedNets(self):
        for child in self.childItems(): 
            self._connectedNets.extend(child.connectedNets())
            
        return self._connectedNets
    # def setConnectedNets(self):
        # self._connectedNets = defaultdict(list)
        # for copperItems in self.copperItems().values(): 
        #     for copperItem in copperItems:
        #         copperItem.setConnectedNets()
        #         for net, items in copperItem.connectedNets():
        #             self._connectedNets[net].extend(items)
        # self._nonNoneNets = [net for net in self._connectedNets if not net is None]
        # print() 
        # print('CUIC.CONNECTEDNETS():', self.connectedNets())
        # print('CUIC.NONNONENETS:', self._nonNoneNets) 
                            
                    # 
    # def updateStuff(self): 
    #     for layer, copperItems in self.copperItems().items(): 
    #         for copperItem in copperItems: 
    #             copperItem.updateStuff()
            
    # def mousePressEvent(self, event): 
    #     self.offset = event.scenePos() - self.scenePos()
    #     super().mousePressEvent(event)
        
    # def mouseMoveEvent(self, event): #QGI.mmE moves all child items, so would call super() for that-- if we didn't need custom snapping behavior. And, still have to update rtrees & sceneBounds & sceneTerminals etc of all descendant Items
    #     # print()
    #     # print('COPPERITEMCONTAINER.MME')
    #     self.setPos(self.scene().snapToGrid(event.scenePos() - self.offset))
        


                
        # super().mouseMoveEvent(event) Do NOT call as we want custom snapToGrid behavior.
        
    # def sceneTerminals(self):#  
    #     return self._sceneTerminals
            
    # def sceneTerminal(self):
    #     return self._sceneTerminal 
    # def setSceneTerminal(self):
    #     self._sceneTerminal = self.scenePos() # (*self.scenePos().toTuple(), self.layer()) # (x, y, layer) 

    # def setSceneTerminals(self): 
        # self._sceneTerminals = []
        # print(f'{self}.COPPERITEMS():', self.copperItems())
        # for layer, copperItems in self.copperItems().items(): 
        #     for copperItem in copperItems :
        #         copperItem.setSceneTerminal()
        #         copperItem.setSceneTerminals()
        #         self._sceneTerminals.append(copperItem.sceneTerminal())
    
    # def layerItems(self): # Moved to FP
    #     return self._layerItems
    # def setLayerItems(self, layerItems): 
    #     self._layerItems = layerItems  
    # def addLayerItem(self, layerItem):
    #     # print()
    #     # print('LAYERITEM:', layerItem)
    #     self.layerItems()[layerItem.layer()].append(layerItem)
    # def removeLayerItem(self, layerItem):
    #     self.layerItems()[layerItem.layer()].remove(layerItem)
        
    # def boundingRect(self):
    #     return self.childrenBoundingRect() or QRectF()
    # def paint(self, painter, option, widget):
    #     pass 
 
# updateRtree()
# setSceneBuffer()
# setTerminals()
# setSceneBounds()  

    def updateRtrees(self):# Update an existing entry in rtree
        self.removeFromRtrees() # rtree removal demands (id, bounds). Thus we must remove B4 .setSceneBufferedBounds()
        self.setSceneBufferedBounds()
        self.insertIntoRtrees()
        
    def insertIntoRtrees(self):
        for layer in self.layers(): 
            self.scene().rtrees[layer].insert(self.id() , self.sceneBufferedBounds())
            
    def removeFromRtrees(self): 
        for layer in self.layers(): 
            self.scene().rtrees[layer].delete(self.id() , self.sceneBufferedBounds())# rtree removal demands (id, bounds). Thus we must remove B4 .setSceneBufferedBounds()
    
    def containsTerminal(self, terminal): # returns true if layers match and terminal pos is contained within shape. terminal: (layer:str, pos:QPoint)
        terminalPos = terminal['pos']
        terminalLayer = terminal['layer']
        if terminalLayer in self.layers(): 
            if self.contains(terminalPos): # QGraphicsItem.contains()
                return True 
        return False 
        

    def setShowingLayers(self, layers): 

        for layer, layer_items in self.copperItems().items():
            if layer in layers: 
                for layer_item in layer_items: 
                    layer_item.show()
            else: 
                for layer_item in layer_items:
                    layer_item.hide()
            
    def copperItems(self):
        return self._copperItems 
    def setCopperItems(self,copperItems):
        self._copperItems = copperItems 
    def addCopperItem(self, layer, copperItem):
        self.copperItems()[layer].append(copperItem)
    def removeCopperItem(self, layer, copperItem):
        self.copperItems()[layer].remove(copperItem)
        
    def addLayer(self, layer):
        self._layers.append(layer)
    def removeLayer(self, layer):
        self._layers.remove(layer)
          
    # def mousePressEvent(self, event):
    #     self.moveStart = event.scenePos()
    #     self.offset = event.scenePos() - self.scenePos() 
    #     super().mousePressEvent(event) # Does not prevent jumping bug # Note base implementation of mPE handles offsets while moving
                
    # def mouseMoveEvent(self, event):
    #     super().mouseMoveEvent(event)
    
    # def hoverEnterEvent(self, event):
    #     current_tooltip = self.toolTip()

    #     self.setToolTip(f"{current_tooltip}\nPos: {self.pos()}\nscenePos: {self.scenePos()}")
    #     return super().hoverEnterEvent(event)
    # def hoverLeaveEvent(self, event):
    #     self.setToolTip("")
    #     super().hoverLeaveEvent(event)
