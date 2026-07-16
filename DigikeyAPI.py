from utils import * #Lauch Browser, login, to get authorization code.
from MyAccessTokenAPI import MyAccessTokenAPI
from DigikeyParser import DigikeyParser 
from PySide6.QtCore import Signal , Slot

import FileOperations

from PySide6.QtNetwork import * 

from TcpServer import TcpServer
from SslServer import SslServer

class DigikeyAPI(QObject): # This class makes use of Digikey's Product Details v4 API. It uses the product details as well as media endpoints to get relevant information on an mpn
    # accessTokenObtained = Signal(str)
    # fetched_part = Signal(str)
    # createdPart = Signal(dict)
    
    _instance = None # class variable for holding a class instance-- do singleton pattern, as we need only one instance, as we need only one access_token.  
    access_token = None
    host = "api.digikey.com"
    
    # product_search_api_path = "products/v4/search" # ProductSearch MyDigikeyAPI path 
    # SHOULD this class only have/need ONE instance? (a singleton class) CGPT says yes & I agree # One a_t lets me make calls up to DK's rate-limits(Which I'll not soon hit). So, only one instance is needed. Getting  >1 would be superfluous. # Don't use a singleton if: I had to authenticate multiple users,or different API configurations, or if access_token was one-time-use or a short lifespan 
    # the SINGLETON PATTERN: #To implement 'the singleton pattern': use the __new__ method, a special double underscore or 'dunder' method, that creates a new instance object, and is automatically called before __init__. __init__, aka the 'constructor' takes the newly created instance object and initializes it with values
    def __new__(cls):
        if cls._instance is None:                                       # _instance is just a _variable we made
            cls._instance = super().__new__(cls)         # Create an instance (but do not initialize) super(MyDigikeyAPI, cls) resolves to 'object'
            # cls._instance = super(DigikeyAPI, cls).__new__(cls)         # Create an instance (but do not initialize) super(MyDigikeyAPI, cls) resolves to 'object'
            cls._instance.client_id = MyAccessTokenAPI.client_id          
        return cls._instance                                            # Return the instance

    def __init__(self):
        super().__init__() # Initialize the QObject
        self.access_token_api = MyAccessTokenAPI()
    
    def getAccessToken(self): # access_tokens expire in 600s, after which, a new a_t is needed. 2-legged oauth has no refresh_token, 3-legged does, but not using 3-legged
        self.access_token = self.access_token_api.getAccessToken() # access_token is needed to query DKAPI for mpn 

    def queryProductDetailsAPI(self, mpn): # Make get request for mpn to Digikey product details (api ,endpoint) 
        self.product_details = f"https://api.digikey.com/products/v4/search/{mpn}/productdetails" # Product Details API endpoint
        response_product_details   = requests.get(self.product_details, headers = self.headers) # media ep needs headers but pd doesn't(?) W/o headers, err: 'X-DIGIKEY-Client-Id header is missing. Ensure the X-DIGIKEY-Client-Id header has a valid key'
        # print() 
        # print("PD HEADERS:", response_product_details.request.headers) 
        self.check_response(response_product_details)
        return response_product_details 
        
    def queryMediaAPI(self , mpn): # Make get request for mpn to Digikey media (api , endpoint) 
        self.media           = f"https://api.digikey.com/products/v4/search/{mpn}/media" # Digikey Media API endpoint
        response_media             = requests.get(self.media, headers=self.headers) # , json=self.body# body=endpoint_info.get('body'),# So far, I've never needed the 'json' 'body' argument. In fact most dnn body, thus I won't bother supporting this till I need it
        self.check_response(response_media)
        return response_media

    @Slot(str)
    def queryDigikey(self, mpn): # We need to know the mpn of a part in order to get it from Digikey's site.
        # Requires access_token from AcessTokenAPI. headers is for media API, product_details API dnn headers(?) Headers 
        if self.access_token is None: 
            print('SELF.ACCESS_TOKEN IS NONE, RETURNING')
            return
            
        self.headers = { 
            "X-DIGIKEY-Client-Id": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "X-DIGIKEY-Locale-Site": "US",
            "X-DIGIKEY-Locale-Language": "en",
            "X-DIGIKEY-Locale-Currency": "USD",
            "X-DIGIKEY-Locale-ShipToCountry": "us",
            "X-DIGIKEY-Customer-Id": '0'
        }# headers:  {'X-DIGIKEY-Client-Id': 'xPJYLpMi0aVZPfuitXzVk2IOln3aFfBo', 'Authorization': 'Bearer 4gz4M0dN8RhAXZJa9XZcbGViaUMs', 'X-DIGIKEY-Locale-Site': 'US', 'X-DIGIKEY-Locale-Language': 'en', 'X-DIGIKEY-Locale-Currency': 'USD', 'X-DIGIKEY-Locale-ShipToCountry': 'us', 'X-DIGIKEY-Customer-Id': '0'}     
        # # I am being bot checked. perhaps I shoud 'disguise' my user agent. 
        #     user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0' # I am being bot-checked. Lets try setting my header's user-agent to my browser's user-agent: 
        #     self.headers['user-agent'] = user_agent      
        # response_product_details   = requests.get(self.product_details, headers = self.headers) # media ep needs headers but pd doesn't(?) W/o headers, err: 'X-DIGIKEY-Client-Id header is missing. Ensure the X-DIGIKEY-Client-Id header has a valid key'
        # print() 
        # print("PD HEADERS:", response_product_details.request.headers) 
        # response_media             = requests.get(self.media, headers=self.headers) # , json=self.body# body=endpoint_info.get('body'),# So far, I've never needed the 'json' 'body' argument. In fact most dnn body, thus I won't bother supporting this till I need it
        dk_info = {'response_media': self.queryMediaAPI(mpn).json() , 
                     'response_product_details': self.queryProductDetailsAPI(mpn).json()
                    } # I really only need the .json() part of a response
        print()
        print('dk_info:', dk_info)
        self.saveToFile(mpn, dk_info)
        self.saveToPickle(mpn, dk_info)
        print('saved dk_info to file')
        return dk_info
        
    def saveToFile(self, mpn, dk_info):
        folder = "dk_part_info"
        file_txt = f"{mpn}_dk.txt".strip() 
        print('FILE_TXT:', file_txt) # 3310Y-001-102L-ND_dk.txt
        file_txt = os.path.join(folder, file_txt)
        print() 
        print('FILE_TXT:', file_txt) # FILE_TXT: dk_part_info\3310Y-001-102L-ND_dk.txt
        FileOperations.write_string_to_file(str(dk_info), file_txt)

    def saveToPickle(self, mpn, dk_info):
        folder = "dk_part_info"
        file_pickle = f"{mpn}_dk.pickle".strip()
        path_pickle = os.path.join(folder, file_pickle)
        with open(path_pickle, 'wb') as fo: 
            # fo.write(dk_info) No BAD dk_info is a dict; can only write str to files. Converting to a string is easy. Converting from a string, is not. 
            # json.dump(dk_info, fo) Cannot use json.dump. JSON format strictly uses doubQuot, but my data has singQuotes. 
            pickle.dump(dk_info, fo)
            
        # # self.fetch_part_finished.emit(str(dk_info)) # AttributeError: 'PySide6.QtCore.Signal' object has no attribute 'emit' ? I had not inherited QObject
        # self.fetched_part.emit(dk_info)


        

    @staticmethod  # note static methods called with self.staticMethod. Can be called within constructor.( instance methods (can,cant) be ccalled in constructor)
    def check_response( r): # Notify me if status ain't 200 
        if r.status_code != 200: # AttributeError: 'str' object has no attribute 'status_code'
            print()
            raise ValueError (f"ERROR. Response: {r} \n json: {r.json()}")
        
# If you try to search DK for 'NotAProduct' you will get 'Error404 Requested Product Not Found': json: {'type': 'https://tools.ietf.org/html/rfc7231#section-6.5.4', 'title': 'Not Found', 'status': 404, 'detail': 'Requested Product NotAProduct Not Found', 'instance': '', 'correlationId': '09363e93-35f7-42e2-ef0d-22ca3154dc7f', 'errors': {}}


     

# QDIALOG.ACCEPT: Base Hides the modal dialog and sets the result code to Accepted.

# SELF.PART: <class 'NoneType'> None
# SELF.MPN_EDIT.text(): 
# 3310Y-001-102L-ND

# DevTools listening on ws://127.0.0.1:63262/devtools/browser/a94a0fd5-8eab-4136-9497-7613d305c82f
# Please sign-in to digikey, manually, in the browser which should have just opened
# After signing in to digikey, press enter to continue...s\.venv\Scripts\Activate.ps1
# Traceback (most recent call last):
#   File "c:\Users\robby\OneDrive\part_database\MyCreatePartDialog.py", line 66, in accept
#     my_digikey_api = MyDigikeyAPI()
#                      ^^^^^^^^^^^^^^
#   File "c:\Users\robby\OneDrive\part_database\MyDigikeyAPI.py", line 24, in __new__
#     cls._instance._initialize()                                 # Call a function we wrote
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "c:\Users\robby\OneDrive\part_database\MyDigikeyAPI.py", line 29, in _initialize
#     self.authenticate()
#   File "c:\Users\robby\OneDrive\part_database\MyDigikeyAPI.py", line 40, in authenticate
#     self.access_token = MyAccessTokenAPI().getAuthorization()
#                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "c:\Users\robby\OneDrive\part_database\MyAccessTokenAPI.py", line 43, in getAuthorization
#     raise ValueError("Authorization code not found in the redirect URL.")
# ValueError: Authorization code not found in the redirect URL.
# [14140:24712:0408/110107.550:ERROR:google_apis\gcm\engine\registration_request.cc:291] Registration response error message: DEPRECATED_ENDPOINT


# mpn = "p5555-nd" # "p5555-nd" is the mpn digikey uses in their api tutorial.
# mpn= "BAR9002ELE6327XTMA1TR-ND" #This is a diode with two child_categories fields 'stead of the normal one. But, no EDA models
# mpn= "BAR9002ELE6327XTMA1"        # This is NOT PURCHASEABLE (?)
# GRM21BR61E106KA73L # mlcc with eda models