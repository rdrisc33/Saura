
# Revamp LVCW 
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtSvg import *  # Must import QtSvg to use svgs as icons
import sys 
from utils import Utils 

class VisibilityButton(QToolButton): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCheckable(True)
        self.setChecked(True)
        self.setIcon(QIcon('images/visible.svg'))
        self.clicked.connect(self.onClicked)

    def onClicked(self, checked): # checked:bool. Indicates state button is in after click
        if checked: # If we checked our vis button, setIcon(visible)
            self.setIcon(QIcon('images/visible.svg'))
        elif not checked: 
            self.setIcon(QIcon('images/notVisible.svg'))

    def setChecked(self, checked):
        super().setChecked(checked)
        if checked: 
            self.setIcon(QIcon('images/visible.svg'))
        elif not checked: 
            self.setIcon(QIcon('images/notVisible.svg'))

        
class LayersVisibilityWidgetItem(QWidget):
    radioButtonClicked = Signal(bool, str)
    visibilityButtonClicked = Signal(bool, str)
    def __init__(self, layer, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self._layer = layer

        self.setLayout(QHBoxLayout())
        
        palette = QPalette()
        palette.setColor(QPalette.Window , Utils.layerColors[layer])
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        
        self._radioButton = QRadioButton()
        self._radioButton.clicked.connect(lambda checked : self.radioButtonClicked.emit(checked , self._layer)) 
        self._radioButton.clicked.connect(self.onRadioButtonClicked)
        pal = QPalette() # Give radio button contrasting colors when checked for better visibility
        pal.setColor(QPalette.Window , Qt.black)
        pal.setColor(QPalette.Accent , Qt.white)
        self._radioButton.setPalette(pal)
        self.layout().addWidget(self._radioButton)
        
        label = QLabel(f" {layer}") # Add a space beforehand for easier on the eyes
        label.setStyleSheet("QLabel { background-color : white;  }")
        self.layout().addWidget(label)
        
        self._visibilityButton = VisibilityButton()
        self._visibilityButton.clicked.connect(lambda checked: self.visibilityButtonClicked.emit(checked, self._layer))
        palette = QPalette()
        palette.setColor(QPalette.Accent , Utils.layerColors[layer])
        self._visibilityButton.setPalette(palette)
        self.layout().addWidget(self._visibilityButton)
        # Get rid of the frame around a QWidget? Use QBoxLayout.setSpacing(0)
        # Get QRadioButton's checked state to have white core : Use QPalettes 
        
    def onRadioButtonClicked(self, checked): 
        if checked: # If we checked our radio Button, setvisButton(checked)
            self._visibilityButton.setChecked(True)
            self._visibilityButton.setIcon(QIcon('images/visible.svg'))


    def radioButton(self):
        return self._radioButton 
    def layer(self):
        return self._layer

# My LVW is taking up too much space! How can I make it scrollable? Thats what a QListWidget does... 

class LayersVisibilityWidget(QWidget): 
    radioButtonClicked = Signal(str)
    VisibilityButtonClicked = Signal(str)
    visibilityUpdated = Signal(dict)

    setActiveLayer = Signal(str)
    # setTopmostLayer = Signal(str)
    showLayer = Signal(str)
    hideLayer = Signal(str, list) # hiddenLayer:str, showingLayers:list # Need both to implement sensible layer hiding
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0) 

        buttonGroup = QButtonGroup(self) 
        self.lvwiDict = {} # A dict to store layerVisWidItems 
        self.visibility = dict(zip(Utils.layers , [True] * len(Utils.layers) )) 
        self.visibility['topmost'] = 'F.Cu'
        # print('VISIBILITY:', self.visibility)
        
        for layer in Utils.layerColors: 
            lvwi = LayersVisibilityWidgetItem(layer)
            lvwi.radioButtonClicked.connect(self.onRadioButtonClicked)
            lvwi.visibilityButtonClicked.connect(self.onVisibilityButtonClicked)
            buttonGroup.addButton(lvwi.radioButton())
            self.lvwiDict[layer] = lvwi
            self.layout().addWidget(lvwi)

        buttonGroup.buttons()[0].setChecked(True) # Check the first button
        
    def onRadioButtonClicked(self, checked, layer):
        print('LAYER:', layer)
        print('CHECKED:', checked)
        self.setActiveLayer.emit(layer)
        self.showLayer.emit(layer)

        # self.visibility[layer] = True
        # self.visibility['topmost'] = layer
        # self.visibilityUpdated.emit(self.visibility)
        
    def onVisibilityButtonClicked(self, checked, layer):
        print('LAYER:', layer)
        print('CHECKED:', checked)

        if checked == True:
            self.showLayer.emit(layer)
            # self.visibility[layer] = True

        elif checked == False: 
            showingLayers = [layer for layer in self.lvwiDict if self.lvwiDict[layer]._visibilityButton.isChecked() ]
            print('SHOWING LAYERS: ', showingLayers)
            self.hideLayer.emit(layer, showingLayers)
            # self.visibility[layer] = False
            


        # self.visibilityUpdated.emit(self.visibility)

    
    # Problem: The LVW is not scrollable, SO it takes up large vertical space... It needs to be scrollable. Utilizing a QScrollArea is easiest. Tried a QListWidget(Which is scrollable), but A QListView would be better suited, but that is an optimization.
        
class LayersVisibilityWidgetScrollWindow(QWidget): 
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            scroll = QScrollArea()
            # scroll.setHorizontalScrollBar()
            self.layersVisibilityWidget = LayersVisibilityWidget()
            scroll.setWidget(self.layersVisibilityWidget)
            scroll.setWidgetResizable(True)
            # scroll.setFixedHeight(200)
        # layout = QtWidgets.QVBoxLayout(self)
            self.setLayout( QVBoxLayout() )
            # layout.addWidget(scroll)
            self.layout().addWidget(scroll)

            groupBox = QGroupBox('Options')
            groupBox.setLayout(QVBoxLayout())
            self.showAllLayersButton         = QPushButton('Show all layers')
            # showAllLayersButton.clicked.connect(self.showAllLayersButtonClicked)
            self.showCopperLayersButton = QPushButton('Show all copper layers')
            self.hideNonCopperLayersButton = QPushButton('Hide non copper layers') 

            # self.showAllLayersButton.clicked.connect(self.onShowAllLayersButtonClicked)
            groupBox.layout().addWidget(self.showAllLayersButton)
            groupBox.layout().addWidget(self.showCopperLayersButton)
            groupBox.layout().addWidget(self.hideNonCopperLayersButton)

            self.layout().addWidget(groupBox)


# lvw = LayersVisibilityWidget()
# lvwsw = LayersVisibilityWidgetScrollWindow(lvw)
# lvwsw.show()


# sys.exit(qApp.exec())

