from lxml import etree 
import sys 

from PySide6.QtWidgets import * 
from PySide6.QtCore import *
from PySide6.QtGui import * 


from FootprintItem import *
from utils import * 
from BoardScene import BoardScene
from MyView import MyView
from FootprintItem import FootprintItem

o = ContainerItem() # No problems 

class TraceItem(QGraphicsLineItem):#, MyGraphicsObject ): When TraceItem inherits both QGLI AND ContainerItem, kernel dies. 
    def __init__(self, line):
        super().__init__(line)  # Causes kernel crash. Why?its due to inheritance of MGO...but why? 
    
l = QLineF(10,10,100,100)
ti = TraceItem(l)

print('TRACEITEM:' , ti)

scene = BoardScene()
view= MyView()
view.setScene(scene)
scene.addItem(ti)
# scene.addItem(li)
# scene.addItem(li)
view.show()

sys.exit(app.exec())