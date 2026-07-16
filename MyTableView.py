import sys, os 
import pandas
from PySide6.QtWidgets import QApplication, QTableView, QMainWindow, QPushButton, QAbstractItemView
from PySide6.QtCore import Signal, Slot, QObject, Qt, QLineF, QMimeData, QByteArray, QModelIndex
from PySide6.QtGui import QDrag
# from MyTableModel import MyTableModel
from utils import * 
from MyGraphicAssign import MyGraphicAssign
import json

class MyTableView(QTableView): 
                              # (part, index      )
    assign_symbol       = Signal(dict, QModelIndex) # part is for the SymbolAssign widget and the index is so I know where to put it back in
    assign_footprint    = Signal(dict, QModelIndex)
    assign_spice_model  = Signal(dict, QModelIndex)
    assign_cad_model    = Signal(dict, QModelIndex)
    myDoubleClicked       = Signal(str, dict, QModelIndex) # (column, part, index). Cant use doubleClick, bc signals are not meant for reimplement and doubleClicked is already a QAbstractItemView Signal
    
    def __init__(self, table_name = None, model=MyTableModel(), parent=None):
        super().__init__(parent)
        
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True) 
        viewport = self.viewport()
        print()
        print('viewport:', viewport)

        self._table_name = table_name
        self.setModel(model)
        # self.assign_symbol.connect(self.on_assign_symbol)
        self.myDoubleClicked.connect(self.on_double_clicked)
        
        # self.table.assign_cad_model.connect(self.)
        # self.table.assign_spice_model.connect(self.)
        self.symbol_path = None 
        self.footprint_path = None 
        self.cad_model_path = None 
        self.spice_model_path = None
        
    @Slot(str) # text;table_name
    def setTableName(self, table_name):
        model = MyTableModel.from_table_name(table_name)
        self.setModel(model)
        
    def on_double_clicked(self, column , part , index):
        if column in['symbol' , 'footprint']: # Assign a graphic
            graphic_assign = MyGraphicAssign(column, part, index, self) # parented on MyTableView, self. #The only reason we pass index is so that we know the index where to insert our result
            graphic_assign.open()
            graphic_assign.all_done.connect(self.on_graphic_assign_all_done) # Note by making graphic_assign blocking;modal, I could know when its completed without needing to .connect() to a signal -- Ezr to code, possibily annoying for user-- but who cares about that 
        else:
            print('This column is not editable')
            # graphic_assign.all_done.connect(self.on_assign_symbol_all_done)
        # elif column in ['cad_model' , 'spice_model']: #Assign a file
        #     file_assign = MyFileAssign(column, part, index)
        #     file_assign.open()
        #     file_assign.all_done.connect(self.on_file_assign_all_done)
        
    def on_graphic_assign_all_done(self, column, part, index, selected_file):
        print()
        print('SYMBOL_ASSIGN ALL_DONE')
        print('SELECTED_FILE:', selected_file)
        self.model().setData(index, selected_file) #  How do I know what QModelIndex to give, to update my table?         

    # def on_assign_symbol(self, graphic_type, part, index): 
    #     symbol_assign = MyGraphicAssign(self, part, index) # parented on MyTableView? #The only reason we pass index is so that we know the index where to insert our result
    #     symbol_assign.open()
    #     symbol_assign.all_done.connect(self.on_assign_symbol_all_done)
        



# Code for drag enable dragging # Code also needed in the drop widget ( thats both the QGView and QGScene)
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.start = event.position().toPoint() # Q: Think the examples used globalPosition(). Any reason I should do the same? 
        
        # item = self.itemAt QTableView has no itemAt
        index = self.indexAt(event.position().toPoint()) #indexAt takes QPoint. event.position()->QPointF. convert QPointF to QPoint with QPointF.toPoint()
        self.record = json.dumps(self.model()._data.iloc[index.row()].to_dict())# get whole record(as a dict), we'll send this in our drag's mimeData as json text
        print('Pressed on Record:', self.record)

        # self.column = self.model().headerData(index.column(), Qt.Horizontal)
        # print('MYTABLEVIEW.COLUMN:', self.column)
        # self.symbol_path = self.model()._data.loc[:,'symbol'].iloc[ index.row() ] # Get the 'symbol' field of this row # This skips the 'proper' qt model API but who cares? Q: How do I do this with the .data() function; the'right' way? 
        # self.footprint_path = self.model()._data.loc[:, 'footprint'].iloc[ index.row() ] # Get the 'footprint' field of this row 
        # print('SYMBOL_PATH:', self.symbol_path)
        # print('FOOTPRINT_PATH:', self.footprint_path)


    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)
        
    def mouseMoveEvent(self, event):
        if QLineF(self.start, event.position()).length() < QApplication.startDragDistance(): # Detect if we clickNDrag; begin QDrag if we do so
            print("DistanceTooShortForDragOperation")
            return 
        # text ='mimeDataGoesHere' # testing
        # self.sym_path =  os.path.join(symbol_path, "LTST-C190GKT.sym") # testing 
        # print('SELF.SYM_PATH:', self.sym_path) 
        drag = QDrag(self)
        print('BEGIN DRAG:')
        mime = QMimeData()

        # drag_info = {
        #     'symbol_path':self.symbol_path,
        #     'footprint_path':self.footprint_path ,
        #     'cad_model_path':self.cad_model_path,
        #     'self.spice_model_path':self.spice_model_path
        #     }
        # plaintext = json.dumps(drag_info)
        plaintext = self.record
        # print('PLAINTEXT FOR DRAG:', plaintext)
        # Q: With weird 'mu' and +- and degrees symbol, is this text really 'plain'text? 
        
        # text = f"symbol_path:{symbol_path}" # Wrap up the text in json or something, or make some other mime data types to hold symbol_path & foopprint_path and such.
        mime.setData('text/plain', QByteArray(plaintext)) # carry path/to/sym/file in our drag's mime data. We'll open&parse the file on a drop
        drag.setMimeData(mime) # remember to set mime data 
        drag.exec() # remember to execute the drag
        print('BEGAN DRAG')
##
    def mouseDoubleClickEvent(self, event):
        print('DCLICK')
        index = self.indexAt(event.position().toPoint()) #indexAt takes QPoint. event.position()->QPointF. convert QPointF to QPoint with QPointF.toPoint()

        column = self.model().headerData(index.column(), Qt.Horizontal) #what column did user click on
        column = column.lower().strip() # normalize the string
        print('COLUMN:', column)
        row = list(self.model()._data.iloc[index.row()])
        part=  dict(zip(self.model()._data.columns , row))
        print()
        print('PART:', part)
        self.myDoubleClicked.emit(column, part, index)
        # if column == 'symbol': 
        #     self.assign_symbol.emit(part, index)
        # elif column == 'footprint':
        #     self.assign_footprint.emit(part, index)
            

            
            
        


# app = QApplication(sys.argv)
# table = MyTableView()
# table.resize(600,200)
# table.show()
# sys.exit(app.exec())        
# I wanna support dragNDrop of parts from the tableView onto my scene