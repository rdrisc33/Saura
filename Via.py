from utils import * 
from ViaItem import ViaItem
from LayersItem import LayersItem

class Via(ContainerItem):
    def __init__(self, outerDiameter, innerDiameter, layers=Utils.CuLayers, *args, **kwargs): # layers : A via may exist on all or some layers, default all
        
        for layer in self.layers():
            self.layer_items[layer].extend(ViaItem(innerDiameter, outerDiameter, layer, self))
