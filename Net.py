# from enum import Enum
# class NetPriority(Enum): 
#     NoPriority          = 0
#     Pad                 = 1
#     NetSymbol           = 2
    
from utils import Utils 
class Net(): 
    """ This class represents an area of connected copper. It can also track net chimeras; 'illegal' nets connected to two+ netSymbols, these chimeras probably represent a critical design flaw.  OK instead of tracking chimeras, I did what kicad does, which is just ignore any extra nets, picking just one and pretending theres only one net.
    WAIT how can I be sure this class is immutable? Since only immutables should reimplement dunderhash"""
    
    # def __init__(self, net=None): 
    def __init__(self, *nets): # can take any number of nets 

        for net in nets: 
            if not isinstance(net, str):
                raise(TypeError, f"Expected 'net' to be a string but got net: {net} of type: {type(net)}")

        self._nets = [net.upper() for net in nets] # Convert everything to uppercase. 0V and GND not 0v nor gnd
        self._net = frozenset(self._nets)

    def __eq__(self, other): 
        if isinstance(other, str):
            if len(self._net) == 1: 
                return other.upper() == list(self._net)[0]
            else:
                return NotImplemented 
        elif not isinstance(other, Net):
            return NotImplemented 
        
        return self._net == other._net

    def __hash__(self): # https://stackoverflow.com/questions/1227121/compare-object-instances-for-equality-by-their-attributes
        return hash(  (self._net,) )
    
    def __str__(self): 
        if len(self.net()) == 1: 
            return f"Net({list(self.net())[0]})"                # Net(GND)
        elif len(self.net()) > 1: 
            return f"Net({', '.join(str(x) for x in self.net())})"  # Net(GND, 3V3)

    def __repr__(self):
        return f"Net({self.net()})"
    
    def net(self):
        return self._net 
    def setNet(self, net): 
        self._net = net 

    def isNull(self):
        if self.net() is frozenset(): 
            return True 
        return False
    
# class Net(): 
#     def __init__(self, net=None, priority = Utils.NetPriority.NoPriority): 
#         self._net = net 
#         self._priority = priority 

#     def __eq__(self, other): 
#         if not isinstance(other, Net):
#             return NotImplemented 
#         return self._net == other._net

#     def __hash__(self): # https://stackoverflow.com/questions/1227121/compare-object-instances-for-equality-by-their-attributes
#         return hash( (self._net,) )
    
#     def __str__(self): 
#         return f"{self._net} {self._priority}"

#     def __repr__(self):
#         return f"Net(net={self.net()}, priority={self.priority()}"
    
#     def net(self):
#         return self._net 
#     def setNet(self, net): 
#         self._net = net 

#     def priority(self):
#         return self._priority 
#     def setPriority(self, priority):
#         self._priority = priority 

#     def isNull(self):
#         if self.net() is None: 
#             return True 
#         return False


# net = Net()
# print('net.isNull():', net.isNull())
# net2 = Net('3V3')
# print('net2.isNull():', net2.isNull())
# net3 = Net(None)
# print('net3.isNull():', net3.isNull())

