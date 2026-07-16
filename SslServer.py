from PySide6.QtNetwork import * 
from PySide6.QtCore import * 
import sys 
from PySide6.QtWidgets import * 

# https://doc.qt.io/qt-6/qsslsocket.html#details

# Encrypted TCP connection using TLS. Ssl encryption operates on top of existing TCP Stream, after socket enters state ConnectedState. 
# The states of a successfully connecting socket is as follows:  HostLookupState-ConnectingState-ConnectedState
# If the connection was successful, the socket will enter ConnectedState, after which, the ssl handshake will occur.
# If the handshake is successful, socket.encrypted.emit()
# Secure connection can be established w/ an immediate, or delayed, ssl handshake. 
# .connectToHostEncrypted(address, port) will handshake immediately after ConnectedState
# socket = QSslSocket()
# socket.encrypted.connect(onEncrypted)
# socket.connectToHostEncrypted('example.com', 443) 

# "The most common way to implement an ssl server is to subclass QTcpServer & reimplement .incomingConnection(socketDescriptor) &  .setSocketDescriptor(socketDescriptor)" --The Docs : https://doc.qt.io/qt-6/qsslsocket.html#startServerEncryption
# QSslSocket.startServerEncryption() # Starts a delayed handshake. Usually called right after receiving a connection

class SslServer(QTcpServer):
    socketReadyRead = Signal(QSslSocket)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.listen(QHostAddress.SpecialAddress.LocalHost , 5000)
        self.newConnection.connect(self.onNewConnection)
        
    def incomingConnection(self, socketDescriptor): # The base implementation creates a QTcpSocket, sets socketDescriptor, stores socket in internal list of pending connections, then emits .newConnection(Hmm, I do not see newConnection.emit in source code) . My Reimplementation does the same, with a QSslSocket rather than QTcpSocket, and also socket.encrypted.connect(self.ready) & socket.startServerEncryption() to begin the handshake 
        socket = QSslSocket()
        socket.setSocketDescriptor(socketDescriptor)
        self.addPendingConnection(socket) # 
        socket.encrypted.connect(lambda : self.onEncrypted(socket)) 
        socket.startServerEncryption() # Initiate the delayed ssl handshake. 
        # self.newConnection.emit() # The base implementation does this... however not in source code nor docs... " This signal is emitted every time a new connection is available"

    def onEncrypted(self, socket):
        print('SOCKET ENCRYPTED!') 
        
    def onNewConnection(self):
        print('ONNEWCONNECTION')
        socket = self.nextPendingConnection()
        socket.sslErrors.connect(self.onSslErrors) # If handshake error occurred, .sslErrors is emitted. Common cause is sslSocket unable to securely identify the peer. The connection will be dropped after this signal is emitted, unless you want to continue connecting despite the errors, in which case you must call QSslSocket.ignoreSslErrors() from the slot connected to this signal. Access the error list with .sslHandshakeErrors()
        socket.readyRead.connect(lambda : self.onReadyRead(socket))

    def onSslErrors(self, errors): # 
        print('ONSSLERRORS:', errors)
            
    def onReadyRead(self, socket):
        self.socketReadyRead.emit(socket)
        data = socket.readAll().data()
        print('SOCKET DATA:', data) 
        data = data.decode()
        print('DECODED SOCKET DATA:', data)
        
        # socket.read()
        # socket.canReadLine()
        # socket.readLine()
        # socket.getChar()
        # Any above read decrypted data from sslSocket. 
        # socket.write()
        # socket.putChar()
        # Socket can write data back to peer w/ above. Encryption will automatically occur, and socket.encryptedBytesWritten.emit() once data has been written to peer. 
        

## TESTING ### 
# app = QApplication(sys.argv)
# server = SslServer()
# print('MADE SERVER')
# sys.exit(app.exec())