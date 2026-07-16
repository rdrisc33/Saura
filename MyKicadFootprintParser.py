from utils import *


class KicadFootprintParser():
    
    def parse_pad(self, pad: etree.Element):
    #     (pad
    #   "NUMBER"                                                  
    #   TYPE                                                      
    #   SHAPE                                                     
    #   POSITION_IDENTIFIER                                       
    #   [(locked)]                                                
    #   (size X Y)                                                
    #   [(drill DRILL_DEFINITION)]                                
    #   (layers "CANONICAL_LAYER_LIST")                           
    #   [(property PROPERTY)]                                     
    #   [(remove_unused_layer)]                                   
    #   [(keep_end_layers)]                                       
    #   [(roundrect_rratio RATIO)]                                
    #   [(chamfer_ratio RATIO)]                                   
    #   [(chamfer CORNER_LIST)]                                   
    #   (net NUMBER "NAME")                                       
    #   (uuid UUID)                                               
    #   [(pinfunction "PIN_FUNCTION")]                            
    #   [(pintype "PIN_TYPE")]                                    
    #   [(die_length LENGTH)]                                     
    #   [(solder_mask_margin MARGIN)]                             
    #   [(solder_paste_margin MARGIN)]                            
    #   [(solder_paste_margin_ratio RATIO)]                       
    #   [(clearance CLEARANCE)]                                   
    #   [(zone_connect ZONE)]                                     
    #   [(thermal_width WIDTH)]                                   
    #   [(thermal_gap DISTANCE)]                                  
    #   [CUSTOM_PAD_OPTIONS]                                      
    #   [CUSTOM_PAD_PRIMITIVES]                                   
    # )
    
#  (pad A smd rect (at 0.75 0.0) (size 0.8 0.8) (layers F.Cu F.Mask F.Paste) (solder_mask_margin 0.102))

        attrs = {
            "number"             : pad.get('name')                  ,# Ex 'A'
            "type"               : pad.get('type')                  , # Ex 'type' 
            "shape"              : pad.get('shape')                 , # Ex 'shape'
            "x"                  : pad.get('x')                     ,
            "y"                  : pad.get('y')                     ,
            "width"              : pad.get('width')                 ,
            "height"             : pad.get('height')                ,
            "layers"             : pad.get('layers').split().strip(),
            "solder_mask_margin" : pad.get('solder_mask_margin')    ,
        }
        return MyPadItem(attrs)
        

    class MyPadItem(QGraphicsItem):
        def __init__(self, ,parent=None):
            
            
            super().__init__(parent)
        def boundingRect(self):
            return self.childrenBoundingRect() or QRectF(0,0,0,0)
        def paint(self, painter, option=None, widget=None):
            self.painter.drawRect(QRectF(-10,-10, 20,20)) 
            
            
        
        
    
    def parse_arc(self, arc: etree._Element): # convert arc from xml representation of .kicad_sym, into constructor args of QPainter.drawArc(rect, startAngle, spanAngle)
        # start X Y 
        # mid X Y 
        # end X Y 
        # angle theta
        # layer LAYER_DEFINITION
        # width WIDTH 
        # STROKE_DEFINITION

        
        c= arc.find('start')
        c_x = float(c.get('X'))
        c_y = float(c.get('Y'))
        
        end = arc.find('end')
        end_x = float(end.get('X'))
        end_y = float(end.get('Y'))
        
        angle = arc.find('angle')
        angle = float(angle.get('angle'))
        
        radius = math.sqrt( (c_x-end_x)^2 + (c_y-end_y)^2 )
        width = height = 2*radius
        left = c_x - radius
        top = c_y + radius
        
        startAngle = math.atan2(c_y - end_y , c_x - end_x) # Calulate the startAngle as used in QPainter.drawArc(rect, startAngle, endAngle)
        spanAngle = math.degrees(startAngle) + angle
        spanAngle = spanAngle % 360
        spanAngle = int(spanAngle * 16 ) # 16 bc qt uses ints for angles bc it optimizes rendering: The startAngle and spanAngle must be specified in 1/16th of a degree, i.e. a full circle equals 5760 (16 * 360)
        
        print('LEFT ,TOP, WIDTH, HEIGHT', left, top, width, height) 
        print( "START_ANGLE", spanAngle)
        print("SPAN_ANGLE", spanAngle)
        
        layer = self.parse_layer(arc)
        width = self.parse_width(arc)
        
        return ( QRectF(left, top, width, height) , startAngle , spanAngle, layer, width) 


    def parse_layer(self, element: etree._Element):
        
        layer = element.find('layer') # 'layer' not 'layers' here
        layer = layer.get('layer')
        print("LAYER:", layer)
        return layer

    def parse_width(self, element):
        
        width = element.find('width')
        width = width.get('width')
        print("WIDTH:", width)
        

    with open('footprints/LEDM1608X80.kicad_mod') as fo: 
        footprint=MySexprParser.parse_footprint(fo)
        footprint=MyKicadFootprintParser(footprint)
        


   