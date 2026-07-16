from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout,QVBoxLayout, QLabel, QLineEdit,QPushButton, QWidget, QFileDialog, QApplication
from PySide6.QtCore import Signal, Slot, Qt
from DigikeyAPI import DigikeyAPI
from DigikeyParser import DigikeyParser
import sys 
import os 


class CreatePartDialog(QDialog):
    # finished = Signal(int) # This signal is emitted when the dialog's result code has been set ( But don't reimplement it)
    emit_mpn = Signal(str) # This signal emits the chosen mpn, and is emitted when the dialog is .finished()
    created_part = Signal(dict) # (part) 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mpn= None
        self.part = None
        self.setWindowModality(Qt.WindowModality.NonModal) # Choose QT.NonModal(nonBlocking) or Qt.WindowModal(kindaBlocking) or Qt.ApplicationModal(all blocking) Default nonModal
        self.add_contents()

    def add_contents(self):
        
        container_label = QWidget()
        layout_label = QHBoxLayout()
        container_label.setLayout(layout_label)
        layout_label.addWidget(QLabel("MPN:"))
        self.mpn_edit = QLineEdit()
        self.mpn_edit.setPlaceholderText("Enter MPN") # Line Edit placeholder text is grayed-out text, shown while line edit is empty
        layout_label.addWidget(self.mpn_edit)
        
        container_dk_result = QWidget()
        layout_dk_result = QHBoxLayout()
        container_dk_result.setLayout(layout_dk_result)
        button_dk_result = QPushButton("Select Prescraped dk_result")
        button_dk_result.clicked.connect(self.on_button_dk_result_clicked)
        layout_dk_result.addWidget(button_dk_result)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout=  QVBoxLayout()
        layout.addWidget(container_label)
        layout.addWidget(button_dk_result)
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        title= 'Create Symbol - Download Symbol'
        self.setWindowTitle(title)
        
    def accept(self):
        print()
        print('QDIALOG.ACCEPT: Base Hides the modal dialog and sets the result code to Accepted.')
# IF user generated a part from a preexisting dk_result, process that
        print() 
        print('SELF.PART:', type(self.part) , self.part)
        
# If we didnt choose a dk_result, scrape the mpn we entered
        if not self.part : 
            print("SELF.MPN_EDIT.text():", self.mpn_edit.text())
            self.mpn = self.mpn_edit.text()
            print
            if not self.mpn: # If user entered nothing, we should reject.
                self.reject()
                return 
            digikey_api = DigikeyAPI() # Comment out for temp offline use 
            digikey_api.getAccessToken()
            if digikey_api.access_token:
                dk_info = digikey_api.queryDigikey(self.mpn)

        # import pickle # ALT OFFLINE DK_INFO 
        # with open(os.path.join('dk_part_info', f"{self.mpn}_dk.pickle"), 'rb') as fo: 
        #     dk_info = pickle.load(fo)
        
        digikey_parser = DigikeyParser(dk_info)
        part = digikey_parser.parse()
        print('PART:', part)
        self.created_part.emit(part)            # digikey_api.accessTokenObtained.connect(lambda : digikey_api.queryDigikey(self.mpn)) # Query Digikey for MPN. Note how lambda function lets me plug CPD's instance variable 'self.mpn' into digikeyapi's .queryDigikey method.

        super().accept() 
        # self.created_part.emit(self.part) 
        self.deleteLater() # 
            
            
        
    def reject(self):
        print()
        print('QDIALOG.REJECT: Hides the modal dialog and sets the result code to Rejected.')
        super().reject()
        self.deleteLater()
        return 

    @Slot(bool)
    def on_button_dk_result_clicked(self, checked):
        print('CLICKED DK_RESULT_BUTTON')
        dk_result_pickle, _ = QFileDialog.getOpenFileName(self, 'Select dk_result', 'dk_results')
        print("DK_RESULT_PICKLE", dk_result_pickle)

        # digikey_api = MyDigikeyAPI()
        # dk_result = digikey_api.fetchPart(self.mpn)
        if dk_result_pickle:
            dk_parser = DigikeyParser.from_pickle(dk_result_pickle)
            self.part = dk_parser.parse() # a dict of attributes representing a part
            print("SELF.PART:", self.part) 
            self.accept() # Accept the dialog if we got a part.
        else: 
            self.reject()
    # @Slot(int) # takes int r: result_code
    # def on_finished(self, result_code ): # I can just do all this in accept()...
        # print()
        # print("SELF.MPN_EDIT.text():", self.mpn_edit.text())
        # if not result_code: 
        #     return None
        # self.mpn = self.mpn_edit.text()
        # print(f"QDIALOG.ON_FINISHED got result code: {result_code}")
        
    @property
    def mpn(self):
        return self._mpn
    @mpn.setter
    def mpn(self,mpn):
        self._mpn = mpn

# app = QApplication(sys.argv)
# dialog = MyMpnDialog()
# dialog.open() # Shows the dialog as a window modal dialog, returning immediately. Connect to the 'finished' signal to know when the dialog has been QDialog.Accepted or QDialog.rejected
# sys.exit(app.exec())

