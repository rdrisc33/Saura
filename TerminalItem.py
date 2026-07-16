# Qt.QtWidgets.QGraphicsObject: A subclass of QGraphicsITEM and QOBJECT. QObject gives signals/slots.
from utils import * 
class TerminalItem(QGraphicsEllipseItem): # MyTerminalItem: A marker where you click and draw wires to/from. 
    def __init__(self, *args, **kwargs ):
        super().__init__(*args, **kwargs)
