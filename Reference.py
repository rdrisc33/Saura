
class Reference():
    def __init__(self, referenceDesignator, referenceNumber):
        super().__init__()
        
        self._referenceDesignator = None    # 'R' for resistors 'C' for capacitors 'L' for inductors 'U for microcontrollers etc
        self._referenceNumber   = None      # The number part of 'R28' 'LED03' etc   
        
        self.setReferenceDesignator(referenceDesignator)
        self.setReferenceNumber(referenceNumber)
        
    def referenceDesignator(self):
        """The R in 'R28'"""
        return self._referenceDesignator
    def setReferenceDesignator(self, referenceDesignator):
        self._referenceDesignator = referenceDesignator
        
    def referenceNumber(self):
        """The 28 in 'R28'"""
        return self._referenceNumber
    def setReferenceNumber(self, referenceNumber):
        self._referenceNumber = referenceNumber
        
    def reference(self):
        """R28" or "LED03"""
        return f"{self.referenceDesignator()}{str(self.referenceNumber())}" 
    