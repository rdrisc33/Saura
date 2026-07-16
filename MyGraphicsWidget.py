from utils import * 

# 3This is my failed attempt to make a QGraphicsItem use layouts
# All I want is something that user can move around on the scene( ez: QGraphicsItem ) AS WELL AS go in layouts( ez QGraphicsLayoutItem ). But getting both DNE? 
# class LayoutGraphicsItem(QGraphicsItem, QGraphicsLayoutItem, QObject) Could this subclass work? Um these are the same classes which QGraphicsWidget inherits... yet QGraphicsWidget is not selectable or moveable. 

class MyGraphicsWidget(QGraphicsWidget):
    def __init__(self, ):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    scene =QGraphicsScene()
    view = QGraphicsView(scene)
    
    g_layout = QGraphicsLinearLayout()
    g_widget = QGraphicsWidget()
    scene.addItem(g_widget)
    # g_widget.setStyleSheet("border:1px solid black") NO BAD graphicswidget has no stylesheet. graphicswidget is not a QGraphicsItem(But it inherits QGraphicsItem..)
    # btn_1_proxy.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable) NO BAD Proxy widgets are not ? selectable in the way QGraphcisItems are

    btn_1 = QPushButton("PushMe")
    btn_1.setStyleSheet("border:1px solid black") 
    btn_1_proxy = QGraphicsProxyWidget() 
    btn_1_proxy.setWidget(btn_1)
    
    g_layout.addItem(btn_1_proxy)
    
    slider_1_proxy = scene.addWidget(QSlider())
    g_layout.addItem(slider_1_proxy)

    
    g_widget.setLayout(g_layout)

    window = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(view)
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec())