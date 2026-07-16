
# Make a client to test the server. IRL, I want to get info from Digikey. Could use the python socket module, or telnet client 
# This sorta works 
import socket
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000        # The port used by the server
print('Nothing is printing in PS')
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        message = ' How Long can this be '
        s.sendall(message.encode('utf-8'))
        print('sent data')
        data = s.recv(1024) # I do not receive anythin back from my server atm 
        print(f"Received from server: {data.decode('utf-8')}")

    except ConnectionRefusedError:
        print(f"Connection refused. Is the server running on {HOST}:{PORT}?")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run this client script in a separate terminal. You should see message echoed by the server and displayed in the client’s output. The server GUI will also log the connection and the received/sent messages.