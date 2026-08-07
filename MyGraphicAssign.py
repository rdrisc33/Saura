from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout,QVBoxLayout, QLabel, QPushButton, QLineEdit, QWidget, QGroupBox, QFileDialog, QGraphicsScene,QGraphicsView, QApplication
from PySide6.QtCore import Signal, Slot, Qt, QModelIndex
from MyThirdPartyDownloadExtract import MyThirdPartyDownloadExtract
from kicadSymbolConverter import KicadSymbolConverter
import webbrowser
import sys
import os
from Database import database

class MyGraphicsAssign(QDialog): # Let user assign symbol and/or footprint to a part, useful for new parts 
    
    def __init__(self, part, parent=None): 
        print('MyGraphicsAssign.__init__()')
        super().__init__(parent)
        self.part = part
        self.add_contents()

    def add_contents(self):
        self.setLayout(QVBoxLayout())
        button_symbol = QPushButton('Add Symbol')
        button_symbol.clicked.connect(self.assign_graphic_symbol)
        button_footprint = QPushButton('Add Footprint')
        button_footprint.clicked.connect(self.assign_graphic_footprint)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok| QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout().addWidget(button_symbol)
        self.layout().addWidget(button_footprint)
        self.layout().addWidget(self.button_box)
        
    @Slot()
    def assign_graphic_symbol(self):
        self.symbol_assign = MyGraphicAssign(self.part, 'symbol') # gotta be self.symbol_assign for memory permanence; to not instantly delete
        # self.symbol_assign = MyGraphicAssign(self.parent(), 'symbol', self.part) # Parenting on 'self.part' makes no sense? 
        self.symbol_assign.open()
        
    @Slot()
    def assign_graphic_footprint(self):
        self.footprint_assign = MyGraphicAssign(self.part, 'footprint')
        self.footprint_assign.open()
        
class MyGraphicAssign(QDialog):
    # finished = Signal(int) # This signal is emitted when the dialog's result code has been set ( But don't reimplement it-- signals aren't meant to be reimplemeneted--if you 'reimplemented' a signal, all you would do is just create another signal with same name, which causes problems down the line(?according to a forum post) same/different type signatures, still bad to do. So make a new Signal
    # all_done = Signal(str, dict, QModelIndex, str) # (graphic_type, part, index, selected_file) # Where graphic_type is 'symbol' 'footprint' 'cad_model' etc. Known from column user double-clicked on in the table, unless its fresh off a scrape
    
    def __init__(self, part, graphic_type, parent=None): # part argument needed such that we can access any snapmagic/ultralibrarian links. Parent&row_idx needed such that I know where to update parent's dataframe-- both may be NOne, in which case its assumed there is no TableWidget displaying our dataframe                    Old strategy: I ditched: where this part is in the table, lets us know where to update the table, if we grabbed this part from the table. NOt that, because Signals/Slots demand correct type of object, we shouldnot set index to None, as None is not of type QModelIndex, instead, we can make a 'empty' QModelIndex(), which satisfies the type constraints. Importantly, passing the QMainWindow as our 'parent' lets us .connect() the dialog's Signals to QMainWindow's Slots, within the dialog's constructor... Also, GraphicAssign & MainWindow classes share the same folder; they depend on each other; I couldn't avoid circular import when they were in separate folders. ( Q on whether this indicates any bad practice? )
        super().__init__(parent)
        self.graphic_type = graphic_type.lower().strip() 
        self.part = part

        # self.mpn= None
        self.mpn = self.part.get('mpn')
        self.selected_file = None
        
        self.setWindowModality(Qt.WindowModality.NonModal) # Choose QT.NonModal(nonBlocking) or Qt.WindowModal(kindaBlocking) or Qt.ApplicationModal(all blocking) Default nonModal
        self.add_contents()
        # if parent():
        #     # if isinstance(parent, MyMainWindow) Circular import since MyMW imports this file... How can I check if MGA's parent is a MMW? (I need MMW access only because I need to .connect() to the database.update() slot... Is this indicative of poor design? How am I supposed to get around this? 
        #     self.
        
    def add_contents(self):
        
        group_box_select_existing = QGroupBox(f"Select Existing {self.graphic_type.capitalize()}") # where self.graphic_type is either 'footprint' or 'symbol' or 'cad_model'  .captitalize() capitalizes first letter 
        layout_select_existing = QHBoxLayout()
        group_box_select_existing.setLayout(layout_select_existing)
        
        btn_select_existing = QPushButton(f"Select Existing {self.graphic_type.capitalize()}:")
        btn_select_existing.clicked.connect(self.on_select_existing) 
        label_select = QLabel(f"Selected  {self.graphic_type.capitalize()}:")
        self.line_edit_select = QLineEdit("")
        
        layout_select_existing.addWidget(btn_select_existing)
        layout_select_existing.addWidget(label_select)
        layout_select_existing.addWidget(self.line_edit_select)
        
        group_box_download = QGroupBox(f"Download {self.graphic_type.capitalize()} from Third Party: ")
        layout_download = QHBoxLayout()
        group_box_download.setLayout(layout_download)

        
        if self.part: 
            eda_models = self.part.get('eda_models', None) # AttributeError: Error calling Python override of QGraphicsObject::mouseDoubleClickEvent(): 'function' object has no attribute 'get'
            url_snapmagic = self.part.get('snapmagic', None)
            url_ultralibrarian = self.part.get('ultralibrarian', None)
            
            print('Snapmagic Link:', url_snapmagic)
            print("Ultralibrarian Link", url_ultralibrarian)
            if url_snapmagic:
                btn_snapmagic = QPushButton("snapmagic")
                layout_download.addWidget(btn_snapmagic)
                btn_snapmagic.clicked.connect(lambda checked: self.on_download(url_snapmagic)) # Signal 'clicked' emits 'checked'.Trash that parameter via a lambda function whcih takes 'checked' but doesn't use it. Also, use 'snapmagic' in the lambda bc we want that argument.
            if url_ultralibrarian:
                print(url_ultralibrarian)
                btn_ultralibrarian = QPushButton("ultralibrarian")
                layout_download.addWidget(btn_ultralibrarian)
                btn_ultralibrarian.clicked.connect(lambda checked: self.on_download(url_ultralibrarian))
            if not (url_snapmagic or url_ultralibrarian): 
                layout_download.addWidget(QLabel('Part has no snapmagic/ultralibrarian links'))
        else: 
                layout_download.addWidget(QLabel('No part is was provided as argument'))


        self.group_box_extract= QGroupBox("Extract")
        self.btn_extract = QPushButton("Extract")
        layout_extract = QVBoxLayout()
        self.group_box_extract.setLayout(layout_extract)
        layout_extract.addWidget(self.btn_extract)
        self.group_box_extract.hide()
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box_select_existing)
        main_layout.addWidget(QLabel("OR:"))
        main_layout.addWidget(group_box_download)
        main_layout.addWidget(self.group_box_extract)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)
        
        title= f'Assign {self.graphic_type.capitalize()}'
        self.setWindowTitle(title)
    
    # def mousePressEvent(self, event):
    def accept(self): # updatee the database with the newly selected 'footprint' or 'symbol' file. 
        print()
        print('QDIALOG.ACCEPT: Base implementation Hides the modal dialog and sets the result code to Accepted.')
        self.part[f"{self.graphic_type}"] = self.selected_file ### update part with assigned graphic. (atm unused)
        # self.all_done.emit(self.graphic_type, self.part, self.index, self.selected_file) # Forwarding the same arguments we got, with the addition of self.selected_file. ( Oh-- which is a bit redundant-- I can NOT do this an move (some) of that code here)
        if self.selected_file is None:  # If we failed to assigned a symbol: do nothing
            print('SELF.SELECTED_FILE is None')
            return
        
        # Update the database. Because we already did a sql INSERT on our scrape to get it in the database, we now need to sqlUPDATE that record. Then reload the tableView.
        column = self.graphic_type
        value = self.selected_file
        rowcount = database.update(self.part, dict({column : value})) # update the database, with a sqlUPDATE stmt. the 'rowcount' return value indicates how many rows were updated 
        super().accept() 

        # if self.parent() is not None and self.row_idx is not None: # update the parent()'s dataframe, using .loc[] syntax. parent() ex
            
        #     self.parent().dataframe().loc[self.row_idx, column] = value 
        #     self.parent().setDataframe(self.parent().dataframe()) # Note we don't need to .setTableName bc we havent altered tableName.
        #     print('REFRESHED TABLEWIDGET WITH NEW VALUE')
            
#         if not self.index.isValid(): # If we supplied an index, use that index. Else, ee need to reverse engineer the data's integer location in the model for .setData function( the case when we scrape a new part or assign symbol via dclick on an item )
# # Get col_idx from df with columns.get_loc
#             col_idx = data.columns.get_loc(self.graphic_type)
# # Getting row_idx from df is...involved. 
#             result = data.loc[     (data['vendor'] == vendor)   &   (data['mfr'] == mfr)   &   (data['mpn'] == mpn)   ] # I need the row number out of this, tho 
#             row_idx = result.iloc[0].name # Get first row only. We just became a series; list, our df.columns just became our series.index; our df.index just became our series.name... confuzing
#             index = QModelIndex(row_idx, col_idx) # Now we know where this data is in our model, we can .setData() on it 
# # Testing : see the itemData at the index b4 we change it
#         print() 
#         print("ITEMDATA FOR INDEX B4 CHANGE:", model.itemData(index))
#         mpn = self.part.get("mpn")
        # role = Qt.UserDataRole # Gotta change this role, and the displayRole, the other roles Need not change(and probably contain None bc I've never used them) 
        # model.setData(index, value, role)
        # role = Qt.DisplayRole 
        # model.setData(index, value, role) 

        # model = MyTableModel.from_table_name(table_name) # if make a new model, Must set it as TableView's model. OR, update existing model... how to access?
        
        
        # model.model_created.emit()
        
        # MyTableModel().created_model.emit(model)
        # MyTableModel().created_model.connect(MyTableView.set)
        # self.spreadsheet.combo_box_tables.clear()
        # self.spreadsheet.combo_box_tables.insertItems(0, list(database.metadata.tables) [1:] ) # Casting a dict as a list() returns a list, of just the keys. (You would think dict.keys() would do this... but it don't)
        # self.graphic_assign.deleteLater()
        # super().accept()
        
    def reject(self):
        print()
        print('QDIALOG.REJECT: Base Implementation Hides the modal dialog and sets the result code to Rejected.')
        self.selected_file = "" # Erase any changes. Don't use None because None is not of type 'str', and signals/slots demand correct Typing.
        super().reject()
        
    @Slot(int)
    def on_select_existing(self, checked):

        folder = os.path.join( self.graphic_type+ 's' ) # folder is either /symbols, /footprints, /cad_models, /spice_models. # WE HAVE TO ADD AN 'S' ONTO self.graphic_type! Bc self.graphic_type is from the table, and table columns are named 'symbol' not 'symbols'
        if not os.path.exists(folder):
            print(f'FOLDER "{self.graphic_type}" DNE')
            return

        self.selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Symbol File",
            folder,
            "All Files (*.*)"
        )
        
        if self.selected_file: 
            print()
            print('GRAPHIC_ASSIGN_i.SELECTED_FILE:', self.selected_file)
            self.line_edit_select.setText(self.selected_file)
        else:
            self.line_edit_select.setText("")
            

    @Slot(str)
    def on_download(self, url):
        webbrowser.open(url) # User downloads 
# Insert a button that lets user ez-extract
        self.group_box_extract.show()
        self.btn_extract.clicked.connect(lambda checked: self.on_extract(url)) # Q: Do I need to mark the function called by my lambda function, as a @Slot? Q: Is it 'bad practice' to use lambda functions, bc they are not named as @Slots? 

        
    def on_extract(self, url): # Extract most recently downloaded Folder from 'Downloads', then rename, convert, & return .sym file as 'self.selected_file'. Now, self.selected_file is ready if we .accept() this dialog. 
        print()
        print("EXTRACTING:")
        root= MyThirdPartyDownloadExtract.unzip_most_recent() # This assumes user just downloaded the zip to downloads folder
        print('ROOT:', root) # ROOT: 3310Y-001-102L
        if 'ultralibrarian' in url.lower():
            ki_sym_file = MyThirdPartyDownloadExtract.ultralibrarian_rename_extracted(root)
        elif 'snapmagic' in url.lower() or 'snap' in url.lower():
            ki_sym_file = MyThirdPartyDownloadExtract.snapmagic_rename_extracted(root) # Hold up, cant invoke instance function, from class...
            
        # Now convert .ki_sym into .sym
        categories = self.part.get('categories')
        print('CATEGORIES:' , categories) 
        save_file = KicadSymbolConverter.convert(ki_sym_file, categories ) # Automatically make converted file the selected_file.
        if save_file: 
            self.selected_file = save_file
            self.line_edit_select.setText(save_file)# populate line_edit with 'self.selected_file' so user can see file was auto-selected. 
        print('SELECTED_FILE:', save_file)
        

        
# Hey what about converting the footprint, where does that happen? 
        
        

    @property
    def mpn(self):
        return self._mpn
    @mpn.setter

    def mpn(self,mpn):
        self._mpn = mpn


# app = QApplication(sys.argv)
# part = {'ultralibrarian': 'https://ultralibrarian.com' , 'snapmagic': 'https://snapmagic.com'}
# dialog = MySymbolAssign(part=part)
# dialog.open() # Shows the dialog as a window modal dialog, returning immediately. Connect to the 'finished' signal to know when the dialog has been QDialog.Accepted or QDialog.rejected


# sys.exit(app.exec())