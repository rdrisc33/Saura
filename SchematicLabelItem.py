from utils import * 

from SchematicItem import SchematicItem

class SchematicLabelItem(SchematicItem): 
    def __init__(self):
        super().__init__()
        
    # This class has stuff for labels like double click to set text
    

class LocalLabelItem(SchematicLabelItem):
    pass 
class HierarchyLabelItem(SchematicLabelItem):
    pass 
class GlobalLabelItem(SchematicLabelItem):
    pass