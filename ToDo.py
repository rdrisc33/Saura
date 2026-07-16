# worst part of relational tables: their column order is set in stone; before creating the table, you need to already know the columns. Thus, perhaps I should fake it with CSVs until I'm sure of my schema.
# For a given category hierarchy, the columns from digikey's p_d endpoint remain constant.
# Spreadsheet to display my part data 
# Schema for my part data 

# usage: part_obj = part('abc123') # --> query all relational tables related to given mpn: 'SELECT * FROM "{mpn}_general", "{mpn"

# CREATE TABLE {part.mpn}_{general} (categories,
#                                    mpn, 
#                                    vendor_part_page, vendor_pn, price,
#                                    vendor,
#                                    manufacturer) 
# Some columns are from p_a; others I scrape & add. But EVERY part can have these properties. Compare to part_attribute like "capacitance": not every part has a capacitance. 

# Strategy for a Spreadsheet app: 
# Have database. sql csv json plaintext DNM
# User has gotta select a category path. Query database for all parts matching that category, & load those parts into a Qt model. Render that model with a QtView, a TableView. 
# Based on user-selected hides/shows/filters, re-render the model to match user needs.

# Every time a user reselects a category, requery the database, load that data into a model, and refresh the tableView to render new data. 

# ATM the important thing is that Each relational table is associated with its category path. (sql would use foreign keys to do this. Csvs could use keys or just filenames) 
# Table names: 

general             --> 
media               -> 'media' endpoint might have 1 or 10 datasheets... just grab the first, slap it into 'general_attributes'
part                -> Ex 'clockSpeed' an 'capacitance' aren't posessed by all parts 
eda_sw_specific     -> fp, sym, simulation, cad, might change inter-eda sw
pricing             -> needed to show break pricing. unit price can go in 'general_attributes'
meta                -> timestamps, where file came from, last edited, etc.  


# it'd be cool to be able to click/drag columns to freeze columns

#

# Code a > KiCAD EDA app. 
# Design my ESC PCBs in said app 
# Design a PCB workflow. Coated vias. 
# Design a PCBA machine 

# Build pcbs using pcb workflow. Assemble pcbs using pcba workflow 
# Design a robot arm, ROV, mothership drone, biomimetic birds and hand, using my pcba workflow 

# Use csv files to store spreadsheets of parts
    # first row is attr name 
    # second row is attr_group --Actually, want to hide attr_group info, so, it would be better to save it in another table. 
# Save csv files in a folder hierarchy copying DK hierarchy. 
# Ditch .rr and .json for csv. 


