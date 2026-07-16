import sys

from PySide6.QtCore import QDate, QFile, Qt, QTextStream
from PySide6.QtGui import (QAction, QFont, QIcon, QKeySequence,
                           QTextCharFormat, QTextCursor, QTextTableFormat)
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (QApplication, QDialog, QDockWidget,
                               QFileDialog, QListWidget, QMainWindow,
                               QMessageBox, QTextEdit)


from MyView import * 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Qt.DockWidgetArea.AllDockWidgetAreas
        # A dock widget may be set as centralWidget
        # DockWidgets may be stacked; a QTabBar will appear to select between stacked widgets
        # QMainWindow(save,restor)State(): 
        #However, QMainWindow and QDockWidget can only .setCentralWidget() and .setWidget() respectively; neither may .setLayout()... Oh but QWidget may .setLayout(), so you can make a centralwidget with a layout. 
        self.my_view = MyView()
        self.setCentralWidget(self.my_view)
        self.create_actions()
        self.create_menus()
        self.create_tool_bars()
        self.create_status_bar()
        self.create_docks()
        self.setWindowTitle("MainWindow")


        
    def create_actions(self):
        icon = QIcon.fromTheme('document-print')
        self.print_action = QAction(icon, "Print", triggered=self.print_)
        
    def print_(self): # note print_ as print is ... 
        printer = QPrinter()
        dlg = QPrintDialog(printer, self) # Use QPrintDialog to configure QPrinter object
        if dlg.exec() != QDialog.Accepted: #If the dialog is accepted by the user, the QPrinter object is correctly configured for printing.
            return
        # painter=QPainter(printer) # QPainter performs painting on paint devices( QPrinters, QWidgets, QPixmaps, & more)
        # self.my_view.render(painter)
        # painter.end()   # End the painter; allow the paint device to be destroyed. (alt use a contextmanager) 
        with QPainter(printer) as painter:
            self.my_view.render(painter)
        self.statusBar().showMessage("READY", 10000) 
        
    def create_menus(self):
        self.file_menu = self.menuBar().addMenu('File')
        # self.file_menu.addAction(save_action)
        self.file_menu.addAction(self.print_action)
        self.file_menu.addSeparator()
        # self.file_menu.addAction(quit_action)
        
    def create_tool_bars(self):
        self.file_tool_bar = self.addToolBar('File')
        self.file_tool_bar.addAction(self.print_action)

    def create_status_bar(self):
        self.statusBar().showMessage('Ready') # QMainWindow comes with self.statusBar(), menuBar(), toolBar() already. 
    
    def create_docks(self):
        dock = QDockWidget('Dock1')
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.generic_list = QListWidget(dock) # a listwidget for the dock widget 
        self.generic_list.addItems(("4,5,6,7"))
        
        dock.setWidget(self.generic_list) # dock Widgets can be inset with either a layout(could hold many widgets) or a widget
        # self.generic_list.currentTextChanged.connect(self.insert_into_list)
        self.addDockWidget(Qt.RightDockWidgetArea, dock) # Slap 'dock' into the main window's right dock area


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())