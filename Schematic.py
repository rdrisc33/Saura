from utils import * 
# from MyView import MyView
from SchematicView import SchematicView
from SchematicScene import SchematicScene
from MyFilterWidget import MyFilterWidget
from MyDatabaseTableSelectWidget import MyDatabaseTableSelectWidget
from ComponentSymbol import ComponentSymbol
from PySide6.QtGui import QDropEvent
from TableWidget import TableWidget

class Schematic(QWidget): # Intended to be a stackedWidget in the mainwindows central Widget , when user is on Schematic window. See MyBoard and MyFabrication for the board and fabrication window widgets.
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True) # Bc the View wants to accept drops, we also need to let the schematic widget accept drops(?)
        # self._view = MyView(self)
        self._view = SchematicView(self)
        self._scene = SchematicScene(self)
        # self._scene.added_part.connect(board._scene.add_part()) Need to .connect to the board's _scene's .addPart function at a level where we have access to it; cannot access here.
        self._view.setScene(self._scene) # Fun Fact _view does NOT take ownership of _scene
        
        layout = QVBoxLayout() 
        layout.addWidget(self._view)
        self.setLayout(layout)
        
        
    def scene(self):
        return self._scene
    def view(self):
        return self._view
    

    # def dragEnterEvent(self, event):
    #     print('MySCHEMATIC.DRAGENTEREVENT')
    #     super().dragMoveEvent(event) # What does base implementation do? 
    # def dragMoveEvent(self, event):
    #     print('MySCHEMATICDRAGMOVEEVENT')
    #     # super().dragMoveEvent(event) # What does base implementation do? 
    # def dropEvent(self, event):
    #     print('MySCHEMATIC.DROPEVENT', event)
    #     # super().dropEvent(event) # What does base implementation do? 
    # def dragLeaveEvent(self, event):
    #     print('MySCHEMATIC.DRAGLEAVEEVENT')
    #     # super().dragLeaveEvent(event)