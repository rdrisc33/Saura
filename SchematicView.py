from MyView import MyView 
from utils import * 

class SchematicView(MyView):
    # gridSpacing = Utils.schematicGridSpacing
    # tickSpacing = Utils.schematicTickSpacing 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, * kwargs)

    def drawBackground(self, painter, rect): 

        # print()
        # print('DRAWBACKGROUND')

        painter.setBrush(Qt.black)
        painter.setPen(QPen(Qt.black, 1)) # Note QPen width 1 makes dots much more visible than width 0 
        # painter.setPen(Qt.NoPen) Makes points disappear

        # Note WHen zooming wayin to wayout , the PEN WIDTH of your painted points becomes important so the user can see it. 
        # I'm content with this for prototype, but production app should dynamically set pen widths based on zoom (?)
        def calculateTickSpacing():
            xScale = painter.transform().m11() # xScale is represented at the transformationMatrix m11 element. 
            # print('XSCALE:', xScale)
            if (xScale <.5): # ZOOMEDWAYOUT
                painter.setPen(QPen(Qt.black, 10)) # Set a wide pen so user can still see the dots 
                tickSpacing = Utils.schematicTickSpacing*10
            elif .5 <= xScale <= 20: 
                painter.setPen(QPen(Qt.black, 1))
                tickSpacing = Utils.schematicTickSpacing
            if xScale > 20: #ZOOMEDWAYIN
                painter.setPen(QPen(Qt.black, .1)) # set a thin pen so user can still see the dots 
                tickSpacing = Utils.schematicTickSpacing/10

            return tickSpacing

        tickSpacing = calculateTickSpacing()
        # print('TICKSPACING:', tickSpacing)
        
        numTicksX = int(rect.width()/tickSpacing) + 2
        numTicksY = int(rect.height()/tickSpacing) + 2 

        xStart = int(rect.left() / tickSpacing) * tickSpacing # important to start drawing points snapped to grid. If start drawing points at rect.left()&rect.top(), induces a 'flowing' effect while zooming
        yStart = int(rect.top() / tickSpacing) * tickSpacing
        
        for i in range(numTicksX): 
            for j in range(numTicksY):
                x = i*tickSpacing + xStart 
                y =  j* tickSpacing + yStart
                painter.drawPoint(QPointF(x , y)) # Note pass a QPointF() to be able to use floats with .drawPoint() 
                # painter.drawEllipse(QPointF(x,y), 1, 1)

        
