###QABSTRACTTABLEMODEL###
    #Abstract means its not meant to be directly used, but subclassed
    #Retreive a model index with .index(row_idx, col_idx)
    #Must reimplement .rowCount(), .columnCount(), and .data(). Should also reimplement .headerData()
    #For editable models, must also reimplement .setData() and .flags()
    #For resizeability, reimplement .insertRows(), insertColumns(), removeRows(), removeColumns().These reimplementations call .beginInsert/RemoveColumns/Rows() before & after insertion/removal of rows/columns, like so: 

    # def insertRow(self, row:int, parent:QModelIndex=None): #Inserts a blank row before 'row' in the child items of the parent specified.
    #     # -> True if row inserted else Flase 
    #     self.beginInsertRows(parent,first=row, last=row) #must call before inserting new rows into the model. This function emits the rowsAboutToBeInserted() signal which connected views (or proxies) must handle before the data is inserted. Otherwise, the views may end up in an invalid state.
    #     #insertrowshere # but wait I have no data to insert, so I guess that happens after insertion of blank rows. 
    #     self.endInsertRows()  must call immediately after insertion of new rows 

###SIGNALS(inherited from QAbstractItemModel)
#DATACHANGED(topLeft, bottomRight,roles)
# MyTableModel.dataChanged(cell, cell) 
#HEADERDATACHANGED(orientation, first, last) 
# MyTableModel.headerDataChanged(Qt.Vertical, 0, len(headerData))
###SLOTS
#.REVERT: Lets the model know that it should discard cached information. (used for row editing)
#.SUBMIT: Lets the model know that it should submit cached information to permanent storage(aka itself?). (used for row editing)

import sys, os 
from PySide6.QtCore import Qt, QDir, Signal, Slot, QAbstractTableModel, QModelIndex, QObject
from PySide6.QtWidgets import QApplication, QFileSystemModel, QSplitter,QTreeView, QListView, QLabel, QWidget, QVBoxLayout, QTableView, QMainWindow
from PySide6.QtGui import QColor, QIcon
import datetime
import pandas
from utils import * 
from Database import database

class MyTableModel(QAbstractTableModel):
    
    # update_database = Signal(str, str, str, str, str, str) # (table_name, mpn, vendor, mfr, column, value)
    # update_database = Signal(str, str, str, str, str, str) # (table_name, mpn, vendor, mfr, column, value)
        
    def __init__(self, data=None, parent=None): # What should the parent of a Model be?
        super().__init__(parent)
        if data is None:  # explicit comparison to 'None' bc pandas.DataFrame objects evaluate neither True nor False. see also df.empty
            print('Data is None')
            data = pandas.DataFrame([
                ["123abc", 'digikey', 'kyocera', 'capacitor_unipolar'],
                [-1,-2,-3, -4],
                ], columns = ['mpn', 'vendor', 'mfr','symbol'], index=['Row 1', 'Row 2'])
        
        if not isinstance(data, pandas.DataFrame):
            data = pandas.DataFrame(data)
        self._data = data # self._data is the core of our model; the data of our model.

        # self.dataChanged.connect(self.on_data_changed)
        self.update_database.connect(database.update) # Have to .connect signals/slots anew every time we instantiate a new model (bad practice-- happens in 3x locations -- )     

        # model.update_database.connect(self.database.update) # bc I create a whole new model every time the columns rearrange, I HAVE to re.connect() the model's signals/slots, which is BAD PRACTICE since it happens in 3x different locations...

        # self.update_database.connect(self.parent().parent().db.update) Q: How come I can't do this? 
        # self.update_database.connect(MyDataBase().update()) Happens elsewhere(IN MySpreadsheet atm), bc we need access to a MyDatabase instance to .connect() to it, but we don't have that here

    # @Slot(str) # This was essentially doing the job of the constructor
    # def create_model(self, table_name):
    #     df = database.get_df(table_name)
    #     if df.empty: # True if Series/DataFrame is entirely empty (no items), meaning any of the axes are of length 0.
    #         print("DF IS EMPTY") 
    #     model = MyTableModel(df)
    #     model.update_database.connect(database.update) # Have to .connect signals/slots anew every time we instantiate a new model (bad practice-- happens in 3x locations -- )     
    #     self.create_model_finished.emit(model)
    
    @classmethod
    def from_table_name(cls, table_name): # Construct a MyTableModel instance via querying database for table_name
        df = database.get_df(table_name)
        return cls(df)
    
    def supportedDragActions(self): # # Note model still must implement .removeRows() to effect dnd moveactions
        return Qt.DropAction.CopyAction #| Qt.DropAction.MoveAction
    
    def rowCount(self, index): # The view only knows how many rows are in this model because rowCount() will tell the view how many rows are in the model
        return self._data.shape[0] # DataFrame.shape is an attribute holding the [numRows, numColumns]
    
    def columnCount(self, index):
        return self._data.shape[1]
    
    def data(self, index, role=Qt.DisplayRole): # The view will ask this model for data. The view will request an INDEX, and a ROLE.
        value = self._data.iloc[index.row() , index.column()] # This MAY BE int or float, and the DisplayRole expects a str ?
        
        if role == Qt.DisplayRole: 
            if self.headerData(index.column()) in [ 'symbol' , 'footprint', 'cad_model', 'spice_model'] and isinstance(value, str): # path: C:/Users/robby/OneDrive/part_database/symbols/LTST-C190GKT.sym
            # print('VALUE:', value)
# self.model()._data.loc[:,'symbol'].iloc[ index.row() ] AKA self.model().data(index, role = Qt.UserRole)
                head, tail = os.path.split(value)
                root, ext = os.path.splitext(tail)
                return root # only show file name, not the abs path: 'LTST-C190GKT' 
            else:
                return str(value)
        
        else: # for all other roles, for now just return the value
            return value # Q: what roles will QTableView query for? 
        
        
        
    def headerData(self, section, orientation = Qt.Horizontal, role=Qt.DisplayRole):
        if role == Qt.DisplayRole: 
            if orientation == Qt.Horizontal: 
                return str(self._data.columns[section]) # DataFrame.columns -> column names, aka headers 
            if orientation == Qt.Vertical:
                return str(self._data.index[section]) # DataFrame.index -> row names 

    def flags(self, index): #Returns the flags for given index. Base implementation sets ItemIsEnabled and ItemIsSelectable flags. We need to additionally set ItemIsEditable flag to make it editable

        # if not self._data.columns : NO BAD THIS FAILED SILENTLY # ValueError: The truth value of a Index is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all(). # HEY HOW COME THIS ERROR DID NOT SHOW FOR ME WTH? # print('True') if self._data.columns else print('False')  # pandas .columns EVALUATION IS UNDEFINED: ValueError: The truth value of a Index is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all(). # HEY HOW COME THIS ERROR DID NOT SHOW FOR ME WTH? 
        if self._data.columns.empty: #  YES GOOD MUST EVALUATE PANDAS.DF INDICES WITH .EMPTY
            print('MODEL._DATA HAS NO COLUMNS. CANNOT TELL WHICH COLUMNS TO MAKE EDITABLE')
            return super().flags(index) # NO EDITING IF NO COLUMNS| Qt.ItemFlag.ItemIsEditable
        # print('Model has Columns, but only select columns should be editable') #We only want certain columns ('symbol' 'footprint' etc) to be editable.
        column = self._data.columns[index.column()]
        if column.lower().strip() in writeable_columns: # This item should be editable
            return super().flags(index) | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled
        else: 
            return super().flags(index) | Qt.ItemFlag.ItemIsDragEnabled
            

    def setData(self, index, value, role=Qt.EditRole): #
        # Sets the role data for the item at index to value. Must be reimplemented for editable models; base implementation returns False.  if successful return True & emit .dataChanged(),  else return False 
        # EditRole: str, so as to edit in an editor
        print()
        print("SETDATA:")
        typ = type(self._data.iloc[index.row(), index.column()])
        try:
            value = (typ)(value) # get type of the data already in df, then cast 'value' as that type
        except: 
            print("SETDATA type(value) different type than what was already in the DataFrame, which pandas disallows.")
            return False
        if role == Qt.UserDataRole or role == Qt.EditRole: # EditRole must be used by the editor delegate, the final value doesn't propogate to cell if displayRole used
            print(f'SETTING DATA FOR {role.value}')
            self._data.iloc[index.row(), index.column()] = value # set this model's data ( which is our DataFrame in _data)
            self.dataChanged.emit(index, index, role) # QAbstractTableModel.dataChanged Signal must be emitted in reimplementations of setData(), (WHY THO) since this signal is emitted whenever an existing item changes. 
            # What does .dataChanged.connect() to? 
            return True
        return False # If False is returned the value displayed will be reverted to the previous value
        
    def get_record(self, row_idx:int):
        row = list(self._data.iloc[row_idx])
        columns = list(self._data.columns)
        record = zip( columns, row ) 
        return record
    
model = MyTableModel() # The one instance of model;singleton, accessible by MyGraphicAssign ( But I need to make a new model() instance every time I reorder columns)
