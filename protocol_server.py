import random
import math
import threading
from socket import *
import rsaFunctions
PUBLIC_EXPONENT = 17;
SERVER_HOST = 12100
SERVER_PORT = "localhost"

def main():
    """Provide the user with a variety of encryption-related actions"""
    createServer(SERVER_HOST,SERVER_PORT)
    
def createServer(listen_port, listen_on):
    """
    waits for a connection
    upon receiving a connection generates public key tuple
    Send 2 bytes (m) that represent the size in bytes of your modulus n
    Send the public modulus n using int.to_bytes(n, m, 'big')
    Send a following '\r\n'
    Send 2 bytes (m) that represent the size in bytes of your public exponent e
    Send the public exponent e using int.to_bytes(e, m, 'big')
    Send a following '\r\n'
    immediately after receive a message from the client
    The first 2 bytes (m) represent the size in bytes of the message
    The message will be followed by a trailing '\r\n'
    decrypt and print that message
    send a b'A' then close the connection
    """
    global lock;
    lock = threading.Lock()
    password = input (
            "Create a password\n"
        )
            #create socket and listen for connection
    paddedPass = password.zfill(20)
    address = (listen_on, listen_port)
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(5)
    global c, addr;
    c, addr = s.accept()
    print('got connection from addr', address)
    #create keys
    key_pair = rsaFunctions.create_keys()
    e,d,n = key_pair
    pub = rsaFunctions.get_public_key(key_pair)
    print("Pub key: " + str(pub))
    global priv
    priv = rsaFunctions.get_private_key(key_pair)
    #send modulus
    m = (n.bit_length() + 7) // 8
    mb = int.to_bytes(m,2,'big')
    c.send(mb)
    c.send(int.to_bytes(n,m,'big'))
    c.send(b'\r\n')
    #send e
    m = (e.bit_length() + 7) // 8
    mb = int.to_bytes(m, 2, 'big')
    c.send(mb)
    c.send(int.to_bytes(e,m,"big"))
    c.send(b'\r\n')
    
    reciever = threading.Thread(target = recieveMessages)
    sender = threading.Thread(target = sendMessages)
    
    while(True):
        guess = b''
        for x in range(20):
            guess += c.recv(4)
        if rsaFunctions.decrypt(priv,guess) != paddedPass:
            c.send(b'F')
        else:
            c.send(b'A')
            break
        
    reciever.start()
    sender.start()
    

def sendMessages():
    print("Send a message: ")
    while(True):
        message = input()
        if len(message) >= 1:
            c.send(message.encode("ascii"))

def recieveMessages():
    while(True):
        data = c.recv(2)
        if data:
            while(True):
                #recieve message
                byte = b''
                while not byte.__contains__(b'\r\n'):
                    byte += c.recv(1)
                byte = byte[:-2]
                decrypted = rsaFunctions.decrypt(priv, byte)
                print("\n")
                print("             Client: " + str(decrypted) + "\n")
                data = b''
                break
    
        
