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
    global tcp_socket
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.connect((server_port, server_host))
    reciever = threading.Thread(target = recieveMessages)
    sender = threading.Thread(target = sendMessages)
    
     #create key from data
    global priv
    priv = rsaFunctions.sendKey(tcp_socket)
    e, n = rsaFunctions.recvKey(tcp_socket)
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
        
        
    global serverName    
    byte = b''
    while not byte.__contains__(b'\r\n'):
        byte += tcp_socket.recv(1)
    byte = byte[:-2]
    serverName = byte.decode("ascii")
    print("\n")
    print("You have entered " + serverName +"'s server!")
    
    
    global name
    
    name = input("Enter your name: ")
    tcp_socket.send(name.encode("ascii"))
    tcp_socket.send(b'\r\n')
    
    
    
    
    reciever = threading.Thread(target=recieveMessages)
    sender = threading.Thread(target= sendMessages)
    
    reciever.start()
    sender.start()
    
def sendMessages():
    print("\n")
    print("You can now enter messages!" +"\n")
    while(True):
        message = input("")
        if len(message) >= 1:
            rsaFunctions.encrypt(pubKey, message,tcp_socket)
            

def recieveMessages():
    while(True):
        data = tcp_socket.recv(2)
        if data:
            while(True):
                #recieve message
                byte = b''
                while not byte.__contains__(b'\r\n'):
                    byte += tcp_socket.recv(1)
                byte = byte[:-2]
                decrypted = rsaFunctions.decrypt(priv, byte)
                print("\n")
                print("             " + serverName + ": " + str(decrypted) + "\n")
                data = b''
                break

if __name__ == "__main__":
    main()
