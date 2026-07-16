# GET ACCESS TOKEN THROUGH OAUTH20. AT is used to make requests of the DK api
# https://developer.digikey.com/documentation?atab=tab_link_4
# This used to use Selenium and 3-legged OAuth, but trying to switch to webbrowser and 2-legged oauth
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs    # Note: urllib.urljoin() can only join two strings, thus I prefer f-strings. os.path.join() can join multiple strings.

import requests 
import webbrowser

from utils import Utils 
from TcpServer import TcpServer
from SslServer import SslServer 

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout,QVBoxLayout, QLabel, QLineEdit, QWidget, QApplication
from PySide6.QtCore import Signal, Slot, Qt, QObject

from utils import Utils 

class MyAccessTokenAPI(QObject): # inherit QObject to use signals/slots 
    # Digikey's instructions : https://developer.digikey.com/documentation?atab=tab_link_4
    host                = "https://api.digikey.com/"
    grant_type_2_legged = 'client_credentials' # 2 legged oauth
    # authorization_uri   = f"{host}v1/oauth2/authorize" #3-legged. This endpoint handles authenticating the user and user consent. The result includes the authorization code. Note there are required query parameters to send, url-encoded
    access_token_endpoint = f"{host}/v1/oauth2/token" # This endpoint is the target of the request. The result of requests to this endpoint is the access token
    
    client_id           = Utils.client_id 
    client_secret       = Utils.client_secret
    
    # 3-legged #authorization_uri   = authorization_uri + f"?response_type=code&client_id={client_id}&redirect_uri={redirect_uri_url_encoded}" # DK will ping back at the redirect_uri, with a authorization_code 
    # print("AUTHORIZATION_URI:", authorization_uri)

    def __init__(self):
        super().__init__() 

    def getAccessToken(self): # As per Digikey's 2-legged oauth instructions : https://developer.digikey.com/documentation?atab=tab_link_4
        
        payload_2_legged = { 
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self.grant_type_2_legged
        }
        

        response = requests.post(self.access_token_endpoint, data=payload_2_legged).json()# "The request for an access token is an HTTPS POST request and must include the following x-www-form-urlencoded data: client_id, client_secret & grant_type. As per the Oauth2.0 spec, 'grant_type' must take the string value 'client_credentials', for 2-legged oauth. "Result of requests to this access_token_endpoint include the access token" # x-www-form-urlencoded data, aka 'form data', is commonly used in HTML forms. Python's requests module form-encodes the dictionary passed the 'data' argument: our dict automatically becomes form-encoded.
        
        print('RESPONSE:', response)
        access_token = response["access_token"]
        print("Access Token:", access_token)
        return access_token
        
        # authorization_code = parse_qs(urlparse(data).query).get('code', [None])[0] # 2-legged does not require auth code 
        # print(f"Authorization code: {authorization_code}")
        # if not authorization_code:
        #     raise ValueError("Authorization code not found in the redirect URL.")
        #     # https://localhost:5000/callback?code=AUXys6Qy&scope= This should be in the browsers URL. authCode parses out fine. 
            
        # payload = { # 3-legged
        #     "code": authorization_code,
        #     "client_id": self.client_id,
        #     "client_secret": self.client_secret,
        #     "redirect_uri": self.redirect_uri,
        #     "grant_type": self.grant_type
        # }
        
        
        # self.refresh_token = response["refresh_token"] # 2-legged OAuth has no refresh token; new request must be made 
        # print("Refresh Token:", self.refresh_token)
        # return access_token 
    # With OAuth completed, I can send a request to the Digikey API

        # print('OPENING SERVER')
        # webbrowser.open(self.authorization_uri) # opens url in web browser w/all my normal logins/cookies, , but, maintains no connection to browser, so, cannot fetch browser.current_url like Selenium can. Either give cookies to selenium or listen for response on a server at redirect_uri 
        # self.server = SslServer()
        # self.server.socketReadyRead.connect(self.onSocketReadyRead)
        
        # self.server = TcpServer() 
        # self.server.socketReadyRead.connect(self.onSocketReadyRead)
        
        # # 3-legged OAuth(Requires user sign-in on browser, to get authorization_code)
        # self.driver.get(self.authorization_uri)#Loads a web page in the current browser session.  
        # print()
        # print("Sign-in to digikey, manually, in the browser which should have just opened")
        # input("After signing in to digikey, press enter to continue...")

        # redirect_url = self.driver.current_url
        # print("REDIRECT_URL:", redirect_url)
        # authorization_code = parse_qs(urlparse(redirect_url).query).get('code', [None])[0]
        # print(f"Authorization code: {authorization_code}\nRedirect URL: {redirect_url}")
        # if not authorization_code:
        #     raise ValueError("Authorization code not found in the redirect URL.")
        #     # https://localhost:5000/callback?code=AUXys6Qy&scope= This was in the browsers URL. authCode parses out fine. 
        # self.driver.quit() # close chrome window
        


        # response = requests.post(access_token_endpoint, data=payload).json() 
        # print('RESPONSE:', response)
        # access_token = response["access_token"]
        # print("Access Token:", access_token)
        # # self.refresh_token = response["refresh_token"] # 2-legged OAuth has no refresh token; new request must be made 
        # # print("Refresh Token:", self.refresh_token)
        # return access_token # With OAuth completed, I can send a request to the Digikey API

    # def onSocketReadyRead(self, socket):
    #     print('SOCKET:', socket)
    #     data = socket.readAll().data()
    #     print('DATA:', type(data), data)
    #     data = data.decode('utf-8') # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd7 in position 11: invalid continuation byte. Note: this may be happening if oauth is sending HTTPS; TLS encrypted bytes, which it likely is. Why would OAuth send unencrypted;HTTP; unicode over the internet? 
    #     print('DATA.DECODE:', type(data), data)
        
    #     authorization_code = parse_qs(urlparse(data).query).get('code', [None])[0]
    #     print(f"Authorization code: {authorization_code}")
    #     if not authorization_code:
    #         raise ValueError("Authorization code not found in the redirect URL.")
    #         # https://localhost:5000/callback?code=AUXys6Qy&scope= This should be in the browsers URL. authCode parses out fine. 
            
    #     # payload = { # 3-legged
    #     #     "code": authorization_code,
    #     #     "client_id": self.client_id,
    #     #     "client_secret": self.client_secret,
    #     #     "redirect_uri": self.redirect_uri,
    #     #     "grant_type": self.grant_type
    #     # }
    #     payload_2_legged = { 
    #         "client_id": self.client_id,
    #         "client_secret": self.client_secret,
    #         "grant_type": self.grant_type_2_legged
    #     }
    #     access_token_endpoint = f"{self.host}/v1/oauth2/token" # Result of requests to this access_token_endpoint include the access token
    #     # 2-leggedOAuth( No user sign-in on browser) ( Not working (was using grant_type for 3legged)) RESPONSE: {'ErrorResponseVersion': '3.0.0.0', 'StatusCode': 400, 'ErrorMessage': 'Invalid Request - Error(s) in Post Request field(s)', 'ErrorDetails': 'code is null or undefined', 'RequestId': 'bf7e2dd6-1c3b-4a2c-c2a4-47a70892c716', 'ValidationErrors': []}
    #     # "The request for an access token is an HTTPS POST request and must include the following x-www-form-urlencoded data: client_id, client_secret & grant_type. As per the Oauth2.0 spec, 'grant_type' must take the string value 'authorization_code' (doublecheckthis)
    #     # x-www-form-urlencoded data, aka 'form data', is commonly used in HTML forms. Python's requests module form-encodes the dictionary passed the 'data' argument. 
    #     # payload = {
    #     #     "client_id": self.client_id,
    #     #     "client_secret": self.client_secret,
    #     #     "grant_type": self.grant_type
    #     # }

    #     response = requests.post(access_token_endpoint, data=payload_2_legged).json() 
    #     print('RESPONSE:', response)
    #     access_token = response["access_token"]
    #     print("Access Token:", access_token)
    #     # self.refresh_token = response["refresh_token"] # 2-legged OAuth has no refresh token; new request must be made 
    #     # print("Refresh Token:", self.refresh_token)
    #     # return access_token 
    # # With OAuth completed, I can send a request to the Digikey API
    #     self.accessTokenObtained.emit(access_token)
    
        ## Chome/Selenium ## 
        # chrome_options = Options() # You should initialize chrome_options inside __init__().
        # service = Service('C:\\Users\\robby\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
        # self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
    # grant_type_3_legged = "authorization_code" # 3legged oauth 
    # redirect_uri = "https://localhost:5000/callback" # Note that redirect_uri must be the same as was given when this application was registered with Digikey.
    # redirect_uri_url_encoded = f"https%3A%2F%2Flocalhost%3A5000%2Fcallback"
    # Digikey authorization endpoint: 
    # NOTE authorization via'3 legged OAuth' requires user to sign in via browser(annoying), BUT the user sign in can be skipped, by choosing to use 2-legged OAuth instead. (I believe. I could not get 2-legged to work(Iwasusingwronggrant_type)) 
    # authorization_uri in full : https://api.digikey.com/v1/oauth2/authorize?response_type=code&client_id=xPJYLpMi0aVZPfuitXzVk2IOln3aFfBo&redirect_uri=https%3A%2F%2Flocalhost%3A5000%2Fcallback # Note I omitted a state query parameter: An opaque value used by the client to maintain state between the request and callback. The authorization server includes this value when redirecting the user-agent back to the client. The parameter SHOULD be used for preventing cross-site request forgery.