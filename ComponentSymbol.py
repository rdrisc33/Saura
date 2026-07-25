from utils import *

from Symbol import Symbol
    # def __init__(self, referenceDesignator, referenceNumber, symbolFile=None ,footprintFile=None , part=None,*args,**kwargs):
    
class ComponentSymbol(Symbol): 
    def __init__(self, referenceDesignator, referenceNumber, file, *args, **kwargs): # 
        super().__init__(referenceDesignator=referenceDesignator, referenceNumber=referenceNumber, file=file, *args, **kwargs)

        self.nameItem().hide() # default hide Symbol names( ex 'STM32C06F6T-R' , we don't want to see that on the schematic )
        
        for pin in self.pins(): 
            pin.nameItem().show()
            pin.numberItem().show()

    # def terminals(self): # IDT we ever need terminals in local coords....
    #     return self._terminals 
    # def setTerminals(self):
    #     self._terminals = []
    #     for pin in self.pins(): 
    #         self._terminals.append(self.term)
        

    def sceneTerminals(self):
        # keys = list(map(QPointF, [t[0] for t in self._sceneTerminals] , [ t[1] for t in self._sceneTerminals]))# Note self_sceneTerminals is keyed on tuples, not QPointF, use map() to revert back to QPointF
        # self._sceneTerminals: { ( 0,0 ) : <pin> , ... }
        
        return self._sceneTerminals # [ ( (0,0) , <pin> ) , ... ]

    def setSceneTerminals(self): # Called by self.mouseMoveEvent
        self._sceneTerminals = []
        for pin in self.pins(): 
            self._sceneTerminals.append( pin.sceneTerminal() )
            

        



        # self._sceneTerminals = {}
        # for pin in self.pins():
        #     self._sceneTerminals[ self.mapToScene(pin.lineItem.line().p1()).toTuple() ] = pin 
        # # print('COMPSYM.SCENETERMINALS:', self.sceneTerminals())
        #     # self._sceneTerminals.append( ( pin.lineItem.line().p1())) NO BAD because pins are in parent coordinates

            
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        print('COMPONENTSYMBOL.SCENETERMINALS():', self.sceneTerminals())    
    # def mouseMoveEvent(self, event):
        
    def mouseMoveEvent(self, event): 
        self.setSceneTerminals()
        super().mouseMoveEvent(event)
        
    @classmethod
    def fromPart(cls, part, referenceNumber):
        file = part.get('symbol')
        referenceDesignator = part.get('referenceDesignator', '?')
        
        return cls(referenceDesignator, referenceNumber, file)
