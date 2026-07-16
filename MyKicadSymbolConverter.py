from utils import *


# I SHOULD PROBALY REWRITE THIS SO THAT IT SKIPS CONVERSION INTO A LIST AND JUST GOES FROM SEXPR -> UNPROCESSEDXML -> XML. But if it aint broke...
# This takes a .kicad_sym file and turns it into a .sym file
class MyKicadSymbolConverter(): # Convert .kicad_sym objects into .xml objects. 
    
    # LIBRARY as in a .kicad_sym file, which the KiCad Docs call a 'library'. library = a .kicad_sym file. Kicad uses 's-expression' file formats
    # LIBRARY_ID as in a kicad symbol stored in a kicad library.  kicad Docs call 'library_id' I might call library_id. 
    # def __init__(self, "Devices.kicad_sym", "C_Small")  For Example
    
    def __init__(self, library_path): 
        if not os.path.exists(library_path):  # Verify library_path exists
            raise FileNotFoundError(f"SELF.LIBRARY_PATH: {library_path} DOES NOT EXIST")
        self.library_path = library_path
        self.symbol_list = self.to_list()
        
    @classmethod
    def convert(cls, library_path, categories):
        c = cls(library_path) # Create instance
        if c.symbol_to_xml(): # Convert this library_id to xml
            c.format_graphics()  # Acts on self.sym and formats that xml. Format before saving
            file_path = c.save(categories) # Save .sym file # Not 'categories' are not known by the file.
        return file_path # Return path of newly saved .sym file
    # Usage 
    # new_file = MyKicadSymbolConverter.convert(library_path)

        
        
        
    def to_list(self):
        with open(self.library_path) as fo: #fo as in libraryObject
            lines = fo.readlines()
            for idx in range(len(lines)):
                lines[idx] = re.sub(r'\n+', '', lines[idx]) #Remove the OG newlines, as they are poorly placed. Alt use line = line.rstrip('\n')
        sexpr_list = sexpdata.loads(''.join(lines)) # # sexpr as in s-expression, the lousy library standard KiCad borrowed from (Some industrial company) which is a bad choice to store data, period. HTML or XML are easier to work with 
        symbol_list = sexpr_list[3:] # remove sexpr headers
        return symbol_list # sexpr file, serialized to list, with headers chopped off, so its a list of the symbols
        
    def symbol_to_xml(self, library_id=None ):
        if library_id == None: 
            _ , lib = os.path.split(self.library_path)
            lib, ext = os.path.splitext(lib)
            library_id = lib
        self.library_id = library_id
        # print('SELF.LIBRARY_ID:', self.library_id)
        
        for symbol in self.symbol_list: 
            lib_id = symbol[1]
            lib_id_normalized = normalize(lib_id) 
            library_id_normalized = normalize(self.library_id) # DONT FORGET TO NORMALIZE THE STRINGS BEFORE COMPARING
            
            if lib_id_normalized == library_id_normalized: 
                # print('LIBRARY_ID MATCHES, PROCESSING SYMBOL')
                # print('SYMBOL:', symbol)
                self.kicad_sym = self.recurse(symbol) # recurse on symbol, and turn it into an etree.Element
                # print("SELF.KICAD_SYM:")
                # print(etree.tostring(self.kicad_sym, pretty_print =True, encoding = str))
                return True
        # print(f'COULD NOT FIND LIBRARY_ID {self.library_id} IN LIBRARY: {self.library_path}')
        return False
    
    def save(self, categories=['']):
        # print('SAVING')
        folder =  os.path.join(symbols_path, *categories ) # symbols/capacitors/ceramic_capacitors or whatever
        # print()
        # print('FOLDER:', folder)
        ext = '.sym'
        file_path = os.path.join(folder, self.library_id + ext) 
        
        # print()
        # print(f"SAVING LIBRARY_ID:{self.library_id} TO SAVE_PATH {file_path}:")
        print(self.kicad_sym)
        
        if not os.path.exists(folder): # If folder DNE, create folder
            os.makedirs(folder)
        if not os.path.exists(file_path): # If file DNE, create file
            with open(file_path, 'x') as fo: # 'x' mode is for writing to a new file
                fo.write(etree.tostring(self.sym, encoding=str,pretty_print=True))
        else:
            # print(f'THIS FILE ALREADY EXISTS: OVERWRITING: {file_path}')
            with open(file_path, 'w') as fo: # 'w' mode for writing to a file
                fo.write(etree.tostring(self.sym, encoding=str,pretty_print=True))
        return file_path
#  [Symbol('symbol'), 'STM32', [Symbol('in_bom'), Symbol('yes')], [Symbol('on_board'), Symbol('yes')], [Symbol('property'), 'MPN', 'CL10B475KQ8NQNC', [Symbol('at'), 0, 6, 0], [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]], Symbol('hide')]], [Symbol('property'), 'symbol_name', '47uF_63V_1608m', [Symbol('at'), 0, 8, 0], [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]]]], [Symbol('property'), 'Category', 'Capacitors', [Symbol('at'), 0, 10, 0], [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]], Symbol('hide')]], [Symbol('property'), 'Package / Case', '0603 [1608 Metric]', [Symbol('at'), 0, 12, 0], [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]], Symbol('hide')]], [Symbol('property'), 'Capacitance', '4.7uF', [Symbol('at'), 0, 14, 0], [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]], Symbol('hide')]], [Symbol('symbol'), 'STM32_0_1', [Symbol('polyline'), [Symbol('pts'), [Symbol('xy'), -1.524, -0.508], [Symbol('xy'), 1.524, -0.508]], [Symbol('stroke'), [Symbol('width'), 0.3302], [Symbol('type'), Symbol('default')]], [Symbol('fill'), [Symbol('type'), Symbol('none')]]], [Symbol('polyline'), [Symbol('pts'), [Symbol('xy'), -1.524, 0.508], [Symbol('xy'), 1.524, 0.508]], [Symbol('stroke'), [Symbol('width'), 0.3048], [Symbol('type'), Symbol('default')]], [Symbol('fill'), [Symbol('type'), Symbol('none')]]]], [Symbol('symbol'), 'STM32_1_1', [Symbol('pin'), Symbol('passive'), Symbol('line'), [Symbol('at'), 0, -2.54, 90], [Symbol('length'), 2.032], [Symbol('name'), '~', [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]]]], [Symbol('number'), '', [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]], Symbol('hide')]]], [Symbol('pin'), Symbol('passive'), Symbol('line'), [Symbol('at'), 0, 2.54, 270], [Symbol('length'), 2.032], [Symbol('name'), '~', [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]]]], [Symbol('number'), '', [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]]]]]]]
    
    @staticmethod
    def random(boundary):
        return QRandomGenerator.global_().bounded(boundary)

    def recurse(self, lst, parent=None, library_id=None, unit_id=None): # lst: an except from a kicad file; the symbol part.(Not the whole file-- delete file headers and pass only one symbol) converted to xml, we foundin this kicad_sym file
        
        def xml_attribute_name_filter(string):
            string = re.sub('/', '_', string) #Substitute fwd slash for underscore _
            string = re.sub(r'\s+', '', string).strip() #remove all whitespace
            return string.lower() #  For column names, since we have underscores not spaces, I prefer all lowercase 'like_this' 'Instead_of_this'


        def xml_attribute_value_filter(string):
            string = re.sub('/', '_', string) #Substitute fwd slash for underscore _
            string = re.sub(r'\s+', '', string).strip() #remove all whitespace
            return string 
        
        def rootmost(lst):
            root = etree.Element('Symbol')
            root.set('KiConverted', 'True')
            return root 
        
        child = None 
        strs = []
        nesteds =[]
        values=[]
        keys = []
        # print()
        token = lst.pop(0).value() # In kicad_sym, first thing in list is ALWAYS a symbol
        # print('TOKEN:', token)
        # print('TYPE(TOKEN)', type(token))
        # if etree.iselement(parent): # If we don't have a library_id, make one
        #     print()
        #     print('PARENT', parent.tag)
        
        if token== 'symbol': # We need to distinguish LIBRARY_ID from UNIT_ID intra-symbol, AND we need to treat different symbols as... different symbols; in one .kicad_sym file, there may be one, or a hundred, symbols.  KiCad only supports two body styles so the only valid values for the "STYLE" are 1 and 2. A "UNIT" value of zero (0) indicates that the symbol is common to all units
            if not etree.iselement(parent): # If we don't have a library_id, make one
                library_id = lst.pop(0) # Pop so it cannot be processed again
                parent = etree.Element("Symbol", name=library_id) # Store name in attribs, NOT as the tag, since some strings are invalid as tag names, like 3capacitor bc it starts with a number. 
                # print('NEW LIBRARY_ID:', library_id)
            elif library_id != lst[0][:len(library_id)]: # If library_id isn't present in lst[0], then we are on a new library_id; a new symbol. #Save existing parent, then overwrite. (ATM WE ONLY SELECT ONE TOKEN SO THIS SHOULDN"T MATTER)
                # print("This loop shouldn't enter")
                unit_id = None #clear the unit_id
                library_id = lst.pop(0) # Pop so it cannot be processed again
                parent = etree.Element(library_id) 
                # print()
                # print('NEW LIBRARY_ID:', library_id)
            elif library_id == lst[0][:len(library_id)]: # if  this is a UNIT_ID...
                unit_id = lst.pop(0) # Check 0, if its unit_id then pop it
                unit = unit_id[len(library_id) +1] 
                style = unit_id[len(library_id)+3]
                # print('UNIT_ID:', unit_id, "UNIT", unit, "STYLE", style)
                child = etree.SubElement(parent, 'graphic', library_id=library_id, unit=unit, style=style)
                # child = etree.Element('graphic', library_id = library_id, unit =unit, style=style)
                # parent.append(child)
                # and now, I need to append onto child while we are in this unit...
                # WHich means I need to track unit... 
                # No I think its ok                
        for i in lst: # Lets glance at our data before we start mutating. NOTE: sexpdata.Symbol()==string evaluates True AS DOES Symbol()==str; must check for sexpdata.Symbol first, then str
            if isinstance(i, (float,int, sexpdata.Symbol)): # floatintSymbol indicate values. Must be paired with keys  NOTE: I manually delete indices from the kiDocs which occupy positional values, which I do not support ( 'at' token, POSITIONAL IDENTIFIER)
                if isinstance(i, sexpdata.Symbol):
                    i = i.value()
                values.append(i) 
            elif isinstance(i, str):
                strs.append(i)
            elif isinstance(i, list):
                sub_token = i[0].value() # a nested token. Add i to nesteds if we support the token or if i is an 'at' sexpr under 'pin'
                if ( sub_token in ns_tokens ) : 
                    pass # continue: skip the current iteration
                elif sub_token == 'at' and token != 'pin': 
                    pass
                elif sub_token == 'at' and token == 'pin': 
                    nesteds.append(i)
                else: 
                    nesteds.append(i)

        len_strs =len(strs)
        len_values = len(values)
        # print()
        # print('TOKEN:', token)
        # print('NESTEDS', nesteds)
        # print('STRS', strs)
        # print('PARENT.TAG', parent.tag)
            
    #ADD CHILDREN# sexprs with all values or nesteds, BOTH need to be a subelement (not attrib) # <pin> is generated with two attributes bc pin has both KEYS and nesteds
        if nesteds:                
            if not etree.iselement(child):
                # child = etree.Element(token) # Don't want to make a child element when token == symbol...
                # parent.append(child)
                child = etree.SubElement(parent, token)
            for grandkid in nesteds:
                # print('GRANDKID:', grandkid)
                self.recurse(grandkid, child, library_id, unit_id)

#HANDLE STRS
# I popped any handled strings, so only unhandled strings are left
        if len_strs==1: # 'name': 'PA0'
            parent.set(xml_attribute_name_filter(token), xml_attribute_value_filter(strs[0]))
            # return parent
        
        if len_strs == 2: # This condition occurs for 'property' tokens and others [ property "Reference" "U" ]
            if token != 'property':  # I WANT to loose the kicad'properties' as they are better suited as PART attributes
                parent.set(xml_attribute_name_filter(strs[0]), xml_attribute_value_filter(strs[1]))
            # return parent # I think return is all thats needed here, to terminate looking deeper, don't think 'parent' is used? 

    #HANDLE KEY:VALUE
    # float, int, non- 'symbol' sexpdata.Symbols become values 
        if len_values==1:
            parent.set(token, str(values[0])) # NOTE: xml element attrib vlaues must be cast to str before being  .set()
            # return parent
        
        elif len_values > 1: # We need to make k:v pairs [ xy X 4 Y 8 ] 
            keys = get_keys(token) # -> None|[empty]|[full]

            if not keys:
                pass# If we can't get keys, there's no point in processing this sexpr 
            elif keys: # sexprs with all values, ALSO need to be a subelement (not attrib) 
                # print('GOT KEYS:', keys)
                # If sexpr has values, it shouldn't have any (supported) nesteds, so 
                if not etree.iselement(child): 
                    child = etree.Element(token) # <xy X=1.0 Y=2.0>
                    parent.append(child) # <xy> onto <polyline>
                z = list(zip(keys, values)) 
                # print('ZIP:', list(z))
                for i in z: 
                    child.set(str(i[0]),str(i[1])) # <xy X=1.0 Y=2.0> #NOTE: xml attribute X=10.1 is a float; must be set as a string.
        return parent 

     
    def format_graphics(self):  # Run first time to format how I like , b4 saving as xml
        pins = []
        polylines = []
        rectangles=[]
                                # KI_SYM:
                                # <STM32C092RBT6>
                                #   <symbol reference="U" ki_fp_filters="LQFP64_STMLQFP64_STM-MLQFP64_STM-L">
                                #     <graphic library_id="STM32C092RBT6" unit="1" style="1">
                                #       <polyline>
                                #         <pts>
                                #           <xy X="7.62" Y="5.08"/>
                                #           <xy X="7.62" Y="-43.18"/>
                                #         </pts>
                                #       </polyline>

        self.sym = etree.Element(self.kicad_sym.tag, self.kicad_sym.attrib) # copy self.kicad_sym to self.sym
        self.sym.text = self.kicad_sym.text #Copy text too
    # Grab attributes from nested 'symbol' element, set them as attributes on the root level 'library_id'(eg STM32t6) elements
        symbol = self.kicad_sym.find('symbol') 
        if symbol is not None: 
            for k,v in symbol.items():
                self.sym.set(k,v)
    
        for graphic_elem in self.kicad_sym.iterdescendants("graphic"): 
            # graphic= etree.SubElement(self.sym, graphic_elem.tag, graphic_elem.attrib)
            # graphic.text = graphic_elem.text
            self.graphic = etree.SubElement(self.sym, 'graphic', unit = graphic_elem.get('unit'), style= graphic_elem.get('style'))
            self.format_pins(graphic_elem)
            self.format_polylines(graphic_elem)
            self.format_rectangles(graphic_elem )
        # print('FORMATTED XML:')
        return etree.tostring(self.sym , encoding = str, pretty_print=True)
            
    def format_pins(self, graphic_elem): #Format pins how I want pins formatted 
        # print()
        # print('FORMAT_PINS:')
        pins = graphic_elem.findall('pin') # use findall not .iterdescendants, bc we later use .sorted(), which likes lists;iterables,  not iterators
        for pin_elem in pins: 
            at = list(pin_elem.iterdescendants('at'))[0]
            # print()
            # print('AT', at )
            x1,y1,angle = list(map( float, [at.get('X'), at.get('Y'), at.get('ANGLE')] ))
            number, name, PIN_ELECTRICAL_TYPE, PIN_GRAPHIC_STYLE, length = pin_elem.get('number'), pin_elem.get('name'), pin_elem.get('PIN_ELECTRICAL_TYPE'), pin_elem.get('PIN_GRAPHIC_STYLE'), float(pin_elem.get('length'))

            # print('X1:', x1) # One "mil" = One "thou" = .001"
            angle_rad = angle/180.0 * math.pi
            x2 = x1 + math.cos(angle_rad)*length
            y2 = y1 + math.sin(angle_rad)*length
            for k,v in (('x1', x1) , ('y1', y1), ('x2', x2), ('y2',y2)): 
                pin_elem.set(k,str(v)) # add new variables to the pin_elem element
            pin_elem.remove(at)# remove the 'at' element. We don't need it anymore
            if 'length' in pin_elem.attrib: # delete the 'length' attribute. We don't need it anymore. (del bc 'length' is attrib not element)
                del pin_elem.attrib['length']
        pins = sorted(pins, key = lambda pin_elem : ( float(pin_elem.get('x1')) , float(pin_elem.get('y1')) ) ) # SORT pins by 'x1', then 'y1'. Note: sorted(iterable) is CORRECT while sorted(iterator) is WRONG
        # print('SORTED_PINS: ', pins)
        for pin_elem in pins: 
            etree.SubElement(self.graphic, pin_elem.tag, pin_elem.attrib) # PARENTED ON self.graphic NOT self.sym 

#   <rectangle>
#     <start X="-20.32" Y="-20.32"/>    # bottom left
#     <end x="20.32" y="20.32"/>        # top right ( This format is BAD for qt. We want topLeft, btmRight, which we can achieve with the QRectF.normalize() function). Also not that startXY is capital while endxy is lowercase, wtf
#   </rectangle>

    def format_rectangles(self, graphic_elem):
        # rectangle_elems = graphic_elem.findall('.//rectangle')
        rectangle_elems = graphic_elem.iterdescendants('rectangle')
        for rectangle_elem in rectangle_elems: 
            # start_elem = rectangle_elem.find('.//start')
            start_elem = list(rectangle_elem.iterdescendants('start'))[0]
            p1 = (float(start_elem.get('X')) , float(start_elem.get('Y')))
            # end_elem = rectangle_elem.find('.//end')
            end_elem = list(rectangle_elem.iterdescendants('end'))[0]
            p2 = float(end_elem.get('x')) , float(end_elem.get('y')) # CAPITALIZATION. In one file I go from digikey, the (rectangle) symbols' start XY were capital, while the rectangles (end xy) were lowercase 
            rectangle_elem.remove(start_elem) # Not sure will work if using .iterdescendants vs.findall
            rectangle_elem.remove(end_elem)
            
            normalized = QRectF(QPointF(*p1),QPointF(*p2)).normalized()# We gotta .normalize our rectangle,  to get with QT's lingo, Must provide (topLeft, btmRight) to our qrectf
            rectangle_elem.set('topLeft', str(normalized.topLeft()))
            rectangle_elem.set('bottomRight', str(normalized.bottomRight()))
            
            # etree.SubElement(self.sym, rectangle_elem.tag, rectangle_elem.attrib)
            etree.SubElement(self.graphic, rectangle_elem.tag, rectangle_elem.attrib)
        # return rectangle_elems
        
    def format_polylines(self, graphic_elem):
        polylines = graphic_elem.findall('polyline')
        for polyline_elem in polylines:
            # print('ADDING POLYLINE', polyline_elem)
            points = polyline_elem.findall('.//xy')
            # points_list = []
            points_str= ""
            for point in points:
                points_str += point.get("X") +"," + point.get("Y") + " "
            points_str = points_str.strip() # Remove the trailing whitespace
            # print( "GENERATED POINTS_STR:", points_str)
            # etree.SubElement(self.sym, polyline_elem.tag , polyline_elem.attrib,  points=points_str) # ex <polyline points="0,1 3,4 5,8". This is how SVGs do it.
            etree.SubElement(self.graphic, polyline_elem.tag , polyline_elem.attrib,  points=points_str) # ex <polyline points="0,1 3,4 5,8". This is how SVGs do it.
            # print('POINTS_LIST', points_list)

### TESTING ###
# # library_path = os.path.join('third_party', 'kicad', 'symbols','GRM21BR61E106KA73L.kicad_sym')
# library_path = os.path.join('third_party', 'kicad', 'symbols', 'GND.kicad_sym')
# print(library_path)


# # library_path = os.path.join('third_party', 'kicad', 'symbols','MIC33153YHJ_TR.kicad_sym')
# new_file = MyKicadSymbolConverter.convert(library_path)
