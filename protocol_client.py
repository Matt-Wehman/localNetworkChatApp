import random
import math
import threading
from socket import *
import rsaFunctions
PUBLIC_EXPONENT = 17;
SERVER_HOST = 12100
SERVER_PORT = "localhost"
global lock
lock = threading.Lock()

def main():
    """Provide the user with a variety of encryption-related actions"""
    createClient(SERVER_HOST,SERVER_PORT)
    
        
def createClient(server_host, server_port):
    """
    creates a connection to a server
    immediately after receive a public key tuple
    receive 2 bytes (D) and decode with m = int.from_bytes(D, 'big')
    receive m bytes (D), and then decode with n = int.from_bytes(D, 'big')
    receive '\r\n'
    repeat for public exponent e

    encrypt and send a message
    Create a plaintext ASCII message
    Encrypt
    Send 2 bytes (m) that give the size of the message in bytes
    Send encrypted messsage
    Send '\r\n'
    receive a b'A' and then close the connection
    """
    
    password = ""
    while(True):
        password = input(
        "Enter a password (max 10 characters):\n"
        )
        if len(password) > 10:
            print("password is too long")
        else:
            break
    #create socket
    print('tcp_send: dst_host="{0}", dst_port={1}'.format(server_host, server_port))
    global tcp_socket
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.connect((server_port, server_host))
    reciever = threading.Thread(target = recieveMessages)
    sender = threading.Thread(target = sendMessages)
        #receive public mod
    m = tcp_socket.recv(2)
    D = tcp_socket.recv(int.from_bytes(m,'big'))
    n = int.from_bytes(D,'big')
    CRLF = tcp_socket.recv(2)

        #receive e
    m = tcp_socket.recv(2)
    D = tcp_socket.recv(int.from_bytes(m, 'big'))
    e = int.from_bytes(D, 'big')
    CRLF = tcp_socket.recv(2)
        #create key from data
    global pubKey
    pubKey = (e,n)
    rsaFunctions.encryptPass(pubKey,password,tcp_socket)
    while(True):
        response = tcp_socket.recv(1)
        if response != b'A':
            password = input(
            "Wrong Password Try Again: \n"
            )
            rsaFunctions.encryptPass(pubKey,password,tcp_socket)
        else:
            break
    
    reciever = threading.Thread(target=recieveMessages)
    sender = threading.Thread(target= sendMessages)
    
    reciever.start()
    sender.start()
    
def sendMessages():
    while(True):
        message = input("Enter a message: ")
        if len(message) >= 1:
            rsaFunctions.encrypt(pubKey, message,tcp_socket)
            

def recieveMessages():
    while(True):
        message = tcp_socket.recv(2048).decode("ascii")
        print(message)

if __name__ == "__main__":
    main()
