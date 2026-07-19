from utils import * 

class TraceItem(CopperItemContainer, QGraphicsLineItem):
    # QGLI has no .setBrush only .setPen
    def __init__(self, traceWidth, layers, line=QLineF()): 
        super().__init__()#layer, line) 
        # self._color                 = Utils.layerColors[layer] 
        self.setTraceWidth(traceWidth) 
        self.setLayers(layers)
        self.setLine(line) # crashes kernel
        self.setBounds() # Note that this'll be (0000) for 'blank' traceItems
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable) 
        
        self.previous_seeker_side = None # Store the side the seeker was last on. Equals 1 for cw side or 2 for ccw side. Never set equal to 0 only 1 or 2.  
        self.adjusting = False # Track whether we are adjusting this trace's position
        self._net = None 

        self._slope = None # If slope is undefined, slope is set to the string 'undefined' otherwise slope is a float
        
        self.l0 = None # l as in QLineF. l0 is self, this TraceItem's QLineF. lines l0123 will NOT mutate after they are created, because they must never be set to 0 length, because that sets their angle to -0.0, but we need that angle info. All the math is done with QLineFs. Only when we're done with maths do we update lineitems li0123. li123 are NOT updated with l0123, because l0123 are arbitrarily long. Instead, we create new, nameless QLineFs to pass to QGLI.setLine(). 
        self.l1 = None 
        self.l2 = None 
        self.l3 = None
        
        self.li1 = None  # li as in lineItem. QGraphicsLineItems cannot mutate their own lines, so QGLI.line().set(P1,P2,Points,Angle) will all silently fail. This is a bitch of a gotcha. To edit a QGLI's line, you must set a wholly new line; use li.setLine(QLineF) every time you want to update a QGLI with a new line. 
        self.li2 = None 
        self.li3 = None 
        
        self.ti0 = None # t as in TraceItem. The TraceItem representing l0 ( aka self, this traceItem ) 
        self.ti1 = None 
        self.ti2 = None
        self.ti3 = None 
        
        
        self.initial_anchor1_orientation = None
        self.initial_anchor1 = None 
        self.initial_anchor2 = None 
        self.arbitrary = QPointF(-1e3, -1e3)        

        
    def queryRtrees(self, layer):
        """query MainWindow.rtrees[layer] for trace"""
        print('self.bufferedBounds():', self.bufferedBounds())
        hitIds = self.scene().rtrees[layer].intersection(self.bufferedBounds())
        hitItems = [self.scene().ids[hitId] for hitId in hitIds]
        return hitItems
        
    def nearestSceneSnap(self, pos):
        """return the snappable point nearest to 'pos'. p1 and p2 are possible snap points for traces. Pads, zones, and vias have just one snap point; their centroid"""
        # calculate distance from p1,p2 to pos 
        # calculate min distance and return corresponding point
        
        if Utils.distance(pos, self.p1()) <= Utils.distance(pos, self.p2()): 
            return self.p1() 
        else: 
            return self.p2()
    
    def netCollision(self): # Returns true if there are any net collisions, else False. A net collision occurs when two items overlap, on the same layer, with different, nonNone, nets.
        hitItems = self.queryRtrees(self.scene().activeLayer()) 
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
        self.setBufferDistance(self._traceWidth) # Crashes kernel
        print('SETTRACEWIDTH DONE')
    def terminals_hits(self):# Return items queried from p1/p2
        ids1 = self.scene().idx.intersection(self.p1_bounds())
        ids2 = self.scene().idx.intersection(self.p2_bounds())
        items = [ self.scene().ids[id] for id in ids1.extend(ids2) ]

    def p1(self):
        return self.line().p1()
    def p2(self):
        return self.line().p2() 
    
    def p1_bounds(self):
        x1,y1= self.line().p1().toTuple()
        p1_bounds =  (x1,y1, x1,y1)
        return p1_bounds 
    
    def p2_bounds(self):
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
            otherItem.setPos(self.mapToScene(self.line.p1()))
            return True

        elif otherItem.contains(self.mapToScene(self.line().p2())):
            otherItem.setPos(self.mapToScene(self.line().p2()))
            return True 
        
    def mouseDoubleClickEvent(self,event):
        print()
        print('TRACEITEM.MOUSEDOUBLECLICKEVENT')
        super().mouseDoubleClickEvent(event) # Base implelentation calls mousePressEvent
        
    # def mousePressEvent(self, event): 
    #     print()
    #     print('TRACEITEM.MOUSEPRESSEVENT')

    #     super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        print('TRACEITEM.RELEASEEVENT')
        super().mouseReleaseEvent(event) # call MyGraphicsObject.mRE to remove the trace, the trace we clicked on, self,  from the rtree, then put it BACK in the rtree, with its new position... which is useless... because we next .removeItem(self.ti0)... but 
        
# add TraceItems to scene, if we were adjusting a trace, based on li123.
        if self.adjusting: 
            self.adjusting = False
            if not self.l1.isNull():
                ti1 = TraceItem(self.traceWidth(), self.layer(), self.li1.line()) # not out of l1, but out of 1i1.line()
                ti1.setPen(QPen(Qt.red, self.trace_width ,c = Qt.RoundCap))
                self.scene().addItem(ti1)
                
            if not self.l2.isNull():
                ti2 = TraceItem(self.traceWidth(), self.layer(), self.li2.line())
  
                ti2.setPen(QPen(Qt.green, self.trace_width, c= Qt.RoundCap))
                self.scene().addItem(ti2)
                
            if not self.l3.isNull():
                ti3 = TraceItem(self.traceWidth() , self. layer() , self.li3.line())
                    
                ti3.setPen(QPen(Qt.blue, self.trace_width, c = Qt.RoundCap))
                self.scene().addItem(ti3)
                
        
            self.scene().removeItem(self.li1)
            self.scene().removeItem(self.li2) # Li2 is None why
            self.scene().removeItem(self.li3)
            self.scene().removeItem(self.test_item)
            
            self.scene().removeItem(self.ti0) # ti0 is always removed after an adjust
            
            
            self.l0 = None             
            self.l1 = None 
            self.l2 = None 
            self.l3 = None
            
            self.ti0 = None 
            self.ti1 = None 
            self.ti2 = None
            self.ti3 = None 

    def mouseMoveEvent(self, event): # Reimplement so user can move traces by grabbing on a line
        print()
        print('TRACE_ITEM.MOUSEMOVEEVENT')  
        if not self.adjusting: 
            print()
            print('ADJUSTING')
            self.prepare_adjust()
            
        self.adjust()
        # if self.previous_seeker_side:  # Lock out of adjust() until we initialize previous_seeker_side: We have to know this, cannot guess this ...? 
        #     self.adjust()
        # else: 
        #     self.adjust()
        # t1,t2,t3, may be added to scene upon their creation-- but their rtree bounds must be updated when they are moved... 

    def prepare_adjust(self):


        # while 1: 
        #     pass  # How come this does not lock up the app? 
    

        self.seeker_orientation = self.three_point_orientation(self.line().p1() , self.line().p2() , self.scene().seeker.scenePos()) # Initialize self.seeker_orientation away from None. This should init to 0, indicating seeker is collinear with l0
        self.previous_seeker_side = self.seeker_orientation # initialize previous_seeker_side. Likely will be 0 here.
                
        self.adjusting = True 
        
        self.l0 = self.line()
        self.ti0 = self # Not a typo, self is traceItem0
        self.ti0.setPen(QPen(Qt.magenta, self.trace_width, c = Qt.PenCapStyle.RoundCap))
        self.calculate_anchors() # anchors, li1, li2 
        
        self.li3 = QGraphicsLineItem(None)#, self._net, self.trace_width)
        self.li3.setPen(QPen(Qt.blue, self.trace_width))
        self.scene().addItem(self.li3)
        self.li3.setPen(QPen(Qt.blue, self.trace_width , c=  Qt.PenCapStyle.RoundCap))
        
        self.test_item = QGraphicsEllipseItem(-10,-10,20,20)
        self.test_item.setBrush(Qt.yellow)
        self.scene().addItem(self.test_item) 
                
    def adjust(self): # After trace laid, drag it around to adjust it 
        # print()
        
        self.calculate_l3()
        self.seeker_orientation = self.three_point_orientation( self.l0.p1() , self.l0.p2(), self.scene().seeker.scenePos() )# , verbose = True)
        print("SELF.SEEKER_ORIENTATION:", self.seeker_orientation)
        
        self.angle1()
        self.angle2()
        
        self.li3.setLine(QLineF(self.li1.line().p2() , self.li2.line().p2()))
        
        if (self.seeker_orientation == 1) or (self.seeker_orientation) == 2: 
            self.previous_seeker_side = self.seeker_orientation # Update previous seeker side if we were on a side; don't update it if we were at 0;inline.
              
        if ( not self.li1.line().isNull() ) and ( not self.li2.line().isNull() ): 
            segment_intersect_li1_li2 = self.segments_intersect(self.li1.line(), self.li2.line()) # Check if l1/l2 SEGMENTS intersect, this can happen if both are acute and they 'overshoot' each other. We do NOT want them to 'overshoot' each other, so clip them at their intersection, if they do intersect. Also note that we don't care if their lines of infinite length intersect, just their segments. 
            if segment_intersect_li1_li2: 
                print('SEGMENT1and2 INTERSECT:', segment_intersect_li1_li2)
                # self.li1.line().setP2(segment_intersect_li1_li2) LineItems cannot modify their lines, they must have a new line set. So this won't do anything. Fails silently
                # self.li2.line().setP2(segment_intersect_li1_li2)
                self.li1.setLine(QLineF(self.li1.line().p1() , segment_intersect_li1_li2)) # Unfortunately, just to set P2, we have to set a whole new line bc QGLIs can't mutate their line. 
                self.li2.setLine(QLineF(self.li2.line().p1() , segment_intersect_li1_li2))
            

        # if not self.li1.line().isNull():
        #     self.li1.show()
        # else: 
        #     self.li1.hide()
            
        # if not self.li2.line().isNull():
        #     self.li2.show()
        # else:
        #     self.li2.hide()
            
        # if not self.li3.line().isNull():
        #     self.li3.show()
        # else:
        #     self.li3.hide()
          
#ANGLE1############################################################################################################################################################################################################################################################################
    def angle1(self):
        angle1 = self.l0.angleTo(self.l1)
        if angle1 > 180: 
            angle1 = 360 - angle1 # For obtuses, Subtract from 360, to only deal with the smallest side of the angle. Draw it out
        
        if angle1 >=90: # obtuse and perpendicular cases 
            print('ANGLE1 PERP | OBTUSE')
            # pass
            self.l1.setPoints(self.anchor1, self.intersects(self.l1, self.l3))
            
        elif angle1 < 90: # If l1 is acute with l0: 
            print('ANGLE1 ACUTE')
            print('L1:', self.l1)
            print('L3:', self.l3)
            
            if self.seeker_orientation == 0: # if seeker is inline w/ l0: 
                    print('Seeker and anchor are inline with l0')
                    self.li3.setLine(QLineF(self.l0.p1() , self.l0.p2()))
                    isect_l1_l3 = self.intersects(self.l1, self.l3) 
                    self.li1.setLine(QLineF(self.anchor1, isect_l1_l3)) # This may set a null line. That is handled later
            elif self.seeker_orientation != 0: 
                print('PREVIOUS SEEKER SIDE:', self.previous_seeker_side)
                if self.previous_seeker_side and ( self.seeker_orientation == self.previous_seeker_side ): # Ignore if previous_seeker_side still equals 0 
                    isect_l1_l3 = self.intersects(self.l1, self.l3) 
                    self.li1.setLine(QLineF(self.anchor1, isect_l1_l3)) # This may set 
                    print('isect_l1_l3:', isect_l1_l3)
                elif self.previous_seeker_side and ( self.seeker_orientation != self.previous_seeker_side ): 
                    print('SEEKER CROSSED SIDES')
                    print(self.l1.p1() == self.l0.p1())
                    if self.initial_anchor1_orientation == self.seeker_orientation: # If init_anch side is skr side, use init_anch as anch. Otherwise, anchor on l0.p1
                        self.anchor1 = self.initial_anchor1
                    else: 
                        self.anchor1 = self.l0.p1() 
                        
                    print('SELF.L1.ANGLE() B4:', self.l1.angle())
                    self.l1 = self.acute_flip(self.l0 , 'p1') # Remake l1 so that its flipped about l0. 
                    print('SELF.L1.ANGLE() AFTER', self.l1.angle())
                    
                    isect_l1_l3 = self.intersects(self.l1, self.l3) 
                    self.li1.setLine(QLineF(self.anchor1, isect_l1_l3)) # This may set 
                    print('isect_l1_l3:', isect_l1_l3)
                    # anchor1_l3_orientation = self.three_point_orientation(self.l3.p1() , self.l3.p2() , self.anchor1)
                    # print('ANCHOR1_L3_ORIENTATION:', anchor1_l3_orientation)
                    # if anchor1_l3_orientation == 0: 
                    #     self.l1.setPoints(self.anchor1, self.anchor1) # set a null line 
                    # else:
                    #     isect_1_3 = self.intersects(self.l1, self.l3)
                    #     print('isect_1_3:', isect_1_3)
                    #     self.l1.setPoints(self.anchor1 , isect_1_3) 
            # l = QLineF(self.li1.line().p2() , self.li3.line().p2()) # 
            # self.li3.setLine(l)
            #eventually, after I get l2 down: self.li3.setLine(QLineF(self.li1.line().p1() , self.li2.line().p1()))
#ANGLE2#########################################################################################################################################################################################################################################################
    def angle2(self):
        angle2 = self.l0.angleTo(self.l2)
        if angle2 > 280: 
            angle2 = 360 - angle2 # For obtuses, Subtract from 360, to only deal with the smallest side of the angle. Draw it out
        
        if angle2 >=90: # obtuse and perpendicular cases 
            print('ANGLE2 IS PERP | OBTUSE')
            # pass
            self.li2.setLine(QLineF(self.anchor2, self.intersects(self.l2, self.l3)))
            
        elif angle2 < 90: # If l2 is acute with l0: 
            print('ANGLE2 ACUTE')
            # print('L2:', self.l2)
            # print('L3:', self.l3)
            
            if self.seeker_orientation == 0: # if seeker is inline w/ l0: 
                    self.li3.setLine(QLineF(self.l0.p2() , self.l0.p2()))
                    isect_l2_l3 = self.intersects(self.l2, self.l3) 
                    self.li2.setLine(QLineF(self.anchor2, isect_l2_l3)) # This may set a null line. That is handled later
                    # print('Seeker and anchor are inline with l0')
            elif self.seeker_orientation != 0: 
                # print('PREVIOUS SEEKER SIDE:', self.previous_seeker_side)
                if self.previous_seeker_side and ( self.seeker_orientation == self.previous_seeker_side ): # Ignore if previous_seeker_side still equals 0 
                    # print('seeker remains on same side ')
                    isect_l2_l3 = self.intersects(self.l2, self.l3) 
                    self.li2.setLine(QLineF(self.anchor2, isect_l2_l3)) # This may set 
                    print('isect_l2_l3:', isect_l2_l3)
                elif self.previous_seeker_side and ( self.seeker_orientation != self.previous_seeker_side ): 
                    # print('SEEKER CROSSED SIDES')
                    print(self.l2.p2() == self.l0.p2())
                    if self.initial_anchor2_orientation == self.seeker_orientation: # If init_anch side is skr side, use init_anch as anch. Otherwise, anchor on l0.p2
                        self.anchor2 = self.initial_anchor2
                    else: 
                        self.anchor2 = self.l0.p2() 
                        
                    print('SELF.L2.ANGLE() B4:', self.l2.angle())
                    self.l2 = self.acute_flip(self.l0 , 'p2') # Remake l2 so that its flipped about l0. 
                    print('SELF.L2.ANGLE() AFTER', self.l2.angle())
                    
                    isect_l2_l3 = self.intersects(self.l2, self.l3) 
                    self.li2.setLine(QLineF(self.anchor2, isect_l2_l3)) # This may set 
                    print('isect_l2_l3:', isect_l2_l3)

            # l = QLineF(self.li3.line().p1() , self.li2.line().p2() )  # 
            # self.li3.setLine(l)
#############################################################################################################################################################

    def acute_flip(self, axis, p1orp2): #-> QLineF, representing self, a line 45degrees acute to axis, flipped about axis. This function is to get the angle of the flipped line correct. The points of the flipped line will be wrong. 
        print('acute_flip')
        ori = self.three_point_orientation(axis.p1() , axis.p2() , self.scene().seeker.scenePos())
        if ori == 0: 
            raise ValueError(f"ori is 0 but expected seeker to be to a side of axis")
        if p1orp2 == 'p1': 
            l = QLineF(axis.p1() , QPointF(1e3, 1e3)) # Note, l will be overwritten shortly after l is returned. Thus, we can/will for from axis.p2() rather than, say, anchorn, which we would need to pass in as a parameter. 
            if ori == 1 : #clockwise: 
                l.setAngle(axis.angle()+45)   
            elif ori == 2: # counterClockwise
                l.setAngle(axis.angle()-45)
            return l
        
        elif p1orp2 == 'p2':
            l = QLineF(axis.p2() , QPointF(1e3,1e3))
            if ori == 1: # clockwise: 
                l.setAngle(axis.angle() +135) 
            elif ori == 2: 
                l.setAngle(axis.angle() -135) 
            return l 

# I drew it out and I thought the angles should be inversed but IDK why it works with them this way, if I inverse them it dnw...
        
    def get_connected_traces(self, point1or2): # Must pay attention to item.line().pn() vs self.line().pn() and p1 vs p2; this gets tricky
        point1or2 = point1or2.lower().strip()
        
        connected_traces = []
        # print('SELF.BOUNDS:', self.bounds()) # (0000)
        self.setBounds()# self.bounds is (0000) if we initialized a blank traceItem. Be sure to recalculate bounds 
        ids = list(self.scene().idx.intersection(self.bounds()))
        items =  [ self.scene().ids[id] for id in ids if not (id is self.id) ]
        # print('HIT THESE ITEMS:' , items)
        # for id in items: 
            # item = self.scene().ids[id] 
        for item in items:
            if item is self: 
                continue # We will hit our own self, ignore self.
            if isinstance(item, TraceItem):
                if point1or2 == 'p1':  # Get traces connected to self.line().p1()
                    if (item.line().p1() == self.line().p1()):
                        distal = item.line().p2() # We may need to know connected_trace's distal point, to use as anchor
                        connected_traces.append( ( item , distal ) )
                    elif  ( item.line().p2() == self.line().p1()): 
                        distal = item.line().p1()
                        connected_traces.append( ( item , distal ) )
                        

                elif point1or2 == 'p2':
                    if (item.line().p1() == self.line().p2()):
                        distal = item.line().p2() # We may need to know the distal point to use as anchor
                        connected_traces.append( ( item , distal ) )
                    elif ( item.line().p2() == self.line().p2()):
                        distal = item.line().p1()
                        connected_traces.append( ( item , distal ) )
                        
        return connected_traces
    
    def calculate_anchors(self):# Calculates self.anchor1 and self.anchor2. -> None 
        connected_traces_1 = self.get_connected_traces('p1')
        connected_traces_2 = self.get_connected_traces('p2')  
        
        self.calculate_anchor(connected_traces_1 , 'p1') # calulate_anchor may add t1 to the scene, so make sure you get_connected_traces before that happens 
        self.calculate_anchor(connected_traces_2,  'p2')

    def calculate_anchor(self, connected_traces, point1or2): # calculate anchor and l1 l2 t1 t2 
        if ( not connected_traces ) or ( len(connected_traces) > 1): 
            if point1or2 == 'p1':
                print('ANCHOR AT L0.P1')
                self.anchor1 = self.l0.p1()
                self.l1 = QLineF(self.anchor1 , self.arbitrary) # Draw line to an arbitrary point, b/c if line is of 0 length, .setAngle and more don't work 
                self.l1.setAngle(self.line().angle() + 45) # Give l1 an acute angle to l0
                
            elif point1or2 == 'p2':
                print('ANCHOR AT L0.P2')
                self.anchor2 = self.line().p2()
                self.l2 = QLineF(self.anchor2, self.arbitrary)
                self.l2.setAngle(self.line().angle() + 135)

        elif len(connected_traces) == 1: 
            print('ANCHOR AT DISTAL')
            if point1or2 == 'p1':
                item, distal = connected_traces[0]
                self.anchor1 = distal 
                self.l1 = item.line() # Remember the QLineF bc we're gonna do math on it 
                self.scene().removeItem(item) # take connected item off scene, inserting a standin QGLI in its place 
                
            elif point1or2 == 'p2':
                item, distal = connected_traces[0]
                self.anchor2 = distal 
                self.l2 = item.line()
                self.scene().removeItem(item) 

        if point1or2 == 'p1':
            print('LEN(CONNECTED_TRACES_1:', len(connected_traces))

            self.initial_anchor1 = self.anchor1
            self.initial_anchor1_orientation = self.three_point_orientation(self.l0.p1() ,self.l0.p2() , self.anchor1)

            self.li1 = QGraphicsLineItem(self.l1) # Create/addToScene a standin QGLI representing our adjusted trace. QGLIs do not go into the scene.rtree. Add TraceItems upon mouseReleaseEvent; when user indicates they are done editing a trace.
            self.li1.setPen(QPen(Qt.red, self.trace_width , c = Qt.PenCapStyle.RoundCap)) 
            self.scene().addItem(self.li1) 

            
        elif point1or2 == 'p2':
            print('LEN(CONNECTED_TRACES_2:', len(connected_traces))
            
            self.initial_anchor2 = self.anchor2
            self.initial_anchor2_orientation = self.three_point_orientation( self.l0.p1() , self.l0.p2() , self.anchor2)
                 
            self.li2=QGraphicsLineItem(self.l2)
            self.li2.setPen(QPen(Qt.green, self.trace_width, c = Qt.PenCapStyle.RoundCap ))
            self.scene().addItem(self.li2)

        # print()
        # print('SELF.L1:', self.l1)
        # print('SELF.li1:', self.li1)
    
    def calculate_l3(self): # Find t3, trace // to l0 thru point (seeker.pos)
        x3, y3 = self.scene().seeker.scenePos().toTuple()
        
        self.recalculate_slope()    
        m3 = self.slope() # bc // 
        print('SLOPE:', m3)
        if m3 == 'undefined': # If slope is vertical its undefined 
            self.l3 = QLineF(x3, -1e3, x3, 1e3) # A vertical line offset at x 
            
        else: 
            
            b3  = y3 - m3*x3 # y = m3*x + b3
            # self.l3 = QLineF(0 , b3 , 1e3, (m3*1e3)+b3) # pick any two xs; choose zero and 1, calculate their y, then amke a line out of it. This must be updates with intersecctions to l1, and l2, else our l3 spans from x=0 to x=1 . BAD Using x=0 to x=1 causes a short segment, susceptible to floating point errors-- MUST use a large enough number to avoid this, instead of choosing x=0 and x=1, choose x = -1e3 and x= 1e3
            self.l3 = QLineF(-1e3 , (m3*-1e3) + b3 , 1e3, (m3*1e3)+b3) # pick any two xs; choose zero and 1, calculate their y, then amke a line out of it. This must be updates with intersecctions to l1, and l2, else our l3 spans from x=0 to x=1 . BAD Using x=0 to x=1 causes a short segment, susceptible to floating point errors-- MUST use a large enough number to avoid this, instead of choosing x=0 and x=1, choose x = -1e3 and x= 1e3
        # print("l3/l0 intersection:" , self.intersects(self.l0, self.l3) )
        # l3 SHOULD be parallel to l0, but they are not, because of floats: l3/l0 intersection: (<IntersectionType.UnboundedIntersection: 2>, PySide6.QtCore.QPointF(10211650317874956.000000, 10211650317874960.000000))
        self.li3.setLine(self.l3)
        
    def recalculate_slope(self):
        if self.line().x1() == self.line().x2(): # In this case, vertical line, slope is undefined, use nan
            self._slope = 'undefined' # I was using float('nan') but stopped because nan == nan is False, so its very hard to know if your float is nan. I don't like nan. Consider False 'undefined' None instead 
        else:
            self._slope = ( self.line().y2() - self.line().y1() ) / ( self.line().x2() - self.line().x1() ) # slope equals rise over run 
        # print('RECALCULATED SLOPE:', self._slope)

    def slope(self):
        return self._slope
    
    def intersects(self, line1, line2): # return intersection point of two QLine/Fs, or None if lines are  // parallel OR collinear OR one or both lines is of zero length. So QLineFs have a segment, defined by their two points, but this function will return intersection point where those lines intersect outside of their segment bounds. Compare against segments_intersect, which returns None if lines intersect outside their segments. 
        if line1.length() == 0 or line2.length() == 0: 
            raise ValueError(f"line1.length(): {line1.length()} line2.length(): {line2.length()} but both lines must be of non-zero length to test intersection")

        intersection_type, intersection_point = line1.intersects(line2) # QLineF.intersects() is highly quirky
        
        if intersection_type is QLineF.IntersectionType.NoIntersection: 
            return None
        elif intersection_type is QLineF.IntersectionType.UnboundedIntersection:
            return intersection_point # Idc if the infinite length lines intersect, I only care if the segments intersect
        elif intersection_type is QLineF.IntersectionType.BoundedIntersection:
            return intersection_point

    def segments_intersect(self, line1, line2): # Returns the intersection point, if segments intersect, else None. So if the infinitely long lines intersect outside of their segments, return None 
        if line1.length() == 0 or line2.length() == 0: 
            raise ValueError(f"line1.length(): {line1.length()} line2.length(): {line2.length()} but both lines must be of non-zero length to test intersection")
        
        intersection_type, intersection_point = line1.intersects(line2)
        if intersection_type is QLineF.IntersectionType.NoIntersection: 
            return None
        elif intersection_type is QLineF.IntersectionType.UnboundedIntersection:
            return None 
        elif intersection_type is QLineF.IntersectionType.BoundedIntersection:
            return intersection_point
        
    @staticmethod 
    def normalize_angle(angle):
        while angle > 360: 
            angle-=360
        while angle < 360: 
            angle += 360 
        return angle 
    
    @staticmethod 
    def reflect_about(line, reflection_axis):
         return reflection_axis.angle() + (reflection_axis.angle() - line.angle()) 
    
    @staticmethod
    def three_point_orientation(p1,p2,p3 , verbose=False): # "https://www.scribd.com/document/521718353/2017-04-28-Continuous-Space-Pathfinding" "Continuous Space Pathfinding Daniel Wisdom 28 April 2017"
        x1,y1 = p1.toTuple()
        x2,y2 = p2.toTuple()
        x3,y3 = p3.toTuple()
        
        cross_product = (y2-y1)*(x3-x2) - (x2-x1)*(y3-y2)
        cross_product = round(cross_product, 12) # Round the cross product  to 12 decimal places. Floats (usually, always) have 16 decimal places. But floats are bad/wrong: .3 * 3 = .9 but python will tell you .3 * 3 = .8999999999999999. So we round.
        if verbose: 
            print('Cross_product:', cross_product)
        if cross_product > 0: # Then cw 
            return 1 
        elif cross_product < 0: # Then ccw
            return 2
        else: # if cp == 0, p1p2p3 collinear 
            return 0 
        
    def hoverEnterEvent(self, event):
        current_tooltip = self.toolTip()
        self.setToolTip(f"{current_tooltip}\nP1: {self.line().p1()}\nP2: {self.line().p2()}") 
        super().hoverEnterEvent(event)

    def clone(self):
        return TraceItem(self.traceWidth() , self.layer() , self.line())