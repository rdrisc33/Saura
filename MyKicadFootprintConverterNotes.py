(footprint "HJDFN3035-14LD-PL-1" 
    (version 20211014)                      #ignore
    (generator pcbnew)                      #ignore

    (layer "F.Cu")                          # ignore
    (tags "MIC33153YHJ-TR ")                # search tags 
    (attr smd)                              # Not even in the Kicad Docs...
    (descr "Description Here")              # Description
    (solder_mask_margin 1.00)               #solder mask distance from ALL pads, defaults to board.solder_mask_margin
    (solder_paste_margin 2.00)              #solder paste distance from ALL pads, defaults to board.solder_paste_margin
    (solder_paste_ratio 2)                  # "defines the percentage of the pad size used to define the solder paste" Huh? 
    (clearance 1.00)                        # clearance between copper objects and pads, defaults to board.clearance
    (zone_connect )                         # type of connection from pads to filled zone. Integer. 0: NC 1: thermal_relief_connection 2: solid_fill_connection
    (thermal_width)                         # width of thermal relief connections. Defaults to zone.thermal_width
    (thermal_gap)                           # distance from pad to thermal relief zone.  Defaults to zone.thermal_gap
    (private_layers)                        # canonical layers 'which are private to this footprint'
    (net_tie_pad_groups)                    # ??? "A space-separated list of quoted strings, each containing a comma-separated list of pad names. Nets attached to pads within a single pad-group are allowed to short."
    GRAPHICS_ITEMS                          # At a minimum, reference designator and value is defined. Additionally,  text, text boxes, lines, rectangles, circles, arcs, polygons, curves, and dimensions, may be defined 
    (fp_text
        TYPE                                                      
        "TEXT"                                                    
        POSITION_IDENTIFIER                                       
        [unlocked]                                                
        (layer LAYER_DEFINITION)                                  
        [hide]                                                    
        (effects TEXT_EFFECTS)              #ignore                                     
        (uuid UUID)                         #ignore                                           
    )
    (fp_text_box                                
        [locked]                                                    
        "TEXT"                                                      
        [(start X Y)]                                               
        [(end X Y)]                                                 
        [(pts (xy X Y) (xy X Y) (xy X Y) (xy X Y))]                 
        [(angle ROTATION)]                                          
        (layer LAYER_DEFINITION)                                    
        (uuid UUID)                                                 
        TEXT_EFFECTS                                                
        [STROKE_DEFINITION]                                         
        [(render_cache RENDER_CACHE)]                               
    )
    (fp_line
        (start X Y)                                               
        (end X Y)                                                 
        (layer LAYER_DEFINITION)                                  
        (width WIDTH)                                             
        STROKE_DEFINITION                                         
        [(locked)]                                                
        (uuid UUID)                                               
    )
   (fp_rect
        (start X Y)                                               
        (end X Y)                                                 
        (layer LAYER_DEFINITION)                                  
        (width WIDTH)                                             
        STROKE_DEFINITION                                         
        [(fill yes | no)]                                         
        [(locked)]                                                
        (uuid UUID)                                               
    )
    (fp_circle
        (center X Y)                                              
        (end X Y)                                                 
        (layer LAYER_DEFINITION)                                  
        (width WIDTH)                                             
        STROKE_DEFINITION                                         
        [(fill yes | no)]                                         
        [(locked)]                                                
        (uuid UUID)                                               
    )
    (fp_arc
        (start X Y)                                               
        (mid X Y)                                                 
        (end X Y)                                                 
        (layer LAYER_DEFINITION)                                  
        (width WIDTH)                                             
        STROKE_DEFINITION                                         
        [(locked)]                                                
        (uuid UUID)                                               
    )
    (fp_poly                           # Polygon
        (pts
            (xy X Y)                                                    
            ...
            (xy X Y)
        )        
        (layer LAYER_DEFINITION)                                  
        (width WIDTH)                   #prior to v7
        STROKE_DEFINITION               #post v7                              
        [(fill yes | no)]               # default no                         
        [(locked)]                                       
        (uuid UUID)                                               
    )
    (fp_curve                           # Ignore. defines a cubic Bezier
        COORDINATE_POINT_LIST                                     
        (layer LAYER_DEFINITION)                                  
        (width WIDTH)                                             
        STROKE_DEFINITION                                         
        [(locked)]                                                
        (uuid UUID)                                               
    )
    
    (pad                                    # list of all pads 
        "NUMBER"                                                  
        TYPE                                #thru_hole, smd, connect, or np_thru_hole.                              
        SHAPE                               #circle, rect, oval, trapezoid, roundrect, or custom.                                           
        (at
            X                                                           
            Y                                                           
            [ANGLE]                                                     
        )        
        [(locked)]                                                
        (size X Y)                                                
        [(drill DRILL_DEFINITION)]                                
        (layers "CANONICAL_LAYER_LIST")                           
        [(property PROPERTY)]                                     
        [(remove_unused_layer)]                                   
        [(keep_end_layers)]                                       
        [(roundrect_rratio RATIO)]                                
        [(chamfer_ratio RATIO)]                                   
        [(chamfer CORNER_LIST)]                                   
        (net NUMBER "NAME")                                       
        (uuid UUID)                                               
        [(pinfunction "PIN_FUNCTION")]                            
        [(pintype "PIN_TYPE")]                                    
        [(die_length LENGTH)]                                     
        [(solder_mask_margin MARGIN)]                             
        [(solder_paste_margin MARGIN)]                            
        [(solder_paste_margin_ratio RATIO)]                       
        [(clearance CLEARANCE)]                                   
        [(zone_connect ZONE)]                                     
        [(thermal_width WIDTH)]                                   
        [(thermal_gap DISTANCE)]                                  
        [CUSTOM_PAD_OPTIONS]                                      
        [CUSTOM_PAD_PRIMITIVES]                                   
    )                                    
    (zone                                 # list of KEEP OUT zones in the fp
        (net NET_NUMBER)                                            
        (net_name "NET_NAME")                                       
        (layer LAYER_DEFINITION)                                    
        (uuid UUID)                                                 
        [(name "NAME")]                                             
        (hatch STYLE PITCH)                                         
        [(priority PRIORITY)]                                       
        (connect_pads [CONNECTION_TYPE] (clearance CLEARANCE))      
        (min_thickness THICKNESS)                                   
        [(filled_areas_thickness no)]                               
        [ZONE_KEEPOUT_SETTINGS]                                     
        ZONE_FILL_SETTINGS                                          
        (polygon COORDINATE_POINT_LIST)                             
        [ZONE_FILL_POLYGONS...]                                     
        [ZONE_FILL_SEGMENTS...]                                     
        )                                   
        (group
        "NAME"                                                      
        (id UUID)                                                   
        (members UUID1 ... UUIDN)                                   
    )                                  
    (model
        "3D_MODEL_FILE"                                           
        (at (xyz X Y Z))                                          
        (scale (xyz X Y Z))                                       
        (rotate (xyz X Y Z))                                      
)

