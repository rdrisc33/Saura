from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPen, QColor

from gerber_writer import * 
from FootprintItem import MyPadItem

class GerberLayer(DataLayer):

    def __init__(self, layer, ):
        
        self.setLayer( layer )
        set_generation_software("Robert Driscoll", 'gerber_writer_example.ipynb', '2025.08')
        trace_width = .254

        if self.layer() == 'F.Cu':
            super().__init__("Copper,L1,Top,Signal")
            self.color = Qt.red
            
        elif self.layer() == 'B.Cu':
            super().__init__(f'Copper,L4,Bot')
            self.color = Qt.blue 
            
        elif self.layer() == 'F.Paste': # Paste,Top|Bot # Locations to apply solder paste
            super().__init__(f'Paste,Top')
            self.color = Qt.green
        elif self.layer() == 'B.Paste':
            super().__init__(f'Paste,Bot')
            self.color = Qt.darkGreen
            
        elif self.layer() == 'F.Fab':
            self.color = Qt.cyan
            super().__init__('FabricationDrawing') # Auxilliary drawing: hole positions, board outline, sizes/tolerances,layer stack, material, finish, etc.
        elif self.layer() == 'B.Fab':
            self.color = Qt.darkCyan
            super().__init__('FabricationDrawing')
        
        elif self.layer() == 'F.SilkS':
            super().__init__('Legend,Top')
            self.color = Qt.gray
        elif self.layer() == "B.SilkS":
            super().__init__('Legend,Bot')
            self.color = Qt.darkGray
            
        elif self.layer() == 'F.Mask': # "Soldermask,Top|Bot<index>" # index is if there is >1 solder mask on a side(Usually omitted, bc only one soldermask per side)
            self.color = Qt.yellow
            super().__init__("Soldermask,Top")
        elif self.layer() == "B.Mask":
            self.color = Qt.darkYellow
            super().__init__("Soldermask,Bot")
            
        elif self.layer() == 'Edge.Cuts': # Profile,P|NP #  Contains only the board profile. P for edge-plated NP if not
            self.color = Qt.darkGreen
            super().__init__('Profile,')
                             
        elif self.layer() == 'F.Adhesive':
            self.color= Qt.red
            super().__init__("Glue,Top")
        elif self.layer() == "B.Adhesive":
            self.color = Qt.darkRed
            super().__init__('Glue,Bot')

        else: 
            raise ValueError(f"Disallowed to instantiate a GerberLayer with invalid layer. layer is: {self.layer()}")
        
    def add_pad(self, pad:MyPadItem):
        w = pad.width 
        h = pad.height
        item = pad.childItem()

        if pad.pad_shape == 'rect': 
            center=  (item.pos() + QPointF(w/2 , h/2)).toTuple()
            smd_pad = Rectangle(w, h ,'SMDPad,CuDef')
            super().add_pad( smd_pad, center , item.rotation()) #AttributeError: 'GerberLayer' object has no attribute 'g_o_stream'

        elif pad.pad_shape == 'circle':
            smd_pad = Circle(w, 'SMDPad')
            # super().add_pad(smd_pad, (item.pos() + QPointF(w/2, h/2)).toTuple() , item.rotation() )
        
    def to_gerber(self, layer_name):
        #check if the datalayer has any contents: to do this, we'll look at the DataLayer.g_o_stream, aka gerber output stream, aka a list, in which all the gerber items are collected 
        print()
        print('LEN(G_O_STREAM):', len(self.g_o_stream))
        if len(self.g_o_stream):
            
            with open(f"gerbers\\{layer_name}" , 'w') as fo: 
                self.dump_gerber(fo)
            
        # with open("gerbers\\MyGerber.gbr", 'w') as fo: 
        # top.dump_gerber(fo)

    def layer(self):
        return self._layer 
    def setLayer(self,layer):
        self._layer = layer
        


      