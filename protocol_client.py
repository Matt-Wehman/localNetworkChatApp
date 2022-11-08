
import threading
from socket import *
import rsaFunctions
PUBLIC_EXPONENT = 17;
SERVER_HOST = 12100
SERVER_PORT = "localhost"
import os
import io
import PySimpleGUI as sg
global lock
import PIL.Image as Image
from PIL import ImageFile, ImageTk
ImageFile.LOAD_TRUNCATED_IMAGES = True

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
        initial = "";
        if len(message) >= 1:
            if(len(message) >= 6):
                for x in range(6):
                    initial += message[x]
                if(initial == "/image"):
                    print("WORKING POG")
                    f = open(r"C:\Users\wehmanm\OneDrive - Milwaukee School of Engineering\Desktop\NP final\final-protocol\images\hqdefault.jpg", "rb").read()
                    tcp_socket.sendall(b'image\r\n' + f + b'\r\n\r\n')
                else:
                    tcp_socket.send(b'message\r\n')
                    rsaFunctions.encrypt(pubKey, message,tcp_socket)
            else:
                tcp_socket.send(b'message\r\n')
                rsaFunctions.encrypt(pubKey, message,tcp_socket)
            

def recieveMessages():
    while(True):
        types = tcp_socket.recv(1)
        data = b''
        if(types):
            while(True):
                while not types.__contains__(b'\r\n'):
                    types += tcp_socket.recv(1)
                if types == b'image\r\n':
                    while not data.__contains__(b'\r\n\r\n'):
                        data += tcp_socket.recv(10)
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
                            byte += tcp_socket.recv(1)
                        byte = byte[:-2]
                        decrypted = rsaFunctions.decrypt(priv, byte)
                        print("\n")
                        print("             " + name + ": " + str(decrypted) + "\n")
                        data = b''
                        break

if __name__ == "__main__":
    main()
