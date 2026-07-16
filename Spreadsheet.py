from utils import *
from sqlalchemy import * 
import sys, os 
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow

from MyFilterWidget import MyFilterWidget
# from MyDatabase import MyDatabase 
from Database import database
from TableWidget import TableWidget
# from MyGraphicAssign import MyGraphicAssign # I moved this class HERE after realizing MMW & MyGraphicAssign needed each other & I couldn't figure out how to do that without circular imports 

class MyComboBoxTables( QComboBox ):
    def __init__(self, parent=None):
        super().__init__(parent)
    def insertItems(self, items):
        items = list(database.metadata.tables)[1:] # names of table in db, grab idx 1 onwards; the 0th table is 'ss_filters', which we don't want to see
        super().insertItems(0, items)
        
class Spreadsheet( QMainWindow ): # Spreadsheet centric interface for selecting parts & adding them to your design. Also provides quality-of-life part browsing features like filtering & sorting parts 

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._toolbar = QToolBar(self) # QTB parented on self 
        self._toolbar.setOrientation(Qt.Orientation.Vertical)
        # Qt.ToolButtonStyle
        add_net_symbol_action       = self._toolbar.addAction('Add Net Symbol')
        add_part_action             = self._toolbar.addAction('Add Part')
        transpose_table_action      = self._toolbar.addAction('Transpose Table')
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self._toolbar) # initialize toolbar area to the left
        
        
        self._filter = None
        
        database.changed.connect(self.reload_part) # Whenever the database entries get updated, or inserted, or deleted, I want to refresh MyTableWidget and possibly combo_box_tables.

        self.filter = MyFilterWidget()
        self.filter.btn_general.clicked.connect(lambda checked: self.filter_btn_clicked(checked, 'general_attributes'))
        # tables= database.metadata.tables.keys()# Exclude the first table bc that is the 'ss_filters' table
#           File "c:\Users\robby\OneDrive\part_database\MySpreadsheet.py", line 43, in __init__
        self.table=TableWidget() 

        self.combo_box_tables = MyComboBoxTables() # Select the table from parts.db Ex 'microcontrollers
        self.reload_combo_box_tables() # Gonna setCurrentText, which in turn triggers table.setTable
        self.combo_box_tables.currentTextChanged.connect(self.table.setTable) 

        # self.combo_box_tables.currentTextChanged.emit(text) # Do this once @ start, after .connections are done,  to put data from database into the model
        
        central_widget_layout = QVBoxLayout()
        central_widget_layout.addWidget(self.combo_box_tables)
        central_widget_layout.addWidget(self.table)
        central_widget_layout.addWidget(self.filter)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(central_widget_layout)

        # self.setLayout(central_widget_layout) 
        # database = MyDatabase()
        # self.table = MyTableView(MyTableModel())
        # model = self.table.model()
        # print("MODEL.UPDATE_DATABASE:", model.update_database)
        # print('database.UPDATE:', database.update)
        # model.update_database.connect(database.update) # bc I create a whole new model every time the columns rearrange, I HAVE to re.connect() the model's signals/slots, which is BAD PRACTICE since it happens in 3x different locations...

            # tables = list(database.metadata.tables) # names of table in db, grab idx 1 onwards; the 0th table is 'ss_filters', which we don't want to see
            # self.combo_box_tables.insertItems(tables)
        #     self.combo_box_tables.currentTextChanged.connect(MyTableModel())
        # TypeError: 'PySide6.QtCore.QObject.connect' called with wrong argument types:
        #   PySide6.QtCore.QObject.connect(QComboBox, str, MyTableModel)
        # Supported signatures:
        #   PySide6.QtCore.QObject.connect(Union[bytes, bytearray, memoryview], PySide6.QtCore.QObject, Union[bytes, bytearray, memoryview], PySide6.QtCore.Qt.ConnectionType = Instance(Qt.AutoConnection))
        #Connections to update the table when user picks a new table 
        # self.combo_box_tables.currentTextChanged.connect(MyTableModel()) NO BAD 
        # self.combo_box_tables.currentTextChanged.connect(MyTableModel)#???MyTableView.setModel)
        # self.combo_box_tables.currentTextChanged.connect(database.create_model)
        # database.create_model_finished.connect(self.table.setModel) # Q: Do I need to decorate .setModel with @Slot? I think so
        # Connections to change the view & database when the model changes. The View protects against user changing model on a restricted column

    def reload_part(self, part):
        print()
        print('SPREADSHEET.RELOAD_PART')
        table_name = part.get('table_name', "")
        print('TABLE_NAME:', table_name)
        if table_name:
            self.reload_combo_box_tables() # 

    def reload_combo_box_tables(self):
        tables = list(database.metadata.tables) # names of table in db, grab idx 1 onwards; the 0th table is 'ss_filters', which we don't want to see
        self.combo_box_tables.clear() # Remove all items from combo_box_tables
        self.combo_box_tables.insertItems(tables) # insert items at idx default idx=0 
        # print('SELF.TABLE.TABLE():', self.table.table())
        self.combo_box_tables.setCurrentText(self.table.table()) # --> c_b_t.CTChanged.cnct(self.setTN) --> table.setDF
        
            
    def setDataframe(self, dataframe):
        print("SPREADSHEET.SETDATAFRAME")
        self.table.setDataframe()
        
    @Slot()
    def filter_btn_clicked(self, checked, filter):
        print()
        print(f'{filter} BUTTON CLICKED')
        self.table.reorder_columns(filter)

#FILTER
    @property 
    def filter(self):
        return self._filter
    
    @filter.setter
    def filter(self, filter):
        if self._filter:
            self._filter.deleteLater()
        self._filter = filter

### TESTING ### 
# app = QApplication(sys.argv) # Gotta create the application instance before ur widgets table.show()
# # table_name = database.get_all_table_names()[1]
# # table = MyTableWidget(table_name)
# spreadsheet = MySpreadsheet()
# spreadsheet.table.reorder_columns('general_attributes')
# spreadsheet.show()
# sys.exit(app.exec())

# COMBO_BOX_TABLES : the drop-down selection box showing names of tables in database(except the ss_filters table, which has info on the tables themselves)








### Just documnentation of the troubles I was having with connecting signals to their slots: 
# ss_filters_table.select(ss_filters).where(ss_filters_table.c.table_name == table_name) # Pick the row from ss_filters_table where the 'categories' column equals the currently chosen table_name
#             stmt = select(ss_filters_table.c.general).where(ss_filters_table.c.table_name == table_name) # SELECT general FROM ss_filters_table #TODO how do I select just the 'categories' column? A: can't use table.select(), as it allows no column arguments. use straigth up select() method. 
#             res = database.execute_stmt(stmt)
#             general_columns = res.fetchone()[0].split(',') # columns = res[0] TypeError: 'CursorResult' object is not subscriptable
#             other_columns = [ c for c in self.table.model()._data.columns if not c in general_columns ]
#             print()
#             # print("self.table.model._data.columns", self.table.model()._data.columns) # self.table.model._data.columns Index(['mpn', 'vendor', 'mfr', 'symbol'], dtype='object')
#             print("GENERAL_COLUMNS:", general_columns)
#             print('OTHER_COLUMNS', other_columns) #"mfr"
#             general_columns.extend(other_columns) 
#             print()
#             print('GENERAL_COLUMNS AFTER:', general_columns)
# # Give the tableView a new model
#             # model = MyTableModel(self.table.model()._data.loc[:, general_columns]) # reorder the model's data. NOTE sometimes we'll want to load straight from database...
            
#             # model.update_database.connect(database.update) # Every Time we instantiate a new .model, we have to connects its signals/ slots anew
#             # self.table.setModel(model)