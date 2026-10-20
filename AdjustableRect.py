from utils import * 
from AdjustHandle import AdjustHandle

class AdjustableRect(QGraphicsRectItem): # Eight adjust handles; those little dots you click on to adjust the shape
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable )

        self.adjustHandleRect = QRectF(-3,-3, 6,6)
        self._leftHandle = AdjustHandle(self.adjustHandleRect, self)
        self._leftHandle.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self._leftHandle.setPos(self.rect().left(), 0)

        self._topHandle = AdjustHandle(self.adjustHandleRect, self)
        self._topHandle.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self._topHandle.setPos(0 , self.rect().top())

        self._rightHandle = AdjustHandle(self.adjustHandleRect, self)
        self._rightHandle.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self._rightHandle.setPos(self.rect().right() , 0)

        self._bottomHandle = AdjustHandle(self.adjustHandleRect, self)
        self._bottomHandle.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self._bottomHandle.setPos(0, self.rect().bottom())
        
        # self._leftHandleHitShape = None 
        self._adjust = None 

    def hideHandles(self):
        self._leftHandle.hide()
        self._topHandle.hide()
        self._rightHandle.hide()
        self._bottomHandle.hide()
        
    def showHandles(self):
        self._leftHandle.show()
        self._topHandle.show()
        self._rightHandle.show()
        self._bottomHandle.show()
        
    def itemChange(self, change, value):# itemChange not working( This was because of diamond inheritance, both BoardScene and DrawScene were inheriting QGraphicsScene, which is a no-no)
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged: # # AdjustableRect handles are hidden if not selected, or, if 2+ shapes are selected.
            print('ITEMSELECTEDHASCHANGED')
            print('SCENE.SELECTEDITEMS():', self.scene().selectedItems())
            if (value == True) and (len(self.scene().selectedItems()) == 1): 
                print('SELF IS SELECTED')
                self.showHandles()
            elif value == True and (len(self.scene().selectedItems())> 1 ):
                self.hideHandles()
            elif value==False: 
                self.hideHandles()
                
        return super().itemChange(change,value) 

    def mousePressEvent(self, event): 
        print('ADJUSTABLERECT.MOUSEPRESSEVENT')
        
        # if self._leftHandleHitShape: 
        #     self.scene().removeItem(self._leftHandleHitShape)

        # self._leftHandleHitShape = view.transform().inverted()[0].map(self._leftHandle.shape()) # YES YES YES 
        # self._leftHandleHitShape = self._leftHandle.mapToParent(self._leftHandleHitShape) # YES YES YES
        view = self.scene().views()[0]
        self._leftHandleHitShape = self._leftHandle.mapToParent(view.transform().inverted()[0].map(self._leftHandle.shape())) # Using the .ItemIgnoresTransformations flag is easy, until you need to do hit detection on that item, in which case, you have to do complex matrix stuff... The docs mention .viewportTransform(), but that dnw here, while .transform() does work here...
        self._topHandleHitShape = self._topHandle.mapToParent(view.transform().inverted()[0].map(self._topHandle.shape())) 
        self._rightHandleHitShape = self._rightHandle.mapToParent(view.transform().inverted()[0].map(self._rightHandle.shape())) 
        self._bottomHandleHitShape = self._bottomHandle.mapToParent(view.transform().inverted()[0].map(self._bottomHandle.shape())) 
        
        if self._leftHandleHitShape.contains(event.pos()):
            print('LEFT HANDLE PRESSED')
            self._adjust = Utils.AdjustHandleLocation.Left

        elif self._topHandleHitShape.contains(event.pos()):
            print('TOP HANDLE PRESSED')
            self._adjust = Utils.AdjustHandleLocation.Top
            
        elif self._rightHandleHitShape.contains(event.pos()):
            print('RIGHT HANDLE PRESSED')
            self._adjust = Utils.AdjustHandleLocation.Right
            
        elif self._bottomHandleHitShape.contains(event.pos()):
            print('BOTTOM HANDLE PRESSED')
            self._adjust = Utils.AdjustHandleLocation.Bottom
        # self._leftHandleHitShape = QGraphicsPathItem(self._leftHandleHitShape, self) # Show item for debugging
        # self._leftHandleHitShape.setPen(QPen(Qt.magenta , 0 )) 

        super().mousePressEvent(event)

    def setRect(self, *args, **kwargs): # When one handle moved, some of the other handles also need to reposition. Accomplish this by reimplementing .setRect to update all handles
        super().setRect(*args, **kwargs)
        # print('SELF.RECT():', self.rect())
        # self._leftHandle.setPos(self.rect().left(), 0)

        self._leftHandle.setPos(self.rect().left(), self.rect().center().y())
        self._topHandle.setPos(self.rect().center().x(), self.rect().top())
        self._rightHandle.setPos(self.rect().right(), self.rect().center().y())
        self._bottomHandle.setPos(self.rect().center().x(), self.rect().bottom())
        
    def mouseMoveEvent(self, event): 

        if self._adjust == Utils.AdjustHandleLocation.Left: 
            # topLeft = QPointF(event.scenePos().x() - self.scenePos().x(), self.rect().top())
            topLeft = QPointF(event.pos().x(), self.rect().top())
            bottomRight = self.rect().bottomRight()

        elif self._adjust == Utils.AdjustHandleLocation.Top: 
            topLeft = QPointF( self.rect().left() , event.pos().y())
            bottomRight = self.rect().bottomRight()

        elif self._adjust == Utils.AdjustHandleLocation.Right: 
            bottomRight = QPointF( event.pos().x(), self.rect().bottom())
            topLeft = self.rect().topLeft()
            
        elif self._adjust == Utils.AdjustHandleLocation.Bottom: 
            bottomRight = QPointF(self.rect().right(), event.pos().y() )
            topLeft = self.rect().topLeft()

        else: 
            return super().mouseMoveEvent(event)
        
        self.setRect(QRectF(topLeft, bottomRight)) # Note we would want to do net collision testing during this

    def mouseReleaseEvent(self, event): 
        print()
        print('ADJUSTABLERECT.MRE')
        self._adjust = None 
        super().mouseReleaseEvent(event)
  
    def shape(self): 
        stroker = QPainterPathStroker() 
        stroker.setWidth(1 if self.pen().width() < 1 else self.pen().width())
        stroker.setJoinStyle(Qt.RoundJoin)
        stroker.setCapStyle(Qt.FlatCap)
        path = QPainterPath()
        path.addRect(self.rect())
        return stroker.createStroke(path)
    
    def paint(self, painter, option , widget): # This is good for debugging. Comment in to draw .shape's hitbox
        
        super().paint(painter, option, widget)
        painter.setPen(QPen(Qt.black if self.pen().color() == Qt.red else Qt.red, 0))
        painter.drawPath(self.shape())

