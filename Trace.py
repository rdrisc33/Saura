from utils import * 
from CopperItemContainer import CopperItemContainer

class TraceBase(): 
    def __init__(self, x1, y1, x2, y2, traceWidth, *args, **kwargs ): 
        super().__init__(*args, **kwargs)
        self._pen = QPen(Qt.black, traceWidth) 
        
        self._x1 = x1 
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2 
        self._traceWidth = traceWidth


        # self.setPen(QPen(Qt.black, traceWidth , c = Qt.PenCapStyle.RoundCap))
        # self.setBrush(QBrush(Qt.black))

    def boundingRect(self):  # https://codebrowser.dev/qt5/qtbase/src/widgets/graphicsview/qgraphicsitem.cpp.html
        if self.traceWidth() == 0.0: 
            x1 = self.x1() 
            y1 = self.y1() 
            x2 = self.x2() 
            y2 = self.y2() 
            lx = min(x1, x2)
            rx = max(x1, x2)  
            ty = min(y1, y2) 
            by = max(y1, y2) 
            return QRectF( lx, ty , rx - lx , by - ty)
        return self.shape().controlPointRect() 
    
    def shape(self):
        p = QPainterPath()
        p.moveTo(QPointF(*self.p1().toTuple()))
        p.lineTo(QPointF(*self.p2().toTuple()))
        if self.pen() == Qt.NoPen: 
            return p
        stroker = QPainterPathStroker() # In computer graphics, 'stroking' is the known difficult problem of offsetting shapes. Qt uses it to calculate 'fillable outlines of shapes': Give a path, get an offset of that path. note it strokes the 'inside' and 'outside' of the given shape, so there's two
        penWidthZero = .00000001 # QT QUIRK: qpps.setWidth(zero or negative) ACTUALLY sets a width of 1. see workaround hack: https://codebrowser.dev/qt5/qtbase/src/widgets/graphicsview/qgraphicsitem.cpp.html#_ZL29qt_graphicsItem_shapeFromPathRK12QPainterPathRK4QPen
        if self.traceWidth() <= 0: 
            stroker.setWidth(penWidthZero)
        else: 
            stroker.setWidth(self.traceWidth()) 
            
        stroker.setJoinStyle(Qt.RoundJoin)
        stroker.setCapStyle(Qt.RoundCap)        
        path = stroker.createStroke(p)
        path.addPath(p) # Include the actual line in your path too
        return path 
    
    def pen(self):
        return self._pen
    
    # def brush(self): QGLI has no brush. Trace should have no brush as well 
    #     return self._brush 

    def x1(self) :
        return self._x1 
    def y1(self): 
        return self._y1 
    def x2(self): 
        return self._x2 
    def y2(self): 
        return self._y2
    def traceWidth(self): 
        return self._traceWidth 
        
    
    def p1(self):
        return QPointF(self._x1, self._y1)
    def setP1(self, p1 ): 
        self.prepareGeometryChange()
        self._x1 , self._y1 = p1.toTuple()
        
    def p2(self):
        return QPointF(self._x2 , self._y2)
    def setP2(self, p2): 
        self.prepareGeometryChange()
        self._x2 , self._y2 = p2.toTuple()

    def line(self):
        return QLineF(self.p1() , self.p2() )
        
    def setLine(self, line): 
        self.prepareGeometryChange()

        self._x1 = line.p1().x()
        self._y1 = line.p1().y()
        self._x2 = line.p2().x()
        self._y2 = line.p2().y()

class TraceItem(LayerItem, TraceBase, QGraphicsItem): 
    def __init__(self, x1, y1, x2, y2, layer, traceWidth, parent, *args, **kwargs ): 
        super().__init__(layer=layer, x1=x1, y1=y1, x2=x2, y2=y2, traceWidth=traceWidth, parent=parent, *args, **kwargs)

        self._layer = layer

        self.setPen(QPen(Utils.layerColors[layer], traceWidth , c = Qt.PenCapStyle.RoundCap))

        # self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def paint(self, painter, option, widget): 
        # print('PAINTING')
        
        painter.setPen(self.pen())
        # painter.drawLine(0,0,100.5,100.5) NO BAD  Qt Quirk : the .drawLine() overload which takes four numbers ONLY ACCEPTS INTEGERS. If you want to use float, use the overload for QPointF or QLineF.  
        painter.drawLine(QLineF(self.x1() , self.y1() , self.x2() , self.y2()))
        
        painter.drawLine(QLineF(0.0,0.0,100.5,100.5)) # Same result
        

    def net(self): 
        return self.parentItem().net()
    
    def setTraceWidth(self, traceWidth): 
        self.prepareGeometryChange() 
        self._traceWidth = traceWidth
        self._pen = QPen(self.pen().color() , traceWidth, c = self.pen().capStyle())
        
    def pen(self):
        return self._pen
    def setPen(self, pen): 
        self.prepareGeometryChange() 
        self._traceWidth = pen.width()
        self._pen = pen # QPen(pen.color() , pen.width(), c = Qt.PenCapStyle.RoundCap)

class Trace(TraceBase, CopperItemContainer, QGraphicsItem): 
    # def __init__(self, layers, traceWidth, p1, p2 , *args, **kwargs ):
        # print('TRACE.ARGS:', args)
        # print('TRACEKWARGS:', kwargs)
        # super().__init__( layers=layers , p1=p1, p2=p2, traceWidth=traceWidth, *args, **kwargs) 
    def __init__(self, x1, y1, x2, y2, layers, traceWidth,net=None, parent=None, *args, **kwargs ): 
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, layers = layers, traceWidth=traceWidth, parent=parent, *args, **kwargs)
        self._x1 = x1 
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2 
        self._traceWidth = traceWidth

        self.l1Anchors = dict()
        self.l2Anchors = dict() 
        self.l1s = dict() 
        self.l2s = dict()

        self.setLayers(layers)
        self.setTraceWidth(traceWidth)
        self.removed = False # Flag for mouseMoveEvent. Has this item been removed from scene 

        # print('SELF.LAYERS:', self.layers())
        if isinstance(self.layers(), str):
            self._layers = [self.layers()]

        self.previousSeekerSide = None # Store the side the seeker was last on. Equals 1 for cw side or 2 for ccw side. Never set equal to 0 only 1 or 2.  
        # self.adjusting = False # Track whether we are adjusting this trace's position
        self._net = None 

        self._slope = None # If slope is undefined, slope is set to the string 'undefined' otherwise slope is a float
        
        self.l0 = None # l as in QLineF. l0 is self, this TraceItem's QLineF. lines l012 will NOT mutate after they are created, because they must never be set to 0 length, because that sets their angle to -0.0, but we need that angle info. All the math is done with QLineFs. Only when we're done with maths do we update lineitems li0123. li123 are NOT updated with l0123, because l0123 are arbitrarily long. Instead, we create new, nameless QLineFs to pass to QGLI.setLine(). 
        self.l1 = None 
        self.l2 = None 
        self.l3 = None
        
        self.li1 = None  # li as in lineItem. QGraphicsLineItems cannot mutate their own lines, so QGLI.line().set(P1,P2,Points,Angle) will all silently fail. This is a bitch of a gotcha. To edit a QGLI's line, you must set a wholly new line; use li.setLine(QLineF) every time you want to update a QGLI with a new line. 
        self.li2 = None 
        self.li3 = None 
        
        self.t0 = None # t as in TraceItem. The TraceItem representing l0 ( aka self, this traceItem ) 
        self.t1 = None 
        self.t2 = None
        self.t3 = None 
        
        self.initialAnchor1Orientation = None
        self.initialAnchor1 = None 
        self.initialAnchor2 = None 
        self.arbitrary = QPointF(-1e9, -1e9)        
    
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable) 


            
        # for layer in self.layers():
        #     TraceItem(self, p1, p2, traceWidth , layer)
        for layer in self.layers(): 
            TraceItem(self._x1 , self._y1 , self._x2 ,self._y2 , layer, traceWidth, self) 
            

    def paint(self, painter, option, widget): 
        pass # Trace paints nothing. TraceItem paints a line. 

    def terminatesWithin(self, rect=None, sceneBounds= None ): # Returns first terminal found within rect|bounds. Returns false if no terminals within rect|bounds. All in scenecoordinates. 
        
        if sceneBounds: 
            l , t , r , b = sceneBounds
            rect = QRectF(l , t , r - l , b - t) 
        for terminal in self.sceneTerminals(): 
            if rect.contains(terminal): 
                return terminal
        return False 
    
    def terminalsWithin(self, rect=None, sceneBounds= None ): # Returns list of terminals found within rect|bounds. If non found, returns an empty list. 
        terminalsWithin =[]
        
        if sceneBounds: 
            l , t , r , b = sceneBounds
            rect = QRectF(l , t , r - l , b - t) 
        for terminal in self.sceneTerminals(): 
            if rect.contains(terminal): 
                terminalsWithin.append(terminal)
        return terminalsWithin
    

    @classmethod 
    def fromLine(cls, line, traceWidth , layers):
        return cls( x1=line.p1().x() , y1=line.p1().y() , x2=line.p2().x() , y2=line.p2().y(), layers=layers, traceWidth=traceWidth)

    @classmethod
    def fromPoints(cls, layers, traceWidth, p1, p2): 
        return cls( x1=p1.x() , y1=p1.y() , x2=p2.x() , y2=p2.y() , layers=layers, traceWidth=traceWidth, )

    def net(self): 
        return self._net
    def setNet(self, net): 
        self._net = net 
        
    def setLine(self, line): 
        # self.prepareGeometryChange() super does this
        super().setLine(line) 
        self.setSceneBounds()
        for child in self.childItems(): 
            if isinstance(child, TraceItem): 
                child.setLine(line) 
                
    def setTraceWidth(self, traceWidth): 
        self.prepareGeometryChange() 
        self._traceWidth = traceWidth
        # self._pen = QPen(self.pen().color() , traceWidth, c = Qt.PenCapStyle.RoundCap)
        
        for child in self.childItems(): # Control child TraceItems 
            if isinstance(child, TraceItem): 
                child.setTraceWidth(traceWidth)


    # def setPen(self, pen): # Slightly confusing: Trace has a pen, yet paints nothing. Why have .setPen? To control child TraceItem's pen widths Nah get rid of it 
    #     self.prepareGeometryChange() 
    #     self._traceWidth = pen.width() 
    #     self._pen = QPen(pen.color() , pen.width(), c = Qt.PenCapStyle.RoundCap)
    #     for child in self.childItems(): 
    #         if isinstance(child, TraceItem): 
    #             child.setPen(pen)

    # def sceneTerminals(self):
    #     return self._sceneTerminals
    # def setSceneTerminals(self):
    #     self._sceneTerminals = [self.p1() , self.p2()]
        
    def nearestSceneSnap(self, pos):
        """return the snappable point nearest to 'pos'. p1 and p2 are possible snap points for traces. Pads, zones, and vias have just one snap point; their centroid"""
        # calculate distance from p1,p2 to pos 
        # calculate min distance and return corresponding point
        
        if Utils.distance(pos, self.p1()) <= Utils.distance(pos, self.p2()): 
            return self.p1() 
        else: 
            return self.p2()
    
    def netCollision(self): # Returns true if there are any net collisions, else False. A net collision occurs when two items overlap, on the same layer, with different, nonNone, nets.
        # hitItems = self.queryRtrees(self.scene().activeLayer()) 
        hitItems = self.queryRtrees()
        for hitItem in hitItems: 
            pass
            
    def sceneTerminals(self):#  
        return self._sceneTerminals
    def setSceneTerminals(self): # Return scene position of p1 and p2
        self._sceneTerminals= [ self.mapToScene(self.line().p1()) , self.mapToScene(self.line().p2()) ]
        # print('SELF.TERMINALS():', self.terminals())
        
    def traceWidth(self):
        return self._traceWidth
    
    def setTraceWidth(self, traceWidth):
        self._traceWidth = traceWidth 
        # self.setPen(QPen(self._color, self._traceWidth, c=Qt.PenCapStyle.RoundCap))
        # print('ABOUT OT SET BUFFER DISTANCE')
        self.setBufferDistance(self._traceWidth)
        print('SETTRACEWIDTH DONE')
    
    def p1SceneBounds(self):
        x1,y1= self.line().p1().toTuple()
        p1_bounds =  (x1,y1, x1,y1)
        return p1_bounds 
    
    def p2SceneBounds(self):
        x2,y2 = self.line().p2().toTuple()
        p2_bounds = (x2,y2, x2, y2)
        return p2_bounds 
    
    def connecteds(self):
        connecteds = [] 
        self.setBounds()
        items = [ self.scene().ids[id] for id in  self.scene().rtrees[self.layer()].intersection(self.bounds()) ]
        for item in items: 
            if isinstance(item, TraceItem):
                if ( item.line().p1() == self.line().p1() ) or ( item.line().p1() == self.line().p2() ): 
                    connecteds.append(
                        {'item':        item, 
                         'proximal':    item.line().p1(), 
                         'distal':      item.line().p2()
                        })
                elif ( item.line().p2() == self.line().p1() ) or ( item.line().p2() == self.line().p2() ): 
                    connecteds.append(
                        {'item':        item,
                         'proximal':    item.line().p2(),
                         'distal':      item.line().p1()
                         })

        return connecteds 
    
    def snap(self, seeker, net): # Snap seeker to this item, if able 
        print('TRACEITEM.SNAP')
        if self._net == net or (self._net == None) or (net == None):
            if self.snapToTerminal(seeker):

                if self._net == None: 
                    self._net = net 
                elif net == None: 
                    net = self._net
                    
            return True 

    def snapToTerminal(self, otherItem):
        if otherItem.contains(self.mapToScene(self.line().p1())): 
            otherItem.setPos(self.mapToScene(self.line().p1()))
            return True

        elif otherItem.contains(self.mapToScene(self.line().p2())):
            otherItem.setPos(self.mapToScene(self.line().p2()))
            return True 
        


    def getConnectedTraces(self): # Must pay attention to item.line().pn() vs self.line().pn() and p1 vs p2; this gets tricky
        # point1or2 = point1or2.lower().strip()
        print()
        connectedTraces = {'p1':[] , 'p2':[]}
        # connected_traces = []
        # self.setBounds()# self.bounds is (0000) if we initialized a blank traceItem. Be sure to recalculate bounds 
        # self.setSceneBounds()
        # print('TRACE.SCENEBOUNDS:', self.sceneBounds()) # (0000)
        # ids = list(self.scene().idx.intersection(self.bounds()))
        ids1 ,ids2 = [] ,[]
        for layer in self.layers(): 
            ids1.extend( self.scene().rtrees[layer].intersection(self.p1SceneBounds()) ) # Hits at p1 
            ids2.extend( self.scene().rtrees[layer].intersection(self.p2SceneBounds()) ) # Hits at p2 

        print()
        print('IDS1:', ids1)
        print('IDS2:', ids2) 
        hitItems1 =  [ self.scene().ids[id] for id in ids1 if not (id is self.id()) ]
        hitItems2 =  [ self.scene().ids[id] for id in ids2 if not (id is self.id()) ]

        print('HITITEMS1:', hitItems1)
        print('HITITEMS2:', hitItems2)

        print('SELF.L0:', self.l0.toLine())
        for hitItem in hitItems1: # Collect traces
            if isinstance(hitItem, Trace): 
                print('HITITEM:', hitItem, hitItem.line().p1().toPoint() , hitItem.line().p2().toPoint()) 
                if (hitItem.line().p1() == self.l0.p1()):
                    distal = hitItem.line().p2() # We may need to know connected_trace's distal point, to use as anchor
                    connectedTraces['p1'].append( ( hitItem , distal ) )
                elif ( hitItem.line().p2() == self.l0.p1()): 
                    distal = hitItem.line().p1()
                    connectedTraces['p1'].append( ( hitItem , distal ) )
                else: 
                    print('NEITHER p1 NOR p2 MATCHES UP' )
        for hitItem in hitItems2: 
            if isinstance(hitItem, Trace):
                if (hitItem.line().p1() == self.l0.p2()):
                    distal = hitItem.line().p2() # We may need to know connected_trace's distal point, to use as anchor
                    connectedTraces['p2'].append( ( hitItem , distal ) )
                elif ( hitItem.line().p2() == self.l0.p2()): 
                    distal = hitItem.line().p1()
                    connectedTraces['p2'].append( ( hitItem , distal ) )

        print('CONNECTEDTRACES:', connectedTraces)
        return connectedTraces

    def angleBetween(self, lineA, lineB): 
        # determines the angle between two lines 
        PI = math.pi
        
        alpha   = math.atan2( - lineA.dy() , lineA.dx() )
        beta    = math.atan2( - lineB.dy() , lineB.dx() ) 

        theta = self.normalizeAngle( beta - alpha )

        print('ANGLEBETWEEN l0 AND ln:', theta)
        if theta == math.pi/4: 
            print('ANGLE1 ACUTE') 
            return 'acute'
        elif theta == PI/2 or theta == 3*PI/2: 
            print('ANGLE1 PERPENDICULAR') 
            return 'perpendicular' 
        elif theta == 3*PI/4 or theta == 5*PI/4: 
            print('ANGLE1 OBTUSE') 
            return 'obtuse'
        else: 
            print('NSTH')
            
    # def angle1(self): 
    #     PI = math.pi
        
    #     alpha   = math.atan2( - self.l0.dy() , self.l0.dx() )
    #     beta    = math.atan2( - self.l1.dy() , self.l1.dx() ) 

    #     theta = self.normalizeAngle( beta - alpha )

    #     print('THETA:', theta)
    #     if theta == math.pi/4: 
    #         print('ANGLE1 ACUTE') 
    #         return 'acute'
    #     elif theta == PI/2 or theta == 3*PI/2: 
    #         print('ANGLE1 PERPENDICULAR') 
    #         return 'perpendicular' 
    #     elif theta == 3*PI/4 or theta == 5*PI/4: 
    #         print('ANGLE1 OBTUSE') 
    #         return 'obtuse'
    #     else: 
    #         print('NSTH')
        
    # def calculateAnchors(self):# Calculates self.anchor1 and self.anchor2. Finds or creates l1 and l2. -> None 
    #     print('CALCULATING ANCHORS:')
    #     connectedTraces = self.getConnectedTraces()

    #     ctp1 = connectedTraces['p1'] 
    #     ctp2 = connectedTraces['p2'] 
        
    #     if ( not ctp1) or ( len(ctp1) > 1): 
    #             print('ANCHOR1 AT L0.P1')
    #             self.anchor1 = self.l0.p1()
    #             self._angle1 = 'acute' # if no connected traces, we will create some, with acute angles to self.
    #             # self.l1 = QLineF(self.anchor1 , self.arbitrary) # Draw line to an arbitrary point, b/c if line is of 0 length, .setAngle and more don't work 
                    
    #             # if self.previousSeekerSide: # Thick traces may see seeker offset from centerline. Can detect side of such offset, and initialize l1 to that side...
    #             #     if self.previousSeekerSide == 1: # if seeker clockwise: loose 45 degrees else gain 45 degrees. 
    #             #         self.l1.setAngle(self.l0.angle() - 45) # Give l1 an acute angle to l0 # TODO: Side acute angle is on depends on side seeker dragged to, yes?  Must wait until MoveEvent
    #             #     if self.previousSeekerSide == 2: # if ccw 
    #             #         self.l1.setAngle(self.l0.angle() +45) 

    #     elif len(ctp1) == 1:
    #         print('ANCHOR1 AT DISTAL')
    #         item, distal = connectedTraces['p1'][0]
    #         self.anchor1 = distal
    #         self.l1 = item.line() # Remember the QLineF bc we're gonna do math on it 
    #         self._angle1 = self.angle1()
            
    #         self.scene().removeItem(item) # take connected item off scene, inserting a standin QGLI in its place 

    #     # print('L1.ANGLE():', self.l1.angle())
        
    #     if ( not ctp2) or ( len(ctp2) > 1): 
    #         print('ANCHOR2 AT L0.P2')
    #         print('self.l0.ANGLE():', self.l0.angle()) # 270.00
    #         self.anchor2 = self.l0.p2()
    #         self._angle2 = 'acute'
    #         # if self.previousSeekerSide: 
    #         #     if self.previousSeekerSide == 1: # if seeker clockwise: loose 45 degrees else gain 45 degrees. 
    #         #         self.l1.setAngle(self.l0.angle() - 45) #  MOVE TO ADJUST Give l1 an acute angle to l0 # TODO: Side acute angle is on depends on side seeker dragged to, yes?  Must wait until MoveEvent
    #         #     if self.previousSeekerSide == 2: # if ccw 
    #         #         self.l1.setAngle(self.l0.angle() +45) 
    #         # self.l2 = QLineF(self.anchor2, self.arbitrary)
    #         # if self.previousSeekerSide: 
    #         #     if self.previousSeekerSide == 1: 
    #         #         self.l2.setAngle(self.l0.angle() - 135) 
    #         #     elif self.previousSeekerSide== 2: 
    #         #         self.l2.setAngle(self.l0.angle() + 135) 

    #     elif len(ctp2) == 1: 
    #         print('ANCHOR2 AT DISTAL')
    #         item, distal = connectedTraces['p2'][0]
    #         self.anchor2 = distal 
    #         self.l2 = item.line()
    #         self._angle2 = self.angle2()
    #         self.scene().removeItem(item) 
            
    #     # print('L2.ANGLE():', self.l2.angle()) # L2.ANGLE(): 44.999999999999986

        
    #     self.initialAnchor1 = self.anchor1
    #     self.initialAnchor1Orientation = Utils.threePointOrientation(self.l0.p1() ,self.l0.p2() , self.anchor1) # What side of l0 is the anchor initially on? Note can be 0

    #     # self.li1 = QGraphicsLineItem(self.l1) # Unneccessary will be overwritten
    #     self.li1 = QGraphicsLineItem() # Create/addToScene a standin QGLI representing our adjusted trace. QGLIs do not go into the scene.rtree. Add TraceItems upon mouseReleaseEvent; when user indicates they are done editing a trace.
    #     self.li1.setPen(QPen(Qt.red, self.traceWidth() , c = Qt.PenCapStyle.RoundCap)) 
    #     self.scene().addItem(self.li1) 
            
    #     self.initialAnchor2 = self.anchor2
    #     self.initialAnchor2Orientation = Utils.threePointOrientation( self.l0.p1() , self.l0.p2() , self.anchor2)
                
    #     # self.li2=QGraphicsLineItem(self.l2)
    #     self.li2=QGraphicsLineItem()
    #     self.li2.setPen(QPen(Qt.green, self.traceWidth(), c = Qt.PenCapStyle.RoundCap ))
    #     self.scene().addItem(self.li2)

    def calculateAnchorAngleLine(self, connectedTraces, pn):  # Return 3-tuple ( anchor, angle, line ) 
        line = None 
        angle = 'acute' 
        


        if ( not connectedTraces) or ( len(connectedTraces) > 1 ):
            if  pn == 'p1': 
                anchor = self.l0.p1()                # Note we don't set line here, do it l8r bc acute angles actually require two lines, one line per side of l0. But we DO collect anchor here 
                
            elif pn == 'p2':
                anchor = self.l0.p2()
                
        elif len(connectedTraces) == 1: 
            item, distal = connectedTraces[0]
            anchor = distal 
            line = item.line() 
            angle = self.angleBetween(self.l0 , line )
            print('FOUND ANGLE TO BE :', angle)
            self.scene().removeItem(item)
            # Note if angle found to be acute we will l8r discard line in favor of two lines, one per side of l0. but if angle found to be obtuse or perpendicular, one line is all we need 

        if angle == 'acute': 
            if pn == 'p1':

                self.l1Anchors[ Utils.threePointOrientation(self.l0.p1() , self.l0.p2() , anchor) ] = anchor # TPO may be 0;inline, that is ok. May also be to a side; 1|2.  L8r, we will only .get( 1|2 , None ) to get any saved anchors to a side 
                print('SELF.L1ANCHORS:', self.l1Anchors)
                l1_1 = QLineF(self.l1Anchors.get(1, self.l0.p1()), self.arbitrary)
                l1_1.setAngle(self.l0.angle() - 45) 
                l1_2 = QLineF(self.l1Anchors.get(2, self.l0.p1()), self.arbitrary)
                l1_2.setAngle(self.l0.angle() + 45) 
                self.l1s[1] = l1_1 
                self.l1s[2] = l1_2 # Create two l1's , with angles dependent on seekerOrientation, and store them 

                print('SELF.L1S:', self.l1s)
        

            if pn == 'p2':
                self.l2Anchors[ Utils.threePointOrientation(self.l0.p1() , self.l0.p2() , anchor) ] = anchor
                
                l2_1 = QLineF(self.l2Anchors.get(1, self.l0.p2()), self.arbitrary) 
                l2_1.setAngle(self.l0.angle() - 135) 
                l2_2 = QLineF(self.l2Anchors.get(2, self.l0.p2()) , self.arbitrary) 
                l2_2.setAngle(self.l0.angle() + 135) 
                self.l2s[1] = l2_1 
                self.l2s[2] = l2_2 

        return anchor, angle, line
    
    # def prepareAdjust(self): # calculate anchors, set l0, create&addToScene empty li3 


    #     # while 1: 
    #     #     pass  # How come this does not lock up the app? 
    
    #     self.l0 = self.line() # Create & save snapshot of line b4 move
    #     self.seekerOrientation = Utils.threePointOrientation(self.l0.p1() , self.l0.p2() , self.scene().seeker.scenePos()) # Initialize self.seeker_orientation away from None. This should init to 0, indicating seeker is collinear with l0
    #     self.previousSeekerSide = self.seekerOrientation # initialize previous_seeker_side. Likely will be 0 here.
                
    #     # self.adjusting = True 
        
    #     self.t0 = self # Not a typo, self is Trace0
    #     self.calculateAnchors() # anchors, l1, l2 , li1, li2 

    #     self.li3 = QGraphicsLineItem()
    #     self.li3.setPen(QPen(Qt.blue, self.traceWidth() , c=  Qt.PenCapStyle.RoundCap))
    #     self.scene().addItem(self.li3)

        
    # def mousePressEvent(self, event): 
    # #     print()
    # #     print('TRACEITEM.MOUSEPRESSEVENT')

    #     self.prepareAdjust()

    def mousePressEvent(self, event): 
        self.l0 = self.line()
        self.t0 = self # Not a typo, self is Trace0
        self.l3 = None 
        self.moved = False # Flag if we did a mouseMoveEvent
        
        print('self.l0', self.l0)
        self.seekerOrientation = Utils.threePointOrientation(self.l0.p1() , self.l0.p2() , self.scene().seeker.scenePos()) # 0,1or2 representing seeker is inline with, or to a side of, l0
        print()
        print('SELF.SEEKERORIENTATION:', self.seekerOrientation)
        self.seekerSide = self.seekerOrientation # May initialize to 0 but never again 
        self.previousSeekerSide = self.seekerOrientation # save previous seeker orientation to know if changes 
        connectedTraces = self.getConnectedTraces()
        self.anchor1 , self.angle1, self.l1 = self.calculateAnchorAngleLine(connectedTraces['p1'] ,'p1') 
        print('SELF.ANCHOR1: ' , self.anchor1) 
        print('SELF.ANGLE1: ', self.angle1)
        print('SELF.L1:', self.l1)
        # self.initialAnchor1 = self.anchor1 

        self.anchor2 , self.angle2, self.l2 = self.calculateAnchorAngleLine(connectedTraces['p2'] , 'p2') 
        # self.initialAnchor2 = self.anchor2 

        self.li1 = QGraphicsLineItem() # Create/addToScene a standin QGLI representing our adjusted trace. QGLIs do not go into the scene.rtree. Add TraceItems upon mouseReleaseEvent; when user indicates they are done editing a trace.
        self.li1.setPen(QPen(Qt.red, self.traceWidth() , c = Qt.PenCapStyle.RoundCap)) 
        self.scene().addItem(self.li1) 
            
        self.li2=QGraphicsLineItem()
        self.li2.setPen(QPen(Qt.green, self.traceWidth(), c = Qt.PenCapStyle.RoundCap ))
        self.scene().addItem(self.li2)

        self.li3 = QGraphicsLineItem()
        self.li3.setPen(QPen(Qt.blue , self.traceWidth() , c = Qt.PenCapStyle.RoundCap))
        self.scene().addItem(self.li3)
        
    # def calculateL3(self): # Find l3, line // to l0 thru point (seeker.pos)
    #     x3, y3 = self.scene().seeker.scenePos().toTuple()
        
    #     self.setSlope()    
    #     m3 = self.slope() # bc // 
    #     if m3 == 'undefined': # If slope is vertical its undefined 
    #         self.l3 = QLineF(x3, -1e9, x3, 1e9) # A vertical line offset at x 
            
    #     else: 
            
    #         b3  = y3 - m3*x3 # y = m3*x + b3
    #         # self.l3 = QLineF(0 , b3 , 1e9, (m3*1e9)+b3) # pick any two xs; choose zero and 1, calculate their y, then amke a line out of it. This must be updates with intersecctions to l1, and l2, else our l3 spans from x=0 to x=1 . BAD Using x=0 to x=1 causes a short segment, susceptible to floating point errors-- MUST use a large enough number to avoid this, instead of choosing x=0 and x=1, choose x = -1e9 and x= 1e9
    #         self.l3 = QLineF(-1e9 , (m3*-1e9) + b3 , 1e9, (m3*1e9)+b3) # pick any two xs; -1e9 and 1e9, calculate their y, then amke a line out of it. This must be updated with intersections to l1, and l2, else our l3 spans from -1e9 to 1e9 . BAD Using x=0 to x=1 causes a short segment, susceptible to floating point errors-- MUST use a large enough number to avoid this, instead of choosing x=0 and x=1, choose x = -1e9 and x= 1e9 ( Ok thats not that large, choose e9)
    #     # print("l3/l0 intersection:" , self.intersects(self.l0, self.l3) )
    #     # l3 SHOULD be parallel to l0, but they are not, because of floats: l3/l0 intersection: (<IntersectionType.UnboundedIntersection: 2>, PySide6.QtCore.QPointF(10211650317874956.000000, 10211650317874960.000000))
    #     print('L3.ANGLE:', self.l3.angle())
    #     self.li3.setLine(self.l3) # Will be overwritten. good for debugging
               
    # def adjust(self): # After trace laid, drag it around to adjust it 
    #     print()
    #     print('ADJUST')
    #     self.li3.show() # May be hidden sometimes but we want it to show up again sometimes
        
    #     self.calculateL3()
    #     self.seekerOrientation = Utils.threePointOrientation( self.l0.p1() , self.l0.p2(), self.scene().seeker.scenePos() )# , verbose = True)
    #     print("SELF.SEEKER_ORIENTATION:", self.seekerOrientation)
        
    #     self.manageL1() 
    #     self.manageL2() 
        
    #     self.li3.setLine(QLineF(self.li1.line().p2() , self.li2.line().p2()))
        
    #     if (self.seekerOrientation == 1) or (self.seekerOrientation) == 2: 
    #         self.previousSeekerSide = self.seekerOrientation # Update previous seeker side if we were on a side; don't update it if we were at 0;inline.
              
    #     if ( not self.li1.line().isNull() ) and ( not self.li2.line().isNull() ): 
    #         segmentIntersectionLi1Li2 = self.segmentIntersection(self.li1.line(), self.li2.line()) # Check if l1/l2 SEGMENTS intersect, this can happen if both are acute and they 'overshoot' each other. We do NOT want to see this 'overshoot', so clip them at their intersection, if they do intersect. Also note that we don't care if their lines of infinite length intersect, just their segments. 
    #         if segmentIntersectionLi1Li2: 
    #             print('SEGMENT1and2 INTERSECT:', segmentIntersectionLi1Li2)
    #             # self.li1.line().setP2(segmentIntersectionLi1Li2) LineItems cannot modify their lines, they must have a new line set. So this won't do anything. Fails silently
    #             # self.li2.line().setP2(segmentIntersectionLi1Li2)
    #             self.li1.setLine(QLineF(self.li1.line().p1() , segmentIntersectionLi1Li2)) # Unfortunately, just to set P2, we have to set a whole new line bc QGLIs can't mutate their line. 
    #             self.li2.setLine(QLineF(self.li2.line().p1() , segmentIntersectionLi1Li2))
    #             self.li3.hide() 
                
        
    # def mouseMoveEvent(self, event): # Reimplement so user can move traces by grabbing on a line
    #     # print()
    #     # print('TRACE_ITEM.MOUSEMOVEEVENT')  
            
    #     self.adjust()
    #     # self.setLine(self.li3.line()) # Update actual line info based of li3 NO BAD we actually just delete self & slap on some net Traces rather than updating trace.
 
    def mouseMoveEvent(self, event): 
        self.moved = True 
        self.li3.show() # May be hidden later 
        # self.t0.hide() # hide self, l8r will be removed from scene in mre 
        print()
        
        if not self.seekerSide: # If seekerSide is still 0, then we have not moved to a side, and we can return 
            print('SEEKER NOT YET MOVED TO EITHER SIDE ')
            return 
        else: # if we have a seeker side, we want to...  
            print('SEEKER IS ON A SIDE ')
            
        self.seekerOrientation = Utils.threePointOrientation(self.l0.p1() , self.l0.p2() , self.scene().seeker.scenePos())
        print('SEEKERORIENTATION:', self.seekerOrientation)
        
        if self.seekerOrientation: # Set the seeker side to 1 or 2 but not 0
            self.seekerSide = self.seekerOrientation
            print('SEEKERSIDE:', self.seekerSide)
            
        if self.seekerOrientation == 0: # if seeker is inline w/ l0: 
            self.li3.setLine(QLineF(self.l0.p1() , self.l0.p2())) # Make li3 into origional lineItem
        
        # if self.seekerSide != self.previousSeekerSide: # then switched sides 
        #     print('SWITCHED SIDES')
        if self.angle1 == 'acute': 
            print('L1ANCHORS:', self.l1Anchors)
            print('L1S:', self.l1s)
            self.anchor1 = self.l1Anchors.get(self.seekerSide , self.l0.p1()) # Get the anchor or set it to p1 if no anchor recorded 
            self.l1 = self.l1s[self.seekerSide]
            

        if self.angle2 == 'acute': 
            print('L2ANCHORS:', self.l2Anchors)
            print('L2S:', self.l2s)
            self.anchor2 = self.l2Anchors.get(self.seekerSide , self.l0.p2()) 
            self.l2 = self.l2s[self.seekerSide]

        self.l3 = self.lineOffsetThroughPoint(self.l0 , self.scene().seeker.scenePos())
        
        isectL1L3 = self.intersection(self.l1, self.l3)  #NONETYPE l1 
        print('isectL1L3:', isectL1L3.toPoint())
        self.li1.setLine(QLineF(self.anchor1, isectL1L3)) # This may set                     


        isectL2L3 = self.intersection(self.l2, self.l3) 
        self.li2.setLine(QLineF(self.anchor2 , isectL2L3))
        
        self.li3.setLine( QLineF( self.li1.line().p2() , self.li2.line().p2() ))
        
        if self.seekerOrientation: 
            self.previousSeekerSide = self.seekerOrientation # Update previous seeker side if we were on a side; don't update it if we were at 0;inline.

        if ( not self.li1.line().isNull() ) and ( not self.li2.line().isNull() ): 
            segmentIntersectionLi1Li2 = self.segmentIntersection(self.li1.line(), self.li2.line()) # Check if l1/l2 SEGMENTS intersect, this can happen if both are acute and they 'overshoot' each other. We do NOT want to see this 'overshoot', so clip them at their intersection, if they do intersect. Also note that we don't care if their lines of infinite length intersect, just their segments. 
            if segmentIntersectionLi1Li2: 
                print('SEGMENT1and2 INTERSECT:', segmentIntersectionLi1Li2)
                # self.li1.line().setP2(segmentIntersectionLi1Li2) LineItems cannot modify their lines, they must have a new line set. So this won't do anything. Fails silently
                # self.li2.line().setP2(segmentIntersectionLi1Li2)
                self.li1.setLine(QLineF(self.li1.line().p1() , segmentIntersectionLi1Li2)) # Unfortunately, just to set P2, we have to set a whole new line bc QGLIs can't mutate their line. 
                self.li2.setLine(QLineF(self.li2.line().p1() , segmentIntersectionLi1Li2))
                self.li3.hide() 
                 
    # def acuteFlip(self, axis, p1orp2): #-> QLineF, representing self, a line 45degrees acute to axis, flipped about axis. This function is to get the angle of the flipped line correct. The points of the flipped line will be wrong. 
    #     print('acute_flip')
    #     print('AXIS.ANGLE():', axis.angle())
    #     ori = Utils.threePointOrientation(axis.p1() , axis.p2() , self.scene().seeker.scenePos())
    #     if ori == 0: 
    #         raise ValueError(f"ori is 0 but expected seeker to be to a side of axis")
    #     if p1orp2 == 'p1': 
    #         l = QLineF(axis.p1() , QPointF(1e9, 1e9)) # Note, l will be overwritten shortly after l is returned. Thus, we can/will for from axis.p2() rather than, say, anchorn, which we would need to pass in as a parameter. 
            
    #         if ori == 1 : #clockwise: 
    #             l.setAngle(axis.angle() - 45)   
    #         elif ori == 2: # counterClockwise
    #             l.setAngle(axis.angle() + 45)
    #         return l
        
    #     elif p1orp2 == 'p2':
    #         l = QLineF(axis.p2() , QPointF(1e9,1e9))
    #         if ori == 1: # clockwise: 
    #             l.setAngle(axis.angle() - 135) 
    #         elif ori == 2: 
    #             l.setAngle(axis.angle() + 135) 
    #         return l 
        


#     def manageL1(self): 
#         print('INITIALIZING L1')
        
#         if self.l1 is None: # If were no connected traces we must initialize l1
#             if self.seekerOrientation: 
#                 self.l1 = QLineF(self.anchor1 , self.arbitrary) # Draw line to an arbitrary point, b/c if line is of 0 length, .setAngle and more don't work 
#                 if self.seekerOrientation == 1: # if seeker clockwise: loose 45 degrees else gain 45 degrees. 
#                     self.l1.setAngle(self.l0.angle() - 45) # Give l1 an acute angle to l0 # Side acute angle depends on side seeker dragged to, yes?  
                    
#                 elif self.seekerOrientation == 2: 
#                     self.l1.setAngle(self.l0.angle() + 45) # Set an acute angle. May be overwritten , if seekerOrientation is to a side.
#             else: # If there were no connectedTraces, then self.l1 is None. If seeker is not to a side yet, nothing to do with li1
#                 return 
# # Thick traces may see seeker offset from centerline. Can detect side of such offset, and initialize l1 to that side...

#         if self._angle1 == 'perpendicular' or self._angle1 == 'obtuse': # obtuse and perpendicular cases 
#             print('ANGLE1 PERPENDICULAR OR OBTUSE')
#             # self.l1.setPoints(self.anchor1, self.intersection(self.l1, self.l3)) l1 a typo meant to be li1? 
#             self.li1.setLine(QLineF(self.anchor1, self.intersection(self.l1, self.l3)))
#             if not self.l1.angle() % 45 != 0: 
#                 print('WARNING: SELF.L1.ANGLE():', self.l1.angle())
            
#         elif self._angle1 == 'acute': # If l1 is acute with l0: 
#             print('ANGLE1 ACUTE')
#             # print('L1:', self.l1)
#             # print('L3:', self.l3)
            
#             if self.seekerOrientation == 0: # if seeker is inline w/ l0: 
#                     print('Seeker and anchor are inline with l0')
#                     self.li3.setLine(QLineF(self.l0.p1() , self.l0.p2())) # Make li3 into origional lineItem

#             elif self.seekerOrientation != 0: 
#                 print('PREVIOUS SEEKER SIDE:', self.previousSeekerSide)
#                 # if self.previousSeekerSide and ( self.seekerOrientation == self.previousSeekerSide ): # Ignore if previous_seeker_side still equals 0 
#                 #     pass

#                 if self.previousSeekerSide and ( self.seekerOrientation != self.previousSeekerSide ): 
#                     print('SEEKER CROSSED SIDES')
#                     # print(self.l1.p1() == self.l0.p1())
#                     if self.initialAnchor1Orientation == self.seekerOrientation: # If init_anch side is skr side, use init_anch as anch. Otherwise, anchor on l0.p1
#                         self.anchor1 = self.initialAnchor1
#                     else: 
#                         self.anchor1 = self.l0.p1() 
#                     print('SELF.L1.ANGLE() B4:', self.l1.angle())
#                     self.l1 = self.acuteFlip(self.l0 , 'p1') # Remake l1 so that its flipped about l0. ( Umm, add 270 degrees? Does that always work? )
#                     print('SELF.L1.ANGLE() AFTER', self.l1.angle()) # Uhh it stayed 45 degrees...
                
                    
#             isectL1L3 = self.intersection(self.l1, self.l3) 
#             print('isectL1L3:', isectL1L3.toPoint())
#             self.li1.setLine(QLineF(self.anchor1, isectL1L3)) # This may set 

#     def angle2(self): 
#         PI = math.pi
        
#         alpha   = math.atan2( - self.l0.dy() , self.l0.dx() )
#         beta    = math.atan2( - self.l2.dy() , self.l2.dx() ) 

#         theta = self.normalizeAngle( beta - alpha )

#         if theta == math.pi/4: 
#             print('ANGLE1 ACUTE') 
#             return 'acute'
#         elif theta == PI/2 or theta == 3*PI/2: 
#             print('ANGLE1 PERPENDICULAR') 
#             return 'perpendicular' 
#         elif theta == 3*PI/4 or theta == 5*PI/4: 
#             print('ANGLE1 OBTUSE') 
#             return 'obtuse'

#     def manageL2(self): 
#         print('INITIALIZING L2')

#         if self.l2 is None: 
#             if self.seekerOrientation:
#                 self.l2 = QLineF( self.anchor2 , self.arbitrary) 
#                 if self.seekerOrientation == 1: 
#                     self.l2.setAngle(self.l0.angle() - 135) 
#                 elif self.seekerOrientation == 2: 
#                     self.l2.setAngle(self.l0.angle() + 135) 
#             else: 
#                 return 
#         # if self.l2 is None: # If were no connected traces we must initialize l2
#         #     print('INITIALIZING L2')
#         #     self.l2 = QLineF(self.anchor1 , self.arbitrary) # Draw line to an arbitrary point, b/c if line is of 0 length, .setAngle and more don't work 
#         #     self.l2.setAngle(self.l0.angle() + 135) # Set an acute angle. May be overwritten , if seekerOrientation is to a side.

#         #     if self.seekerOrientation: # Thick traces may see seeker offset from centerline. Can detect side of such offset, and initialize l2 to that side...
#         #         if self.seekerOrientation == 1: # if seeker clockwise: loose 45 degrees else gain 45 degrees. 
#         #             self.l2.setAngle(self.l0.angle() - 135) # Give l2 an acute angle to l0 # TODO: Side acute angle is on depends on side seeker dragged to, yes?  Must wait until MoveEvent
#         #         # if self.seekerOrientation == 2: # if ccw 
#         #         #     self.l2.setAngle(self.l0.angle() +45) 
                        
#         # if not self._angle2: # If was a single connected Trace, detect angle, otherwise, we already set angle 'acute'
#         #     self.angle2()
        
        
#         if self._angle2 == 'perpendicular' or self._angle2 == 'obtuse': # obtuse and perpendicular cases 
#             self.li2.setLine(QLineF(self.anchor2, self.intersection(self.l2, self.l3)))
#             if not self.l2.angle() % 45 != 0: 
#                 print('WARNING: SELF.L2.ANGLE():', self.l2.angle())
            
#         elif self._angle2 == 'acute': # If l2 is acute with l0: 
#             if self.seekerOrientation == 0: # if seeker is inline w/ l0: 
#                 self.li3.setLine(QLineF(self.l0.p1() , self.l0.p2()))
#                 isect_l2_l3 = self.intersection(self.l2, self.l3) 
#                 self.li2.setLine(QLineF(self.anchor2, isect_l2_l3)) # This may set a null line. That is handled later
#                 # print('Seeker and anchor are inline with l0')
#             elif self.seekerOrientation != 0: 
#                 # print('PREVIOUS SEEKER SIDE:', self.previous_seeker_side)
#                 if self.previousSeekerSide and ( self.seekerOrientation == self.previousSeekerSide ): # Ignore if previous_seeker_side still equals 0 
#                     # print('seeker remains on same side ')
#                     isect_l2_l3 = self.intersection(self.l2, self.l3) 
#                     self.li2.setLine(QLineF(self.anchor2, isect_l2_l3)) # This may set 
#                     # print('isect_l2_l3:', isect_l2_l3.toPoint())
#                 elif self.previousSeekerSide and ( self.seekerOrientation != self.previousSeekerSide ): 
#                     # print('SEEKER CROSSED SIDES')
#                     print(self.l2.p2() == self.l0.p2())
#                     if self.initialAnchor2Orientation == self.seekerOrientation: # If init_anch side is skr side, use init_anch as anch. Otherwise, anchor on l0.p2
#                         self.anchor2 = self.initialAnchor2
#                     else: 
#                         self.anchor2 = self.l0.p2() 
                        
#                     # print('SELF.L2.ANGLE() B4:', self.l2.angle()) # L2.ANGLE(): 44.999999999999986

#                     self.l2 = self.acuteFlip(self.l0 , 'p2') # Remake l2 so that its flipped about l0. 
#                     # print('SELF.L2.ANGLE() AFTER', self.l2.angle())
                    
#                     isect_l2_l3 = self.intersection(self.l2, self.l3) 
#                     self.li2.setLine(QLineF(self.anchor2, isect_l2_l3)) # This may set 
#                     # print('isect_l2_l3:', isect_l2_l3.toPoint())





        

    
    

        
    # def setSlope(self):
    #     # if self.l0.x1() == self.l0.x2(): # In this case, vertical line, slope is undefined
    #     if self.l0.x1() == self.l0.x2(): 
    #         self._slope = 'undefined' # I was using float('nan') but stopped because nan == nan is False, so its very hard to know if your float is nan. I don't like nan. Consider False 'undefined' None instead 
    #     else:
    #         self._slope = ( self.l0.y2() - self.l0.y1() ) / ( self.l0.x2() - self.l0.x1() ) # slope equals rise over run # SLOPE: -1.6928932644993518e-16
    #         self._slope = round(self._slope, 9)
    #     print('SLOPE:', self._slope)

    # def slope(self):
    #     return self._slope

#     def mouseReleaseEvent(self, event):
#         print('TRACE.RELEASEEVENT')
#         super().mouseReleaseEvent(event) # call MyGraphicsObject.mRE to remove the trace, the trace we clicked on, self,  from the rtree, then put it BACK in the rtree, with its new position... which is useless... because we next .removeItem(self.t0)... but 
        
# # add TraceItems to scene, if we were adjusting a trace, based on li123.
#         # if self.adjusting: 
#         #     self.adjusting = False

#         if not self.l1.isNull():
#             t1 = Trace.fromPoints(self.layers() , self.traceWidth(), p1 = self.li1.line().p1() , p2 = self.li1.line().p2()) # not out of l1, but out of 1i1.line()
#             # t1 = TraceItem(self.traceWidth(), self.layer(), self.li1.line()) # not out of l1, but out of 1i1.line()
#             # t1.setPen(QPen(Qt.red, self.traceWidth() ,c = Qt.RoundCap))
#             self.scene().addItem(t1)
            
#         if not self.l2.isNull():
#             t2 = Trace.fromPoints(self.layers() , self.traceWidth(), self.li2.line().p1() , self.li2.line().p2())
#             # t2 = TraceItem(self.traceWidth(), self.layer(), self.li2.line())

#             # t2.setPen(QPen(Qt.green, self.traceWidth(), c= Qt.RoundCap))
#             self.scene().addItem(t2)
            
#         if not self.l3.isNull() and self.li3.isVisible():
#             t3 = Trace.fromPoints(self.layers(), self.traceWidth()  , self.li3.line().p1() , self.li3.line().p2())
#             # t3 = TraceItem(self.traceWidth() , self. layer() , self.li3.line())
                
#             # t3.setPen(QPen(Qt.blue, self.traceWidth(), c = Qt.RoundCap))
#             self.scene().addItem(t3)
            
    
#         self.scene().removeItem(self.li1)
#         self.scene().removeItem(self.li2) # Li2 is None why
#         self.scene().removeItem(self.li3)
#         # self.scene().removeItem(self.test_item)
        
#         self.scene().removeItem(self.t0) # t0 is self, always removed after an adjust
        
#         # self.l0 = None             # No need to reset, bc we delete self anyway
#         # self.l1 = None 
#         # self.l2 = None 
#         # self.l3 = None

#         # self.li1 = None 
#         # self.li2 = None 
#         # self.li3 = None 
        
#         # self.t0 = None 
#         # self.t1 = None 
#         # self.t2 = None
#         # self.t3 = None 

#         # self.initialAnchor1 = None # In case we adjust same trace again reset everything
#         # self.initialAnchor2 = None 
#         # self.anchor1 = None 
#         # self.anchor2 = None 
#         # self._angle1 = None 
#         # self._angle2 = None
#         # self.previousSeekerSide = None 
 
    def mouseReleaseEvent(self, event):
        print('TRACE.RELEASEEVENT')
        super().mouseReleaseEvent(event) # call MyGraphicsObject.mRE to remove the trace, the trace we clicked on, self,  from the rtree, then put it BACK in the rtree, with its new position... which is useless... because we next .removeItem(self.t0)... but 
        
# add TraceItems to scene, if we were adjusting a trace, based on li123.
        # if self.adjusting: 
        #     self.adjusting = False

        if (self.l1 is not None) and (not self.l1.isNull()):
            t1 = Trace.fromPoints(self.layers() , self.traceWidth(), p1 = self.li1.line().p1() , p2 = self.li1.line().p2()) # not out of l1, but out of 1i1.line()
            # t1 = TraceItem(self.traceWidth(), self.layer(), self.li1.line()) # not out of l1, but out of 1i1.line()
            # t1.setPen(QPen(Qt.red, self.traceWidth() ,c = Qt.RoundCap))
            self.scene().addItem(t1)
            
        if (self.l2 is not None) and (not self.l2.isNull()):
            t2 = Trace.fromPoints(self.layers() , self.traceWidth(), self.li2.line().p1() , self.li2.line().p2())
            # t2 = TraceItem(self.traceWidth(), self.layer(), self.li2.line())

            # t2.setPen(QPen(Qt.green, self.traceWidth(), c= Qt.RoundCap))
            self.scene().addItem(t2)
            
        if (self.l3 is not None) and (not self.l3.isNull()) and (self.li3.isVisible()):
            t3 = Trace.fromPoints(self.layers(), self.traceWidth()  , self.li3.line().p1() , self.li3.line().p2())
            # t3 = TraceItem(self.traceWidth() , self. layer() , self.li3.line())
                
            # t3.setPen(QPen(Qt.blue, self.traceWidth(), c = Qt.RoundCap))
            self.scene().addItem(t3)
            
    
        self.scene().removeItem(self.li1)
        self.scene().removeItem(self.li2) # Li2 is None why
        self.scene().removeItem(self.li3)
        # self.scene().removeItem(self.test_item)
        
# Dont remove self.t0, if we only did a press-release
        if self.moved: 
            self.scene().removeItem(self.t0) # t0 is self, always removed after an adjust

    @staticmethod 
    def normalizeAngle(angle):
        while angle > 360: 
            angle-=360
        while angle < 360: 
            angle += 360 
        return angle 

    @staticmethod
    def intersection(line1, line2): # return intersection point of two QLine/Fs, or None if lines are  // parallel OR collinear OR one or both lines is of zero length. So QLineFs have a segment, defined by their two points, but this function will return intersection point where those lines intersect outside of their segment bounds. Compare against segments_intersect, which returns None if lines intersect outside their segments. 
        print('LINE1:', line1)
        print('LINE2:', line2)
        if line1.length() == 0 or line2.length() == 0: # Note distinction between l123 being of 0 length and li123 being of 0 length. l123 cannot be of 0 length, but li123 can be(and li are not used in this function)
            raise ValueError(f"line1.length(): {line1.length()} line2.length(): {line2.length()} but both lines must be of non-zero length to test intersection")

        intersection_type, intersection_point = line1.intersects(line2) # QLineF.intersects() is highly quirky
        
        if intersection_type is QLineF.IntersectionType.NoIntersection: 
            return None
        elif intersection_type is QLineF.IntersectionType.UnboundedIntersection:
            return intersection_point # Idc if the infinite length lines intersect, I only care if the segments intersect
        elif intersection_type is QLineF.IntersectionType.BoundedIntersection:
            return intersection_point

    @staticmethod
    def segmentIntersection(line1, line2): # Returns the intersection point, if segments intersect, else None. So if the infinitely long lines intersect outside of their segments, return None 
        if line1.length() == 0 or line2.length() == 0: 
            raise ValueError(f"line1.length(): {line1.length()} line2.length(): {line2.length()} but both lines must be of non-zero length to test intersection")
        
        intersection_type, intersection_point = line1.intersects(line2)
        if intersection_type == QLineF.IntersectionType.NoIntersection: 
            return None
        elif intersection_type == QLineF.IntersectionType.UnboundedIntersection:
            return None 
        elif intersection_type == QLineF.IntersectionType.BoundedIntersection:
            return intersection_point
    @staticmethod 
    def lineOffsetThroughPoint(line , point):
        offset = line.p1() - point
        p1 = line.p1() - offset
        p2 = line.p2() - offset 
        
        l = QLineF(p1 , p2) 
        return l
    
    @classmethod
    def fromPoints(cls, layers, traceWidth, p1, p2): 
        return cls( p1.x() , p1.y() , p2.x() , p2.y() , layers=layers, traceWidth=traceWidth, )


    def hoverEnterEvent(self, event):
        current_tooltip = self.toolTip()
        self.setToolTip(f"{current_tooltip}\nP1: {self.line().p1()}\nP2: {self.line().p2()}") 
        super().hoverEnterEvent(event)

    def clone(self):
        return TraceItem(self.traceWidth() , self.layer() , self.line())


