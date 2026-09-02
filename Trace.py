from utils import * 
from CopperItemContainer import CopperItemContainer
from Net import Net 

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

# Trace.boundingRect is returning a null rect...
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
            # bR = QRectF( lx, ty , rx - lx , by - ty)
            # print('TRACE.BOUNDINGRECT:', bR)
            # return bR
        return self.shape().controlPointRect() # Seems to return OK values 
        # cPR = self.shape().controlPointRect() 
        # print()
        # print('TRACE.CONTROLPOINTRECTANGLE:', cPR)
        # print('X1,Y1,X2,Y2:', self._x1, self._y1, self._x2, self._y2)
        # return cPR
    
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
    def __init__(self, x1, y1, x2, y2, layers, traceWidth, net=Net(), parent=None, *args, **kwargs ): 
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, layers = layers, traceWidth=traceWidth, parent=parent, *args, **kwargs)
        self._x1 = x1 
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2 
        self._traceWidth = traceWidth
        self._net = net 

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
    
    @classmethod 
    def fromLine(cls, line, traceWidth , layers, net = Net()):
        return cls( x1=line.p1().x() , y1=line.p1().y() , x2=line.p2().x() , y2=line.p2().y(), layers=layers, traceWidth=traceWidth, net=net)

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
        self.setSceneTerminals() 
        self.updateRtree()
        
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
        x1,y1= self.mapToScene(self.line().p1()).toTuple() # Think this equivalent to below 
        # x1,y1= self.line().p1().toTuple() 
        p1Bounds =  (x1,y1, x1,y1)
        return p1Bounds 
    
    def p2SceneBounds(self):
        x2,y2 = self.line().p2().toTuple()
        p2Bounds = (x2,y2, x2, y2)
        return p2Bounds 
    
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
        print('P1SceneBounds:', self.p1SceneBounds())
        
        for layer in self.layers(): 
            print('LAYER:', layer)
            print('RTREE HITS FOR p1SceneBounds:', list(self.scene().rtrees[layer].intersection(self.p1SceneBounds())))
            ids1.extend( self.scene().rtrees[layer].intersection(self.p1SceneBounds()) ) # Hits at p1 
            ids2.extend( self.scene().rtrees[layer].intersection(self.p2SceneBounds()) ) # Hits at p2 

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
                    print('P1: NEITHER p1 NOR p2 MATCHES UP' )
        for hitItem in hitItems2: 
            if isinstance(hitItem, Trace):
                if (hitItem.line().p1() == self.l0.p2()):
                    distal = hitItem.line().p2() # We may need to know connected_trace's distal point, to use as anchor
                    connectedTraces['p2'].append( ( hitItem , distal ) )
                elif ( hitItem.line().p2() == self.l0.p2()): 
                    distal = hitItem.line().p1()
                    connectedTraces['p2'].append( ( hitItem , distal ) )
                else: 
                    print('P2: NEITHER p1 NOR p2 MATCHES UP' )
        print('CONNECTEDTRACES:', connectedTraces)
        return connectedTraces

    def angleBetween(self, lineA, lineB): 
        # determines the angle between two lines 
        PI = math.pi
        
        alpha   = math.atan2( - lineA.dy() , lineA.dx() )
        beta    = math.atan2( - lineB.dy() , lineB.dx() ) 

        theta = self.normalizeAngleRadians( beta - alpha ) # Example value, which is way off: 361.5707963267949. So we must snap to nearest 45 degrees 
        theta = self.snapAngleRadians(theta)

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
    
    def mousePressEvent(self, event): 
        self.l0 = self.line()
        self.t0 = self # Not a typo, self is Trace0
        self.l3 = None 
        self.adjusted = False # Flag if we did a mouseMoveEvent
        
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
 
    def mouseMoveEvent(self, event): 

        self.li3.show() # May be hidden later 
        # self.t0.hide() # hide self, l8r will be removed from scene in mre 
        print()
            
        self.seekerOrientation = Utils.threePointOrientation(self.l0.p1() , self.l0.p2() , self.scene().seeker.scenePos())
        print('SEEKERORIENTATION:', self.seekerOrientation)
        
        if self.seekerOrientation: # Set the seeker side to 1 or 2 but not 0
            self.seekerSide = self.seekerOrientation
            print('SEEKERSIDE:', self.seekerSide)
        
        if not self.seekerSide: # If seekerSide is still 0, then we have not moved to a side, and we can return 
            print('SEEKER NOT YET MOVED TO EITHER SIDE ')
            return 
        else: # if we have a seeker side, we want to...  
            self.adjusted = True 
            print('SEEKER IS ON A SIDE ')
            
        if self.seekerOrientation == 0: # if seeker is inline w/ l0: 
            self.li3.setLine(QLineF(self.l0.p1() , self.l0.p2())) # Make li3 into origional lineItem
        

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
        self.li1.setLine(QLineF(self.anchor1, isectL1L3)) # This may set Null


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
                 
    def mouseReleaseEvent(self, event):
        print('TRACE.RELEASEEVENT')
        super().mouseReleaseEvent(event) # call MyGraphicsObject.mRE to remove the trace, the trace we clicked on, self,  from the rtree, then put it BACK in the rtree, with its new position... which is useless... because we next .removeItem(self.t0)... but 
        
# add TraceItems to scene, if we were adjusting a trace, based on li123.
        # if self.adjusting: 
        #     self.adjusting = False

        if (self.l1 is not None) and (not self.l1.isNull()):
            if self.li1.line().isNull(): print('WARNING LI1 IS NULL')
            t1 = Trace.fromPoints(self.layers() , self.traceWidth(), p1 = self.li1.line().p1() , p2 = self.li1.line().p2()) # not out of l1, but out of 1i1.line()
            # t1 = TraceItem(self.traceWidth(), self.layer(), self.li1.line()) # not out of l1, but out of 1i1.line()
            # t1.setPen(QPen(Qt.red, self.traceWidth() ,c = Qt.RoundCap))
            self.scene().addItem(t1)
            
        if (self.l2 is not None) and (not self.l2.isNull()):
            if self.li2.line().isNull(): print('WARNING LI2 IS NULL')
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
        if self.adjusted:
            self.scene().removeItem(self.t0) # t0 is self, always removed after an adjust

    @staticmethod 
    def normalizeAngleDegrees(angle):
        while angle > 360: 
            angle-=360
        while angle < 360: 
            angle += 360 
        return angle
     
    @staticmethod 
    def normalizeAngleRadians(angle):
        PI = math.pi
        while angle > 2*PI:
            angle -= 2*PI
        while angle <2*PI:
            angle += 2*PI
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


    def snapAngleRadians(self , angle, snapTo=math.pi/4): # angle in radians. return angle snapped to nearest multiple of snapTo, default pi/4
        
        angle = round(angle / (snapTo)) * snapTo # pemdas 12/3/4 different 12/(3/4)
        # print('SNAPPED TO ANGLE(degrees):', angle *180/math.pi)
        return self.normalizeAngleRadians(angle) 