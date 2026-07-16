# Good docs: Qt Signals and slots : https://doc.qt.io/qtforpython-6/tutorials/basictutorial/signals_and_slots.html#tutorial-signals-and-slots
# signals and slots are for qobjects ; to use signals slots in a class, the class must be derived from QObject. All Qt objects are derived from QObject, but thas not enough, you must specifically inherit QObject in your classes, if you want your classes to use signnals
# PySide Advanced: Signals and Slots
# Inherit QObject to use signals 
# TypeHints are mandatory
# Use the Signal class to define signals 
# use the @ Slot(typehint) decorator to define slots
# signal().connect(slot) 
# signal().emit(object_to_emit)

import sys 
from PySide6.QtCore import Qt, Signal, Slot, QRectF, QObject
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QGraphicsItem, QGraphicsEllipseItem, QTableWidget, QGraphicsView, QGraphicsScene


class MyItem(QGraphicsEllipseItem, QObject):
    clicked =Signal(QTableWidget)
    def __init__(self, *args):
        QGraphicsEllipseItem.__init__(self, *args)
        QObject.__init__(self)
        self.clicked.connect(MyWindow.on_item_clicked)
        
    def mousePressEvent(self,event):
        table = QTableWidget(2,4)
        self.clicked.emit(table)
        super().mousePressEvent(event)
        
class MyWindow(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        

# on view double click, get the item beneath mouse if any 
# THE VIEW NEEDS TO HANDLE ITEM DOUBLE CLICKS
    @Slot(QTableWidget)
    def on_item_clicked(table):
        print('ON_ITEM_CLICKED:', table)

   
app = QApplication(sys.argv)
window = MyWindow()
item = MyItem(-20,-20,40,40)
scene = QGraphicsScene()
scene.addItem(item)
view = QGraphicsView(scene)
view.show()

sys.exit(app.exec())