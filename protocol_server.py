import random
import math
import threading
from socket import *
from tkinter.tix import IMAGETEXT
import rsaFunctions
import os
import io
import PIL.Image as Image
from PIL import ImageFile, ImageTk
import PySimpleGUI as sg


ImageFile.LOAD_TRUNCATED_IMAGES = True
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
            "Create a password:\n"
        )
    global name
    name = input("Enter your name: \n")
            #create socket and listen for connection
    print("Waiting for other users " + "\n")
    paddedPass = password.zfill(20)
    address = (listen_on, listen_port)
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(5)
    global c, addr;
    c, addr = s.accept()
    #create keys
    
    global priv
    priv = rsaFunctions.sendKey(c)
    e, n = rsaFunctions.recvKey(c)
    global pubKey
    pubKey = (e,n)    
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
        
    c.send(name.encode("ascii"))
    c.send(b'\r\n')
        
    byte = b''
    while not byte.__contains__(b'\r\n'):
        byte += c.recv(1)
    byte = byte[:-2]
    name = byte.decode("ascii")
    print(name + " has joined the server!")
    
    reciever.start()
    sender.start()
    

def sendMessages():
    print("\n")
    print("You can now enter messages!" +"\n")
    while(True):
        message = input("")
        initial = ""
        if len(message) >= 1:
            if(len(message) >= 6):
                for x in range(6):
                    initial += message[x]
                if(initial == "/image"):
                    import drawer
                else:
                    c.send(b'message\r\n')
                    rsaFunctions.encrypt(pubKey, message,c)
            else:
                c.send(b'message\r\n')
                rsaFunctions.encrypt(pubKey, message,c)

def recieveMessages():
    while(True):
        types = c.recv(1)
        data = b''
        if(types):
            while(True):
                while not types.__contains__(b'\r\n'):
                    types += c.recv(1)
                if types == b'image\r\n':
                    while not data.__contains__(b'\r\n\r\n'):
                        data += c.recv(10)
                    data = data[:-4]
                    f = open("picof.png","wb")
                    f.write(data)
                    f.close()
                    im = Image.open("picof.png")
                    layout = [
                        [sg.Image(key='-IMAGE-', size=(im.width,im.height))],
                    ]
                    window = sg.Window("epic", layout, margins=(0, 0), finalize=True)
                    image = ImageTk.PhotoImage(image=im)
                    window['-IMAGE-'].update(data=image)
                    window.read()
                elif types == b'message\r\n':
                        #recieve message
                        byte = b''
                        while not byte.__contains__(b'\r\n'):
                            byte += c.recv(1)
                        byte = byte[:-2]
                        decrypted = rsaFunctions.decrypt(priv, byte)
                        print("\n")
                        print("             " + name + ": " + str(decrypted) + "\n")
                        data = b''
                        break
    
        
        
