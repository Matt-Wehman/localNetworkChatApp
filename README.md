# FPP (Fake PictoChat Protocol)

## Introduction
This protocol is built to mock the chat room functionality of the pitcoChat application on the nintendo DS lite. The protocol will run on a TCP backend. 

## How to use

### Setup
- Pip install pillow, PySimpleGUI, and tkinter
- Make sure you are using two computers on the same network OR use the same computer to host both the client and server.
- If you are using two computers find the ip address of the server computer.
- Download the program on the server and client computer
- On both computers change the variable `SERVER_PORT` in `protocol_server.py` and `protocol_client.py` to the ip of the server.
- If using the same computer then make sure the `SERVER_PORT` variable is set to localhost.

### Host and Connect to Chat

- Run the `Main.py` file on the server and client pc.
- On the server click the "host" button then set a password and username.
- The client should now click "join" and enter the password.
- The computers should now be connected! (if not just try running the program again on both machines)

### How to draw and send an image
- Within the textox type the command `/image`
- Draw an image
- Click the "send" button on the bottom right section of the pop-up window
- Exit out of the pop-up window 
- Click the "send" button under the text box (the same one you use to send a message).


## Features
- Block size(images), content length(password), and unknown length transfer support(messages)
- RSA 16 bit encryption
- Password protected
- Drawing image support



