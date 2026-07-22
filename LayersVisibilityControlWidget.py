from PySide6.QtWidgets import * 
from PySide6.QtCore import *
from PySide6.QtGui import * 

from utils import Utils 
import sys

# TODO: make check box bgnd color same as layer color(.setBackground Instead, for now--Problem is, PySide6 gives no access to checkbox color...)(  TODO Make unchecked items mostly transparent.setBackground has unexpected behavior when dynamically changing alpha , think bc mousing over items default changes color)
class ListWidget(QListWidget):
    # setTopmostLayer = Signal(str)       #layer: str
    toggleLayerVisibility = Signal(Qt.CheckState, str) #checkState: Qt.CheckState , layer: str
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.itemClicked.connect(self.onItemClicked)
        
    def onItemClicked(self, item): # Checkable items can be checked, unchecked and partially checked with the setCheckState() function
        print('ITEM CLICKED:', item.text())
        checkState = item.checkState() # .checkState() of item when it was clicked.
        print('CHECKSTATE:', checkState)
        
        if checkState == Qt.CheckState.Checked: 
            checkState = Qt.CheckState.Unchecked
            
            item.setCheckState(checkState)
            item.setIcon(QIcon('images/notVisible.svg'))
        elif checkState == Qt.CheckState.Unchecked:
            checkState = Qt.CheckState.Checked 
            # self.setTopmostLayer.emit(item.text())
            
            item.setCheckState(checkState)
            item.setIcon(QIcon('images/visible.svg'))
        self.toggleLayerVisibility.emit(checkState, item.text())
            # item.setBackground(item.background().setAlpha(1.0)) DNW Note int 1 interpreted as 1/255; gotta use float
            
            
            
class ListWidgetItem(QListWidgetItem):
    def __init__(self, text):
        icon = QIcon("images/visible.svg") 
        super().__init__(icon, text)
        self.setBackground(Utils.layerColors[text])
        self.setFlags(Qt.ItemIsEnabled)
        # self.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled| Qt.ItemIsSelectable) You would expect LWIs were enabled, UserCheckable, and selectable. This behavior was undesired, items could be all combos of un/checked & un/selected. Wound up relying only on .itemClicked Signal to un/check items.

        self.setCheckState(Qt.Checked) 
        
         
class LayersVisibilityControlWidget(QWidget):
    
    # setTopmostLayer = Signal(str)
    onlyShowCopperLayers = Signal()
    toggleLayerVisibility = Signal(Qt.CheckState, str)# 
    
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.listWidget = ListWidget()
        # self.listWidget.setTopmostLayer.connect(self.setTopmostLayer) # propagate the signal
        self.listWidget.toggleLayerVisibility.connect(self.toggleLayerVisibility) # propagate the signal
        for layer in Utils.layers: 
            item = ListWidgetItem(layer)
            self.listWidget.addItem(item)
            
        self.layout().addWidget(self.listWidget)
        
        options_group_box = QGroupBox('Options')
        options_group_box.setLayout(QVBoxLayout())
        only_show_cu_layers_btn = QPushButton('Only Show Cu Layers')
        # only_show_cu_layers_btn.clicked.connect(self.onlyShowCopperLayers)
        only_show_cu_layers_btn.clicked.connect(self.onlyShowCopperLayersBtnClicked)
        options_group_box.layout().addWidget(only_show_cu_layers_btn)
        
        self.layout().addWidget(options_group_box)        

    def onlyShowCopperLayersBtnClicked(self):
        self.onlyShowCopperLayers.emit()
        for count, layer in enumerate(Utils.layers): 
            if layer in Utils.CopperLayers: 
                self.listWidget.item(count).setCheckState(Qt.CheckState.Checked)
                self.listWidget.item(count).setIcon(QIcon("images/visible.svg"))
            else: 
                self.listWidget.item(count).setCheckState(Qt.CheckState.Unchecked)
                self.listWidget.item(count).setIcon(QIcon("images/notVisible.svg"))
                    

# lvcw = LayersVisibilityControlWidget()
# lvcw.show()
    
# sys.exit(qApp.exec())