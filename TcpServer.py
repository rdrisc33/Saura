from PySide6.QtWidgets import * 
from PySide6.QtNetwork import *
from utils import Utils 
from PySide6.QtCore import Signal
import sys 

class TcpServer(QTcpServer): 
    socketReadyRead = Signal(QTcpSocket)
    
    def __init__(self , address = Utils.HOST , port = Utils.PORT):
        super().__init__()
        self.listen( address , port) # 
        self.newConnection.connect(self.onNewConnection)
        self.sockets = [] # Track sockets 
        
    def onNewConnection(self): # Setup connection to new socket
        print('ONNEWCONNECTION')
        socket = self.nextPendingConnection() # Accept the pending connection as a connected QTcpSocket. -> QTcpSocket in QAbstractSocket:COnnectedState, used to communicate with client
        socket.readyRead.connect(lambda : self.onSocketReadyRead(socket)) # Signal .readyRead emitted every time data received. Typical to .connect to a slot, read all available data there. # .readyRead Signal doesnt emit the socket; lambda function lets me pass socket as a parameter. 
        socket.disconnected.connect(lambda : self.onSocketDisconnected(socket))
        self.sockets.append(socket)
        # socket.disconnected.connect(self.onSocketDisconnected)
        # socket.errorOccurred.connect(self.onSocketErrorOccurred) # Best practice to catch errors 
        

    def onSocketDisconnected(self, socket):
        self.sockets.remove(socket)
        socket.deleteLater()
        
    def onSocketReadyRead(self, socket):
        self.socketReadyRead.emit(socket)
        print('ONSOCKETREADYREAD')
        data = socket.readAll().data().decode('utf-8')
        print('GOT DATA: ', data)
        # print('DATA.encode():', type(data.encode()), data.encode()) DATA.encode(): <class 'bytes'> b' How Long can this be '
        socket.write(data.encode()) # Write QByteArray Echo back to client
        
## TESTING ### 
# app = QApplication(sys.argv)
# s = TcpServer()
# print('MADE SERVER')
# sys.exit(qApp.exec())
