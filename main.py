import protocol_server
import protocol_client
def start():
    clientOrServer = input("Type 1 to start a server, type 2 to start a client: ")
    if clientOrServer == "2":
        protocol_client.main()
    elif clientOrServer == "1":
        protocol_server.main()
if __name__ == '__main__':
    start()