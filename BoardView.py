from MyView import MyView 
from PySide6.QtCore import *
from PySide6.QtWidgets import* 
from PySide6.QtGui import *

class BoardView(MyView):
    def __init__(self, *args, **kwargs ):
        super().__init__(*args, **kwargs)
        self.grid_spacing = 4 # as in 4mm. 
        self.tick_spacing = self.grid_spacing
     
    def drawBackground(self, painter, rect):
        # painter.drawPoint(QPointF(10,10))

        painter.setPen(QPen(Qt.black, 0))
        painter.setBrush(Qt.black)
        
        num_ticks_x = int(rect.width()/ self.tick_spacing) +1 # Plus one so our dots arent short of the edge
        num_ticks_y = int(rect.height()/self.tick_spacing) +1
        
        for x in range(num_ticks_x):
            for y in range(num_ticks_y):
                 
                # painter.drawEllipse(QPoint(x*self.tick_spacing, y*self.tick_spacing) , 1, 1) drawEllipse can only work with integer radii
                # painter.drawPoint(QPoint(x*self.tick_spacing + rect.left() , y*self.tick_spacing+rect.top()))
                painter.drawPoint(QPoint(x*self.tick_spacing , y*self.tick_spacing))
            
        # super().drawBackground(painter, rect) # Base implementation calls scene.drawBackground, if no brush set(which is default). If pen is set, will draw background with pen. Reimplement to paint a custom background(and Dont call super, bc it'll fill with the pen we set)

    # def mousePressEvent(self, event):
    #     # print('BOARDVIEW.MOUSEPRESSEVENT:')
    #     super().mousePressEvent(event)