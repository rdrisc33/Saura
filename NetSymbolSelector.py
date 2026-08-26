from utils import *
from View import View 
from Symbol import Symbol

class NetSymbolSelector(QWidget):
        
    def __init__(self):
        super().__init__()
        
        self.setLayout(QHBoxLayout())
        self.file_path = os.path.join( os.getcwd() , Utils.SymbolDirectoryName, Utils.NetSymbolDirectoryName) 
        self.files = os.listdir( self.file_path)
        self.files = [file for file in self.files if os.path.splitext(file)[1] == '.sym']
        self.files = [os.path.splitext(file)[0] for file in self.files]
        print('SELF.FILES:', self.files)# net_symbol_selector = QWidget()
        if not self.files: 
            print(f'Could not find NetSymbols at: {self.file_path}')
            return 
        self.list_widget = ListWidget(self.files)

        self.item_viewer = ItemViewer()
        self.item_viewer.viewItem(self.list_widget.currentItem().text())
        self.list_widget.currentTextChanged.connect(self.item_viewer.viewItem)


        self.layout().addWidget(self.list_widget)
        self.layout().addWidget(self.item_viewer)

class ListWidget(QListWidget):
    def __init__(self, files, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addItems(files)
        self.addItems(['a', 'b','c','d','e', 'f','g','h']) 
        self.setCurrentRow(0)
        scroll_bar = QScrollBar(self)
        scroll_bar.setStyleSheet("background : lightgreen;")
        self.setVerticalScrollBar(scroll_bar)
        print(self.currentItem())
    
    def mouseMoveEvent(self, event):
        if QLineF(event.position() , self.start).length() > QApplication.startDragDistance(): 
            print('BEGAN DRAG')
            drag = QDrag(self)
            mimeData = QMimeData()
            self.file = os.path.splitroot(self.currentItem().text())[0]
            
            record = {'file': self.file , 'reference': os.path.splitroot(self.file)[0] }
            mimeData.setText(json.dumps(record))
            drag.setMimeData(mimeData)
            drag.exec()
            
            
    def mousePressEvent(self, event):
        self.start = event.position()
        super().mousePressEvent(event)# Enable base implementation to handle things like selecting & more.

class ItemViewer(View):
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.setScene(QGraphicsScene())
        self.scene().addItem(QGraphicsRectItem(-10,-10,20,20))

    @Slot(str)
    def viewItem(self, item):
        if self.scene():
            self.scene().clear() # Remove & delete all items on scene 
            file = item + '.sym'
            file = os.path.join(os.getcwd(), Utils.SymbolDirectoryName, Utils.NetSymbolDirectoryName, file)
            print()
            print('FILE: ', file)
            net_symbol = Symbol(file)
            self.scene().addItem(net_symbol)
        else:
            print('SCENE IS NONE')
        
# net_symbol_selector = NetSymbolSelector()
# net_symbol_selector.show()

# mw = MainWindow()
# mw.show()
# sys.exit(app.exec())
