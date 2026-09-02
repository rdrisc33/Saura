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
        NormalMode      = 0 
        AddTraceMode    = 1
        AddViaMode      = 2
        DeleteMode      = 3
        
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

    symbolFont = QFont("Segoe UI", 2)
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
        
    layers = [
        'F.Cu',
        'B.Cu',
        # 'Inr.1',
        # 'Inr.2',
        # 'Inr.3',
        # 'Inr.4',
        'F.CrtYd',
        'B.CrtYd',
        'F.Fab',
        'B.Fab',
        'F.SilkS',
        'B.SilkS',
        'F.Mask',
        'B.Mask',
        'F.Paste',
        'B.Paste'
    ]

    layerColors = {
        'F.Cu'      :       Qt.red                     ,
        'B.Cu'      :       Qt.blue                    ,
        # 'Inr.1'     :       QColor(255, 165,0)         ,                  # https://html-color.codes/orange
        # 'Inr.2'     :       QColor(127, 255, 0)        ,
        # 'Inr.3'     :       QColor(100,200,100)        ,
        # 'Inr.4'     :       QColor(50,200,200)         ,    
        'F.Paste'   :       Qt.darkRed                 ,
        'B.Paste'   :       Qt.darkBlue                ,
        'F.SilkS'   :       QColor(255,250,134)     ,    # Manilla
        'B.SilkS'   :       QColor(250,128,114)     ,    # Salmon
        'F.Mask'    :       Qt.green                   ,
        'B.Mask'    :       Qt.darkGreen               ,
        'F.CrtYd'   :       Qt.magenta                 ,
        'B.CrtYd'   :       Qt.cyan                    ,
        'F.Fab'     :       Qt.gray                    ,  
        'B.Fab'     :       QColor(65,65,100)               # darkish bluish                             ,
    }

    CopperLayers = [ 'F.Cu', 'B.Cu' ,'Inr.1', 'Inr.2', 'Inr.3', 'Inr.4'] 
 
# class LayerItem(): # LIs have no electrical connectivity, & include silkscreen, courtyard, mask & do not go in rtree & are .childItems 
#     def __init__(self, layer, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         self._layer                     = None 
#         self._color                     = None 
        
#         self.setLayer(layer)
#         # print()
#         # print('SELF:', self)
#         # print('SELF.LAYER():', self.layer())
#         self.setColor(Utils.layerColors[self.layer()])
        
#     def layer(self):
#         return self._layer
#     def setLayer(self, layer):
#         self._layer = layer
#     def color(self):
#         return self._color
#     def setColor(self, color):
#         self._color = color
        
# class LineItem(LayerItem, QGraphicsLineItem): 
#     def __init__(self, layer, *args, **kwargs): 
#         super().__init__(layer, *args, *kwargs)



    

class LayerItem(): 
    """Items which have just one layer. Always childItems of Via, Trace, Zone, Pad, Footprint"""
    def __init__(self, layer, net = None, *args, **kwargs): 
        super().__init__( *args, **kwargs)
    
        self.setLayer(layer)
        self._net = net
        
        
    def sceneBounds(self):

        rect =self.mapToScene(self.boundingRect()).boundingRect()
        return ( rect.left() , rect.top() , rect.right() , rect.bottom() )


    def sceneBufferedBounds(self): 
        # rect =self.mapToScene(self.boundingRect()).adjusted(-)
        pass
        
    def connectedNets(self): 
        self._connectedNets = [self.net()] 
        # r = proposedShape.boundingRect()
        # proposedBounds = (r.left() , r.top() , r.right() , r.bottom())
        hitIds = self.scene().rtrees[self.layer()].intersection(self.sceneBounds())
        # hitIds = self.scene().rtrees[self.layer()].intersection(proposedBounds)
        hitItems = [self.scene().ids[hitId] for hitId in hitIds]
        for hitItem in hitItems: 
            if self.collidesWithItem(hitItem):
                self._connectedNets.append(hitItem.net())
        
        return self._connectedNets
            

    def insertIntoRtree(self): 
        self.scene().rtrees[self.layer()].insert(self.id() , self.sceneBufferedBounds())

            

    def net(self):
        return self._net 
    def setNet(self, net): 
        self._net = net 
        
    def showLayer(self, layer): 
        print('SHOWLAYER')
        if self.layer() == layer: 
            
            self.show()
            self.setZValue(1)
        else: 
            self.setZValue(0)

    def hideLayer(self, layer):
        print('HIDELAYER')
        if self.layer() == layer: 
            self.hide() 
            self.setZValue(0)

    def layer(self):
        return self._layer
    def setLayer(self, layer):
        self._layer = layer

# class CopperItemContainer(LayersItem): # Base class of FP TR ZN VA PD classes. Not useful by itself
#     def __init__(self, layers, *args, **kwargs):
#         # print('CUIC.LAYERS:', layers)
#         # print('CUIC.ARGS:', args)
#         # print('CUIC.KWARGS:', kwargs)
#         super().__init__(layers, *args, **kwargs)
#         # print('COPPERITEMCONTAINER.INIT')
#         # self._layer                 = None    Moved to BoardItem
#         # self._layers                = layers  Moved to BoardItem
#         # self._layerItems            = defaultdict(list) # { 'F.Cu': LineItem} Phasing out
#         self._terminals             = None 
#         self._nonNoneNets           = None 
#         self._sceneTerminal         = None      # 3-Tuple (scenePosX,scenePosY,layer) 
#         self._sceneTerminals        = None      # self.terminals are point(s) on a pad, via, which are connectable. Ex TraceItem self.terminals are p1,p1. Via self.terminals are center aka origin, pad self.terminals are pad origin(NOT necessarily pad centroid, think solder bridge pads), and Footprint self.terminals are pads/vias contained in the footprint
#         self._buffer                = None      # QGraphicsPolygonItem representing item's shape, buffered by (mostLikely) scene.tracewidth
#         self._sceneBuffer           = None      # A QPolygonF(?) representing item's shape, buffered by .bufferDistance(), in scene coordinates 
#         self._bounds                = None      # A 4-tuple(left top right bottom). unbuffered. used by ... ?
#         self._sceneBounds           = None      # A 4-tuple(left top right bottom), buffered by .bufferDistance(). Used in the rtree
#         self._bufferedBounds        = None      # A 4-tuple(left top right bottom) buffered by .bufferDistance(). local coordinates 
#         self._sceneBufferedBounds   = None      # ._bufferedBounds in scene coordinates
#         self._id                    = None 
#         self._net                   = None 
#         # self._copperItems           = phasing out defaultdict(list) # {'F.Cu': [PadItem , ViaItem] , 'Inr_1': [ZoneItem, ... }


#     def queryRtrees(self):
#         """query MainWindow.rtrees for self.sceneBufferedBounds() at each layer in self.layers """
#         # print('self.SceneBufferedBounds():', self.sceneBufferedBounds())
#         hitIds = [] 
#         for layer in self.layers(): 
#             hitIds.extend( self.scene().rtrees[layer].intersection(self.sceneBufferedBounds()) )
#         # print(f'HIT {len(hitIds)} ITEMS')
#         hitItems = [self.scene().ids[hitId] for hitId in hitIds]
#         return hitItems
    
#     def showLayer(self, layer): 
#         for childItem in self.childItems(): 
#             childItem.showLayer(layer)
            
#     def hideLayer(self, layer):
#         for childItem in self.childItems():
#             childItem.hideLayer(layer)
            
#     def insertIntoRtree(self): 
#         for layer in self.layers(): 
#             self.scene().rtrees[layer].insert(self.id() , self.sceneBufferedBounds())
#         # for child in self.childItems(): 
#         #     if isinstance(child, LayerItem): 
#         #         child.insertIntoRtree()
                
#     def net(self):
#         return self._net 
#     def setNet(self, net):
#         self._net = net
      
#     def setBufferDistance(self, bufferDistance): # Upon construction, item may not have a scene, thus it cannot know scene.traceWidth aka bufferDistance, thus we must wait until item is added to scene to implement buffer functions. 
#         self._bufferDistance = bufferDistance 
#         self.setBuffer()
#         # print('BUFFER:', self.buffer())
#         self.setSceneBuffer() 
#         # print('SETSCENEBUFFER')
#         self.setBufferedBounds() # Must have bounds to insert into rtree ( Would do this in constructor, except requires bufferWidth, which is taken from scene)
#         self.setSceneBufferedBounds()
        
#     # def insertIntoRtree(self):
#     #     self.scene().rtrees[self.layer()].insert(self.id() , self.sceneBufferedBounds())
        
#     def removeFromRtree(self):
#         for layer in self.layers(): 
#             self.scene().rtrees[layer].delete(self.id() , self.sceneBufferedBounds())
        
#     def updateRtree(self): # Update existing entry in rtree
#         self.removeFromRtree() # rtree removal demands (id, bounds). Thus we must remove B4 .setSceneBufferedBounds()
#         self.setSceneBufferedBounds()
#         self.insertIntoRtree()
        
#     # def layer(self): # CuICs won't all have just one layer
#     #     return self._layer
#     # def setLayer(self, layer):
#     #     self._layer = layer
        
#     def layers(self):
#         return self._layers
#     def setLayers(self, layers):
#         self._layers = layers
        
#     def copperLayers(self):
#         return [layer for layer in self.layers() if layer in Utils.CopperLayers]
        
#     def id(self):
#         return self._id 
#     def setId(self, id):
#         self._id = id
        
#     # def mouseMoveEvent(self, event):
#     #     print('CUITEM.MOUSEMOVEEVENT:')
#     #     self.updateRtree()
#     #     self.setSceneBuffer()
#     #     self.setTerminals()
#     #     self.setSceneBounds()
#     #     super().mouseMoveEvent(event)
    
#     def bounds(self): 
#         return self._bounds
#     def setBounds(self): # UNBUFFERED bounds. Local position. Used for .... ? 
#         rect =self.boundingRect()
#         self._bounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 

#     def sceneBounds(self):
#         return self._sceneBounds
#     def setSceneBounds(self):
#         rect =self.mapToScene(self.boundingRect()).boundingRect()
#         self._sceneBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 
        
#     def buffer(self):
#         return self._buffer
#     def setBuffer(self):#, bufferDistance = None): 
            
#         stroker = QPainterPathStroker()
#         stroker.setWidth(self._bufferDistance)
#         stroker.setJoinStyle(Qt.BevelJoin) # ry roundJoin for irl
#         stroker.setCapStyle(Qt.FlatCap)
        
#         path = self.shape() 
#         path.closeSubpath() # Often, .shape() -> an unclosed shape
#         strokerPath = stroker.createStroke(path)
#         expandedPath = path.united(strokerPath) #Unite the fillable areas of the paths into one consolidated path
#         self._buffer = expandedPath.toFillPolygon()  # convert to a QPolygonF then to a QGPolygonItem.

#     def sceneBuffer(self):
#         return self._sceneBuffer
#     def setSceneBuffer(self):
#         self._sceneBuffer = self.mapToScene(self.buffer())

#     def bufferedBounds(self):
#         return self._bufferedBounds
#     def setBufferedBounds(self):#, self._bufferDistance=None): # calulate and set new bounds. Bounds describes a bounding rectangle around a shape, in the form of a 4-tuple (xmin ymin xmax ymax), aka (left top right bottom). Bounds is borrowed from how the the python modules Shapely/rtree use bounds; bounds is not from Qt. calculate_bufferedBounds returns the bounds, buffered by self._bufferDistance(most likely = currently selected scene.traceWidth()). The bounds 4-tuple is used bt the rtree module to describe rectangles. Note that, because Qt considers pen_width in .boundingRect, I have to manually set a 0 width pen away from the default width-of-1 pen, else the buffered bounds will be .5 wider than supposed to.
#         rect = self.boundingRect().adjusted(-self._bufferDistance,-self._bufferDistance, self._bufferDistance,self._bufferDistance)
#         self._bufferedBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 
    
#     def sceneBufferedBounds(self):
#         return self._sceneBufferedBounds
#     def setSceneBufferedBounds(self):
#         rect = self.mapToScene(self.boundingRect().adjusted(-self._bufferDistance,-self._bufferDistance, self._bufferDistance,self._bufferDistance)).boundingRect() # 
#         self._sceneBufferedBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 
        
#     def connectsToItem(self, item): # -> True if self is connected to other. Connected as in electrically connected.

#         if  isinstance(item, CopperItemContainer): 
#             for t in item.sceneTerminals():  # Try cheap check: do terminal exact positions match 
#                 print("SELF:", self)
#                 print('SELF.SCENETERMINALS():', self.sceneTerminals())
#                 if any(t == t2 for t2 in self.sceneTerminals()): 
#                     return True 
#             for t in item.sceneTerminals(): # Try cheap-ish check: does shape contain termianal
#                 if self.contains(t): 
#                     return True
#             if self.collidesWithItem(item): # Try expensive check: do shapes collide at all
#                 return True 
#             else: 
#                 return False 
            
#         # elif isinstance(other, QPoint): # idt this is used
#         #     if any( t == other for t in self.terminals() ): # Initial fast check to see if terminals perfectly align
#         #         return True 
#         #     elif self.contains(other): # (low cost?) check to see if point is within other
#         #         return True 
#         #     # elif self.collidesWithItem No such thing as cWI for a point
            
#         else: 
#             print('MW.connectsTo() SOMETHING WRONG ')

#     # def connectedNets(self): 
#     #     return self._connectedNets
#     def nonNoneNets(self):
#         return self._nonNoneNets

#     def connectedNets(self):
#         for child in self.childItems(): 
#             self._connectedNets.extend(child.connectedNets())
            
#         return self._connectedNets
#     # def setConnectedNets(self):
#         # self._connectedNets = defaultdict(list)
#         # for copperItems in self.copperItems().values(): 
#         #     for copperItem in copperItems:
#         #         copperItem.setConnectedNets()
#         #         for net, items in copperItem.connectedNets():
#         #             self._connectedNets[net].extend(items)
#         # self._nonNoneNets = [net for net in self._connectedNets if not net is None]
#         # print() 
#         # print('CUIC.CONNECTEDNETS():', self.connectedNets())
#         # print('CUIC.NONNONENETS:', self._nonNoneNets) 
                            
#                     # 
#     # def updateStuff(self): 
#     #     for layer, copperItems in self.copperItems().items(): 
#     #         for copperItem in copperItems: 
#     #             copperItem.updateStuff()
            
#     # def mousePressEvent(self, event): 
#     #     self.offset = event.scenePos() - self.scenePos()
#     #     super().mousePressEvent(event)
        
#     # def mouseMoveEvent(self, event): #QGI.mmE moves all child items, so would call super() for that-- if we didn't need custom snapping behavior. And, still have to update rtrees & sceneBounds & sceneTerminals etc of all descendant Items
#     #     # print()
#     #     # print('COPPERITEMCONTAINER.MME')
#     #     self.setPos(self.scene().snapToGrid(event.scenePos() - self.offset))
        


                
#         # super().mouseMoveEvent(event) Do NOT call as we want custom snapToGrid behavior.
        
#     # def sceneTerminals(self):#  
#     #     return self._sceneTerminals
            
#     # def sceneTerminal(self):
#     #     return self._sceneTerminal 
#     # def setSceneTerminal(self):
#     #     self._sceneTerminal = self.scenePos() # (*self.scenePos().toTuple(), self.layer()) # (x, y, layer) 

#     # def setSceneTerminals(self): 
#         # self._sceneTerminals = []
#         # print(f'{self}.COPPERITEMS():', self.copperItems())
#         # for layer, copperItems in self.copperItems().items(): 
#         #     for copperItem in copperItems :
#         #         copperItem.setSceneTerminal()
#         #         copperItem.setSceneTerminals()
#         #         self._sceneTerminals.append(copperItem.sceneTerminal())
    
#     # def layerItems(self): # Moved to FP
#     #     return self._layerItems
#     # def setLayerItems(self, layerItems): 
#     #     self._layerItems = layerItems  
#     # def addLayerItem(self, layerItem):
#     #     # print()
#     #     # print('LAYERITEM:', layerItem)
#     #     self.layerItems()[layerItem.layer()].append(layerItem)
#     # def removeLayerItem(self, layerItem):
#     #     self.layerItems()[layerItem.layer()].remove(layerItem)
        
#     # def boundingRect(self):
#     #     return self.childrenBoundingRect() or QRectF()
#     # def paint(self, painter, option, widget):
#     #     pass 
 
# # updateRtree()
# # setSceneBuffer()
# # setTerminals()
# # setSceneBounds()  

#     def updateRtrees(self):# Update an existing entry in rtree
#         self.removeFromRtrees() # rtree removal demands (id, bounds). Thus we must remove B4 .setSceneBufferedBounds()
#         self.setSceneBufferedBounds()
#         self.insertIntoRtrees()
        
#     def insertIntoRtrees(self):
#         for layer in self.layers(): 
#             self.scene().rtrees[layer].insert(self.id() , self.sceneBufferedBounds())
            
#     def removeFromRtrees(self): 
#         for layer in self.layers(): 
#             self.scene().rtrees[layer].delete(self.id() , self.sceneBufferedBounds())# rtree removal demands (id, bounds). Thus we must remove B4 .setSceneBufferedBounds()
    
#     def containsTerminal(self, terminal): # returns true if layers match and terminal pos is contained within shape. terminal: (layer:str, pos:QPoint)
#         terminalPos = terminal['pos']
#         terminalLayer = terminal['layer']
#         if terminalLayer in self.layers(): 
#             if self.contains(terminalPos): # QGraphicsItem.contains()
#                 return True 
#         return False 
        

#     def setShowingLayers(self, layers): 

#         for layer, layer_items in self.copperItems().items():
#             if layer in layers: 
#                 for layer_item in layer_items: 
#                     layer_item.show()
#             else: 
#                 for layer_item in layer_items:
#                     layer_item.hide()
            
#     def copperItems(self):
#         return self._copperItems 
#     def setCopperItems(self,copperItems):
#         self._copperItems = copperItems 
#     def addCopperItem(self, layer, copperItem):
#         self.copperItems()[layer].append(copperItem)
#     def removeCopperItem(self, layer, copperItem):
#         self.copperItems()[layer].remove(copperItem)
        
#     def addLayer(self, layer):
#         self._layers.append(layer)
#     def removeLayer(self, layer):
#         self._layers.remove(layer)
          
#     # def mousePressEvent(self, event):
#     #     self.moveStart = event.scenePos()
#     #     self.offset = event.scenePos() - self.scenePos() 
#     #     super().mousePressEvent(event) # Does not prevent jumping bug # Note base implementation of mPE handles offsets while moving
                
#     # def mouseMoveEvent(self, event):
#     #     super().mouseMoveEvent(event)
    
#     # def hoverEnterEvent(self, event):
#     #     current_tooltip = self.toolTip()

#     #     self.setToolTip(f"{current_tooltip}\nPos: {self.pos()}\nscenePos: {self.scenePos()}")
#     #     return super().hoverEnterEvent(event)
#     # def hoverLeaveEvent(self, event):
#     #     self.setToolTip("")
#     #     super().hoverLeaveEvent(event)

    
        

        

        
# class CopperItem(): # Cu Items have electrical connectivity &include TI PI VI ZI & can go in rtree. Cu Items have a single layer.  Has a bunch of stuff they all need like 'buffer' and 'bounds' and 'buffered_bounds' & are .childItems 
#     def __init__(self, layer, *args, **kwargs):
#         self._connectedNets         = None 
#         super().__init__(*args, **kwargs)
#         self.nonNoneNets            = None 
#         self._layer                 = None    
#         self._sceneTerminal         = None      # 3-Tuple (scenePosX,scenePosY,layer) 
#         self._sceneTerminals        = None      # self.terminals are point(s) on a pad, via, which are connectable. Ex TraceItem self.terminals are p1,p1. Via self.terminals are center aka origin, pad self.terminals are pad origin(NOT necessarily pad centroid, think solder bridge pads), and Footprint self.terminals are pads/vias contained in the footprint
#         self._buffer                = None      # QGraphicsPolygonItem representing item's shape, buffered by (mostLikely) scene.tracewidth
#         self._sceneBuffer           = None      # A QPolygonF(?) representing item's shape, buffered by .bufferDistance(), in scene coordinates 
#         self._bounds                = None      # A 4-tuple(left top right bottom). unbuffered. used by ... ?
#         self._sceneBounds           = None      # A 4-tuple(left top right bottom), buffered by .bufferDistance(). Used in the rtree
#         self._bufferedBounds        = None      # A 4-tuple(left top right bottom) buffered by .bufferDistance(). local coordinates 
#         self._sceneBufferedBounds   = None      # ._bufferedBounds in scene coordinates
#         self._id                    = None 
#         self._net                   = None 
        
#         self.setLayer(layer)
#         # print('SELF.LAYER:', self.layer())
#         self._color = Utils.layerColors[self.layer()]

        # self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable) # NO BAD we in fact do NOT want CuItems movable, only their parent items movable
        
    # def queryRtrees(self):
    #     hitIds = self.scene().rtrees[self.layer()].intersection(self.sceneBufferedBounds())
    #     hitItems = [self.scene().ids[hitId] for hitId in hitIds]
    #     return hitItems 
    
    # def setConnectedNets(self): 
    #     self._connectedNets = defaultdict(list)
    #     # for item in self.collidingItems(): Bc scene does not take layers into account, use rtrees instead.
    #     for item in self.queryRtrees():
    #         if isinstance(item, CopperItem): 
    #             if not self.collidesWithItem(item):
    #                 continue 
    #             self._connectedNets[item.net()].append(item)
    #     print('SELF._CONNECTEDNETS:', self._connectedNets)
    #     self._nonNoneNets = [net for net in self._connectedNets if not net is None]
    #     print() 
    #     print('CUI.CONNECTEDNETS():', self.connectedNets())
    #     print('CUI.NONNONENETS:', self._nonNoneNets) 

        

        

        
        
    # def net(self):
    #     return self._net 
    # def setNet(self, net):
    #     self._net = net
    # def mouseMoveEvent(self, event): 
    #     print("COPPERITEM.MME")
    #     self.updateStuff() 
    #     super().mouseMoveEvent(event)

    # def updateStuff(self):
    #     self.setSceneTerminal()
    #     self.setSceneTerminals()
    #     self.setSceneBounds()
    #     self.setSceneBuffer()
    #     self.setSceneBufferedBounds()
    #     self.updateRtree()
        
    # def sceneTerminal(self): # # CuItem has only one terminal (x,y,layer) 
    #     return self._sceneTerminal
    # def setSceneTerminal(self):# Center must be at origin; shape must be symmetric about origin. While that is the case, .scenePos() will be the center
    #     # print()
    #     # print('CuI.SETSCENETERMINAL: CuI.SCENEPOS():', self.scenePos().toPoint())
    #     self._sceneTerminal = (*self.scenePos().toTuple(), self.layer()) # (x, y, layer) 
        
    # def sceneTerminals(self):
    #     return self._sceneTerminals
    # def setSceneTerminals(self):
    #     # self._sceneTerminals = [self.sceneTerminal()] 
    #     self._sceneTerminals = [ (*self.scenePos().toTuple(), self.layer())]
        
    # Note no ._terminal bc copperItem local-position terminals will never be updated 

    # def setBufferDistance(self, bufferDistance): # Upon construction, item may not have a scene, thus it cannot know scene.traceWidth aka bufferDistance, thus we must wait until item is added to scene to implement buffer functions. 
    #     self._bufferDistance = bufferDistance 
    #     self.setBuffer()
    #     self.setSceneBuffer()
    #     self.setBufferedBounds() # Must have bounds to insert into rtree ( Would do this in constructor, except requires bufferWidth, which is taken from scene)
    #     self.setSceneBufferedBounds()
        
    # # def insertIntoRtree(self):
    # #     self.scene().rtrees[self.layer()].insert(self.id() , self.sceneBufferedBounds())
        
    # def removeFromRtree(self):
    #     self.scene().rtrees[self.layer()].delete(self.id() , self.sceneBufferedBounds())
        
    # def updateRtree(self): # Update existing entry in rtree
    #     self.removeFromRtree() # rtree removal demands (id, bounds). Thus we must remove B4 .setSceneBufferedBounds()
    #     self.setSceneBufferedBounds()
    #     self.insertIntoRtree()
        
    # def layer(self):
    #     return self._layer
    # def setLayer(self, layer):
    #     self._layer = layer
        

        
    # def id(self):
    #     return self._id 
    # def setId(self, id):
    #     self._id = id
        
    # # def mouseMoveEvent(self, event):
    # #     print('CUITEM.MOUSEMOVEEVENT:')
    # #     self.updateRtree()
    # #     self.setSceneBuffer()
    # #     self.setTerminals()
    # #     self.setSceneBounds()
    # #     super().mouseMoveEvent(event)
    
    # def bounds(self): 
    #     return self._bounds
    # def setBounds(self): # UNBUFFERED bounds. Local position. Used for .... ? 
    #     rect =self.boundingRect()
    #     self._bounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 

    # def sceneBounds(self):
    #     return self._sceneBounds
    # def setSceneBounds(self):
    #     rect =self.mapToScene(self.boundingRect()).boundingRect()
    #     self._sceneBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 
        
    # def buffer(self):
    #     return self._buffer
    # def setBuffer(self):#, bufferDistance = None): 
    #     # if self._bufferDistance is None : 
    #     #     if self.scene() is None: 
    #     #         raise ValueError(f"Item needs a scene to know the scene's current traceWidth for self._bufferDistanceing but item has no scene")
    #     #     self._bufferDistance = self.scene().traceWidth()
            
    #     stroker = QPainterPathStroker()
    #     stroker.setWidth(self._bufferDistance)
    #     stroker.setJoinStyle(Qt.BevelJoin) # ry roundJoin for irl
    #     stroker.setCapStyle(Qt.FlatCap)
        
    #     path = self.shape() 
    #     path.closeSubpath() # Often, .shape() -> an unclosed shape
    #     strokerPath = stroker.createStroke(path)
    #     expandedPath = path.united(strokerPath) #Unite the fillable areas of the paths into one consolidated path
    #     self._buffer = expandedPath.toFillPolygon()  # convert to a QPolygonF then to a QGPolygonItem.

    # def sceneBuffer(self):
    #     return self._sceneBuffer
    # def setSceneBuffer(self):
    #     self._sceneBuffer = self.mapToScene(self.buffer())

    # def bufferedBounds(self):
    #     return self._bufferedBounds
    # def setBufferedBounds(self):#, self._bufferDistance=None): # calulate and set new bounds. Bounds describes a bounding rectangle around a shape, in the form of a 4-tuple (xmin ymin xmax ymax), aka (left top right bottom). Bounds is borrowed from how the the python modules Shapely/rtree use bounds; bounds is not from Qt. calculate_bufferedBounds returns the bounds, buffered by self._bufferDistance(most likely = currently selected scene.traceWidth()). The bounds 4-tuple is used bt the rtree module to describe rectangles. Note that, because Qt considers pen_width in .boundingRect, I have to manually set a 0 width pen away from the default width-of-1 pen, else the buffered bounds will be .5 wider than supposed to.
    #     rect = self.boundingRect().adjusted(-self._bufferDistance,-self._bufferDistance, self._bufferDistance,self._bufferDistance)
    #     self._bufferedBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 
    
    # def sceneBufferedBounds(self):
    #     return self._sceneBufferedBounds
    # def setSceneBufferedBounds(self):
    #     rect = self.mapToScene(self.boundingRect().adjusted(-self._bufferDistance,-self._bufferDistance, self._bufferDistance,self._bufferDistance)).boundingRect() # 
    #     self._sceneBufferedBounds = ( rect.left() , rect.top() , rect.right() , rect.bottom() ) 

    # # def terminals(self):
    # #     return self._terminals 
    
    # # def setTerminals(self):
    # #     pass # To be implemented by (Trace,Via,Pad,Zone)Item
    
    # def connectsTo(self, other): # -> True if self is connected to other. Connected as in electrically connected.

    #     if  isinstance(other, CopperItem): 
    #         for t in other.terminals():  # Try cheap check: do terminal exact positions match 
    #             if any(t == t2 for t2 in self.terminals()): 
    #                 return True 
    #         for t in other.terminals(): # Try cheap-ish check: does shape contain termianal
    #             if self.contains(t): 
    #                 return True
    #         if self.collidesWithItem(other): # Try expensive check: do shapes collide at all
    #             return True 
    #         else: 
    #             return False 
            
    #     # elif isinstance(other, QPoint): # idt this is used
    #     #     if any( t == other for t in self.terminals() ): # Initial fast check to see if terminals perfectly align
    #     #         return True 
    #     #     elif self.contains(other): # (low cost?) check to see if point is within other
    #     #         return True 
    #     #     # elif self.collidesWithItem No such thing as cWI for a point
            
    #     else: 
    #         print('MW.connectsTo() SOMETHING WRONG ')
            
    # def setTerminals(self): # Note this only works if items are built with origin also being spot where connections snap to (aka build pads w/ origin @ center as per usual -- This is NOT common practice so ditch it)
    #     #pad: 
    #     self._terminals = [] # clear existing
    #     # Get centers(self.terminals bc pads can be irregular, think solder bridge pads which can look like a v-shape)
        
    #     self.terminals().append(item.terminal())
    #             break # Break out the for loop ; consider only the first pad_item, as all pad_items should share the same terminal
    #             # terminal = terminal( item.childItems()[0].mapToScene(item.boundingRect()).boundingRect() )# Pick out just one childItem to get self.terminals(in scene coords), self.terminals should all be equal

    #     # # Trace.update_terminals
    #     # p1,p2 =  ( self.line().p1() , self.line().p2() )  # TraceItems have one child, QGraphicsLineItem, which draws the trace
    #     # if p1 != p2:
    #     #     self.terminals = [p1,p2]
        
    #     # # Via.update_terminals
    #     # self.terminals = [self.center()]
        

# Default pen is black w/ stroke_width='1'. Lets use a stroke width of 0(aka 'cosmetic' 'hairline' pen)
# layer_colors = {
# None            : Qt.black , 
# 'F.Cu'          : Qt.red,
# 'B.Cu'          : Qt.blue,
# 'F.CrtYd'       : Qt.magenta , # 
# 'B.CrtYd'       : Qt.darkMagenta ,
# 'F.Fab'         : Qt.gray, 
# 'B.Fab'         : Qt.darkGray,
# 'F.SilkS'       : QColor(50,100,100, 1),
# 'B.SilkS'       : Qt.darkYellow,
# 'F.Mask'		: Qt.darkGreen,
# 'B.Mask'		: Qt.green,
# 'F.Paste'		: Qt.darkRed,
# 'B.Paste'		: Qt.darkBlue,
# }
             

### MONKEYPATCHING FUNCTIONS
## MONKEYPATCH: Assign the following functions and attributes to QGraphics(Rect, Polygon, Ellipse, Line)Items, WITHOUT modifying the source code: a monkeypatch
#Monkeypatching a method onto a class will give access to self, if you monkeypatch correctly; if you instantiate the instance AFTER adding the function to the class: A.func=func a=A() a.func Is now a bound function
    # Tricky: We aren't inside a class, so why did we name the first variable self? A: bc this function is intended for monkeypatching. monkeypatching will turn this function to a bound function; a method, which will indeed have access to self.

# MONKEYPATCH: Assign the following functions and attributes to QGraphics(Rect, Polygon, Ellipse, Line)Items 


# NOTE if we are a pad, via, or trace, then self IS the pad, via, or trace item
# NOTE .pads .vias .self.terminals are for FootprintItems and 
# NOTE Zones would likely be a rect or polygon or path item)

#TODO:  pad_item , layer_items, ... 

# QGraphicsProxyWidget.is_design_item         =None

# ### QGRAPHICSRECTITEM
# QGraphicsRectItem.layer_items                =None 
# QGraphicsRectItem.is_design_item             =None # Indicate whether you want this to be a design item: go into rtree, have an id, etc. Should be set for traces, pads, vias, zones, footprints. Should not be set for grid dots, plain QGLineItems, plain QGRectItems, etc.
# QGraphicsRectItem.layer                      =None
# QGraphicsRectItem.net                        =None
# QGraphicsRectItem.id                         =None
# QGraphicsRectItem.layers                     =None
# QGraphicsRectItem.reference                  =None
# QGraphicsRectItem.value                      =None
# QGraphicsRectItem.reference_item       =None
# QGraphicsRectItem.name                       =None
# QGraphicsRectItem.name_item                  =None
# QGraphicsRectItem.file                       =None
# QGraphicsRectItem.number                     =None
# QGraphicsRectItem.number_item                =None
# QGraphicsRectItem.pad_item                   =None 
# QGraphicsRectItem.via_item                   =None 
# QGraphicsRectItem.trace_item                 =None
# QGraphicsRectItem._buffer                    =None
# QGraphicsRectItem.buffer                     =CopperItemContainer.buffer
# QGraphicsRectItem.calculate_buffer                 =CopperItemContainer.setBuffer
# # .layer_items
# # ._bufferedBounds
# # ._bounds


# QGraphicsRectItem.bounds                     =lambda:None

# QGraphicsRectItem.pads                       =lambda:None
# QGraphicsRectItem.vias                       =lambda:None 
# QGraphicsRectItem.connected                  =lambda:None

# # .isDesignItem ?

# ###QGRAPHICSELLIPSEITEM
# QGraphicsEllipseItem.layer_items =None
# QGraphicsEllipseItem.is_design_item                     =None
# QGraphicsEllipseItem.layer                      =None
# QGraphicsEllipseItem.net                        =None
# QGraphicsEllipseItem.id                         =None
# QGraphicsEllipseItem.layers                     =None
# QGraphicsEllipseItem.reference                  =None
# QGraphicsEllipseItem.value                      =None
# QGraphicsEllipseItem.reference_item       =None
# QGraphicsEllipseItem.name                       =None
# QGraphicsEllipseItem.name_item                  =None
# QGraphicsEllipseItem.file                       =None
# QGraphicsEllipseItem.number                     =None
# QGraphicsEllipseItem.number_item                =None
# QGraphicsEllipseItem.pad_item                   =None
# QGraphicsEllipseItem.via_item                   =None
# QGraphicsEllipseItem.trace_item                 =None
# QGraphicsEllipseItem._buffer                    =None
# QGraphicsEllipseItem.calculate_buffer                 =CopperItemContainer.setBuffer
# QGraphicsEllipseItem.pads                       =lambda:None
# QGraphicsEllipseItem.calculate_bounds           = CopperItemContainer.setBounds
# QGraphicsEllipseItem.bounds                     =lambda:None

# QGraphicsEllipseItem.vias                       =lambda:None 
# QGraphicsEllipseItem.connected                  =lambda:None

# ###QGRAPHICSPOLYGONITEM
# QGraphicsPolygonItem.layer_items =None
# QGraphicsPolygonItem.is_design_item             =None
# QGraphicsPolygonItem.layer                      =None
# QGraphicsPolygonItem.net                        =None
# QGraphicsPolygonItem.id                         =None
# QGraphicsPolygonItem.layers                     =None
# QGraphicsPolygonItem.reference                  =None
# QGraphicsPolygonItem.value                      =None
# QGraphicsPolygonItem.reference_item       =None
# QGraphicsPolygonItem.name                       =None
# QGraphicsPolygonItem.name_item                  =None
# QGraphicsPolygonItem.file                       =None
# QGraphicsPolygonItem.number                     =None
# QGraphicsPolygonItem.number_item                =None
# QGraphicsPolygonItem.pad_item                   =None
# QGraphicsPolygonItem.via_item                   =None
# QGraphicsPolygonItem.trace_item                 =None
# QGraphicsPolygonItem._buffer                    =None
# QGraphicsPolygonItem.calculate_buffer                 =CopperItemContainer.setBuffer
# QGraphicsPolygonItem.pads                       =lambda:None
# QGraphicsPolygonItem.vias                       =lambda:None 
# QGraphicsPolygonItem.connected                  =lambda:None
# QGraphicsPolygonItem.bounds                     =lambda:None


# ###QGRAPHICSLINEITEM
# QGraphicsLineItem.layer_items =None
# QGraphicsLineItem.is_design_item             =None
# QGraphicsLineItem.layer                      =None
# QGraphicsLineItem.net                        =None
# QGraphicsLineItem.id                         =None
# # QGraphicsLineItem.layers                     =None
# QGraphicsLineItem.reference                  =None
# QGraphicsLineItem.value                      =None
# QGraphicsLineItem.reference_item       =None
# QGraphicsLineItem.name                       =None
# QGraphicsLineItem.name_item                  =None
# QGraphicsLineItem.file                       =None
# QGraphicsLineItem.number                     =None
# QGraphicsLineItem.number_item                =None
# QGraphicsLineItem.pad_item                   =None
# QGraphicsLineItem.via_item                   =None
# QGraphicsLineItem.trace_item                 =None
# QGraphicsLineItem._buffer                    =None
# QGraphicsLineItem.calculate_buffer                 =CopperItemContainer.setBuffer
# QGraphicsLineItem.pads                       =lambda:None
# QGraphicsLineItem.vias                       =lambda:None 
# QGraphicsLineItem.connected                  =lambda:None
# # QGraphicsLineItem.bounds                     =lambda:None


# ###QGRAPHICSPATHTEM
# QGraphicsSimpleTextItem.layer_items =None
# QGraphicsPathItem.is_design_item             =None
# QGraphicsPathItem.layer                      =None
# QGraphicsPathItem.net                        =None
# QGraphicsPathItem.id                         =None
# QGraphicsPathItem.layers                     =None
# QGraphicsPathItem.reference                  =None
# QGraphicsPathItem.value                      =None
# QGraphicsPathItem.reference_item       =None
# QGraphicsPathItem.name                       =None
# QGraphicsPathItem.name_item                  =None
# QGraphicsPathItem.file                       =None
# QGraphicsPathItem.number                     =None
# QGraphicsPathItem.number_item                =None
# QGraphicsPathItem.pad_item                   =None
# QGraphicsPathItem.via_item                   =None
# QGraphicsPathItem.trace_item                 =None
# QGraphicsPathItem._buffer                    =None
# QGraphicsPathItem.calculate_buffer                 =CopperItemContainer.setBuffer
# QGraphicsPathItem.pads                       =lambda:None
# QGraphicsPathItem.vias                       =lambda:None 
# QGraphicsPathItem.connected                  =lambda:None
# QGraphicsPathItem.bounds                     =lambda:None


# ###QGRAPHICSSIMPLETEXTTEM
# QGraphicsSimpleTextItem.layer_items =None
# QGraphicsSimpleTextItem.is_design_item                     =None
# QGraphicsSimpleTextItem.layer                              =None
# QGraphicsSimpleTextItem.net                                =None
# QGraphicsSimpleTextItem.id                                 =None
# QGraphicsSimpleTextItem.layers                             =None
# QGraphicsSimpleTextItem.reference                          =None
# QGraphicsSimpleTextItem.value                              =None
# QGraphicsSimpleTextItem.reference_item               =None
# QGraphicsSimpleTextItem.name                               =None
# QGraphicsSimpleTextItem.name_item                          =None
# QGraphicsSimpleTextItem.file                               =None
# QGraphicsSimpleTextItem.number                             =None
# QGraphicsSimpleTextItem.number_item                        =None
# QGraphicsSimpleTextItem.pad_item                           =None
# QGraphicsSimpleTextItem.via_item                           =None
# QGraphicsSimpleTextItem.trace_item                         =None
# QGraphicsSimpleTextItem._buffer                            =None
# QGraphicsSimpleTextItem.calculate_buffer                 =CopperItemContainer.setBuffer
# QGraphicsSimpleTextItem.pads                               =lambda:None
# QGraphicsSimpleTextItem.vias                               =lambda:None 
# QGraphicsSimpleTextItem.connected                          =lambda:None
# QGraphicsSimpleTextItem.bounds                             =lambda:None


# OK, now we can call QRectF.buffer(10) etc without getting 'Error: method or attribute DNE'. Hooray! 
# Note that the PySide6 source code hasn't been changed, but, w/ this monkeypatch, we can act like it was. 


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

