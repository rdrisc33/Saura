# bare bones draw line app 

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from utils import *
from enum import Enum
from NonConnectivityItem import *
from LayersItem import * 

# How to draw arcs? Can I borrow the Inkscape arc engine? 
# Do lines , rects, ellipses, b4 arcs.

# How to adjust shapes? Overlay 'adjust nodes' on shape, if mouse over adjust node, adjust that particular dimension(s)

class DrawScene(QGraphicsScene):
    
    def __init__(self, *args, **kwargs ):
        super().__init__(*args, **kwargs)
        self._mode = Utils.BoardSceneMode.NormalMode 
        self._line = None 
        self._rect = None 
        self._ellipse = None 
        
    def mousePressEvent(self, event): 
        print('DRAWSCENE.MPE')
        if self._mode == Utils.BoardSceneMode.NormalMode: 
            return super().mousePressEvent(event)

        self.startPos = event.scenePos()
        
        if self._mode == Utils.BoardSceneMode.DrawLineMode: # Note DrawLineMode lets us draw sequential lines, while draw(Rect,Ellipse)Utils.BoardSceneMode only lets us draw one shape at a time. This is bc drawing one line at a time is a pain
            # self._line = LayerLineItem( self.activeLayer() , QLineF(self.startPos, self.startPos))
            # self._line.setFlags(QGraphicsItem.ItemIsSelectable)
            self._line = DrawnLineItem( self.activeLayer() , QLineF(self.startPos, self.startPos))
            # self._line = QGraphicsLineItem(QLineF(self.startPos, self.startPos))
            self.addItem(self._line)

        elif self._mode == Utils.BoardSceneMode.DrawRectMode: 
            if not self._rect: 
                # self._rect = QGraphicsRectItem(QRectF(self.startPos, self.startPos))
                # self._rect = LayerRectItem( self.activeLayer() , QRectF(self.startPos, self.startPos))
                # self._rect = DrawnRectItem( self.activeLayer() , QRectF(self.startPos, self.startPos))
                self._rect = LayersRectItem( [self.activeLayer()] , 1, QRectF(self.startPos , self.startPos))
                self.addItem(self._rect)
            elif self._rect: 
                self._rect = None 

        elif self._mode == Utils.BoardSceneMode.DrawEllipseMode: 
            if not self._ellipse: 
                # self._ellipse = QGraphicsEllipseItem(QRectF(self.startPos , self.startPos))
                # self._ellipse = LayerEllipseItem(self.activeLayer() , QRectF(self.startPos , self.startPos))
                self._ellipse = DrawnEllipseItem(self.activeLayer() , QRectF(self.startPos , self.startPos))
                self.addItem(self._ellipse) 
            elif self._ellipse: 
                self._ellipse = None                 

    def mouseMoveEvent(self, event): 
        print('DRAWSCENE.MME')
        if self._mode == Utils.BoardSceneMode.NormalMode: 
            super().mouseMoveEvent(event)
            
        elif self._mode == Utils.BoardSceneMode.DrawLineMode:
            if self._line: 
                self._line.setLine(QLineF(self.startPos , event.scenePos()))

        elif self._mode == Utils.BoardSceneMode.DrawRectMode: 
            if self._rect: 
                self._rect.setRect(QRectF(self.startPos, event.scenePos()).normalized())

        elif self._mode == Utils.BoardSceneMode.DrawEllipseMode:
            if self._ellipse: 
                self._ellipse.setRect(QRectF(self.startPos, event.scenePos()).normalized())

    def mouseDoubleClickEvent(self, event): 
        print('DRAWSCENE.MDCE')
        # self._mode = Utils.BoardSceneMode.NormalModeNO BAD bc this drops out of addTraceMode as well as draw modes 
        if (self.mode() == Utils.BoardSceneMode.DrawRectMode) or (self.mode() == Utils.BoardSceneMode.DrawLineMode) or (self.mode() == Utils.BoardSceneMode.DrawEllipseMode):
            self.setMode(Utils.BoardSceneMode.NormalMode)
            self._line = None 
            self._ellipse = None 
            self._rect = None 
            self._arc = None 
            self._curve = None 
            
        super().mouseDoubleClickEvent(event)

    def onDrawLineActionTriggered(self):
        print('drawLine')
        self._mode = Utils.BoardSceneMode.DrawLineMode

    def onDrawRectActionTriggered(self): 
        print('drawRect')
        self._mode = Utils.BoardSceneMode.DrawRectMode

    def onDrawEllipseActionTriggered(self):
        print('drawEllipse')
        self._mode = Utils.BoardSceneMode.DrawEllipseMode
    
# mw = QMainWindow() 

# scene = DrawScene()
# drawLineAction = QAction('Line', mw, triggered = scene.onDrawLineActionTriggered )
# drawRectAction = QAction('Rectangle', mw, triggered = scene.onDrawRectActionTriggered)
# drawEllipseAction = QAction('Ellipse', mw, triggered = scene.onDrawEllipseActionTriggered)

# drawMenu = mw.menuBar().addMenu('Draw')
# drawMenu.addAction(drawLineAction)
# drawMenu.addAction(drawRectAction)
# drawMenu.addAction(drawEllipseAction)

# view = QGraphicsView()
# view.setMouseTracking(True)
# view.setScene(scene)
# mw.setCentralWidget(view)
# mw.show()

# sys.exit(app.exec())