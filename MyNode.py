from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtCore import QRectF, Qt
from utils import *

class MyNode(QGraphicsEllipseItem):
    rect= QRectF(-2,-2,4,4)
    _color = wireItemColor
    
    def __init__(self, parent=None):
        super().__init__(MyNode.rect, parent)
        self.setBrush(self._color)
        self.setPen(Qt.NoPen)
        

