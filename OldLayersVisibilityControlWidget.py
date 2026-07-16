from PySide6.QtWidgets import * 
from PySide6.QtCore import *
from PySide6.QtGui import * 

from utils import Utils 

class VisibilityButton(QPushButton):
    
    def __init__(self):
        icon = QIcon('images/visible.svg')
        super().__init__(icon, '')
        self.setCheckable(True)
        # self.setSizePolicy(QSizePolicy.Policy.Fixed , QSizePolicy.Policy.Fixed)
        self.setChecked(True)
        # self.clicked.connect(self.on_toggled) # Use toggled, not clicked, bc toggled also covers when button is programmatically 'clicked'
        self.toggled.connect(self.on_toggled)
        
    def on_toggled(self, checked):
        if checked: 
            self.setIcon(QIcon('images/visible.svg'))
        else:
            self.setIcon(QIcon('images/notVisible.svg'))
        
class VisibilityAndSelectionButton(QWidget):
    toggleVisibility = Signal(bool, str) # checked:bool , layer:str
    
    def __init__(self, text,parent=None):
        super().__init__(parent)
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setLayout(QHBoxLayout())
        
        self.text = text
                
        self.visibilityButton = VisibilityButton()
        self.visibilityButton.toggled.connect(self.on_visibility_toggled) # Anytime we toggle a visibilityButton, visibilityButton.toggled will emit. This makes it so that visAndSelBtn.visToggled(visibilityChecked, layer) also emits 
        self.selectionButton = QPushButton(text)
        self.selectionButton.setCheckable(True)
        
        self.layout().addWidget(self.visibilityButton)
        self.layout().addWidget(self.selectionButton)
        
    def on_visibility_toggled(self, checked ): 
        self.toggleVisibility.emit(checked, self.text)
            
class LayersVisibilityControlWidget(QWidget):
    
    setTopmostLayer = Signal(str)
    onlyShowCuLayers = Signal()
    toggleLayerVisibility = Signal(bool, str)# visibilityChecked:bool , layer:str
    
    def __init__(self):
        super().__init__()
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setLayout(QVBoxLayout())
        
        selectionButtonGroup = QButtonGroup(self) # A logical group of buttons so that only one of them can be checked at a time      
        selectionButtonGroup.buttonToggled.connect(self.selectionButtonToggled) # This fires once for every button in the buttongroup
        
        for layer in Utils.layers: 
            visSelBtn = VisibilityAndSelectionButton(layer)
            visSelBtn.toggleVisibility.connect(self.toggleLayerVisibility   )
            selectionButtonGroup.addButton(visSelBtn.selectionButton)
            self.layout().addWidget(visSelBtn)
            
        self.layout().itemAt(0).widget().selectionButton.setChecked(True) # Initialize the first selectionButton to checked. This is a confusing line but it reaches into the layout(), gets the 0th idx in the layout, then gets that idx's .widget(), which has a .selectionButton, then sets that selectionButton checked.
        options_group_box = QGroupBox('Options')
        options_group_box.setLayout(QVBoxLayout())
        only_show_cu_layers_btn = QPushButton('Only Show Cu Layers')
        # only_show_cu_layers_btn.clicked.connect(self.onlyShowCuLayers)
        only_show_cu_layers_btn.clicked.connect(self.only_show_cu_layers_btn_clicked)
        options_group_box.layout().addWidget(only_show_cu_layers_btn)
        
        self.layout().addWidget(options_group_box)        
        
    def only_show_cu_layers_btn_clicked(self):
        self.onlyShowCuLayers.emit()
        for count, layer in enumerate(Utils.layers): 
            if layer in Utils.CuLayers: 
                self.layout().itemAt(count).widget().visibilityButton.setChecked(True)
            else: 
                self.layout().itemAt(count).widget().visibilityButton.setChecked(False)
                    
    def selectionButtonToggled(self, btn, checked):
        print("BTN TOGGLED:", btn)
        print("BTN CHECKED:", checked)
        if checked: 
            self.setTopmostLayer.emit(btn.text())