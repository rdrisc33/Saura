# from enum import Enum
# class NetPriority(Enum): 
#     NoPriority          = 0
#     Pad                 = 1
#     NetSymbol           = 2
    
from utils import Utils 
class Net(): 
    def __init__(self, net=None, priority = Utils.NetPriority.NoPriority): 
        self._net = net 
        self._priority = priority 

    def __eq__(self, other): 
        if not isinstance(other, Net):
            return NotImplemented 
        return self._net == other._net

    def __hash__(self): # https://stackoverflow.com/questions/1227121/compare-object-instances-for-equality-by-their-attributes
        return hash( (self._net,) )
    
    def __str__(self): 
        return f"{self._net} {self._priority}"

    def __repr__(self):
        return f"Net(net={self.net()}, priority={self.priority()}"
    
    def net(self):
        return self._net 
    def setNet(self, net): 
        self._net = net 

    def priority(self):
        return self._priority 
    def setPriority(self, priority):
        self._priority = priority 


    
    