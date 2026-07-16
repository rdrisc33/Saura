import zipfile
from utils import *
import os 
import glob # Unix-pathname expansion 
import re

class MyThirdPartyDownloadExtract():
    def unzip_most_recent(pathname="C:\\Users\\robby\\Downloads\\*"):
        #Get the second-latest file in directory: 
        # glob.glob(pattern) -> list of paths matching pattern
        # os.path.getmtime(path) -> last modification time of path, in float, since 1990. See also getatime(time of last Access) and 
        # sorted(glob.glob('*'), key=os.path.getmtime, reverse=True)[1] # Get second to latest file in dir
        matches= glob.glob(pathname) # -> list of all files in "Downloads"
        matches=sorted(matches, key = os.path.getmtime) # Sort files according to time of last modification
        most_recent_match= matches[-1]   # Get the latest folder 
        head,tail = os.path.split(most_recent_match)# \CL32A157MQVNNNE.zip
        root, ext = os.path.splitext(tail)
        root = re.sub(r'\(.\)', '', root) # When you download the same thing twice windows automatically suffixes (1) onto filename, which I want to ignore. Regex dot '.' character matches anything. Regex () characters mean 'capture group', escape capture group with backslash\. So to match (1) we need this regex: Note it has to be a raw string(r"") Else the escape backslash isn't valid.... ": r"\(.\)"" :  
        
        with zipfile.ZipFile(most_recent_match, 'r') as zip_ref: # unzip the zip folder, into graphics_path. 
            zip_ref.extractall(kicad_third_party_path) # extractall(parts/third_party)
            return root # filename,no extension, always equal to mpn (?)
        
    def ultralibrarian_rename_extracted(root):
        # The names coming from ultralibrarian are real stoopid. Rename them: 
        base = kicad_third_party_path  # third_party/kicad
        folder =  os.path.join(base , root ) # third_party/kicad/MIC33153YHU_TR or whatever the mpn is 
        
        # FileExistsError: [WinError 183] Cannot create a file when that file already exists: 'parts\\third_party\\kicad\\KiCADv6' -> 'parts\\third_party\\kicad\\MIC33153YHJ_TR'
        path1 = os.path.join(base ,'KiCADv6')
        # print('PATH1:', path1)
        # print("FOLDER:", folder)
        if not os.path.exists(folder): # Rename Check if exists first, bc if exists, err: FileExistsError: [WinError 183] Cannot create a file when that file already exists: 'third_party\\kicad\\KiCADv6' -> 'third_party\\kicad\\MIC33153YHJ_TR')
            os.rename( path1, folder  ) # rename folder 'third_party/kicad/KiCADv6'  to 'third_party/kicad/STM32C064' or whatever the mpn of the part is 

        folder_footprints= os.path.join(folder, 'footprints')
        if not os.path.exists(folder_footprints):
            os.rename(os.path.join(folder, 'footprints.pretty'), folder_footprints)  # Rename 'footprints.pretty' to 'footprints', if not exists
        ki_sym_file = os.path.join( folder, root + '.kicad_sym' ) 
        os.rename( glob.glob(os.path.join(folder , '*.kicad_sym'))[0] , ki_sym_file ) # Default naming is 'timestamp.kicad_sym', rename to 'STM32C064.kicad_sym' or whatever the mpn of the part is 
        print('KI_SYM_FILE:', ki_sym_file)
        return ki_sym_file
    
        # os.remove("parts/graphics/KiCADv6/footprints.pretty") # Access is denied? See shutils for removing nonempty dirs         
    def snapmagic_rename_extracted(url):
        print("Sorry, Snapmagic Extraction is NOT YET SUPPORTED")
        return None
# root= ThirdPartyDownloadExtract.unzip_most_recent()
# ki_sym_file = ThirdPartyDownloadExtract.ultralibrarian_rename_extracted(root)
    
# print(ki_sym_file)
        