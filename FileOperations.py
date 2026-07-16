# FileOperations    
import os 
import csv 

encoding = 'utf8'
delimiter = ";"

def insert_into_csv(path, headers, row):
    if not file_is_csv(path):
        print('FILE EXTENSION IS NOT .csv BUT NEEDS TO BE')
        return
    if not directories_exist(path): 
        create_directories(path)
    if not file_exists(path):
        create_file(path)
        append_lists_to_file(path, headers, row)
    else: 
        if headers_match(path, headers): 
            append_list_to_file(path, row)

def file_exists(path):
    return True if os.path.exists(path) else False 

def create_file(path):
    with open(path, 'w', encoding = encoding) as fo: 
        fo.write('')
        
def directories_exist(path):
    dirname = os.path.dirname(path)
    return True if os.path.exists(dirname) else False 

def create_directories(path):
    os.makedirs(os.path.dirname(path))
    
def file_is_csv(path):
    print('PATH: ', path)
    return True if os.path.splitext(path)[1] == '.csv' else False #TypeError: expected str, bytes or os.PathLike object, not tuple

def append_list_to_file(file, lst):
    with open(file, 'a',encoding = encoding, newline = '') as fo: # Docs say: If csvfile is a file object, it should be .open()ed with newline=''
        writer = csv.writer(fo,delimiter = delimiter)
        writer.writerow(lst) # Write one row, lst
        
def append_lists_to_file(file, *lsts):
    # print()
    # print('FILE:', file)
    with open(file, 'a', encoding = encoding, newline = '') as fo: 
        writer = csv.writer(fo, delimiter = delimiter)
        print()
        print("LSTS", lsts)
        writer.writerows(lsts) # Write rows, lsts
            
            
    
def get_file_headers(file):
    with open(file,encoding = encoding ) as fo:  
        
        headers=  fo.readline() # -> str
        print()
        print('FILE_HEADERS:',headers)
        headers = headers.split(';') # -> list
        print('FILE_HEADERS.SPLIT()', headers)
        return headers 

        
def headers_match( file, headers): 
    file_headers = get_file_headers(file)
    
    if not file_headers: 
        print('FILE DNH HEADERS', file)
        return False
    else: 
        file_headers = [header.lower().strip() for header in file_headers if isinstance(header, str)]
        headers = [h.lower().strip() for h in headers if isinstance(h, str)]
        if file_headers == headers:
        # Some poor attempts to compare headers against file_headers
            print('HEADERS MATCH UP WITH FILE_HEADERS: ', headers)
            return True
        else: 
            print(f"FILE_HEADER DNM HEADERS:")
            print("HEADERS:\n", headers)
            print("FILE_HEADERS\n", file_headers )
            return False
        


def write_string_to_file(string, file):
    # with open(file, 'w') as fo: BAD default encoding is 'str' aka unicode. To use special chars, set encoding='utf8' UnicodeEncodeError: 'charmap' codec can't encode character '\u03bc' in position 3: character maps to <undefined> 
        with open(file, 'w', encoding='utf8') as fo: 
            fo.write(str(string))
    

# crazy_characters = ['°',
# 'μ', 
# '±',
# '%',
# 'µ'
# ]
# write_string_to_file( ' '.join(crazy_characters) , tst)

# with open(tst, 'r', encoding='utf8') as fo:  # Good, reading our utf8 file as utf8. 
# # with open(tst, 'r', encoding = None) as fo:  NO BAD utf8 encoded files must be utf8 decoded in order to read 
#     lines = fo.readlines()
# print(lines)


