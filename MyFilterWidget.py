from utils import * 
from MyFilterWidget import * 
from TableWidget import * 

class MyFilterWidget(QWidget): # A Widget. A splitter with a MyTableWidget on the left, and a MyFilterWidget on the right. 
    def __init__(self, mpn=None, categories=None, parent=None):
        super().__init__(parent)
        self.btn_general = QPushButton("general")
        self.btn_category_specific = QPushButton("category_specific")
        self.btn_primary = QPushButton("primary")
        self.btn_price = QPushButton("price")

        btn_group = QButtonGroup(self) # Invisible, but, manages the buttons within: Exclusive buttonGroups only allow ONE button to be on at a time.(NOte: exclusive buttonGroups need one button set ON initially) buttonGroup is exclusive by default.
        btn_group.addButton(self.btn_general)
        btn_group.addButton(self.btn_category_specific)
        btn_group.addButton(self.btn_primary)
        btn_group.addButton(self.btn_price)  
        
        group_box = QGroupBox("Filter Columns") # Aesthetic box drawn around a layout. To put items in a groupBox, put em in a layout, then set that layout
        
        group_box_layout=QHBoxLayout()
        group_box_layout.addWidget(self.btn_general)
        group_box_layout.addWidget(self.btn_category_specific)
        group_box_layout.addWidget(self.btn_primary)
        group_box_layout.addWidget(self.btn_price)
        group_box.setLayout(group_box_layout)

        
        main_layout= QHBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)
        # I can't .connect() here--Bc I need access to slots belonging to spreadsheet instance, which doesn't exist here. 