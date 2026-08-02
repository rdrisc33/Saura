from utils import * 

from Symbol import Symbol

class Label(Symbol): 
    def __init__(self):
        super().__init__()
        
    # This class has stuff for labels like double click to set text
    

class LocalLabel(Label):
    pass 
class HierarchyLabel(Label):
    pass 
class GlobalLabel(Label):
    pass