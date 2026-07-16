from utils import *
from PySide6.QtCore import QObject, Signal, Slot 
import pandas

#sqlalchemy imports
from sqlalchemy import Table, select, insert, update, delete
from sqlalchemy import Column, String, Text, Integer, Float # TEXT( you don't have to supply a length) vs VARCHAR( you have to supply a length and everything crashes if you get it wrong)(use TEXT over VARCHAR; use Text over String in sqlalchemy) 
from sqlalchemy import MetaData, create_engine
from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint, CheckConstraint
from sqlalchemy.exc import IntegrityError 
from urllib.parse import urlparse

class Database(QObject):    
    # create_model_finished = Signal(MyTableModel) # obsolete
    changed = Signal(dict) # part . ONLY 'table_name' field used. 'Changed' bc I want to know anytime anything changes, whether via a sqlUPDATE or sqlINSERT stmt. Also, this signal is used when ss_filters table sqlUPDATES, ex when primary_attributes is set. 
    
    def __init__(self, database_path=database_path):
        super().__init__()
        self.database_path = database_path
        # self.table_name = 'ceramic_capacitors'
        # self.db_path = 'parts/parts.db'
        # self.record = { "mpn":'123abc',  "A": 'a', "B":'b',}
        self.engine = create_engine(f"sqlite:///{self.database_path}")
        self.metadata = MetaData()
                        

        filt_table = Table("ss_filters", self.metadata, *ss_filters_columns, 
                           PrimaryKeyConstraint('table_name'),
        )
        self.metadata.create_all(self.engine) # Create ss_filters table if not exists
        self.metadata.reflect(self.engine) # Load all tables from the database into the metadata object. Call again to load tables newly added to database. Does not remove tables if tables no longer exist in database

    def get_record(self, mpn, table_name, vendor=None, mfr=None): # key: a dict of column_name: column values forcomparison in our where clause; WHERE mpn=='1a' and 'vendor'=='kyocera' etc... 
         # Q: How Do I autoload metadata with all the tables? 
        self.metadata.reflect(self.engine) # Load tables from the database into the metadata object; Make sure we have an up to date metadata object 
                
        table = Table(table_name, self.metadata, autoload_with = self.engine) # alt table = self.metadata.tables[table_name]
        
        # f"SELECT mpn FROM table WHERE mpn == {mpn}"
        # stmt = table.select().where(table.c.mpn == mpn).where(table.c.vendor==vendor).where(table.c.mfr==mfr)
        # stmt = select(table).where(table.c.mpn == mpn, table.c.vendor==vendor, table.c.mfr== mfr) # Equivalent
        # stmt = table.select().where(table.c.mpn == mpn, table.c.vendor==vendor, table.c.mfr== mfr) # Equivalent 
        stmt = select(table).filter_by(mpn=mpn, vendor=vendor, mfr=mfr)  # sqlalchemy.filter_by generates where clauses with equality comparisons:
        if vendor is None and mfr is None: 
            stmt = select(table).filter_by(mpn=mpn) # I can't be bothere to retype vendor & mfr 
            # For simple “equality” comparisons against a single entity, there’s also a popular method known as Select.filter_by() which accepts keyword arguments that match to column keys or ORM attribute names. It will filter against the leftmost FROM clause or the last entity joined:
            # >>> print(select(User).filter_by(name="spongebob", fullname="Spongebob Squarepants"))
            # SELECT user_account.id, user_account.name, user_account.fullname
            # FROM user_account
            # WHERE user_account.name = :name_1 AND user_account.fullname = :fullname_1
        elif vendor is None: 
            stmt = select(table).filter_by(mpn=mpn , mfr=mfr)
        elif mfr is None: 
            stmt = select(table.filter_by(mpn=mpn , vendor=vendor))
            
        print('GENERATED STATEMENT:', stmt)
        result = self.execute_stmt(stmt)
        fetch_one = result.fetchone() # Look at the first row-- is it an empty list? 
        if fetch_one:
            record = dict(zip(result.keys(), fetch_one))
        else: 
            record = None
        return record 
        # else: e
        #     for table_name, _ in self.metadata.tables.items(): # for every table_name, table pair in autoloaded metadata: 
        #         record = self.get_record(mpn, vendor, mfr, table_name = table_name)
        #         if record:
        #             break 

    # def update_symbol(self, table_name, mpn ,set_column, set_value): 
    # tbale_name is our key 
    def get_filter(self, table_name, filter:str): #get a preset column order for 'table_name' (Ex 'capacitors_ceramic_capacitors') based on the 'filter'(Ex 'general_attributes' or 'category_specific')  you want to apply
        ss_filters = self.metadata.tables.get('ss_filters')
        # key = {ss_filters.c.table_name: table_name}
        statement = select(ss_filters.c.get(filter)).where(ss_filters.c.table_name == table_name)
        # NOte we wanna select the column 'filter'('general_attributes' or 'part_specific', etc)  from ss_filters. we can access that column via dict-like interface: ss_filters.c.get(column_name)
        # print("STATEMENT:", statement)
        result = self.execute_stmt(statement)

        
        fetch_one = result.fetchone() # Look at the first row-- is it an empty list? 
        if fetch_one: # FETCH_ONE will be a tuple whose 0 index is a comma-sep string : ('name,symbol,footprint,package/case,reference,unit_price,mpn,vendor_part_page,mfr,vendor,standard_pricing,vendor_part_number,table_name,categories',)
            filter_columns = fetch_one[0].split(',') 
            if verbose:
                print('FILTER_COLUMNS:', filter_columns)
        else: 
            filter_columns = None
        return filter_columns  
        

    def execute_stmt(self, stmt):
        try:
            with self.engine.begin() as connection: 
                result= connection.execute(stmt)
        except IntegrityError:  # IntegrityError is thrown on attempt to add a row with 'mpn'which is already in table-- We don't want duplicates
            print('entry already in database, and dont want repeats. Doing Nothing.')
            return None
        except Exception as e: 
            print("EXCEPTION:", e) 
            return None
        else: 
            # print('RESULT:', result)
            return result
# try: test for errors 
# except: Handle exception 
# else: execute code when no error 
# finally: execute code regardless

    def table_name_exists(self, table_name:str):
        if not isinstance(table_name, str):
            print(f'ARG "TABLE_NAME" IS TYPE: {type(table_name) } BUT EXPECTED str)')
        table = self.metadata.tables.get(table_name, None)
        if table is None: 
            # print(f'Table {table_name} DNE')
            return False
        # print(f"TABLE: {table_name} EXISTS")
        return True # Don't return the table, return True. sqlalchemy.Table objects don't work in boolean evaluation: if self.table_name_exists() wouldn't be able to be evaluated, and someone will inevitably try to do "if self.table_name_exists()"
        
    def get_df(self, table_name:str):  # Get a table from SQL DB, turn into DataFrame, -> DataFrame
        if verbose: 
            print()
            print('DATABSE.GET_DF.TABLE_NAME:', table_name)
        # table = Table(table_name, self.metadata, autoload_with = self.engine) # autoload; load, the part's table
        if not self.table_name_exists(table_name): 
            print(f"TABLE_NAME: {table_name} DOES NOT EXIST! ")
            return None
        table = self.metadata.tables.get(table_name)
        
        sql_statement = select(table) 
        with self.engine.begin() as connection: 
            df = pandas.read_sql(sql_statement, connection, dtype = str) # IMPORTANT: convert all your datatypes to string with dtype = str
        return df # Slots can return values , however the return value is only accessible when the slot is not called as a slot but as a normal method
    # Q: Does sqlalchemy allow select('capacitors_ceramic')? No. So, autoload the Table() object, then select(table_obj)

    def create_columns_from_attributes(self, attributes):
        columns = []
        for k,v in attributes.items():
            if isinstance(v, str):
                columns.append(Column(k, Text))
            elif isinstance(v, int): 
                columns.append(Column(k, Integer))
            elif isinstance(v, float):
                columns.append(Column(k, Float))
            elif isinstance(v, (dict, list)):
                pass # DO NOT TRY TO ADD DICTS OR LISTS TO SQL, it won't work. BUT, Its useful for the part dict to store some values as lists or dicts, so allow dicts/lists in the part dict, just prevent them from going into the dict
            else: # 
                print(f"TYPE OF VALUE IS: {type(v)} -- IS THIS ACCEPTABLE FOR A SQL VALUE?")
                columns.append(Column(k, Text))
        print('LEN(COLUMNS)', len(columns))
        return columns 

    def create_table(self, table_name, columns):  #TODO: ALSO CREATE A RECORD IN THE "SS_FILTERS" TABLE !!!

        if self.table_name_exists(table_name):
            print(f"Table {table_name} already exists, doing nothing")
            return
        # Make a table object on metadata. Then use metadata.create_all(self.engine) to make the table if not exists
        ss_filters = self.metadata.tables.get("ss_filters")
        table = Table(table_name, self.metadata, *columns,        
                      PrimaryKeyConstraint( 'mpn', 'mfr', 'vendor'),
                    # UniqueConstraint('mpn', 'mfr', 'vendor')) Pretty sure PK enforces unique 
                      ForeignKeyConstraint( [ 'table_name' ] , [ss_filters.c.table_name],  # (columns:Sequence, refcolumns:sequence) #Prevent addition of entry if value DNE in  ss_filters 'table_name' column. #Sql Equivalent: FOREIGN KEY 'table_name' REFERENCES 'ss_filters.table_name'(?)
                        onupdate=  "CASCADE",
                        ondelete = "CASCADE")#"SET NULL"),)
                    )
        self.metadata.create_all(self.engine)
        return table
    
# STATEMENT: INSERT INTO ss_filters (table_name, general, category_specific, "primary", custom) VALUES (:table_name, :general, :category_specific, :primary, :custom)
    def insert_into_ss_filters(self, table_name, attributes):
        ss_filters = self.metadata.tables.get('ss_filters')
        general = ','.join(general_schema)
        category_specific= attributes.pop('category_specific_schema') # Be sure to POP category_specific_schema, bc we don't want it to show up after this
        designator = '?'
        for map in reference_designator_map: # 'capacitors' 'microcontrollers' 'resistors' etc
            if map in table_name: 
                reference_designator = reference_designator_map.get(designator,'?') # Try to get 'C' for capacitors and 'R' for resistors, ? if cant
                break # No reason to continue
            
        values = (table_name,           #  table_name: already a str
                  general,              # general_schema db
                  category_specific,    # category_specific_schema, gotta turn into a string 
                  '',                   # primary_attributes is unknown
                  reference_designator, # designator might be known ex 'C' or 'R', else '?'
                  ''                    # custom_filters are unknown
        )
        stmt = insert(ss_filters).values(values)
        print('STATEMENT:', stmt)
        result = self.execute_stmt(stmt)
        if result: 
            print("INSERT RESULT ROWCOUNT:", result.rowcount) # What data is in the result of an INSERT Statement? Oh-- rowcount
        # stmt = insert(user_table).values(name="username", fullname="Full Username")
        return result
    

    def insert_into_table(self, record:dict):
        
        # if self.table_name_exists(table_name):
        table_name = record.get('table_name')  
        if table_name is None: 
            raise ValueError(f"TABLE_NAME IS NONE. MYDIGIKEYPARSER.TO_DATABASE()")        
        table = self.metadata.tables.get(table_name, None) 
        # if table: COMPARING TABLE OBJECTS IS TRICKY: HAVE TO COMPARE AGAINST NONE EXPLICITLY, AS TABLE OBJECTS DO NOT EVALUATE TO EITHER TRUE OR FALSE  raise TypeError("Boolean value of this clause is not defined") 
        if table is None: # If table didn't exist, FIRST update ss_filters, then create table, then insert on that table
            print('CREATING TABLE')

            self.insert_into_ss_filters(table_name, record) 
            columns = self.create_columns_from_attributes(record)
            table = self.create_table(table_name, columns)

        record.pop('category_specific_schema') # Be sure to POP category_specific_schema, bc we don't want it to show up after this
        stmt = table.insert().values(record) # sqlalchemy.exc.CompileError: Unconsumed column names: eda_models : 
        print('STMT:', stmt) #sqlalchemy.exc.CompileError: Unconsumed column names: category_specific_schema
        # Attempts to insert part which exists in table throws IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: ceramic_capacitors.mpn. Handle this with a try:except block
        try:
            with self.engine.begin() as connection: 
                result = connection.execute(stmt)#sqlalchemy.exc.CompileError: Unconsumed column names: table_name

                row_idx = result.inserted_primary_key[0] if len(result.inserted_primary_key) else 0# .inserted_primary_key: -> the primary key of the row just SQLINSERTed. ONLY works when 1) your table HAS a primary key and 2) result is of an INSERT statement. 
                if not row_idx:
                    return None
                self.changed.emit(record )
                # print('MADE A CHANGE IN THIS ROW_IDX:', row_idx)
                # self.changed.emit(record , row_idx) # We changed this record, at this row_idx. row_idx is needed because...Oh. It is not needed.
                
        except IntegrityError:  # IntegrityError is thrown on attempt to add a row with 'mpn'which is already in table-- We don't want duplicates
            print('entry already in database, and no repeats allowed. Doing Nothing.')

    @Slot(dict, dict) # Where part is part BEFORE update and Where newData holds the key:value pair that we're gonna update-- I wanted to split it in update_key, update_value, but dict keys can be int or float or str, as can dict values, yet Signals have to know their type. Also, 'update' is a sqlalchemy namespace
    def update(self, part, newData): # SqlUPDATE: update(user_table).where(user_table.c.id == 5).values(name="user #5")
        print()
        print('MyDATABASE.UPDATE:')
        table_name = part.get('table_name')
        table = self.metadata.tables.get(table_name, None)
            
        if table is None: 
            print(f'sqlUPDATE invalid: COULD NOT GET TABLE: {table_name}')
            return 
        
        mpn = part.get('mpn', None)

        stmt = update(table).where(table.c.mpn == mpn).values(newData)
        print("STMT", stmt) # UPDATE "integrated circuits (ics)_embedded_microcontrollers" SET symbol=:symbol WHERE "integrated circuits (ics)_embedded_microcontrollers".mpn = :mpn_1
        rowcount =self.execute_stmt(stmt).rowcount
        print('ROWCOUNT:', rowcount) # UPDATE stmts don't return a result object. UPDATE stmt success is indicated in the .rowcount attribute, which returns the no. of rows matching the WHERE clause-- and you compare it to the number of rows expected to match(aka1)
        if rowcount:
            # part = part.update(newData) # NO BAD this sets part to None 
            part.update(newData) # affect changes to part dict b4 letting the world know part was updated
            self.changed.emit(part) # In My(Board,Schematic)Scene : database.changed.connect(self.reload_part) : This reloads the 
            
        return rowcount
    
    def update_ss_filters(self, table_name, newData: dict):
        if not isinstance(newData, dict): 
            print('NEWDATA SHOULD BE DICT BUT GOT TYPE: ', type(newData))
        ss_filters = self.metadata.tables.get('ss_filters')
        stmt = update(ss_filters).where(ss_filters.c.table_name == table_name).values(newData) # newData: { 'primary_attributes': }
        print("STMT", stmt.compile())# UPDATE "integrated circuits (ics)_embedded_microcontrollers" SET symbol=:symbol WHERE "integrated circuits (ics)_embedded_microcontrollers".mpn = :mpn_1
        rowcount = self.execute_stmt(stmt).rowcount # UPDATE stmts don't return a result object. UPDATE stmt success is indicated in the .rowcount attribute, which returns the no. of rows matching the WHERE clause-- and you compare it to the number of rows expected to match(aka1)
        # print('ROWCOUNT:', rowcount)
        if not rowcount: # If sqlUPDATEing ss_filters worked, we STILL need to propogate new primary_attributes to 'capacitors_ceramic_capacitors' table:
            raise ValueError(f"Failed to update ss_filters. Table_name: {table_name} newData: {newData}")
        stmt = update(self.metadata.tables.get(table_name)).values(newData) # In 'capacitors_ceramic_capacitors' table, sqlUPDATE all cells under primary_attributes column to self.primary attributes  
        print()
        print('STMT:', stmt)
        print()
        if not self.execute_stmt(stmt).rowcount: 
            raise ValueError(f'UPDATED ss_filters BUT FAILED TO PROPOGATE CHANGE TO TABLE_NAME: {table_name}')
        self.changed.emit({'table_name':table_name}) # NOrmally, database.changed() emits the full part dict, but only the 'table_name' field is used; as long as we supply table name, ss.reload_part(which ONLY needs table_name) will still trigger the Sig/Slot workflow that refreshes table, such that we can see this change take affect.
        return rowcount
    
    
# Create an instance, which will be the ONLY Database instance; a singleton, intended for import by other modules, such that all module may access the SAME instance of MyDatabase.
database = Database()

### TESTING ###
# ss_filters = database.metadata.tables.get('ss_filters')
# record = {'mpn':1 , "vendor":2, 'mfr': 3 , 'table_name' :'capacitors_ceramic_capacitors'}
# db.insert_into_table('capacitors_ceramic_capacitors', record)