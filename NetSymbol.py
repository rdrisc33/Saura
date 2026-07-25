from utils import *

from Symbol import Symbol

class NetSymbol(Symbol):
    def __init__(self, referenceDesignator, referenceNumber, file):
        super().__init__(referenceDesignator=referenceDesignator, referenceNumber=referenceNumber, file=file)
        self._sceneTerminals = [] 

    def setSceneTerminals(self):
        for pin in self.pins(): 
            self._sceneTerminals.append(pin.scenePos())

    def net(self): 
        """The net of a NetSymbol is the same as its referenceDesignator"""
        return self.referenceDesignator()