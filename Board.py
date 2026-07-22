from PySide6.QtWidgets import*
from PySide6.QtGui import *
from PySide6.QtCore import *

# from MyView import MyView
from BoardView import BoardView 
# from MyScene import MyScene
from FootprintItem import FootprintItem
from BoardScene import BoardScene
from utils import Utils 
from LayersVisibilityControlWidget import LayersVisibilityControlWidget

import sys
import os

    
class Board(QWidget): # Board goes in the stacked widget centralWidget of the MainWindow. Shares stackedwidget with  MySchematic and MyFabrication 
    netclasses = {
        'default': 
            {'units': 'mm', 
            'clearance': 0.2 ,
            'track_width': 0.2 ,
            'via_size': 0.6 ,
            'via_hole': 0.3 ,
            'u_via_size': 0.3 ,
            'u_via_hole': 0.1 ,
            'dp_width': 0.2 ,
            'dp_gap': 0.25 } ,
        }
    
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True) 

        self.view = BoardView()
        # self._scene = MyScene(-1000,-1000, 2000,2000)
        self._scene = BoardScene()#-1000,-1000, 2000,2000)
        # self._scene.addEllipse(QRectF(-20,-20, 40,40), QPen(Qt.darkRed)) # Draw an origin mark

        self.view.setScene(self._scene)

        self.layersVisibilityControlWidget = LayersVisibilityControlWidget()
        # self.layersVisibilityControlWidget.setTopmostLayer.connect(self._scene.setTopmostLayer)
        self.layersVisibilityControlWidget.toggleLayerVisibility.connect(self.onVisibilityToggled)
        self.layersVisibilityControlWidget.onlyShowCopperLayers.connect(self._scene.onlyShowCopperLayers)
        
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.view)
        self.layout().addWidget(self.layersVisibilityControlWidget)
        
        
        # btn = QPushButton("Create Gerbers", self)
        # btn.clicked.connect(self.create_gerbers)
        # self.layout().addWidget(btn)
    def scene(self):
        return self._scene 
    
    def onVisibilityToggled(self, checkState , layer): # CheckState is an enum, Qt.CheckState, can be on/off/partial 
        print()
        print('LAYER:', layer)
        print('CHECKSTATE', checkState)
        if checkState == Qt.CheckState.Checked: 
            self._scene.showLayer(layer)
        elif checkState== Qt.CheckState.Unchecked: 
            self._scene.hideLayer(layer)

            
    def onlyShowCopperLayers(self):
        print('SHOWING ONLY CU LAYERS')
        for layer in Utils.layers: 
            if layer in Utils.CopperLayers: 
                self.showLayer(layer)
            else: 
                self.hideLayer(layer)
                
    def create_gerbers(self):
        
        from ComponentSymbol import ComponentSymbol
        from FootprintItem import FootprintItem, MySubFootprint,  MyCircleItem, MyPadItem
        from TerminalItem import TerminalItem
        from WireItem import WireItem
        from GerberLayer import GerberLayer
        from utils import Utils 
        
        gerber_layers =  {}

        for kicad_canonical_layer in kicad_canonical_layers:
            gerber_layers.update( {kicad_canonical_layer:GerberLayer(kicad_canonical_layer) } )
            
        # print("datalayers:", datalayers) # a dict of gerber layers 

        for item in self._scene.items():
            if isinstance(item, FootprintItem):
                
                for i in [ layer_item for layer_item in item.childItems() if isinstance(layer_item, MySubFootprint) ] : 

                    print('I:', i , type(i) )
                    print('I.LAYER():', i.layer())
                    print('I.LAYERS():',i.layers())
                    if isinstance(i, MyPadItem):
                        print('IS A PAD ITEM')
                        for l in i.layers():
                            
                            gl = gerber_layers[l]     
                            gl.add_pad(i)
                        
                    elif isinstance(i, MyCircleItem):
                        print('IS A CIRCLE ITEM')
                        print('')
                        gl = gerber_layers[i.layer()]
                        gl.add_trace_arc(i.start, i.end, i.center, orientation="+", width=.254,function="Conductor")
                        
        for layer_name, layer  in gerber_layers.items(): 
            layer.to_gerber(layer_name)
                
###GERBER SPEC### 
# One gerber file per layer; Each gerber file has a dedicated layer .
# Layer0 DNE, starts at layer1

# Non/Plated span from layer1 to layer4 : (NonPlated , Plated), 1,4 ,(NPTH|PTH|Blind|Buried) , (Drill,Rout,Mixed)


###TESTING###
# app = QApplication(sys.argv)
# screen_dpi = app.screens()[0].physicalDotsPerInch()
# # print('PHYSICAL_DPI:', screen_dpi)  PHYSICAL_DPI: 113.41395348837209

# board = MyBoard()

# board.show()

# sys.exit(app.exec())