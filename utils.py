from PySide6.QtWidgets import * 
from PySide6.QtCore import *
from PySide6.QtGui import * 

# () around imports allows imports to span multiple lines. w/o (), a backslash would need to be added at each EOL 
# from PySide6.QtSvgWidgets import QSvgWidget, QGraphicsSvgItem
# from PySide6.QtSvg import  (QSvgRenderer, QSvgGenerator,)
# Renderer: Draw SVG files onto paint devices. Rendering is perfomed with QPainter; render on any QPaintDevice(screen, a file, a widget, etc). Load as xml, or with filename
# Genrerator: Provides a paint device used to create SVG drawings 

# from PySide6.QtXml import QDomDocument                  # like xml.etree.ElementTree but for Qt
# from PySide6.QtSvgWidgets import (
# QGraphicsSvgItem,                                       # NOTE this is for using svgs as icons/button icons. See QSvgRenderer to draw SVGs more complicated-ly.
# QSvgWidget                                              # display svg drawings, as icons, like how QLabel displays text/bitmap images
# ) 


###
# Digikey API & oauth Library depencies
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from urllib.parse import urlparse, parse_qs, urljoin

#'Normal' imports
import sys
import os
import pandas
import rtree as rectangletree # I want to use the name 'rtree' for my rtrees so rename this module
import pickle
import sqlite3
import csv
import requests
import webbrowser
import json
from collections import namedtuple , defaultdict
import io
import csv 
import pickle
import sexpdata # use sexpdata.loads() sexpdata.dumps() to turn sexpressiions into /out of lists. 
import time
from scipy.sparse import coo_array
from lxml import etree
from collections import defaultdict
from sexpdata import loads 
import pandas as pd 
from enum import Enum
from sqlalchemy import Column, Text
from PySide6.QtNetwork import * 
import sexpdata
import math 
import os
import re # 'Regular Expressions' 

# from LayersItem import * 

app = QApplication(sys.argv)

defaultTraceWidth = .2



class Utils: 
    

        
    grid4mm = 1 / 25.4 * 4 
    grid1mm = 1 / 25.4 
    grid1in = 1 
    grid50thou = .05
    fileGridStep = 1.27  # kicad symbols are designed on .05inch grid, .05inches = 1.27mm 
    gridPt1mm = 1 / 25.4 * .1 # board grid step is .1mm 

    schematicGridSpacing = qApp.screens()[0].physicalDotsPerInch() * grid4mm # SchematicScene gridSpacing is 4mm aka 17.86046511627907 pixels
    schematicTickSpacing = schematicGridSpacing

    boardGridSpacing = schematicGridSpacing 
    boardTickSpacing = boardGridSpacing
    
    epsilon = 1e-9 # epsilon is a value used to compare floats against. 



    class BoardSceneMode(Enum):
### Standard Modes 
        NormalMode      = 0 
        AddTraceMode    = 1
        AddViaMode      = 2
        DeleteMode      = 3
### Draw Modes 
        DrawLineMode    = 4
        DrawRectMode    = 5
        DrawEllipseMode = 6 
        DrawArcMode     = 7 
        DrawPolygonMode = 8
        DrawCurveMode   = 9
        
    class Shape(Enum):
        
        Rectangle = 0 
        Ellipse = 1
        Path = 2
        Line = 3 
        Pixmap = 4
        Polygon = 5
        SimpleText = 6 
        Text = 7
        
        Footprint = 8
        ComponentSymbol = 9 
        LabelSymbol = 10
        HierarchyLabelSymbol = 11
        GlobalLabelSymbol = 12

    @staticmethod
    def snapToGrid(point: QPointF , gridSpacing):
        pt = QPointF( round(point.x()/gridSpacing)*gridSpacing , 
                      round(point.y()/gridSpacing)*gridSpacing ) 
        return pt
    
    def pointWithinSegment(point, line, epsilon = 1e-9): #  https://stackoverflow.com/questions/328107/how-can-you-determine-a-point-is-between-two-other-points-on-a-line-segment. Q: Where did his equations for CP, DP, come from? Q: Best value for epsilon? 
        a, b, c = line.p1() , line.p2() , point
        
        crossProduct = (c.y() - a.y()) * (b.x() - a.x()) - (c.x() - a.x()) * (b.y() - a.y())
        
        if abs(crossProduct) > epsilon: 
            return False 

        dotProduct = (c.x() - a.x()) * (b.x() - a.x()) + (c.y() - a.y())*(b.y() - a.y())
        print('DOTPRODUCT:', dotProduct)
        # if dotProduct < 0: # Inclusive of endpoints 
        if dotProduct <= 0: # Exclusive of endpoints (to test if point WITHIN line, I want exclusive)()
            return False 

        squaredLengthBA = (b.x() - a.x())*(b.x() - a.x()) + (b.y() - a.y())*(b.y() - a.y())
        print('SQUAREDLENGTHBA:', squaredLengthBA)
        if dotProduct >= squaredLengthBA: 
            return False 
        
        else: 
            print('POINT IS WITHIN SEGMENT')
            return True 

    @staticmethod
    def distance(pointA , pointB): 
        return math.sqrt( (pointA.x()-pointB.x())**2 + (pointA.y() - pointB.y())**2)
    
    @staticmethod
    def rangesOverlap(a1,a2 , b1,b2) : 
        # First, make sure that ranges are 'well ordered':  n1 < n2 
        if a1 > a2: 
            a1, a2 = a2, a1 # Switch 1&2
        if b1 > b2: 
            b1, b2 = b2, b1
        # Its a mindfuck, but ranges overlap if the start of one range is <= end of the other AND vice versa
        return a1 <= b2 and b1 <= a2

    @staticmethod
    def wiresAreOrthagonal(wire1, wire2): 
        line1 = wire1.line()
        line2 = wire2.line() 

        p1 = line1.p1()
        p2 = line1.p2()
        p3 = line2.p1()
        p4 = line2.p2()
        
        x1, y1 = p1.toTuple() 
        x2, y2 = p2.toTuple()
        x3, y3 = p3.toTuple()
        x4, y4 = p4.toTuple()

        orient1 = Utils.threePointOrientation(p1,p2,p3) 
        orient2 = Utils.threePointOrientation(p1,p2,p4)
        orient3 = Utils.threePointOrientation(p3,p4,p1)
        orient4 = Utils.threePointOrientation(p3,p4,p2)
        
        orientations = [orient1, orient2, orient3, orient4]
        numZeroes = orientations.count(0)
        
        if numZeroes == 2: # Then these wires are perpendicular
            return True
    
    @staticmethod
    def junction(line1, line2): 
        """Returns a tuple which differs depending on junction type of line1 and line2. 
        Zeroeth index of the return tuple is junctionType, a Utils.JunctionType. 
        If junctionType is Utils.JunctionType.Tee, this function will return a 2-tuple (junctionType, zero) where zero is orient1, orient2, orient3, or orient4, whichever one was zero. Google three point orientation
        IF junctionType is Utils.JunctionType.L,   this function will return a 2-tuple (junctionType, orientations) (for wire dragging)
        If junctionType is any other Utils.JunctionType, this function will return a 1-tuple (junctionType)
        Note (5) is an int while (5,) is a tuple. This used in this functions return statements  """
        
        p1 = line1.p1()
        p2 = line1.p2()
        p3 = line2.p1()
        p4 = line2.p2()
        
        x1, y1 = p1.toTuple() 
        x2, y2 = p2.toTuple()
        x3, y3 = p3.toTuple()
        x4, y4 = p4.toTuple()

        orient1 = Utils.threePointOrientation(p1,p2,p3) 
        orient2 = Utils.threePointOrientation(p1,p2,p4)
        orient3 = Utils.threePointOrientation(p3,p4,p1)
        orient4 = Utils.threePointOrientation(p3,p4,p2)
        
        orientations = [orient1, orient2, orient3, orient4]
        numZeroes = orientations.count(0)
        
        if numZeroes == 1: # Then this is a Tee intersection. Will split, if no 'L' @ split point 
            zero = [orient1, orient2, orient3, orient4].index(0) # Find the idx of the single zero. We can tell how we should split based on which orient is 0.
            return ( Utils.JunctionType.Tee , zero )
        
        elif numZeroes == 2: # Then this is a L intersection. No action.
            return ( Utils.JunctionType.L , orientations) 
        
        elif numZeroes == 4: #Then these lines are collinear. Check if they are adjacent collinear, or overlapping collinear, or nonintersecting
            if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4: # Then these are adjacent collinear. 
                return ( Utils.JunctionType.CollinearAdjacent , )
            else: 
                x1, y1 = p1.toTuple() 
                x2, y2 = p2.toTuple()
                x3, y3 = p3.toTuple()
                x4, y4 = p4.toTuple()
        
                # Test if X range overlaps: 
                xOverlap = Utils.rangesOverlap(x1, x2 , x3 , x4)
                yOverlap = Utils.rangesOverlap(y1,y2 , y3, y4) 
                if xOverlap or yOverlap: # If x-rangesoverlap OR y-ranges overlap, these lines overlap
                    return ( Utils.JunctionType.CollinearOverlap ,)
                
        elif orient1 != orient2 and orient3 != orient4: # Then these lines are intersecting. Note no action needed here(no split. intersecting lines in EDA SW are supposed to not connect
            return ( Utils.JunctionType.Intersecting , )
        
        return ( Utils.JunctionType.NonIntersecting , )
    
    @staticmethod
    def threePointOrientation(p1,p2,p3 , verbose=False): # https://www.geeksforgeeks.org/dsa/orientation-3-ordered-points/ "https://www.scribd.com/document/521718353/2017-04-28-Continuous-Space-Pathfinding" "Continuous Space Pathfinding Daniel Wisdom 28 April 2017"
        x1,y1 = p1.toTuple()
        x2,y2 = p2.toTuple()
        x3,y3 = p3.toTuple()
        
        cross_product = (y2-y1)*(x3-x2) - (x2-x1)*(y3-y2)
        cross_product = round(cross_product, 12) # Round the cross product  to 12 decimal places. Floats (usually, always) have 16 decimal places. But floats are bad/wrong: .3 * 3 = .9 but python will tell you .3 * 3 = .8999999999999999. So we round.
        if verbose: 
            print('Cross_product:', cross_product)
        if cross_product > 0: # Then cw. 
            # return 1 NOTE: Qt coordinate system y axis is flipped, so invert UGH so confusing
            return 2
        elif cross_product < 0: # Then ccw
            # return 2
            return 1 
        else: # if cp == 0, p1p2p3 collinear 
            return 0 
        
    SauraPath = os.path.join('C:\\', 'Users', 'robby', 'OneDrive','Saura') # Note 'C:\\' not 'C:' 

    numDigitsToRoundTo = 12
    class JunctionType(Enum):
        """Utils.junctionTypes names may be colloquial, like 'L' and 'Tee' . Both 'L' and 'Tee' refer to orthagonal segments. However L refers to orthagonal segments sharing a endpoint/terminal, while Tee refers to orthagonal segments not sharing an endpoint/terminal, see Saura Junction Tutorial"""
        NonIntersecting     = 0
        L                   = 1 
        Tee                 = 2 
        CollinearOverlap    = 3 
        CollinearAdjacent   = 4 
        Intersecting        = 5 
        


    
    # C:\Users\robby\OneDrive\Saura\symbols\netSymbols
    viaClearance        = 1 # mm 
    viaPlatingThickness = 1 # um typical
    
    class ViaStyle(Enum):
        Through                     = 0 
        BlindBuried                 = 2 
      
    SymbolDirectoryName = 'symbols'
    footprint_directory_name = 'footprints'
    NetSymbolDirectoryName = 'netSymbols'
     

    client_id = "xPJYLpMi0aVZPfuitXzVk2IOln3aFfBo"
    client_secret = "rC5ut52nzaa4LHGR"
    
    HOST = QHostAddress.SpecialAddress.LocalHost # LocalHost equivalent to QHostAddress( '127.0.0.1' ) # The server's hostname or IP address
    PORT = 5000        # The port used by the server

    symbolFont = QFont("Segoe UI", 1)
    footprintFont = QFont("Segoe UI", 1) # Likely must change-- gerber only knows font as a path with stroke width
    footprint_placeholder_font = QFont("Segoe UI", 6) # for humans to read


    class ValuePreference(Enum): # DesignItems have a ._value. Usually it is visible on the sch & brd. ._value defaults to '._designator'. You can specify for ._value to default to something else with this enum
        ReferenceDesignator          = 1         # R for resistors, C for capacitors
        DesignatorAsDecimal = 2         # 4R7 for a 4.7ohm resistor, 2C2u for a 2.2uF capacitor
        Mpn                 = 3         # STM32C06T6 for that microcontroller
        Name                = 4         # 'Red LED' or whatever you chose as a name. Note with no standardization/restrictions on name, theres enough rope to hang yourself
        PrimaryAttributes   = 5         # 4C7uF_16V_2202 for a 4.uF, 16V rated, 2202 package resistor
        EmptyString         = 6         # '' for footprints where is_discrete = False , ex, mechanical holes, artwork, a weird large trace that ppl use as a zone ... 

    designator_value_preferences = {
        'resistors'            : [ValuePreference.DesignatorAsDecimal]                     ,
        'capacitors'           : [ValuePreference.DesignatorAsDecimal]                     ,
        'inductors'            : [ValuePreference.DesignatorAsDecimal]                     , 
        'diodes'               : [ValuePreference.DesignatorAsDecimal]                     , 
        'microcontrollers'     : [ValuePreference.PrimaryAttributes, ValuePreference.Mpn]  ,
        'NetSymbols'           : [ValuePreference.Name]                                    , 
        'Label'                : [ ValuePreference.Name]                                   ,
        
    }

    class NetPriority(Enum):
        NoPriority              = 0
        Pad                     = 1 
        NetSymbol               = 2 
        HierarchyLabel          = 3 
        GlobalLabel             = 4
        
    class SchematicItemKinds(Enum): # Used as keys in MW.veins[vein_id]
        Wire                                    = 0
        Pin                                     = 1
        ComponentSymbol                         = 2
        NetSymbol                               = 3
        HierarchyLabel                          = 4
        GlobalLabel                             = 5
        # LocalLabel                              = 4 
        # Label                                   = 6 
        
        
    class BoardItemKinds(Enum): # Used in MW.nets as keys 
        Trace           = 1
        Pad             = 2
        Zone            = 3
        Via             = 4 
        Footprint       = 5 # Does FP even count...?
        
    
    # class NetPriority:  Deprecated for SchematicItemKinds
    #     NoPriority      = 0  # Unused? 
    #     Wire            = 1  # Unsure if Wire/Via should be equal? Either way, neither have any prefernce for which net they are connected to
    #     Via             = 2  # 
    #     Pin             = 3  # Pins have low priority. Pin nets ( named 'referenceValue-pinNumber' Ex C1-1 , D1-1 , U1-1) are used in abscence of NetSymbols or labels.
    #     NetSymbol       = 4  #
    #     Label           = 5  # 
    class Layers(Enum):
        NoLayers        = 0 
        All       = 1
        Cu        = 18
        NonCu     = 19
         

# I can't really see a good way to write layers excapt as strings...
    # class Layers():
    #     F_Cu            = 'F.Cu'
    #     B_Cu            = 'B.Cu'
    #     Inr_1           = 'Inr.1'
    #     Inr_2           = 'Inr.2'
    #     Inr_3           = 'Inr.3'
    #     Inr_4           = 'Inr.4'
    #     F_CrtYd         = 'F.CrtYd'
    #     B_CrtYd         = 'B.CrtYd'
    #     F_Fab           = 'F.Fab'
    #     B_Fab           = 'B.Fab'
    #     F_SilkS         = 'F.SilkS'
    #     B_SilkS         = 'B.SilkS'
    #     F_Mask          = 'F.Mask'
    #     B_Mask          = 'B.Mask'
    #     F_Paste         = 'F.Paste'
    #     B_Paste         = 'B.Paste'
        

    layerColors = {
        'F.Cu'      :       QColor(Qt.red)                     ,
        'B.Cu'      :       QColor(Qt.blue)                    ,
        # 'Inr.1'     :       QColor(255, 165,0)         ,                  # https://html-color.codes/orange
        # 'Inr.2'     :       QColor(127, 255, 0)        ,
        # 'Inr.3'     :       QColor(100,200,100)        ,
        # 'Inr.4'     :       QColor(50,200,200)         ,    
        'F.Paste'   :       QColor(Qt.darkRed)                 ,
        'B.Paste'   :       QColor(Qt.darkBlue)                ,
        'F.SilkS'   :       QColor(255,250,134)     ,    # Manilla
        'B.SilkS'   :       QColor(250,128,114)     ,    # Salmon
        'F.Mask'    :       QColor(Qt.green)                   ,
        'B.Mask'    :       QColor(Qt.darkGreen)               ,
        'F.CrtYd'   :       QColor(Qt.magenta)                 ,
        'B.CrtYd'   :       QColor(Qt.cyan)                    ,
        'F.Fab'     :       QColor(Qt.gray)                    ,  
        'B.Fab'     :       QColor(75,75,100)          ,     # darkish bluish       
        'edge.cuts' :       QColor(200,200,200)         # Gray
    }
    
    layers = list(layerColors)

    copperLayers = [ 'F.Cu', 'B.Cu' ,'Inr.1', 'Inr.2', 'Inr.3', 'Inr.4'] 

line_length_threshold = 10 # 10 pixels is line length threshold.

from enum import Enum
class ViaColors(Enum):
    ViaHoleColor = QColor(10, 50, 100 ) 
    ViaColor      = QColor( 20, 200, 150)

def pretty_print(xml):
    xml = etree.tostring(xml, pretty_print = True)
    print(xml.decode(), end = '') # str.decode(): decodes str, default UTF-8



class BoardSceneModes(Enum):
	  normalMode, addTraceMode, deleteTraceMode = range(3)

class MyWidgets(Enum):
    Schematic = 0 
    Board     = 1
    
     
# grid_4mm = 1 / 25.4 * 4 
# grid_1mm = 1 / 25.4 
# grid_1in = 1 
# grid_50thou = .05
# file_grid_step = 1.27  # kicad symbols are designed on .05inch grid, .05inches = 1.27mm 
# grid_pt1mm = 1 / 25.4 * .1 # board grid step is .1mm 
# # kicad_symbol_scale_factor = dpi * grid_4mm / file_grid_step  # scale_factor = 1/1.27 * 50 
# # self.setScale(kicad_symbol_scale_factor) # scale item so it fits on the scene's grid

table_name_column = 'table_name'
general_attributes_column = 'general_attributes'

ss_filters_columns = [Column("table_name", Text, nullable = False) , 
        Column("general_attributes", Text),
        Column("category_specific_attributes", Text),
        Column("primary_attributes", Text),
        Column('reference', Text),
        Column("custom", Text), 
        ]
  
verbose = False
class CreateChoices(Enum):
  DRAW = 0
  DOWNLOAD = 1 
  CONVERT = 2  # How should I associate string values...?

test_dataframe = pandas.DataFrame([ [1,2,3,4] , [5,6,7,8] ], columns = ['A', 'B', 'C', 'D'] )
create_choices = ['draw', 'download', 'convert'] # These are the choices a user can make when creating a new graphic(symbol or footprint) : they can draw one, from scratch, download one, from a third party site, or convert one, from a supported file(.kicad_sym atm)
# pyqt units are pixels. Thus I would not expect a grid of 10pixels to match up. 
# scale the grid, so that its pixels are in mils ~113DPI. 
# 100mil grid 


symbol_font = QFont("Segoe UI", 2)
footprint_font = QFont("Segoe UI", 1) # Likely must change-- gerber only knows font as a path with stroke width
footprint_placeholder_font = QFont("Segoe UI", 6) # for humans to read


wireItemColor = QColor(Qt.magenta)
kicad_canonical_layers = [
    'F.Cu', 'B.Cu',
    'F.Paste', 'B.Paste',
    'F.Fab', 'B.Fab',
    'F.Mask','B.Mask',
    'F.SilkS', 'B.SilkS',
    'Edge.Cuts',
    ]

writeable_columns = ['symbol', 'footprint', 'spice_model', 'cad_model', 'primary_attributes', 'reference']

database_path = "parts/parts.db" 
#abspath takes a path in current directory and gives its absolute path
symbols_path = os.path.abspath('symbols') # c:\Users\robby\OneDrive\Saura\symbols
footprints_path = os.path.abspath('footprints')
spice_models_path = os.path.abspath('spice_models')
cad_models_path = os.path.abspath('cad_models')

kicad_third_party_path = os.path.join( 'third_party', 'kicad') # This is where 3rd party graphics are extracted to 
kicad_third_party_symbols_path = os.path.join(kicad_third_party_path, 'symbols')
kicad_third_party_footprints_path = os.path.join(kicad_third_party_path, 'footprints')
general_schema = [ # Sql tables demand a fixed column order; schema. Here, I set a ordered list,which will carry over into schema. But, a user will want to view parts in differing column orders. To support this, we will later provide filters, defining often desired column orders.
    'primary_attributes',  # AKA NAME (?)
    'symbol',               
    'footprint',            
    'package/case',       
    'datasheet',      
    'reference', 
    'mpn',                  
    'unit_price',           
    'vendor_part_page',     
    'mfr',         
    'vendor',      
    'standard_pricing', 
    'vendor_part_number',   
    'table_name',
    'categories',   
    # 'category_specific_schema'# saved in  a different table, ss_filters   
    ]
# Remember, Sqlite has bad ALTER TABLE support, so its usually easier to delete & re-create the table w/ new column order, than it is to insert a column  

terminal_radius = 1
KICAD8_SYMBOL_DIR = "C:/Users/robby/AppData/Local/Programs/KiCad/8.0/share/kicad/symbols/" # Swap the backslashes for fwd slashes with ctrlH on the selected string
dir = 'parts/'                     #For practice
seekerRadius = 2 # Radius about pointer, self.self.terminals within which will becoonme snap location for our line( NOT our cursor -- we don't want to steal control of mouse from user. But its good to steal control of our line item from the cursor)
# alt names for 'seeker' : 'seeker' 'scanner' 

reference_designator_map = { # TODO: cover all cases of reference_designators https://en.wikipedia.org/wiki/Reference_designator
'capacitor'             : 'C' , 
'resistor'              : 'R' ,
'inductor'              : 'L' ,
'crystal'               : 'X' ,
'oscillator'            : 'X' ,
'resonator'             : 'X' ,
'diode'                 : 'D' ,
'integrated_circuit'    : 'U' ,
}

@staticmethod
def xml_attribute_name_filter(string):
  string = re.sub(r'/', '_', string) #Substitute fwd slash for underscore _
  string = re.sub(r'\s+', '', string).strip() #remove all whitespace
  string = string.replace('~', '') 
  return string.lower() #  For column names, since we have underscores not spaces, I prefer all lowercase 'like_this' 'Instead_of_this'

@staticmethod
def xml_attribute_value_filter(string):
  string = re.sub(r'/', '_', string) #Substitute fwd slash for underscore _
  string = re.sub(r'\s+', '', string).strip() #remove all whitespace
  return string 


# _[**0-9]_

@staticmethod
def normalize(string): 
  string = string.lower() 
  string = string.replace('-', '_') # Hyphens become underscore
  # string = string.replace('/', '_') 
  string = re.sub(r"\s+([**A-Za-z0-9])\s+" , r'\1', string ) # remove spaces around nonalphanumeric characters.  The \1 is a regex capture group thing
  return string
#  Pro Tip: re.sub(r'\W+', '', your_string) By Python definition '\W == [**a-zA-Z0-9_], which excludes all numbers, letters and _
def normalize_sql_table_name(categories:list):
  string = '_'.join(categories)     # Join w/ underscore
  string = string.replace(" ", "_") # Spaces become underscore
  string = string.replace(",", "")  # delete commas
  string = normalize(string)
  return string
# CATEGORIES: ['connectors, interconnects', 'barrel connectors', 'barrel connector accessories']
# SELF.TABLE_NAME "connectors,_interconnects_barrel_connectors_barrel_connector_accessories"
# Try simpler: 


# string =re.sub( "_+[**A-Za-z0-9]_+" , "_", string) # replace any _*_ pattern with _  (This happens on "Package / Case") 
#         string = re.sub(r'\s+', '', string) #replacde any whitespace with underscore
#         string = re.sub("_+", "_", string) # replace any multiple underscores with underscore 
#         return string 
# string = "Package / Case"
# print(xml_attribute_name_filter(string))



# Some weird Ki characters 
# ~                                     Used for: ???





# 1) TOKEN. 
# 2) Special handling of some tokens. increment st_idx, depending on element.
# 3) Try get_keys(). 
# 4) Look at all values. IF any are list, subelement. If none are list, add parent kv attributes 

at_string = """(symbol "STM32C011J4M6" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
(property "Reference" "U" (id 0) (at 63.5 10.16 0)
    (effects (font (size 1.524 1.524)))
)
(at "3.0" "4.0" "360degrees" )
      (pin bidirectional line (at 0 -7.62 0) (length 7.62)
        (name "PA13" (effects (font (size 1.27 1.27))))
        (number "7" (effects (font (size 1.27 1.27))))
      ))"""
      
symbol_string =   """(symbol "STM32C011J4M6" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
(property "Reference" "U" (id 0) (at 63.5 10.16 0)
    (effects (font (size 1.524 1.524)))
)
(property "Value" "STM32C011J4M6" (id 1) (at 63.5 7.62 0)
    (effects (font (size 1.524 1.524)))
)

(symbol "STM32C011J4M6_0_1"
    (polyline
    (pts
        (xy 1.1 2.2)
        (xy 3.3 -4.4)
    )
    (stroke (width 0.127) (type default) (color 0 0 0 0))
    (fill (type none))
    )
    (polyline
    (pts
        (xy 10.1 20.2)
        (xy 30.3 -40.4)
    )
    (stroke (width 0.127) (type default) (color 0 0 0 0))
    (fill (type none))
    )

    (pin bidirectional line (at 127 -2.54 180) (length 7.62)
    (name "PB7/PC14-OSCX_IN" (effects (font (size 1.27 1.27))))
    (number "1" (effects (font (size 1.27 1.27))))
    )
    (pin bidirectional line (at 127 0 180) (length 7.62)
    (name "PB6/PA14-BOOT0/PC15-OSCX_OUT" (effects (font (size 1.27 1.27))))
    (number "8" (effects (font (size 1.27 1.27))))
    )
)
)      """
# 7.62mm = .3in
full_symbol_string =   """(symbol "STM32C011J4M6" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)

    (property "Reference" "U" (id 0) (at 63.5 10.16 0)
      (effects (font (size 1.524 1.524)))
    )
    (property "Value" "STM32C011J4M6" (id 1) (at 63.5 7.62 0)
      (effects (font (size 1.524 1.524)))
    )
    (property "Footprint" "SO-8_STM" (id 2) (at 0 0 0)
      (effects (font (size 1.27 1.27) italic) hide)
    )
    (property "Datasheet" "STM32C011J4M6" (id 3) (at 0 0 0)
      (effects (font (size 1.27 1.27) italic) hide)
    )
    (property "ki_keywords" "STM32C011J4M6" (id 4) (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "ki_locked" "" (id 5) (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "ki_fp_filters" "SO-8_STM SO-8_STM-M SO-8_STM-L" (id 6) (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (symbol "STM32C011J4M6_0_1"
      (polyline
        (pts
          (xy 7.62 5.08)
          (xy 7.62 -17.78)
        )
        (stroke (width 0.127) (type default) (color 0 0 0 0))
        (fill (type none))
      )
      (polyline
        (pts
          (xy 7.62 -17.78)
          (xy 119.38 -17.78)
        )
        (stroke (width 0.127) (type default) (color 0 0 0 0))
        (fill (type none))
      )
      (polyline
        (pts
          (xy 119.38 -17.78)
          (xy 119.38 5.08)
        )
        (stroke (width 0.127) (type default) (color 0 0 0 0))
        (fill (type none))
      )
      (polyline
        (pts
          (xy 119.38 5.08)
          (xy 7.62 5.08)
        )
        (stroke (width 0.127) (type default) (color 0 0 0 0))
        (fill (type none))
      )
      (pin bidirectional line (at 127 -2.54 180) (length 7.62)
        (name "PB7/PC14-OSCX_IN" (effects (font (size 1.27 1.27))))
        (number "1" (effects (font (size 1.27 1.27))))
      )
      (pin power_in line (at 127 -7.62 180) (length 7.62)
        (name "VDD/VDDA" (effects (font (size 1.27 1.27))))
        (number "2" (effects (font (size 1.27 1.27))))
      )
      (pin power_in line (at 0 -12.7 0) (length 7.62)
        (name "VSS/VSSA" (effects (font (size 1.27 1.27))))
        (number "3" (effects (font (size 1.27 1.27))))
      )
      (pin bidirectional line (at 0 0 0) (length 7.62)
        (name "PA0/PA1/PA2/PF2-NRST" (effects (font (size 1.27 1.27))))
        (number "4" (effects (font (size 1.27 1.27))))
      )
      (pin bidirectional line (at 0 -2.54 0) (length 7.62)
        (name "PA11[PA9]/PA8" (effects (font (size 1.27 1.27))))
        (number "5" (effects (font (size 1.27 1.27))))
      )
      (pin bidirectional line (at 0 -5.08 0) (length 7.62)
        (name "PA12[PA10]" (effects (font (size 1.27 1.27))))
        (number "6" (effects (font (size 1.27 1.27))))
      )
      (pin bidirectional line (at 0 -7.62 0) (length 7.62)
        (name "PA13" (effects (font (size 1.27 1.27))))
        (number "7" (effects (font (size 1.27 1.27))))
      )
      (pin bidirectional line (at 127 0 180) (length 7.62)
        (name "PB6/PA14-BOOT0/PC15-OSCX_OUT" (effects (font (size 1.27 1.27))))
        (number "8" (effects (font (size 1.27 1.27))))
      )
    )
  )"""

# s = sexpdata.loads(symbol_string)
# print(s)
# print(symbol_string)
ns_tokens = ['pin_numbers', 'pin_names', 'in_bom', 'on_board', 'effects', 'stroke', 'fill', 'font', 'size', 'id']                              #ignore these tokens. 
tokens_supported_condition = {'at': "'at' token supported under 'pin' token"}

#'id' maybe useful under some tokens. Not useful under 'property' token. Only appearing under 'property' atm, so remove 
dns_values = ['STROKE_DEFINITION', 'TEXT_EFFECTS', 'FILL_DEFINITION',]  #ignore these values 
special_tokens =['symbol', 'property' , 'at'] # These tokens have structure such that these tokens need to be specially handled(atm this is implemented in str_count)

documentation = { 

'symbol':
"""
    (symbol
    "LIBRARY_ID" | "UNIT_ID"
    [(extends "LIBRARY_ID")] 
    [(pin_numbers hide)] 
    [(pin_names [(offset OFFSET)] hide)] 
    (in_bom yes | no)
    (on_board yes | no)                                         
    SYMBOL_PROPERTIES...                                        
    GRAPHIC_ITEMS...                                            
    PINS...                                                     
    UNITS...                                                    
    [(unit_name "UNIT_NAME")]                                   
)""",

'pin': 
"""
    (pin
    PIN_ELECTRICAL_TYPE                                         
    PIN_GRAPHIC_STYLE   
    POSITION_IDENTIFIER                         
    (length LENGTH)                                             
    (name "NAME" TEXT_EFFECTS)                                  
    (number "NUMBER" TEXT_EFFECTS)                              
  )""",

'at':
"""
    (at
    X
    Y
    [ANGLE]
    )""",
  
'property':
  """
    (property
    "KEY"                                                     
    "VALUE"                                                   
    (id N)                                                    
    POSITION_IDENTIFIER                                       
    TEXT_EFFECTS                                              
  )""",
  
'polyline':
"""  (polyline
    COORDINATE_POINT_LIST                                       
    STROKE_DEFINITION   
    FILL_DEFINITION                                             
  )""",

'rectangle':
"""  (rectangle
    (start X Y)                                                 
    (end X Y)                                                   
    STROKE_DEFINITION                                           
    FILL_DEFINITION                                             
  )""", 
  
'pts':
"""
  (pts
    (xy X Y)                                                    
    ...
    (xy X Y)
  )""",
  # ... becomes sexpr.Symbol. If ..., pass 
  
'xy' : "(xy X Y)",
'xyz': "(xyz X Y Z)",


'image': 
"""
  (image
    POSITION_IDENTIFIER                                         
    [(scale SCALAR)]                                            
    [(layer LAYER_DEFINITIONS)]                                 
    UNIQUE_IDENTIFIER                                           
    (data IMAGE_DATA)                                           
  )""",
  
'start':
"""    (start X Y)
""",
'end':
"""
(end x y)
""",

}
# print(documentation.get('property'))
# print(symbol_string)
def get_keys(token, verbose=False): 
    keys = []
    # print()
    # print('TYPE(token): ', type(token), token )
    docs = documentation.get(token, None)
    # if not docs: 
    if token in ns_tokens: # DoNotSupport this token
        return None
    else: 
        # print()
        # print('TYPE(DOCS)', type(docs) )
        # print('DOCS:', docs)
        docs = loads(docs)
        docs.pop(0)

        for idx in docs: 
            # print("DOC[IDX] :", idx)
            if isinstance(idx, sexpdata.Symbol): 
                keys.append(idx.value())
            elif isinstance(idx, sexpdata.Brackets):
                brack = idx[0][0]
                if verbose: 
                    print('BracketData: ', brack)
                if isinstance(brack, list): 
                    if verbose: 
                        print("BracketDataIsListTypeSoIDC")
                    pass
                elif isinstance(brack, sexpdata.Symbol):
                    if verbose: 
                        print('BrackIsSymbolSoAppendToKeys:', brack.value())
                    keys.append(brack.value())
            elif isinstance(idx, str): 
                if verbose: 
                    print(f'DOCScontains 1+ string. REquires special processing. Do nothing')    
            if verbose: 
                print('KEYS:', keys)
    return keys # None | [] | [populated]
# x = get_keys('pin')




def random(boundary):
    return QRandomGenerator.global_().bounded(boundary)




class Geometry():
    extra_small_rect = QRectF(-1, -1, 2, 2)
    small_rect = QRectF(-10, -10, 20, 20)
    med_rect = QRectF(-100,-100, 200, 200)
    origin_rect = QRectF(-2,-2,4,4)

class PartData(Enum): # Note that these are all just held in the 'part' dict... this probably shouldn't exist...
    MPN               = 0 # Manufacturer Product Number Ex. STM32C064
    VENDOR            = 1 # Vendor                      Ex. Digikey
    MFR               = 2 # Manufacturer                Ex. Kyocera
    DATABASE_PATH     = 3 # location of database        Ex. /parts/parts.db
    CATEGORIES        = 4 # comman sep string (Convenience, shows up in database_path) Ex. "capacitors , capacitors_ceramic"
    TABLE_NAME        = 5 # capacitors_ceramic
    PART              = 6 # dictionary representing all data. May as well include it until sure we dont need it Ex {'mpn':"STM32C0", 'mfr', "Kyocera", 'database_path': "/parts/parts.db", 'price': ".32"}
    #Q: should I include symbol_path, footprint_path? 
class ItemData(Enum):
    SYMBOL_REFERENCE  = 6 # R for resistors, C for capacitors, I:inductors, U:IC's, etc
    SYMBOL_VALUE      = 7 # R1 R2 R3
    SYMBOL_GRAPHIC    = 8 # C_Small, STM32Co64, etc.
    FOOTPRINT_GRAPHIC = 9 # 0603, 1206, etc
    
    
# item_data = {
#     'name': }


delimiter = ';'
encoding = 'utf-8'

