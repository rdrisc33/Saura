from utils import * 

# This sets up a view that is able to zoom in/out, can scroll via click and drag, and other basic view stuff. Inherited by BoardView and SchematicView, which are further configured to work for the board/schematic respectively.

class View(QGraphicsView): 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True) # Must enable to allow drops (as in drag and drop drops)
        
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        # self.grabGesture(Qt.GestureType.PinchGesture) # Zoom in by pinching the trackpad. NOTE: trackpad zoom works fine w/o this line 
        # self.setDragMode(QGraphicsView.ScrollHandDrag) # Behavior for LMB clicking & dragging the mouse the scene. This behavior only affects mouse clicks, that are not handled by any item. (NOTE: I like this mode, but for the cursor becomes hand cursor all the time... not just when i click/drag...)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # Qt::ScrollBarAlwaysOff
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.horizontalScrollBar().setRange(-100000, 100000)
        # self.verticalScrollBar().setRange(-100000, 100000)
        self.setSceneRect(-10000, -10000, 20000, 20000)


        dpi = qApp.screens()[0].physicalDotsPerInch()


    def wheelEvent(self, event): # Wheel as in mouseWheel 
        
        delta = event.angleDelta().y() # How much mouseWheel scrolled
        scaleFactor = math.pow(2.0, -delta / 500)
        self.scaleScene(scaleFactor)

    def scaleScene(self, scaleFactor):
        zoom = self.transform().scale(scaleFactor, scaleFactor).m11() # Scale current transform to predict zoom. The x scale lives in the matrix's m11 element      #  Used to do this , which also works: .mapRect(QRectF(0, 0, 1, 1)).width() # QTransform.mapRect(rect) -> QRectF, mapped onto the given QTransform. Note that we gave a unit rectangle; a rectangle where width&height=1. So, we are testing to see how much a unit scales under this transform. Note that self.transform() includes any previous scaling; representing the currently applied zoom, which we should limit to a certain range 

        if zoom < 0.01 or zoom > 100: # Prevent crazy scale changes.
            return

        self.scale(scaleFactor, scaleFactor) 


    def mouseMoveEvent(self,event):
        super().mouseMoveEvent(event)
        self.viewport().update()    # After drawing my grid dots via reimplementing BoardView.drawBackground, the dots would be erased when the seeker moved over them. Redrawing the background with every moveEvent prevents that
        