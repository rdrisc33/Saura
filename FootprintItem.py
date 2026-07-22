import lxml.etree as etree
from utils import *
from Reference import Reference 
from BoardItem import BoardItem
# from Component import Component


# class Polygon():
#     def __init__(self, elem, parent):
#         super().__init__(elem, parent)
        
#         points_str = elem.get('points')
#         points = [ list(map(float , pt.split(','))) for pt in points_str.split() ] # get a list of lists from a string
#         points = [QPointF(pt[0] , pt[1]) for pt in points] # Make points into QPointFs
#         polygon = QGraphicsPolygonItem( points, parent=self) # Create polygon item
#         polygon.setPen(QPen(Qt.GlobalColor.darkYellow , 0))
#         self.setChildItem(polygon)

    

# A note on stacking order. Items are stacked according to zValue, then insertion order. Default zValue is 0. zValue only works between sibling items; items that have the same parent.Thus I set the pad to have a z value of 1, so that default the pad appears on top of the Fab and other layers. Then I also set pad childrenItems zValue to make the different pad layers stack in different orders. Then, to make the pad._nameItem appear on top of the pad, I also set pad._nameItem.setZValue(1)
# class FootprintItem(Component, CopperItemContainer, QGraphicsItem):
# class FootprintItem( Reference, CopperItemContainer, QGraphicsItem):
class FootprintItem( BoardItem, Reference, QGraphicsItem):
    font = footprint_font


    def __init__(self, referenceDesignator, referenceNumber, file, layer = "F.Cu"):
        super().__init__(referenceDesignator=referenceDesignator, referenceNumber=referenceNumber) 
        # print('FOOTPRINTITEM.INIT')
        self._file = None 
        self._layer = None 
        
        self._nets = None 
        self._copperItems = defaultdict(list)
        
        # self._layerItems = None 
        
        self.setFile(file)
        self.setLayer(layer)
        
        self._referenceItem = BoardSimpleTextItem(self.layer(), self.reference(), self)
        self._referenceItem.setFont(Utils.footprintFont)

        self._pads = []
        # self.terminal_items = set() # A set of items(think pads) whose origin makes for connection points: In a footprint, pads are what you connect to
        self.drawGraphics()
        self.setNets()
        
        self._nameItem = BoardSimpleTextItem(self.layer(), "", self)
        self._nameItem.setFont(self.font)
        self._nameItem.setZValue(20)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        print('FOOTPRINTITEM CREATED') 
        # print('FOOTPRINTITEM.COPPERITEMS:', self.copperItems()) # {'F.Cu': [<FootprintItem.PadItem(0x21be98e6b00, parent=0x21be98e6a00, pos=0,0) at 0x0000021BE7617FC0>, <FootprintItem.PadItem(0x21be98e7400, parent=0x21be98e76c0, pos=0,0) at 0x0000021BE8493D00>], 'F.Paste': [<FootprintItem.PadItem(0x21be98e7740, parent=0x21be98e6a00, pos=0,0) at 0x0000021BE8493800>, <FootprintItem.PadItem(0x21be98e7440, parent=0x21be98e76c0, pos=0,0) at 0x0000021BE8493FC0>], 'F.Mask': [<FootprintItem.PadItem(0x21be98e7380, parent=0x21be98e6a00, pos=0,0) at 0x0000021BE8493A40>, <FootprintItem.PadItem(0x21be98e7b80, parent=0x21be98e76c0, pos=0,0) at 0x0000021BE84A0200>]})

        
    def copperItems(self):
        return self._copperItems 
    def setCopperItems(self,copperItems):
        self._copperItems = copperItems 
    def addCopperItem(self, layer, copperItem):
        self.copperItems()[layer].append(copperItem)
    def removeCopperItem(self, layer, copperItem):
        self.copperItems()[layer].remove(copperItem)
        
    def nets(self):
        print('FOOTPRINTITEM.COPPERITEMS():', self.copperItems()) # FOOTPRINTITEM.COPPERITEMS(): defaultdict(<class 'list'>, {})
        return self._nets 
    def setNets(self):
        self._nets = set()
        for childItem in self.childItems(): 
            print('CHILDITEM:', childItem)
            self._nets.add(childItem.net())
            
        if None in self._nets: 
            self._nets.remove(None)
            
        self._nets = list(self._nets)
        # self._nets = set()
        # for copperItems in self.copperItems().values(): 
        #     print('COPPERITEMS:', copperItems)
        #     for copperItem in copperItems: 
        #         print('COPPERITEM.NET():', copperItem.net())
        #         self._nets.add(copperItem.net())
                
# need a system for assigning nets 
# also need to know if CuIC or CuI that means more

    def updateRtrees(self): 
        for childItem in self.childItems(): 
            childItem.updateRtrees()
        # for pad in self.pads():
        #     pad.updateRtrees()
                      
    def mouseMoveEvent(self, event): # Note that when parent footprint gets a moveEvent, parent footprint does NOT send that event to children# QGI.mmE moves all decendant items, so call super() for that. But still have to update rtrees & bounds of all descendant Items
        # print('FOOTPRINTITEM.MOUSEMOVEEVENT')
        super().mouseMoveEvent(event)    
        self.updateRtrees()
        
        # When footprint moves, need to update ratsnest. How do I run MainWindow.updateRatsnest from here? A: signals and slots. As QObjects have sig/slots, and QGraphicsItems are not Qobjects, we would need to subclass QObject to use signals/slots...
        # self.moved.emit()

        
    def sceneTerminalsOnNet(self, net):
        terminals = []
        for pad in self.pads(): 
            if pad.net() == net: 
                terminals.append(pad.sceneTerminal())
    
    def file(self):
        return self._file 
    def setFile(self, file):
        self._file = file
    def layer(self):
        return self._layer 
    def setLayer(self, layer):
        self._layer =  layer
    
    def boundingRect(self):
        return self.childrenBoundingRect() or QRectF()
    
    def paint(self, painter, option, widget):
        pass # ChildItems draw themselves
    
    def mirror(self): # 
        pass 

    def pads(self):
        return self._pads 
    


    # def terminals(self): # NOTE 'terminal' is place where traces connect, which is the job of pads, NOT FP. thus fp has  .terminals().
    
    def drawGraphics(self):
        root = etree.parse(self.file()).getroot() # lxml.parse returns an Elementroot as opposed to an Element. Use ET.getroot() to get the root elem.
        self._name = root.attrib.get('name')
        # if self._name: 
        #     self._nameItem.setText(self._name)
            
        # pad_elems = root.findall('pad')                              #
        line_elems = root.findall('line')                            #
        arc_elems = root.findall('arc')                              #
        circle_elems =root.findall('circle')    
        polygon_elems =root.findall('polygon')                        #
        # Not yet supported:
        # texts =root.findall('text')                              #
        # text_boxes =root.findall('text_box')                      #
        # rects =root.findall('rect')                              #
        # quad_bez_curve =root.findall('quad_bez_curve')          #
        # keep_out_zone =root.findall('keep_out_zone')            #
        # model =root.findall('model')   
        # print()                         #
        # print("MYFOOTPRINTITEM SELF:", type(self), self)
        for pad_elem in root.findall('pad') : 
            # print('PAD_ELEM:', pad_elem)
            # p = PadItem(pad_elem, self) 
            pad = Pad(pad_elem, self)
            # for layer in pad.layers(): 
            #     if layer in Utils.CopperLayers: # Pads also appear on the mask and silks layers, but we can ignore those as copperItems
            #         self.addCopperItem(layer, pad )
            self.pads().append(pad)# Note if p is not referenced by anything, p will be garbage collected; deallocated; deleted. When p is deallocated, its childrenItems are, too, so no more pads. To avoid this, maintain a reference to p; put p in a list
            pad.setZValue(1) 
            
            pad.setNet(pad.parentItem().reference() + '_' + pad.name()) # Ex 'C3_1' 

                
        for line in line_elems: 
            # MyLineItem(line, self)
            x1 = float(line.get('x1')) 
            y1 = float(line.get('y1')) 
            x2 = float(line.get('x2')) 
            y2 = float(line.get('y2')) 
            
    
            stroke_width = float(line.get('stroke_width', 0))
            stroke_width = .1 # For debugging
    
            layer = line.get('layer')  
            if layer:
                lineItem = BoardLineItem(layer, x1, y1, x2, y2, self)
                lineItem.setPen(QPen(Utils.layerColors[layer] , stroke_width))
                # self.addLayerItem(lineItem)
                # self.copperItems()[layer] = lineItem NO BAD remember to extend the copperItems 
                # self.copperItems()[layer].append(lineItem) NO BAD Footprint Lines are not copperItems. They have no connectivity. They can be added as childItems 
                # They arent copperItems but if they are merely childItems, they kinda get 'lost'... track them as layerItems.                
                
    @classmethod
    def from_part(cls, part, referenceNumber):
        file = part.get('footprint')
        referenceDesignator = part.get('referenceDesignator', '?')
        
        c=  cls(file, referenceDesignator, referenceNumber)
        # c.setPart(part) # FPItems dont track part. Component tracks both FPI & part
        return c
    
    # def setBuffer(self, buffer_width , net=None): # DesignItem reimplemt. A buffer is the expanded border of a _padShape. traceWidth() and net are important. A buffer represents where a trace cant enter. Items whose net is currently selected, do not get buffered, because nets are able to join with items of the same net. Vias/pads/kozs/traces can all get buffered. A single footprint, may have many pads, each of which will be buffered 
    #     print()
    #     self._buffer = QPainterPath()
    #     for childItem in self.childItems():
    #         # print("TYPE(CHILDITEM):" ,type(childItem))
    #         # print('ChildItem:', childItem)
    #         # print('Item.net:', childItem.net)
    #         if childItem.net is None: 
    #             continue # skip over items with None net
            
    #         if childItem.net != net: # Items of the same net are joinable; don't become buffer. Also, items might not have a net, ex pads of newly placed fp don't have net yet, and the act of joining netless items with netted item will assign net to the netless item.
    #         # if isinstance(item, (MyViaItem, MyPadItem, MyZoneItem, MyTraceItem) )  : # Contrast usage of .isinstance against always using a QGraphicsItem subclass w/ a .hull() implementation : the second one likely flows better.
    #             childItem.calculate_buffer(buffer_width)
    #             print()
    #             print("CHILDITEM:", childItem)# CHILDITEM: <FootprintItem.PadItem(0x28c4685fe40, parent=0x28c4685ee00, pos=0,0, z=1) at 0x0000028C47152100>
    #             print("CHILDITEM.BUFFER:", childItem.buffer())
    #             buffer = childItem.buffer()
    #             # print('BUFFER:', buffer)
    #             if buffer: 
    #                 self._buffer.addPolygon(buffer)
                
    #     return self.mapToScene(self._buffer.toFillPolygon())
    #     # return self._buffer.toFillPolygon() WHICH IS IT: MAPTO SCENE OR NAY? BC item.buffer() already did .mapToScene  

    def snap(self, seeker, net=None , layer=None): 
        # print('FPITEM.SNAP')
        seeker.setPos(self.scenePos())
        
    

    

    # def boundingRect(self):
    #     return self.childrenBoundingRect() or QRectF()  
    
    # def paint(self, painter, option, widget):
    #     pass
            
    def mouseDoubleClickEvent(self, event): # If we double click on a footprint...
        # self.doubleClicked.emit(self.part) # self.footprint_assign = MyGraphicsAssign
        # part = self.data(PartData.PART.value)
        # print('PartData.PART.value:', part)
        if self.scene().mode() == BoardSceneModes.normalMode:# We can't import BoardScene here, bc we import this module in BoardScene, that would be a circular import. so, put BoardModes in  :AttributeError: Error calling Python override of QGraphicsObject::mouseDoubleClickEvent(): type object 'Utils' has no attribute 'BoardSceneModes'
            pass
            # self.graphic_assign = MyGraphicAssign(self.part(), 'footprint')
            # self.graphic_assign.open()
        elif self.scene().mode() == BoardSceneModes.addTraceMode:
            pass
        super().mouseDoubleClickEvent(event)

    # def mousePressEvent(self, event): 
    #     print()
    #     print('MyFootprintItem.mousePressEvent')
    #     self.offset = self.scenePos() - event.scenePos() 
    #     super().mousePressEvent(event)

    # def layerItems(self):
    #     return self._layerItems
    # def setLayerItems(self, layerItems): 
    #     self._layerItems = layerItems  
    # def addLayerItem(self, layerItem):
    #     # print()
    #     # print('LAYERITEM:', layerItem)
    #     self.layerItems()[layerItem.layer()].append(layerItem)
    # def removeLayerItem(self, layerItem):
    #     self.layerItems()[layerItem.layer()].remove(layerItem)
             
    
        
# Prob: debug_rect still present after release of drag : BUT gone after another double click: 
# Relase of drag sees BoardScenemouseReleaseEvent, but not itemmouseReleaseEvent


# class PadBase(QGraphicsItem):
class PadBase():
        
    def __init__(self, elem,*args, **kwargs):#, parent): 
        super().__init__(*args, **kwargs)#parent)
        self._centroid          = None 
        
        self.elem = elem          
        self.setPadShape(elem.get('shape').lower().strip())
        self.setPath(self.createPath())        
        self.setCentroid()
  
    def nearestSceneSnap(self, pos): 
        return self.mapToScene(self.centroid())
    
    def boundingRect(self):
        return self._boundingRect
        
    def paint(self, painter, option, widget):
            pass # To Be further reimplemented 
    
    def name(self):
        return self._name 
    def setName(self, name):
        self._name = name 
        
    def nameItem(self):
        return self._nameItem 
    def setNameItem(self, nameItem):
        self._nameItem = nameItem
        
        
    def padShape(self):
        return self._padShape
    def setPadShape(self, padShape):
        self._padShape = padShape
        
    def createPath(self):
        path = QPainterPath()
        
        if (self._padShape == 'rect') or (self._padShape == 'circle'): 
            self.left =          float(self.elem.get('left')) 
            self.top =           float(self.elem.get('top')) 
            self.width =         float(self.elem.get('width'))
            self.height=         float(self.elem.get('height'))
            # c_x =           float(elem.get('c_x'))
            # c_y =           float(elem.get('c_y'))
            self._boundingRect = QRectF(self.left, self.top, self.width, self.height)
            self.setCentroid()

            # self.setupNameItem(self.left, self.top) moved
            
            if self._padShape == 'rect':
                path.addRect(self.left, self.top, self.width, self.height)
            elif self._padShape == 'circle': 
                path.addEllipse(self.left, self.top, self.width, self.height)
                
        elif self._padShape == 'custom': 
            print('CUSTOM PADS NOT YET IMPLEMENTED')
                
        return path
              
    def path(self):
        return self._path
    def setPath(self, path):
        self._path = path 
    
    def shape(self):
        return self.path() # default imp probably does the same thing 
        
    # def setupNameItem(self, left , top ): This not part of padBase; part of Pad, not PadItem

    #     self._name = self.elem.get('name') 
    #     if self._name: 
    #         self._nameItem = BoardSimpleTextItem(self.layer(), self._name, self) # _nameItem is parented on self, the container_item representing this pad 
    #         self._nameItem.setFont(footprint_font)
    #         self._nameItem.setPos(QPointF(left, top))
    #         self._nameItem.setZValue(2) # Stack pad_name atop the backgroundpads(z0) and topmostLayer(z1)
    #     # print()
    #     # print("POSITION:", self._nameItem.pos())
      
    def pointOfInaccessibility(self):
        pass # Need to implement POI for freaky shaped pads. NO simply demand that origin==terminal. See shapely.polylabel. POI guarantees centroid inside shape.
    
    def centroid(self):
        return self._centroid 
    
    def setCentroid(self): # Recalculate centroid 
        if (self._padShape == 'rect') or (self._padShape == 'circle'): 
            self._centroid = QPointF( self.left + self.width/2 , self.top + self.height/2 )
        elif self._padShape == 'custom': 
            self._centroid = self.pointOfInaccessibility()
    
class Pad(PadBase, CopperItemContainer, QGraphicsItem):# CopperItem, PadBase):

    def __init__(self, elem, parent): # elem: xml describing this pad. parent: the Footprint to which this pad belongs 
        super().__init__( elem=elem, parent=parent) 
        self._terminal          = None 
        self._sceneTerminal     = None 
        self._terminals         = None 
        self._sceneTerminals    = None 


        self.setRotation(float(elem.get('angle', 0)))

        layers = elem.get('layers')
        if layers == '': 
            layers = "F.Cu, F.Paste, F.Mask"
       
        layers = [layer.strip() for layer in layers.split(',')] # Convert string into list 
            
        self.setLayers(layers)
                    
        for layer in self.layers():
            PadItem(layer, elem, Utils.layerColors[layer], self)            # Create padItem
# AttributeError: 'PadItem' object has no attribute '_layer'

        self.setSceneTerminals() # Pad only has one terminal, but have the option of having it in a list, for a consistent api, with Trace, which has two terminals.
        self.setupNameItem()
        
        # print('LAYER:', layer)


    def setupNameItem(self ):

        self._name = self.elem.get('name') 
        if self._name: 
            self._nameItem = BoardSimpleTextItem(self.layer(), self._name, self) # _nameItem is parented on self, the container_item representing this pad 
            self._nameItem.setFont(footprint_font)
            self._nameItem.setPos(QPointF(self.left, self.top))
            self._nameItem.setZValue(2) # Stack pad_name atop the backgroundpads(z0) and topmostLayer(z1)
        # print()
        # print("POSITION:", self._nameItem.pos())
        
    def sceneTerminal(self):
        return self._sceneTerminal
    def setSceneTerminal(self):# 
        self._sceneTerminal = self.mapToScene(self.centroid()) # (x,y layer)
        
    def sceneTerminals(self):
        return self._sceneTerminals
    def setSceneTerminals(self):
        self.setSceneTerminal()        
        self._sceneTerminals = [self.sceneTerminal()]

        
    def terminal(self):
        return self._terminal
    def terminals(self): # Via Item only has one terminal. Still, to keep the api consistent, reimplement .terminals 
        return self._terminals

        
    # def boundingRect(self):
    #     return self._boundingRect or QRectF()
    
    # def paint(self, painter, option, widget):
    #     painter.setPen(self.pen())
    #     painter.setBrush(self.brush())
    #     painter.drawPath(self.path())
       
        
    def brush(self):
        return self._brush
    def setBrush(self, brush):
        self._brush = brush
        
    # def setBuffer(self, buffer_width = None ): # Returns a QPolygonF, representing the buffered shape
    #     # self.pad_template.shape() This would return path, of bR. No good.
    #     if buffer_width == None: 
    #         buffer_width = self.scene().traceWidth()
    #     stroker = QPainterPathStroker()
    #     stroker.setWidth(buffer_width)
    #     stroker.setJoinStyle(Qt.BevelJoin) 
    #     stroker.setCapStyle(Qt.FlatCap)
        
    #     path = self.shape() # self.pad_template better be a QGraphicsPathItem to use .path()
    #     strokerPath = stroker.createStroke(path)
    #     expandedPath = path.united(strokerPath) #Unite the fillable areas of the paths into one consolidated path
    #     self._buffer = expandedPath.toFillPolygon() # convert to a QPolygonF. 

    def snap(self, seeker, net, layer):
            
        print('PADITEM.SNAP')
        if self.net() == net or (self.net() == None) or (net == None):
            # seeker.setPos(self.scenePos()) NO BAD the pad's .scenePos is offset from its centroid.
            print('SELF.TERMINAL:', self.terminal())
            seeker.setPos(self.terminal()[0:2]) # terminal() -> xylayer
                
            if self.net() == None: 
                self.setNet(net) 
            elif net == None: 
                net = self.net() 

#MRO: padItem, CopperItem, BoardItem, PadBase, QGI, object
class PadItem(CopperItem, PadBase, QGraphicsItem):
    def __init__(self, layer, elem, color, parent):
        print('PAD.MRO():', PadItem.mro())
        super().__init__(layer=layer,elem= elem, parent=parent)# Pad is parented on parent, a FootprintItem. # Its good to use keywords when passing args, when inheritance is at play, because you don't need to remember the order of arguments 
        self._terminals = []
        self.color = color
        self._net = None 
        
    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        painter.drawPath(self.path())

    # def mouseMoveEvent(self, event): 
    #     print('PAD.MOUSEMOVEEVENT')
    #     super().mouseMoveEvent(event)
        

                

