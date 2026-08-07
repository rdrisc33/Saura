import sexpdata 

import os 
import lxml.etree as etree
import math
from utils import * 
from PySide6.QtCore import QRectF
dnp_fp_tokens = [ 
    
    ]
class KicadFootprintConverter():
    def __init__(self, kicadModFile ): # Kicad footprint files have extension '.kicad_mod'        
        # print()
        # print('FILE:', kicadModFile)
        with open(kicadModFile) as fo: 
            sexpression = sexpdata.load(fo)
            
        if sexpression[0].strip().lower() != 'footprint': # Then this is not a footprint, so return 
            print('SEXPRESSIION[0] != "footprint"')
            return None
        
        self.sexpression = sexpression
        self.kicadModFile = kicadModFile
        
    @classmethod
    def convert(cls, kicadModFile):
        c = cls(kicadModFile)
        
        footprint = etree.Element('footprint') # Initiate rootmost element
        footprint.set('name', c.sexpression[1])
        
        c.footprint = c.recurse(c.sexpression[2:], footprint) # recurse on the sexpr
        c.post_process()
        save_file = c.save()
        return save_file
        
    def recurse(self, sexpr, parent, child = None ):
        
        token = str(sexpr.pop(0)).lower().strip()
        #  type(s) could be: str, sexpdata.Symbol, list, int, float ...
        symbols = [] # holds sexpdata.Symbols
        strings = [] # holds strings 
        values = [] # holds values, BOTH sexpdata AND strings 
        nums = [] 
        lists = []
        for i in sexpr: 
            if isinstance(i , sexpdata.Symbol): 
                symbols.append(str(i))
                values.append(str(i))
            elif isinstance(i, str):
                strings.append(i)
                values.append(i)
            
            elif isinstance(i, (float, int)):
                nums.append(i)
            elif isinstance(i , (list, tuple)): 
                lists.append(i)             

        ### DEBUGGING ### 
        # print('TOKEN:', token) 
        # print("SYMBOLS:", symbols)
        # print("STRINGS:", strings)
        # print('VALUES:', values)
        # print('NUMS:', nums) 
        # print('LISTS:', lists)
            
#HANDLE BY TOKEN
    #Single value attribute
        if token in ['angle', 'layer', 'fill', 'width', 'descr', 'solder_mask_margin', ]:
            if token == 'width': # pre Kicadv7, for line width. post Kiv7, 'effects' token holds width
                parent.set('stroke_width', str(sexpr[0])) #In kicad, sometimes 'width' means stroke width, and sometimes it means shape width
            else:
                parent.set(token, str(sexpr[0])) # [0] bc we .pop()ed token 
        elif token == 'attr': # attr is a kicad-specific sexpression token. AFAIK, it only holds 'smd' or 'tht' indicating fp is smd or tht
            self.attr = ', '.join(symbols) # I need self.attr later, so make it a instance variable (self.)
            parent.set('attr' ,self.attr) 
        elif token == 'fp_text': 
            if sexpr[1].lower().strip() == 'reference': # reference is the only thing that needs to be in a footprint file. Value is not needed here
                parent.set(['reference'] , sexpr[1])
    #multiple value attributes
        elif token == 'size': 
            parent.set('width', str(sexpr[0]))
            parent.set('height', str(sexpr[1]))
        elif token =='layers':
            parent.set('layers' , ', '.join(symbols)) 
        elif token == 'start': 
            if parent.tag == 'line': # set x1y1
                parent.set('x1' , str(sexpr[0]) ) # 0 bc we .pop()ed token
                parent.set('y1' , str(sexpr[1]) )
            else:
                parent.set('start_x' , str(sexpr[0]) ) # 0 bc we .pop()ed token
                parent.set('start_y' , str(sexpr[1]) )
        elif token == 'end':
            if parent.tag == 'line': # set x2y2
                parent.set('x2' , str(sexpr[0]) ) # 0 bc we .pop()ed token
                parent.set('y2' , str(sexpr[1]) )
            else: # happens for 'circle' (and more?)
                parent.set('end_x' ,str(sexpr[0]))
                parent.set('end_y' ,str(sexpr[1]))
        elif token == 'at': 
            parent.set('x', str(sexpr[0]))
            parent.set('y', str(sexpr[1]))
        elif token =='center': 
            parent.set('c_x', str(sexpr[0]))
            parent.set('c_y', str(sexpr[1]))
# TODO: ZONE

            
            
# TODO: ZONE
#   (zone (net 0) (net_name "") (layer "F.Cu") (hatch full 0.508)
#     (connect_pads (clearance 0))
#     (min_thickness 0.254)
#     (keepout (tracks not_allowed) (vias not_allowed) (pads allowed ) (copperpour not_allowed) (footprints allowed))
#     (fill (thermal_gap 0.508) (thermal_bridge_width 0.508))
#     (polygon
#       (pts
#         (xy -0.4445 -0.5715)
#         (xy 0.4445 -0.5715)
#         (xy 0.4445 0.5715)
#         (xy -0.4445 0.5715)
#       )
#     )
#   )
    #CHILDREN
        elif token == 'pad': # this is a pad item. It will have children items
            child = etree.SubElement(parent, 'pad')
            kv = zip( [ 'name' , 'type' , 'shape'], values) # Note that 'name' may sometimes be a string, or a sexpdata.Symbol #   (pad "1" smd rect (at -1.4 -1.5) (size 0.4318 0.2794) (layers "F.Cu" "F.Paste" "F.Mask"))
            child.attrib.update(kv) 
            for lst in lists: 
                self.recurse(lst, child)
        elif token.startswith('fp_'): # Ex 'fp_arc' 'fp_line' 
            if token == 'fp_poly': # rename it 
                token = 'fp_polygon' 
            child=  etree.SubElement(parent, token[3:]) # lop off the 'fp_' part
            # for lst in lists: 
            #     self.recurse(lst, child)
        elif token == 'pts': 
            points_str = ""
            for point in lists:
                points_str+= str(point[1]) + "," + str(point[2]) + " " # 1 and 2 bc we 
            points_str = points_str.strip() # Remove the trailing whitespace 
            parent.set('points',points_str )
            
        if child is None: 
            for lst in lists: 
                self.recurse(lst, parent)
        elif child is not None: 
            for lst in lists: 
                self.recurse(lst, child)
            
        return parent 
    
    def post_process(self, verbose = False ): # remove elements of 0 length/ remove duplicate elements
        # TODO: REMOVE DUPLICATE ELEMENTS
        self.copy = etree.Element('footprint', self.footprint.attrib)
        # print('MyKiFpCvtr.FOOTPRINT:', self.footprint)
        # etree.tostring(self.footprint, encoding = str, pretty_print = True)
        for descendant in self.footprint.iterdescendants(): 
            if descendant.tag == 'pad':  # both rect and circular pads have their centers stored in x and y ( Bc this form easily converts to gerber)
                c_x =   float(descendant.attrib.pop('x')) # dont pop(?) , could use when drawing gerber
                c_y =   float(descendant.attrib.pop('y'))

                width = float(descendant.attrib.get('width'))
                height = float(descendant.attrib.get('height'))
                left = c_x - width/2 
                top = c_y - height/2
                descendant.set('left', str(left))
                descendant.set('top', str(top))
                descendant.set('c_x', str(c_x))
                descendant.set('c_y', str(c_y))
            elif descendant.tag == 'circle': # kill circles of 0 radius -- get their parent elem(self.footprint) then remove.
                c_x = float(descendant.get('c_x')) # Center not used by Qt but is used by gerbers, so we'll let it stay
                c_y = float(descendant.get('c_y'))
                end_x = float(descendant.get('end_x')) # Gerber wants these to draw arcs 
                end_y = float(descendant.get('end_y'))

                radius = math.sqrt( (end_x - c_x)**2 + (end_y - c_y)**2 ) # Pythag theorem. Helps to draw it 
                if radius == 0: 
                    if verbose: 
                        print()
                        print('CIRCLE HAS 0 RADIUS. REMOVING FROM:', descendant.getparent())
                    descendant.getparent().remove(descendant) # remove descendant. This will removal will apply to self.footprint
                    
            elif descendant.tag == 'line': #kill lines of 0 length
                x1 = float(descendant.get('x1'))
                y1 = float(descendant.get('y1')) 
                x2 = float(descendant.get('x2')) 
                y2 = float(descendant.get('y2'))
                if (x1,y1) == (x2, y2) : # If this line goes nowhere, remove it from self.footprint
                    descendant.getparent().remove(descendant) # remove descendant
            etree.SubElement(self.copy, descendant.tag, descendant.attrib)
        # print()
        # print('MyKiFpCvtr.FOOTPRINT:', self.footprint)
        

    def save(self, verbose = False): # Perhaps 'setup_folders'
        _, tail = os.path.split(self.kicadModFile)
        root, _ = os.path.splitext(tail)
        
        attr = [a.lower().strip() for a in self.attr.split(',')]
        if verbose: 
            print('FP FILE ATTR:', attr)  
# (footprint "G-21_MUR" (version 20211014) (generator pcbnew)
#   (layer "F.Cu")
#   (tags "GRM21BR61E106KA73L ")
#   (attr smd)
        save_folder = os.path.join( 'footprints', *attr, root) # Ex 'footprints/smd/GRM21BR6106KA73L'
        if verbose: 
            print('SAVE_FOLDER:', save_folder)
        save_file = os.path.join( save_folder, root + '.fp' )# Ex footprints/smd/GRM21BR6106KA73L/G-21_MUR-L.fp'
        if not os.path.exists(save_folder): # make folder if dne
            os.makedirs(save_folder)
        if not os.path.exists(save_file): # make file if dne
            with open(save_file, 'x') as fo: # open() 'x' mode is for creating blank file( open file, write nothing, then close)
                pass
        with open(save_file, 'w') as fo: 
            fo.write(etree.tostring(self.footprint, encoding = str, pretty_print = True)) #should encoding be 'utf-8' (is that same as str)
        if verbose: 
            print('CONVERTED FOOTPRINT FILE HERE:', save_file, )
            print("FILE CONTENTS:")
            print(etree.tostring(self.footprint, encoding = str, pretty_print =True))
        return save_file


### TESTING ###

# save_file = MyKicadFootprintConverter.convert(os.path.join(kicad_third_party_footprints_path , 'LED_SML-D12U1WT86.kicad_mod'))

save_file = KicadFootprintConverter.convert(os.path.join(kicad_third_party_footprints_path , 'GRM21BR61E106KA73L', 'G-21_MUR.kicad_mod'))














