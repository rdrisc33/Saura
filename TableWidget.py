from PySide6.QtCore import Qt , QLineF, QMimeData
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QAbstractItemView, QAbstractScrollArea, QHeaderView
from PySide6.QtGui import QIcon, QPixmap , QDrag 
import sys
import os 
import json
import pandas 
from utils import *
from MyGraphicAssign import MyGraphicAssign
from MyPrimaryAttributesAssign import MyPrimaryAttributesAssign
from Database import database # import my database singleton 

from urllib.parse import urlparse 
from PySide6.QtGui import QBrush
from PySide6.QtCore import Qt # needed for GlobalColor
import webbrowser

# self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)   What would this do

class TableWidget(QTableWidget):
    # clicked = Signal(dict) # record: dict, representing part which was clicked . 
    def __init__(self, table=None, parent=None):
        super().__init__(parent)
        
        if table is None: 
            if len(database.metadata.tables) <= 1: # Check if there are tables in database, if there are, pick a table to show, but if not, show some default data. 
                self.setTable("")
                dataframe = test_dataframe
                self.setDataframe(dataframe)
                print()
                print('DATAFRAME:', dataframe)
            else: 
                table = list(database.metadata.tables)[1] # [1] because [0] is ss_filters table, which I dont wanna see
                self.setTable(table)
                
        if table is not None: # Check a second time: did we pick a table? if so , set it
            self.setTable(table) # setTableName 
            
        self.horizontalHeader().clicked.connect(self.on_horizontal_header_clicked) # Doesn't do anything
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel) # Change from default ScrollPerItem; default makes for a blocky scroll
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setAlternatingRowColors(True) # Aesthetic
        self.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents) # Not sure what this does... SizeAdjustPolicy: This enum specifies how the size hint of a QAbstractScrollArea should adjust when the size of the viewport changes. Default no adjust. AdjustToContents: The scroll area will always adjust to the viewport
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents) # overkill.. cell with longest text dictates column length
        # self.resizeRowsToContents() # Not strictly needed
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # NOT FOR ME QHeaderView will automatically resize the section to fill the available space. The size cannot be changed by the user or programmatically.

        self.resizeColumnsToContents()

            
    def mouseMoveEvent(self, event):
        # print('MYTABLEWIDGET.MOUSEMOVEEVENT')
        if QLineF(event.position(), self.start).length() < QApplication.startDragDistance():
            # print('Distance too short to begin QDrag')
            return 
        # self.clicked.emit(self.record) This doesnt quite work how I want 
        drag = QDrag(self) # Stopped using QDrag in favor of (Sch/Brd)Scene.addDesignItemMode
        # print('JSON.DUMPS(self.record):', json.dumps(self.record))
        mime_data = QMimeData()
        mime_data.setText(json.dumps(self.record))
        drag.setMimeData(mime_data)
        # drag.setPixmap()
        # print('ABOUT TO EXEC')
        drag.exec()
        print('DRAGDONE')
        
    def mousePressEvent(self, event):
        print('MYTABLEWIDGET.MOUSEPRESSEVENT')
        self.start = event.position()
        self.record = self.itemAt(event.position().toPoint()) # Returns None or the item at given QPoint 
        if not self.record: 
            return 
        row_idx, col_idx = self.record.row(), self.record.column()
        self.record = self.dataframe().iloc[row_idx].to_dict()
        print('PRESSED THIS RECORD:', self.record)
        # self.clicked.emit(self.record) # I didn't like this feauure
        super().mousePressEvent(event) # Enable base implementation to handle things like selecting & more.

    def on_item_selection_changed(self):  # Q why this emits no args? 
        # print(f"Item Selection Changed:")
        pass
            
    def on_horizontal_header_clicked(self):
        print('HorizontalHeaderClicked:')

    def mouseDoubleClickEvent(self, event):
        print()
        print('MyTableWidget.MOUSEDOUBLECLICKEVENT')
        item = self.itemAt(event.position().toPoint())
        column = self.horizontalHeaderItem(item.column()).text()
        print('COLUMN:', column)
        row_idx = item.row()
        
        if not column in writeable_columns: # Handle non-writeable columns(open url if it is url)
            print('This column is not editable')
            data = item.data(Qt.ItemDataRole.UserRole) # See if I stored a url in the userDataRole
            print('DATA:', data)
            if isinstance(data, str):
                if urlparse(data).scheme: # If this has a 'http' in it: 
                    webbrowser.open(data)
            
                    
        else: 
            part = self.dataframe().iloc[row_idx].to_dict()
            # row_idx = item.row()
            print('PART:', part)
            if column == 'primary_attributes':
                primary_attribute_assign = MyPrimaryAttributesAssign(part, self)
                primary_attribute_assign.open()
            if column == 'reference_designator': 
                print('You double clicked the "reference_designator" column') # User can assign a new reference_designator at a table level. reference_designator is stored at a table level in ss table
                
            else:
            # Then, I need to launch a MyGraphicAssign, or a MyPrimaryAttributes assign, depending on which colum was clicked.
                self.graphic_assign = MyGraphicAssign(part, column, self)
                self.graphic_assign.open() # Launch dialog or won't show up
        # return super().mouseDoubleClickEvent(event)

        
    
    def table(self):
        return self._table
    
    def setTable(self, table):
        
        if not isinstance(table, (str,None) ):
            raise TypeError(f'TABLENAME: {table}\nIS OF TYPE{type(table)}\nBUT EXPECTED str|None TYPE')
        
        if (table is None) or(table == ""):
            self._table = table
            dataframe = test_dataframe
            self.setDataframe(dataframe)
            return True
        else: 
            df = database.get_df(table)
            if df is not None: 
                self._table = table 
                # print( f'SET MyTableWidget._table to : {self._table}')
                self.setDataframe(df)
                self.reorder_columns('general_attributes') # Automatically apply the 'general_attributes' column order
                return True
        print('setTable Error')
        return False
            
    def dataframe(self):
        return self._dataframe
    
    def setDataframe(self, dataframe): 
        self._dataframe = dataframe
# Wrangle the tableWidget to display the dataframe
        num_rows, num_cols = self.dataframe().shape
        self.setRowCount(num_rows)
        self.setColumnCount(num_cols)
        if not dataframe.columns.empty:
            self.setHorizontalHeaderLabels(dataframe.columns)
        if not dataframe.index.empty:
            self.setVerticalHeaderLabels(dataframe.index)

# Other processing 
        for row_idx in range(num_rows):
            for column_idx in range(num_cols):
                value = str(dataframe.iloc[row_idx, column_idx]) 
                table_item = QTableWidgetItem(value) # Note we'll add items to table via .setItem() not via setting a parent. Table Items hold text, mostly, but also checkboxes &icons.
                parse = urlparse(value)
                # print('PARSE:', parse)
                
                if os.path.exists(str(value)): # If this is a path, don't show the full path, but the root
                    head,tail = os.path.split(value)
                    # print('df value is a path that exists')
                    root, ext = os.path.splitext(tail)
                    table_item.setText(root) # Only display the name of the file 
                    
                elif parse.scheme: # if this has a url 'scheme' (http or https), show a blue 'view' hyperlink
                    # print('THIS IS A URL:', value )
                    table_item.setText('view')
                    table_item.setForeground(Qt.GlobalColor.blue) # Make the text color blue 
                    font = table_item.font() # Get the current font so we can underline it
                    font.setUnderline(True) 
                    table_item.setFont(font) # Make the text underlined 
                    # We enact hyperlink behavior via doubleClickEvent
                    table_item.setData(Qt.ItemDataRole.UserRole, value) # Put hyperlink in UserRole. When we doubleClickEvent on 'datasheet', we'll webbroswer.open( UserRole's text )
                    # mpn = parse_path.split('/') # If theres something in the second-to-last slash, maybe its the mpn: display it. Nah this doesn't work because we get all sorts of urls, too varied for this to work     
        # Process 'primary_attributes such that actual values are displayed.
                elif dataframe.columns[column_idx] == 'primary_attributes':

                    column = dataframe.loc[: , 'primary_attributes']
                    # print()
                    # print('column:', type(column), column)
                        # capacitance,voltage_rated,package/case
                        # Name: primary_attributes, dtype: object
                    for count, cell in enumerate(column): 
                        name = []                                           # Blank name
                        primary_attributes = cell 
                        if not primary_attributes:                          # Don't proceed if primary_attributes haven't been assigned
                            table_item.setText("") 
                        else:
                            primary_attributes = primary_attributes.split(',')                # convert primary_attributes to list
                            # print("PRIMARY_ATTRIBUTES:", primary_attributes)
                            
                            if primary_attributes:                              # check if we made a list
                                for attribute in primary_attributes:            # 
                                    name.append(dataframe.iloc[count].loc[attribute])             # assemble name -- use pandas .loc[] syntax
                                name = '_'.join(name)                           # convert name to string
                                name = name.replace(' ', '')                    # remove all spaces
                                # print('Assembled name: ', name)                 #
                                table_item.setText( name ) 

                self.setItem(row_idx, column_idx, table_item)
                # print()
                # print("ITEM.SIZEHINT", table_item.sizeHint()) # An invalid size hint : ITEM.SIZEHINT PySide6.QtCore.QSize(-1, -1)

    def update(self, row_idx, column, value): 
            self.dataframe().loc[self.row_idx, column] = value 
            self.setDataframe(self.parent().dataframe()) # Note we don't need to .setTableName bc we havent altered tableName.
            # print('REFRESHED TABLEWIDGET WITH NEW VALUE')

    def reorder_columns(self, filter:str):
        filter_columns = database.get_filter( self.table(), filter)
        if not filter_columns:  
            return 
        # We got a new column order but we still want to show columns not included in the new_column order, tack them onto the end 
        all_columns = self.dataframe().columns
        filter_columns.extend( [ c for c in all_columns if not c in filter_columns])
        # print('NEW_COLUMN_ORDER:', filter_columns)
        self.setDataframe( self.dataframe().loc[:, filter_columns] ) 

   


# df = pandas.DataFrame([[0,1,2], [3,4,5]], columns = ['A', 'symbol', 'footprint'], index = ['a','b'])

# self.reorder_columns(database.get_table('ss_filters')) # too hard to get 

# print(df.index.empty) # See if df has a set index
# df['B'].iloc[0] = 'HiThere' # set a new value to the dataframe # DONT USE THIS CHAINING SYNTAX! It will be depreceated in pandas 3.0-- use .loc[] instead! ( NOTE: it ok to do df['B'] -- by itself -- don't chain a .iloc[] onto it)
# df.loc[0, 'B'] = 10# To set a new value to the dataframe, you should use .loc[row , col] But, note that new value should be of same type as oldvalue. 
# This is weird-- since I set index, pandas uses that index to lookup rows-- thus there is no row '0' anymore, its row 'a'-- and the call to df.loc[0,'B'] = 10  causes a new row, with row_idx = 0, to be appended to the df.
# df['B'] = 0 # Set whole column to a new value

### TESTING ### 
# app = QApplication(sys.argv) # Gotta create the application instance before ur widgets table.show()
# table = database.get_all_tables()[1]
# table = MyTableWidget(table)
# table.reorder_columns('general_attributes')
# table.show()
# sys.exit(app.exec())


        
    