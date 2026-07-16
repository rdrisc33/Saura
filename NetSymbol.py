from utils import *

from SchematicSymbolItem import SchematicSymbolItem

class NetSymbol(SchematicSymbolItem):
    def __init__(self, referenceDesignator, referenceNumber, file):
        super().__init__(referenceDesignator=referenceDesignator, referenceNumber=referenceNumber, file=file)
        

