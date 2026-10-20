from utils import *

class BoardSeeker(QGraphicsEllipseItem): # The seeker is a tranform-ignoring EllipseItem which visually assists user by snapping to points of interest, and representing the extent/range of items to be considered for hit detection. 
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations) 
        self.setPen(QPen(Qt.green , 2)) # penWidth 2 for better visibility
        self.setZValue(1)
        
        # self.shapeItem = QGraphicsPathItem(self.shape(), self) # visualize
        # self.shapeItem.setPen(QPen(Qt.red, 0))
        
    def shape(self): # I want to return an appropriate hitBox for my transform-ignoring shape 
        path = QPainterPath() 
        path.addEllipse(self.rect())
        if not self.scene(): 
            return path 
        
        view = self.scene().views()[0]          # Get the view
        viewTransform = view.transform()        # get the view transform 
        print('VIEW.TRANSFORM:', viewTransform) 
        
        viewScale = 1/viewTransform.m11() # extract the xScale, at m11. Inverse bc want to map from view coords, to item coords
        scaleTransform = QTransform()
        scaleTransform.scale(viewScale, viewScale)
        seekerHitShape = scaleTransform.map(path)        # Scale seeker.shape based on zoom level. Still in seeker local coords

        return seekerHitShape

    def sceneBounds(self):
        if not self.scene():
            return None 
        r = self.mapToScene(self.shape().boundingRect()).boundingRect()
        return ( r.left(), r.top(), r.right() , r.bottom())
