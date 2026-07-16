from utils import * 

class CentralWidget(QStackedWidget):
    def __init__(self,schematic, board, parent=None):
        super().__init__(parent)
        self._schematic         = None 
        self._board             = None
        self.setAcceptDrops(True) # 
        
        self.setSchematic(schematic)
        self.setBoard(board)
        
    def setSchematic(self, schematic):
        if self.schematic(): #  Run only once
            print('You already set a schematic')
            return 
        self.addWidget(schematic)
        self._schematic = schematic

    def schematic(self):
        return self._schematic
    
    def setBoard(self, board):
        if self.board(): # Run only once
            print('You already set a board.')
            return 
        self.addWidget(board)
        self._board = board

        
    def board(self):
        return self._board
    