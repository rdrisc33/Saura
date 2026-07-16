from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout,QVBoxLayout, QLabel, QLineEdit, QWidget, QApplication, QPushButton, QFileDialog
from PySide6.QtCore import Signal, Slot, Qt
import os
import sys 

from utils import *
from MyKicadSymbolConverter import MyKicadSymbolConverter
from MyKicadFootprintConverter import MyKicadFootprintConverter

class MyCreateDialog(QDialog):
    emit_choice = Signal(str) # This signal emits the chosen mpn, and is emitted when the dialog is .finished()
    
    def __init__(self, create, parent=None): # 'create' is the thing we're creating: 'symbol' , 'footprint', 'spice_model', 'cad_model' 
        super().__init__(parent)
        self.setWindowTitle(f"Create {create.capitalize()}") # Create Symbol , Create Footprint, etc
        self._create = create
        self.setWindowModality(Qt.WindowModality.NonModal) # Choose QT.NonModal(nonBlocking) or Qt.WindowModal(kindaBlocking) or Qt.ApplicationModal(all blocking) Default nonModal
        self.add_contents()
        self.resize(200,200)
        self.show() 

    def add_contents(self):
        layout = QVBoxLayout()
        for opt in CreateChoices: # draw, download, convert
            button = QPushButton(f"{opt.name.capitalize()}:")
            button.clicked.connect(lambda : self.on_button_clicked(button)) # Use a lambda function to 1) ignore the 'checked' paramter emitted by .clicked & 2)inject info on which button was pressed, via the argument 'button'. 
            layout.addWidget(button)

        # button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.Cancel) # This dialog dont need a button box.
        # layout.addWidget(button_box)
        
        self.setLayout(layout)

    def on_button_clicked(self, button): # Slots have access to self! bc 'self' is the first parameter... The emitted stuff goes after self... Ah, but I need the button within self which was clicked... that can be sent in a lambda
        print(f"BUTTON: {button} CLICKED")
        # if self.text() == create_choices[0]: 
        print()
        # print('button.text().lower():',button.text().lower()) # WARNING : HAS A COLON WHICH MUST BE REMOVED FOR STR COMPARISON
        # print('CreateChoices.CONVERT.name.lower()', CreateChoices.CONVERT.name.lower())
        if 'convert' in button.text().lower().strip().strip(':'):  # if this is the 'convert' button, use a QFileDialog to let user pick file to convert.
            
            if self._create == 'symbol':
                self.path = kicad_third_party_symbols_path
            elif self._create == 'footprint':
                self.path = kicad_third_party_footprints_path
                
            selected_files, _ = QFileDialog.getOpenFileNames(self, 'Select File(s) to convert to .sym files:', self.path, filter = "All Files (*)")
            print('SELECTED_FILES:', selected_files)
            print('_:', _)
            if len(selected_files) == 0: 
                print('NO FILE SELECTED')
                self.deleteLater()
            elif len(selected_files) == 1:
                print('SELECTED_FILE:', selected_files[0])
                self.convert_file(selected_files[0])
            elif len(selected_files) > 1:
                print('SELECTED_FILES:', selected_files)
                for file_path in selected_files: 
                    self.convert_file(file_path)
            self.deleteLater() # We are done, lets close out.
        else: 
            print(f"CREATE_SYMBOL_DIALOG BUTTON {button.text()} NOT MATCHING UP?")
            
    def convert_file(self, file_path):
        if self._create.lower() == 'symbol':
            save_file = MyKicadSymbolConverter.convert(file_path)
        if self._create.lower()== 'footprint':
            save_file = MyKicadFootprintConverter.convert(file_path)

        print('CONVERTED FILE HERE: ', save_file)
       
        
            
                
# converter = MyKicadSymbolConverter(library_path)
# if converter.symbol_to_xml():  # Convert this library_id to xml
#     converter.format_graphics() # acts on self.sym and formats that xml, format before saving
#     file_path = converter.save() 

