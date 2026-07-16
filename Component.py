from PySide6.QtWidgets import * 
from PySide6.QtCore import *
from PySide6.QtGui import *
from utils import Utils  

from ComponentSymbol import ComponentSymbol
from FootprintItem import FootprintItem
from Reference import Reference

class Component(Reference):
    
    def __init__(self, referenceDesignator, referenceNumber):
        #, mpn, mfr, vendor): 
        # symbolFile=None ,footprintFile=None , part=None, *args,**kwargs):
        # Note part serves as primary key ( mpn, mfr, vendor )
        super().__init__(referenceDesignator, referenceNumber)
        
        self._isDiscrete = False 
        self._inBom = False 
        self._primaryAttributes = None 
        self._value = None # '4R7' for a 4.7ohm resistor
        self._name = None 
        self._mpn = None 
        self._symbolItem = None 
        self._footprintItem = None 
        self._symbolFile = None 
        self._footprintFile = None 
        self._id = None                         # Trace,Via,Zone,Pad, items don't need a reference. (No 'T37' for a trace, no V9 for a via) Nor do they need a value, so leave those fields None. But, since they're going in the rtree, they need an id; the rtree requires a unique id. 

        self.referenceItem = QGraphicsSimpleTextItem(self.reference())  # "R4" "C1" "?3" etc. Parented on 'self'; child items draw themselves. TODO: position of reference value needs to be intelligently set
        self.referenceItem.setFont(Utils.symbolFont)

        self.valuePreference = Utils.ValuePreference.ReferenceDesignator
        
    @classmethod
    def fromPart(cls, part, referenceNumber):#, *args, **kwargs): 
        referenceDesignator = part.get('referenceDesignator', '?')
        
        c = cls( referenceDesignator, referenceNumber)
        
        c.setPart(part)
        c.setSymbolFile(part.get('symbol')) # TODO change part key to symbolFile 
        c.setFootprintFile(part.get('footprint'))
        return c

        # open the file, check if its a netSym or not, return 
    def part(self):
        return self._part
    def setPart(self, part):
        self._part = part 
        
    
    def symbolItem(self):
        return self._symbolItem
    def setSymbolItem(self, symbolItem):
        self._symbolItem = symbolItem 

        
    def footprintItem(self):
        return self._footprintItem
    def setFootprintItem(self, footprintItem):
        self._footprintItem = footprintItem

        
    def symbolFile(self):
        return self._symbolFile
    def setSymbolFile(self, symbolFile):
        self._symbolFile = symbolFile 
        self.setSymbolItem(ComponentSymbol(self.referenceDesignator(), self.referenceNumber(), self.symbolFile()))

        
    def footprintFile(self):
        return self._footprintFile 
    def setFootprintFile(self, footprintFile):
        self._footprintFile = footprintFile
        self.setFootprintItem(FootprintItem(self.referenceDesignator(), self.referenceNumber(), self.footprintFile() ))
        
    def part(self):
        return self._part
    def setPart(self, part):
        self._part = part

    def set_id(self, id):
        if not self._id: 
            self._id = id
        else: 
            print('Self._id already set, change will not go through')




    # def mpn(self):
    #     return self._mpn 
    # def mfr(self):
    #     return self._mfr 
    # def vendor(self):
    #     return self._vendor