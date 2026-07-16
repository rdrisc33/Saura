import pickle 
import os 
from utils import * 
from collections import defaultdict
import webbrowser 
from Database import Database
from PySide6.QtCore import Signal, Slot
# part.attributes = MyDigikeyParser(dk_result).attributes
# from MyDatabase import database

class DigikeyParser():
    parsed = Signal(dict)
    
    def __init__(self, dk_result):
        self.dk_result = dk_result

        
    # def to_database(self, attributes ): # Note this is done by MW
    #     #Insert into the 
    #     if not attributes: 
    #         print('SELF.ATTRIBUTES NOT FOUND, DID YOU .parse() YET?')
    #         return
            
    #     database.insert_into_table( attributes) # Insert record into table NOTE GOTTA BE TABLE NAME TODO: change as thats bad_practice
        #     if database.table_name_exists(table_name): # If the table is in database, get that table
        #         table = database.metadata.tables.get(table_name)
        #     else:
        #         columns = database.create_columns_from_attributes(attributes)
        #         table = database.create_table(table_name , columns)
            
        # ALSO INSERT INTO THE SS_FILTERS TABLE (handled by insert_into_table)
        # if database.table_name_exists('ss_filters'):
        #     database.insert_into_table('ss_filters', attributes)
    
    @Slot()
    def parse(self):
        attributes = {}
        
        product_details_attributes = self.product_details_handler(self.dk_result['response_product_details'])
        attributes.update(product_details_attributes)
        
        media_attributes = self.media_handler(self.dk_result['response_media'])
        attributes.update(media_attributes)
        # self.to_database(attributes)
        print()
        print("ATTRIBUTES:", attributes)
        self.attributes=  attributes 
        # self.parsed.emit(self.attributes) 
        return attributes
    
    @classmethod
    def from_pickle(cls, dk_result_pickle):    
        print()
        print('RUNNING FROM_DK_RESULT_PICKLE...')
        head, tail = os.path.split(dk_result_pickle) # Make it work if we give abs path or just filename
        
        path = os.path.join('dk_results', tail)
        with open(path, 'rb') as fo:# Open in ReadBinary, rb, mode 
            dk_result = pickle.load(fo) 
        print()
        print('DK_RESULT:', type(dk_result), dk_result)
        return cls(dk_result)

    def product_details_handler(self, response_product_details): 
        D = response_product_details.get('Product')
        attributes = {}
        
        attributes.update({ 
            'mpn'                   : D.get('ManufacturerProductNumber'),
            'mfr'                   : D.get('Manufacturer').get('Name'),
            'vendor'                : 'Digikey'
        })

        category_specific_attributes = self.get_category_specific_attributes(D) # populate category_specific_attributes
        attributes.update(category_specific_attributes)
        # print()
        # print("CATEGORY_SPECIFIC_ATTRIBUTES:", category_specific_attributes)
        # attributes.update( {'category_specific_attributes' : category_specific_attributes}) # OK: database cannot accept dict as a value. This value is a dict, so do not provide it to the database, EXCLUDE it from part. INstead, include cat_spec_schema, which is a string

        self.category_specific_schema = ','.join(category_specific_attributes)
        # print()
        # print("self.category_specific_schema:", self.category_specific_schema) 
        attributes.update( {'category_specific_schema' : self.category_specific_schema} )# I want this in my ss_tables, NOT in 'part', so make it a instance variable but NOT part of dict. NO. Make it part of dict, then .pop() it when we use it.
        
        print()
        print('D.GET("CATEGORY")', D.get('Category'))
        self.categories = self.populate_categories(D.get("Category"))  # -> list. lists can't go into the database tho
        print("SELF.CATEGORIES:", self.categories) # CATEGORIES: ['connectors, interconnects', 'blade type power connectors', 'blade type power connector assemblies']
        self.reference_designator = reference_designator_map.get(self.categories[0][0], '?') 
        if self.reference_designator == '?' :
            print('COULD NOT GET A reference_designator DESIGNATOR FOR THIS PART')

        # self.table_name = categories[-1] # We can just use the last category as table_name esp to start NO USE FULL CATEGORIES AS TABLE NAME
         #categories:  -> string ( bc list needs to go into csv as str anyway bc commas are seen by csv) ( OK but change the csv delimiter to semicolon; and now we can store lists in csv) (No, save as a list, convert to a string as needed) (Separately, save a 'table_name' attribute as a string)
        print()
        # print("SELF.CATEGORIES:", self.categories)
        self.table_name = normalize_sql_table_name(self.categories)
        # print('SELF.TABLE_NAME', self.table_name)
# CATEGORIES: ['connectors, interconnects', 'barrel connectors', 'barrel connector accessories']
# SELF.TABLE_NAME connectors,_interconnects_barrel_connectors_barrel_connector_accessories
        attributes.update({ 
            'primary_attributes'    : "", # User sets primary_attributes ex 'capacitance,voltage-rated,package/case for capacitors, or 'clock frequency,flash memory,package/case for microcontrollers.
            'symbol'                : "", # User sets symbol
            'footprint'             : "", # User sets footprint
            'package/case'          : category_specific_attributes.get("package/case", None) ,                #DK keeps package/case within 'category_specific_attributes'. Note all smd/tht parts have this attribute, however, DK does sell other stuff that like lenses, which don't have a package/cas attribte
            'datasheet'             : "", # Fetched from the media_endpoint
            'reference_designator'  : self.reference_designator, 
            'unit_price'            : D.get('UnitPrice'),
            'table_name'            : self.table_name,
            'vendor_part_number'    : D.get('ProductVariations')[0].get('DigiKeyProductNumber'),    #Get digikey part number 
            'vendor_part_page'      : D.get('ProductUrl'),
            'standard_pricing'      : str(D.get('ProductVariations')[0].get('StandardPricing')) ,
            'categories'            : ','.join(self.categories),
            } )
        
        return attributes 

    def get_category_specific_attributes(self, D):         # Directly set some self.part attributes, which Digieky has organized under 'Parameters'.
        category_specific_attributes = {}
        # self.part.mpn = D.get('ManufacturerProductNumber')
        # print('fetched mpn: ', self.part.mpn)
        parameters = D.get('Parameters')# [{},{}, ...]  #parameters = [{'ParameterText':'Voltage-Rated', 'ValueText':'16V'... }]
        # print('PARAMETERS', parameters)
        for param in parameters: 
            attribute_name=normalize(param.get("ParameterText"))# key   = 'Voltage - Rated' -> voltage_rated. Package / Case -> package/case
            attribute_value = param.get("ValueText")  # value = '16V' # Needs not be normalized, as long as save file is encoded in 'utf8', utf8 is needed to handle special symbols like 'micro' 'degrees' and 'plusMinus'
            category_specific_attributes.update({ attribute_name: attribute_value})
        return category_specific_attributes 

    # The DK api returns 1+ childcategory, I call 'child_categories'. (maybe I should call descr sub-categories.) This info is found in ['Product']['Category']['Name'] & ['Product']['Category'][ChildCategories']['Name']. There is bogus info idc about, like 'categoryID'; I only want to grab the Name. This function is recursive. Once a child category is entered, the function is called within the child category.
    def populate_categories(self, category_data, categories=[]): # Somehow, 'categories=[capacitors] upon start? 
        print('CATEGORIES: (in populate_categories): ', categories)
        if "Name" in category_data:
            categories.append(normalize(category_data["Name"])) # remember to normalize ! 
        # Recursively search child categories
        if "ChildCategories" in category_data: #DON'T SPELL AS categories BEWARE OF CTRL H! 
            for child in category_data["ChildCategories"]:
                self.populate_categories(child, categories)      # Recursive function to detect all 'ChildCategories'. 
                
        return categories
    
    def media_handler(self, response_media):
        """ pass the requests.response.json() object from the media endpoint -> a dict of attributes. """
        attributes = {}
        media_links = response_media.get("MediaLinks")#  -> [{},{}] 
        
        # Normal dict throws error on attempt to .get() keys which dne. defaultdict adds a key:defaultValue pair, on attempt to .get() keys which dne. You must specify a type for the default value. int->0 str->'' list->[], etc. defaultdicts handy for tracking counter variables. 
        # Initialize defaultdict with int, so it returns default 0. If a key which dne is accessed, a k:v pair will be added w/ default value, instead of throwing an keyError, like a dict would.
        counters= defaultdict(int)
        
        for link in media_links:
            url = link.get('Url') 
            media_type = link.get('MediaType', None )                           # "Datasheets" "EDA Models" return None if 'MediaType' wasn't available  (utility of this questionable?)
            media_type = f"{media_type.replace(' ', '_').lower().rstrip('s')}"  # "datasheet"  "eda_model" 
            counters[media_type] += 1                   # For each "datasheet" or 'eda_model' provided, increment a counter. 
            first_datasheet_flag = False                # Additonal flag still needed bc media endpoint returns 'Datasheets' and 'HTML Datasheets' fields(ugh).
    # Special handling of 'datasheet' and 'eda_model'; these go to 'attributes'. All other data from media endpoint go to 'other_attributes'
            if 'datasheet' in media_type and not first_datasheet_flag:  # Take the first datasheet. (addtl datasheets & 'html_datasheets' will get put in 'otherattributes' if needed )
                attributes.update({'datasheet' : url}) 
                first_datasheet_flag = True
            elif 'eda_model' in media_type:                             # I want 'eda_model' field as DK provides, to go in 'other', yet I want to sfilter out the individual SM/UL sites which it links to
                # Try to grab snapmagic/UL links as their own field. If non-sm/uL links, add links to 'eda_model' field.
                if 'snapeda.com' in url.lower() or 'snapmagic.com' in url.lower():  # The site chnged its name to 'snapmagic' but Digikey still uses the url 'snapeda.com' 
                    attributes.update({"snapmagic" : url})
                    self.snapmagic = url
                elif 'ultralibrarian.com' in url.lower():
                    self.ultralibrarian = url
                    attributes.update({"ultralibrarian" : url})
                else:                                           # I tried to add 'snapmagic' and 'UL' fields, but if 'eda_model' has links to elsewhere, shove those links into 'eda_model' field.
                    if counters[media_type] == 1:               # first 'eda_model' url  gets written
                        attributes['eda_model'] =  url    
                    elif counters[media_type] > 1:              # second+ 'eda_model' urls get appended on top of the first; # I don't want to overwrite 'eda_model' with url, bc there may be 2 'eda_model' fields...
                        attributes['eda_model'] = attributes.get('eda_model', '') + ', ' + url 
            else:                   
                # attributes.update( {f"{media_type}_{counters[media_type]}" : url } )                                # Shove "product_photos" and other useless data into 'other attributes'. WAIT DONT-- This makes a dynamic schema, sql can't tolerate changing shemas. Store addtl media data under 'other_media' column in a json string
                attributes['misc_media'] = attributes.get('misc_media', '') + ', ' + url
                
            media_filter=[ # This is a filter -- I can't know media_schema because it changes so often 
                'datasheet',
                'eda_model',
                'ultralibrarian',
                'snapmagic',
                'misc_media'
                ]
            ordered_attributes = {k:attributes.get(k,'') for k in media_filter}  # ONLY support these four since 
                    
            # for k,v in attributes.items(): 
            #     ordered_attributes.update({k:v})
        print("ORDERED_ATTRIBUTES:", ordered_attributes)

            # ordered_attributes.update({k:v} for k,v in attributes.items() if not any( k == key for key in ordered_attributes.keys()))
        return ordered_attributes

