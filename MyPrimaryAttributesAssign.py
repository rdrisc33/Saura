from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout,QVBoxLayout, QLabel, QPushButton, QLineEdit, QWidget, QGroupBox, QFileDialog, QGraphicsScene,QGraphicsView, QApplication, QComboBox, QSizePolicy
from PySide6.QtCore import Signal, Slot, Qt, QModelIndex
from MyThirdPartyDownloadExtract import MyThirdPartyDownloadExtract
from MyKicadSymbolConverter import MyKicadSymbolConverter
import webbrowser
import sys
import os
from Database import database

class MyPrimaryAttributesAssign(QDialog): # Let user assign symbol and/or footprint to a part, useful for new parts 
    
    def __init__(self, part, parent=None): 
        super().__init__(parent)
        self.part = part
        self.combo_boxes = []
        self.no_selection = "No Selection"
        self.current_attributes = self.part.get('primary_attributes', "").split(',') # Get existing primary_attributes if any, so as to set default combo_box values. Also cast to list.
        print("SELF.CURRENT_ATRIBUTES:", self.current_attributes)
        print()
        self.add_contents()

    def add_contents(self):
        self.setLayout(QVBoxLayout())
        
    # Create a sort of header, displaying the MPN & table_name
        
        self.mpn_layout = QHBoxLayout()
        self.mpn_layout.addWidget(QLabel("MPN:"))
        self.mpn_layout.addWidget(QLabel(self.part.get('mpn' , "" )))
        self.mpn_widget = QWidget()
        self.mpn_widget.setLayout(self.mpn_layout)
        
        self.table_name_layout = QHBoxLayout()
        self.table_name_layout.addWidget(QLabel('Table Name:'))
        self.table_name_layout.addWidget(QLabel(self.part.get('table_name', "")))
        self.table_name_widget = QWidget()
        self.table_name_widget.setLayout(self.table_name_layout)
        
        self.header_layout = QVBoxLayout()
        self.header_layout.addWidget(self.table_name_widget)
        self.header_layout.addWidget(self.mpn_widget)
        self.header_widget = QWidget() 
        self.header_widget.setLayout(self.header_layout)
        
        self.layout().addWidget(self.header_widget)
                

        self.texts = list(self.part)
        self.texts.insert(0, self.no_selection) # str "No Selection" Allow for nothing to be selected 
        
        self.add_additional_attribute('Primary:')
        self.add_additional_attribute('Secondary:')
        self.add_additional_attribute('Tertiary:')
        for c, attr in enumerate(self.current_attributes): # Try to set default combo_box values based on primary_attributes, if any
            try: 
                idx = self.texts.index(attr)
                self.combo_boxes[c].setCurrentIndex(idx) 
            except ValueError: 
                self.combo_boxes[c].setCurrentText("") # Its possible that we have not yet assigned primary attributes, in which case, selection box should show ""
            
        # self.button_more.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum) This didn't make the '+' button small to fit its "+".

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        self.layout().addWidget(button_box)
        
    def add_additional_attribute(self, title):

        label = QLabel(title) # Ex 'Primary:', 'Secondary:', "Tertiary:"
        combo_box = QComboBox()
        self.combo_boxes.append(combo_box) # Track our cboxes so we can get their .currentText() in .accept()
        combo_box.insertItems(0, self.texts)# part is a dict, when cast as list, changes to list of just keys.

        container = QWidget() # To hold a label and line edit 
        layout = QHBoxLayout()
        container.setLayout(layout)
        layout.addWidget( label )
        layout.addWidget( combo_box )
        
        self.layout().addWidget(container)
           
    def accept(self):
        print()
        print('QDIALOG.ACCEPT: Base implementation Hides the modal dialog and sets the result code to Accepted.')
        self.primary_attributes = "" # Get ready to assign new primary_attributes...
        for combo_box in self.combo_boxes: 
            if combo_box.currentText() == self.no_selection: # Stop 
                break 
            self.primary_attributes += f",{combo_box.currentText()}" # Problem, this guarantees a string starting with comma
        self.primary_attributes = self.primary_attributes.strip(',') # Rid the starting comma
        print('ASSIGNED THESE PRIMARY ATTRIBUTES:', self.primary_attributes)
        
        if (self.primary_attributes == "") or (self.primary_attributes.split(',') == self.current_attributes): # Don't update the database 
            return 
        # self.part.update( {'primary_attributes' : self.primary_attributes} )  # Update dict self.part
        # Update the database. Because we already did a sql INSERT on our scrape to get it in the database, we now need to sqlUPDATE that record. Then reload the tableView.
        
        database.update_ss_filters(self.part.get('table_name') , {'primary_attributes' : self.primary_attributes})
        # rowcount = database.update(self.part, newData) # update the database, with a sqlUPDATE stmt. the 'rowcount' return value indicates how many rows were updated. database.update emits Signal .changed(table_name), which .connects to spreadsheet.setTableName(table_name), which refreshes data via tableWidget.setDataframe and ss.comboBoxTables.setCurrentText()
        # This is how I WAS updating the dataframe, but: I think I would have database update dataframe: 
        # if self.parent() is not None and self.row_idx is not None: # update the parent()'s dataframe, using .loc[] syntax. parent() ex
        #     self.parent().dataframe().loc[self.row_idx, column] = value 
        #     self.parent().setDataframe(self.parent().dataframe()) # Note we don't need to .setTableName bc we havent altered tableName.
        #     print('REFRESHED TABLEWIDGET WITH NEW VALUE')
        super().accept() 
    def reject(self):
        print()
        print('QDIALOG.REJECT: Base Implementation Hides the modal dialog and sets the result code to Rejected.')
        super().reject()
        
# app = QApplication(sys.argv)
# part = {'ultralibrarian': 'https://ultralibrarian.com' , 'snapmagic': 'https://snapmagic.com'}
# part = {'primary_attributes': '', 'symbol': 'C:/Users/robby/OneDrive/part_database/symbols/LTST-C190GKT.sym', 'footprint': '', 'package/case': '4-DIP Module', 'reference': None, 'unit_price': 4.9, 'mpn': 'IRM-01-12', 'vendor_part_page': 'https://www.digikey.com/en/products/detail/mean-well-usa-inc/IRM-01-12/7704612', 'mfr': 'MEAN WELL USA Inc.', 'vendor': 'Digikey', 'standard_pricing': "[{'BreakQuantity': 1, 'UnitPrice': 4.9, 'TotalPrice': 4.9}, {'BreakQuantity': 5, 'UnitPrice': 4.7, 'TotalPrice': 23.5}, {'BreakQuantity': 10, 'UnitPrice': 4.5, 'TotalPrice': 45.0}, {'BreakQuantity': 25, 'UnitPrice': 4.4, 'TotalPrice': 110.0}]", 'vendor_part_number': '1866-2990-ND', 'table_name': 'power_supplies_board_mount_ac_dc_converters', 'categories': 'power supplies_board mount,ac dc converters', 'type': 'Enclosed', 'number of outputs': '1', 'voltage_input': '85 ~ 305 VAC, 120 ~ 430 VDC', 'voltage_output 1': '12V', 'voltage_output 2': '-', 'voltage_output 3': '-', 'voltage_output 4': '-', 'current_output (max)': '83mA', 'power (watts)': '1 W', 'applications': 'ITE (Commercial)', 'features': 'Universal Input', 'operating temperature': '-30°C ~ 85°C (With Derating)', 'efficiency': '74%', 'mounting type': 'Through Hole', 'size/dimension': '1.33" L x 0.87" W x 0.59" H (33.7mm x 22.2mm x 15.0mm)', 'approval agency': 'CB, CE, cURus, TUV', 'datasheet': 'https://www.meanwell.com/upload/pdf/IRM-01/IRM-01-spec.pdf', 'eda_model': '', 'ultralibrarian': '', 'snapmagic': '', 'misc_media': ', https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/2540/MFG_IRM-01.jpg, https://www.meanwellusa.com/Upload/PDF/RoHS_PFOS.pdf, https://www.meanwell.com//Upload/PDF/MW%20REACH%20SVHC%20declaration-2025.pdf, https://www.digikey.com/product-highlight/m/mean-well/irm-90-series-ac-dc-industrial-pcb-mount-power-module, https://www.traceparts.com/els/digikey/goto?Product=33-22052023-101082&SelectionPath=1|1|4|1|4|4|4|4|4|, https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/4892/Product_Change_Notice_29-DEC-2020.pdf, https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/59/Product_Upgrade_Notice_17-JAN-2020.pdf'}
# dialog = MyPrimaryAttributesAssign(part=part)
# dialog.open() # Shows the dialog as a window modal dialog, returning immediately. Connect to the 'finished' signal to know when the dialog has been QDialog.Accepted or QDialog.rejected


# sys.exit(app.exec())