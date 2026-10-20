from utils import * 
# AdjustableRect handles are hidden if not selected, or, if 2+ shapes are selected. Use itemChange with QGraphicsItem.GraphicsItemCHange.ItemSeletedHasChanged
# Changing the rect height demands changing pos of left/right adjust handles, if l/r adjust handles are to stay centered. Can reimplement .setRect to also reposition all handles
# How do I 'indent'/'unindent' the adjust nodes when user mouses over them? Who cares? don't implement this. Good enough to give the nodes a gradient brush
# The node hit box is bigger than the nodes themselves. To accomplish this, subclass QGraphicsRectItem, and reimplement .shape to return a larger path
# The node hit box also scales up/down with zoom. To accomplish this ... 

class AdjustHandle(QGraphicsRectItem): 
    expandHitBoxBy = 10 # TODO This ideally would scale with zoom, actually. Also, the expansion doesn't even seem to be working 
    
    def __init__(self, *args, handleShape=Utils.AdjustHandleShape.Rect, **kwargs ):
        self.handleShape = handleShape
        super().__init__(*args, **kwargs )

    def shape(self): # AdjustableRect handle hit box is bigger than the handle itself. To implement, subclass QGraphicsRectItem, reimplementing .shape to return a slightly larger hitbox
        path = QPainterPath()
        path.addEllipse(self.rect().adjusted(-self.expandHitBoxBy/2 , -self.expandHitBoxBy/2 , self.expandHitBoxBy/2 , self.expandHitBoxBy/2))
        # print('PATH:', path)
        return path

    def paint(self, painter, option, widget): # Increase visibility & contrast of adjust handles with a radial gradient

        painter.setPen(QPen(Qt.black, 0 ))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.shape())
        
        gradient = QRadialGradient(self.rect().center().x()-2, self.rect().center().y()-2, self.rect().width()/2)
        gradient.setColorAt(0,Qt.white)    # if raised, go darkYellow to yellow
        gradient.setColorAt(1,Qt.gray)

        painter.setBrush(gradient)
        painter.setPen(QPen(Qt.black, 0))

        if self.handleShape == Utils.AdjustHandleShape.Rect:
            painter.drawRect(self.rect())
        if self.handleShape == Utils.AdjustHandleShape.Circle:
            painter.drawEllipse(self.rect())

    def mousePressEvent(self, event):
        print()
        print('ADJUSTHANDLE.MOUSEPRESSEVENT')
        super().mousePressEvent(event)