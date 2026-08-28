from utils import * 
from Trace import Trace 

class Ffline: 
    # Angles in radians. If angles in degrees, _degrees should be attached to variable name 
    def __init__(self, here, there, scene):  # here,there: draw this ffline from here, to there. scene: need a reference to the scene, for scene.tracewidth, and scene.ids, and scene.rtrees( but we don't want to add fflines to the scene, until we know them and their connecteds are valid, so ffline is not a QGraphicsItem)
        # print('ADDING FFLINE')
        self.here = here
        self.there = there 
        
        self._scene = scene
        self._octant = None 
        self._startAngle = 0 
        self._startAngleThreshold = 20         
        
        self._lineA = QLineF() # QLineF is used to do all maths, before it is set as Traces line 
        self._lineB = QLineF()

        layers = [ self.scene().activeLayer() ]
        self._traceA = Trace.fromLine(self._lineA, self.scene().traceWidth(), layers )
        self._traceB = Trace.fromLine( self._lineB, self.scene().traceWidth() , layers)         
        self.traces = [self._traceA , self._traceB]
        self.scene().addItem(self._traceA)
        self.scene().addItem(self._traceB)
        
        # self._lineItem = QGraphicsLineItem(QLineF(here, there) ) # Debugging. A dashed line item going start to finish
        # self._lineItem.setPen(QPen(Qt.black, 0 , s = Qt.PenStyle.DashLine))
        # self.scene().addItem(self._lineItem)

        self.setPoints(here, there)
        
        # self.dxLineItem = QGraphicsLineItem()
        # self.dxLineItem.setPen(QPen(Qt.darkRed, 0, s = Qt.DashLine))
        # self.scene().addItem(self.dxLineItem)
        
        # self.dyLineItem = QGraphicsLineItem() 
        # self.dyLineItem.setPen(QPen(Qt.darkBlue, 0 , s = Qt.DashLine))
        # self.scene().addItem(self.dyLineItem)

        # self.lineItemA = QGraphicsLineItem(self._lineA)
        # self.lineItemA.setPen(QPen(Qt.blue, 0.1 , s = Qt.PenStyle.DashLine))
        # self.scene().addItem(self.lineItemA)

        # self.lineItemB = QGraphicsLineItem(self._lineB)
        # self.lineItemB.setPen(QPen(Qt.darkBlue , .1 , s = Qt.PenStyle.DashDotLine))
        # self.scene().addItem(self.lineItemB)
        
    def dx(self):
        return self._dx
    def setDx(self):
        self._dx = self.there.x() - self.here.x() 
    
    def setDy(self): 
        self._dy = self.there.y() - self.here.y()
    def dy(self):
        return self._dy

    def theta(self):
        return self._theta
    def setTheta(self):
        self._theta = self.normalizeAngle( math.atan2( -self.dy(), self.dx() ) ) # Note y is flipped because in QT, positiveY is downwards while atan2 positiveY is upwards. Also, atan2 returns from -pi to 0 to pi, so normalize that angle to 0-2Pi
        print('THETA(degrees):', self._theta * 180/math.pi)
            
    def withinThreshold(self): 

        if math.sqrt(self.dx()**2 + self.dy()**2) < self.startAngleThreshold(): # if we are within threshold, assign startAngle
            return True 

    def octant(self):
        return self._octant 
    def setOctant(self , octant):
        self._octant = octant
        
    def startAngle(self):
        return self._startAngle 
    def setStartAngle(self): 
        self._startAngle = self.snapAngle(self.theta())
        
    def startAngleThreshold(self):
        return self._startAngleThreshold 
    def setStartAngleThreshold(self, startAngleThreshold):
        self._startAngleThreshold = startAngleThreshold

    # elif self.getOctant(self.theta()) != self.octant(): # If we are in a new octant, assign startAngle
    #     print('WE ARE IN A NEW OCTANT')
    #     self.setStartAngle(self.getStartAngle(self.theta()))
    #     self.setOctant(self.getOctant(self.theta())) 


    def setPoints(self, here , there): # Draw ffline from here to there, if no collisions. 
        # print('SETTING FFLINE POINTS:')
        # self._lineItem.setLine(QLineF(here, there))
        # print()
        if here == there: 
            # print('HERE==THERE; RETURNING')
            return # Both self.linea/b will be null

        if isinstance(here, tuple):
            here = QPointF(*here)
            there = QPointF(*there)
            
        self.here = here
        self.there = there 

        self.setDx() 
        # self.dxLineItem.setLine(QLineF(self.here, self.here + QPointF(self.dx(), 0)))
        self.setDy() 
        # self.dyLineItem.setLine(QLineF(self.dxLineItem.line().p2() , self.there))
        self.setTheta()

        if self.withinThreshold(): 
            print('WITHIN THRESHOLD')
            self.setStartAngle()
        # else:  
        #     octant = self.getOctant(self.theta())
        #     if octant != self.octant(): 
        #         self.setOctant(octant)
        #         self.setStartAngle()

        # print('OCTANT:', self.octant())

        self._lineA.setP1(self.here)
        self._lineA.setP2(self.there) # This is gonna be overwritten; just need to ensure line is not null

        if (self.startAngle() + (math.pi/4) < self.theta() ) or  (self.startAngle() - (math.pi/4) > self.theta()):  # implement a sort of 'angle locking' thing that lets user draw traces more comfortably; we only want to change the start angle of our trace if its move 45degrees past current startangle 
            self.setStartAngle()
        print('STARTANGLE:', self.startAngle())
        # print('SELF.HERE == LINEA.P1():', self.here == self._lineA.p1())
        self._lineA.setAngle(self.startAngle()*180/math.pi)
        # print('SELF.HERE == LINEA.P1():', self.here == self._lineA.p1())






# It seems this block is causing some problems 

        # Depending on whether trace a is at an angle, or hor/vert, the distance varies:

        if self._lineA.angle() % 90 == 0: # If the angle is hor/vert, 
            print('STARTING OUT HOR/VERT')
            self._lineA.setLength( abs(abs(self.dx()) - abs(self.dy())) )
        else:
            print('STARTING OUT FORTYFIVEN DEGREES')
            self._lineA.setLength( math.sqrt(2) * abs(min(abs(self.dx()) , abs(self.dy()))) ) # This is the fortyfivedegree distance component of our ffline. see ffline distance.

        self._lineB.setPoints( self._lineA.p2() , self.there )  # better be QPointFs

        self._traceA.setLine(self._lineA)
        # print('SELF.HERE == LINEA.P1():', self.here == self._lineA.p1())
        # # self.lineItemA.setLine(self._lineA)
        # print('SELF.HERE == TRACEA.LINE().P1():', self.here == self._traceA.line().p1())


        # self.lineItemB.setLine(self._lineB)
        self._traceB.setLine(self._lineB)
        # print('SELF.THERE == TRACEB.P2():' ,self.there == self._traceB.line().p2())
        # print(self._traceA.line())
        # print(self._traceB.line())























#
        # if self.isColliding():
        #     print('DETECTED COLLISION. TRY ALT ROUTE.')
        #     self.altAttempt() # Try an alternate attempt: change the startAngle. If this one don't work, ffline.is_valid = False
        #     if self.isColliding():
        #         print("This ffline is colliding")
        #         return False  # The ffline we drew from here to there collided with something

        # # print('UPDATING RTREE')
        # self._traceA.updateRtree() # If no collisions, update rtree
        # self._traceB.updateRtree()

        return True 
                
    def isColliding(self): # Returns 2-tuple (is_colliding , (test_traceA , test_trace_b) ). If is_colliding, test traces will both be None, else they will be set to their non-colliding traces 

        self._lineA.setAngle(self.startAngle() * 180/math.pi ) # better be in degrees
        # Depending on whether trace a is at an angle, or hor/vert, the distance varies:
        if self._lineA.angle() % 90 == 0: # If the angle is hor/vert, 
            self._lineA.setLength( abs(abs(self.dx()) - abs(self.dy())) )
        else:
            self._lineA.setLength( math.sqrt(2) * abs(min(abs(self.dx()) , abs(self.dy()))) ) # This is the fortyfivedegree distance component of our ffline. see ffline distance.

        if self.traceCollides(self._traceA):
            return True

        if self.traceCollides(self._traceB): 
            return True
        
        return False # If we made it here, test traces did not collide

    def connecteds(self, item):
        pass
            
    def traceCollides(self, trace):
        # print('SELF.SCENE().ITEMS:', len(self.scene().items()), self.scene().items())
        hitItems = trace.queryRtrees()
        for hitItem in hitItems:
            # print('HITITEM:', hitItem)
            if hitItem == self:
                continue
            if hitItem.net() == trace.net(): # Traces on the same net are not collisions; these are joinable
                continue
            # elif hitItem.collidesWithItem(trace.sceneBufferedBounds()): # Can this be used if trace is not on the scene? Also: cWI needs item but gave bounds. Try cWP:
            # elif hitItem.collidesWithPath(trace.bufferedSceneShape()):
            elif hitItem.collidesWithItem(trace): # Think needs to be bufferedShape
                if hitItem.net() == None and trace.net() != None:
                    hitItem.setNet(trace.net())
                elif hitItem.net() != None and trace.net() == None:
                    trace.setNet(hitItem.net)
                else: 
                    return True # Item collides w/ another item
            
        return False # Item does not collide
        
    def netCollision(self):
        pass
        

    # MyBoardScene.trace_collides(self, trace):

    def altAttempt(self): # Change the start angle and 
        pi = math.pi
        
        if self.theta() < self.startAngle() : 
            # self.setStartAngle( Ffline.getStartAngle(self.theta() - pi/4 ) ) 
            self.setStartAngle( Ffline.snapAngle(self.theta() - pi/4 ))
        elif self.theta() > self.startAngle(): 
            # self.setStartAngle( Ffline.getStartAngle(self.theta() + pi/4 ) )
            self.setStartAngle( Ffline.snapAngle(self.theta() + pi/4 ))
        # Note that if self.theta == self.startAngle, the fflines only viable startAngle is startAngle_degreess current value, & startAngle will NOT change, will get tested again, and again be found to collide-- no compute hit bc so rarely happens 
        
    def finalize(self): # creates & adds to scene  self.trace_(a,b), based off line_item_(a,b)'s line, them removes line_item_n Should happen once, in Utils.BoardSceneMode.AddTraceModeDoubleClickEvent,  when our traces are finalized;not colliding; ready to be id'd and go into rtree.
        
        if self._traceA.line().isNull(): # null aka line of 0 length
            print('TRACEA IS NULL')
            self.scene().removeItem(self._traceA) # standin QGLi no longer needed

        if self._traceB.line().isNull():
            self.scene().removeItem(self._traceB)
        
    def scene(self): # B/c this class takes a reference to a scene, 
        return self._scene

                
    @staticmethod
    def getOctant(theta): # return 1-8 representing the octant we are in ( like a quadrant but there's eight sections )
        pi = math.pi
        theta = Ffline.normalizeAngle(theta)
        if 0*pi/4 <= theta <= 1*pi/4:
            return 1 # as in octant 1
        if 1*pi/4 <  theta <= 2*pi/4:
            return 2 # as in octant 2 
        if 2*pi/4 <  theta <= 3*pi/4:
            return 3
        if 3*pi/4 <  theta <= 4*pi/4:
            return 4
        if 4*pi/4 <  theta <= 5*pi/4:
            return 5
        if 5*pi/4 <  theta <= 6*pi/4:
            return 6
        if 6*pi/4 <  theta <= 7*pi/4:
            return 7
        if 7*pi/4 <  theta <= 8*pi/4:
            return 8

    # @staticmethod
    # def getStartAngle(theta): 
    #     pi = math.pi
    #     theta = Ffline.normalizeAngle(theta) # atan2 returns -pi<theta<=pi , so, you'll want to normalize the angle first 
    #     if 0 <= theta <= pi/8 or 15*pi/8 < theta <= 2*pi: #  To determine which direction the user is trying to draw the line at initially, look in octants rotated 22.5 degrees ( pi/ 16) ( draw a picture to better understand)
    #         return 0 # as in 0 degrees 
    #     elif pi/8 < theta <= 3*pi/8: # 
    #         return 2*pi/8 # as in 45 degrees 
    #     elif 3*pi/8 < theta <= 5*pi/8:
    #         return 4*pi/8
    #     elif 5*pi/8 < theta <= 7*pi/8:
    #         return 6*pi/8
    #     elif 7*pi/8 < theta <= 9*pi/8:
    #         return 8*pi/8
    #     elif 9*pi/8 < theta <= 11*pi/8:
    #         return 10*pi/8
    #     elif 11*pi/8 < theta <= 13*pi/8:
    #         return 12*pi/8
    #     elif 13*pi/8 < theta <= 15*pi/8:
    #         return 14*pi/8
        
    def snapAngle(self , angle): # angle in radians. return angle snapped to nearest pi/4
        angle = round(angle / (math.pi/4)) * math.pi/4 # pemdas 12/3/4 different 12/(3/4)
        print('SNAPPED TO ANGLE(degrees):', angle *180/math.pi)
        return self.normalizeAngle(angle) 
    
    @staticmethod
    def normalizeAngle(theta): # Return an angle between 0 and 2 pi
        pi = math.pi 
        while theta > 2*pi : # as long as theta is out of bounds
            theta -= 2*pi
        while theta < 0: 
            theta += 2*pi
        # print('NORMALIZED THETA:', theta)
        return theta 