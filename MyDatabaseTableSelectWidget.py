from utils import * 
from Database import Database

class MyDatabaseTableSelectWidget(QComboBox):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.db = Database()
        tables= self.db.metadata.tables.keys()
        print('TABLES:', tables)
        self.insertItems(0, tables)
        
# HOw Do I reach from this file into MySchematic, in order to update MySchematic.table upon selection change, without a circular import? A: create an instance of this widget in MySchematic, and only .connect() it after its been instantiated there. Plus, connect it to a slot belonging to MySchematic, don't keep the slot here! 

        
# QCombobox shows the currently selected item, and a pop up list of selectable items when clicked. Comboboxes can contain pixmaps too, via overloads. .setEditable() then .setCompleter() to enable auto-complete. You cannot alter the selecteionMode of the view with .setSelectionMode(why?)
# Default a QStandardItemModel stores the items, and a QListView displays the popuplist. Access with .model() and .view() 
# .setItemData() 
# .itemText()a
# .setModel()
# .setView()

# Populate with .insertItem/s(). 
# .currentText() get text of currently selected item
# .text(idx) get text of item at idx
# .count() Number of items in combobox
# setEditable() # enable editing
# setCompleter() # set autocompletion, for editable comboboxes. 

# .setItemText() 
# .removeItem() 
# .clear() Remove all items in combobox
# Editable comboboxes default InsertAtBottom. Change with .setInsertPolicy()
# .clearEditText() clears displayed string, w/o changing contents( For editable comboboxes)
# A QValidator constrains the input to an editable combobox. .setValidator