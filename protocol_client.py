import random
import math
from socket import *
import prime_generator_ex
PUBLIC_EXPONENT = 17;

def main():
    """Provide the user with a variety of encryption-related actions"""

    # Get chosen operation from the user.
    while True:
        action = input(
            "Select an option from the menu below:\n"
            "(1-CS) create_server\n"
            "(2-JS) join_server\n"
        )
        # Execute the chosen operation.
        if action in ["1", "CS", "cs", "create server"]:
            createServer(12100,"localhost")
        elif action in ["2", "JS", "js", "join server"]:
            createClient(12100,"localhost")
        else:
            print("Unknown action: '{0}'".format(action))
            break

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
    password = input (
            "Create a password\n"
        )
            #create socket and listen for connection
    paddedPass = password.zfill(20)
    address = (listen_on, listen_port)
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(5)
    c, addr = s.accept()
    print('got connection from addr', address)
    #create keys
    key_pair = create_keys()
    e,d,n = key_pair
    pub = get_public_key(key_pair)
    print("Pub key: " + str(pub))
    priv = get_private_key(key_pair)
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
    
    while(True):
        guess = b''
        for x in range(20):
            guess += c.recv(4)
        if decrypt(priv,guess) != paddedPass:
            c.send(b'F')
        else:
            c.send(b'A')
            break
        
    while(True):
        #recieve message
        m = c.recv(2)
        byte = b''
        while not byte.__contains__(b'\r\n'):
            byte += c.recv(1)
        byte = byte[:-2]
        decrypted = decrypt(priv, byte)
        print("Decrypted message:", decrypted)
        c.send(b'A')
        
def decrypt(priv,byte):
    message = byte.decode('ASCII')
    decrypted = ""
    for i in range(0, len(message), 4):
        enc_string = message[i: i + 4]
        enc = int(enc_string, 16)
        dec = apply_key(priv, enc)
        if dec >= 0 and dec < 256:
            decrypted += chr(dec)
        else:
            print("Warning: Could not decode encrypted entity: " + enc_string)
            print("         decrypted as: " +
                    str(dec) + " which is out of range.")
            print("         inserting _ at position of this character")
            message += "_"
    return decrypted
    
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
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.connect((server_port, server_host))
        
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
    pubKey = (e,n)
    encryptPass(pubKey,password,tcp_socket)
    while(True):
        response = tcp_socket.recv(1)
        if response != b'A':
            password = input(
            "Wrong Password Try Again: \n"
            )
            encryptPass(pubKey,password,tcp_socket)
        else:
            break
    
    while(True):
        message = input("Enter a message: ")
        encrypt(pubKey, message,tcp_socket)
        

def encrypt(pubKey, message, tcp_socket):
    encrypted = ""
    for c in message:
        encrypted += "{0:04x}".format(apply_key(pubKey, ord(c)))
    size = encrypted.encode().__sizeof__()
    tcp_socket.send(int.to_bytes(size, 2, 'big'))
    tcp_socket.send(encrypted.encode())
    tcp_socket.send(b'\r\n')
        
def encryptPass(pubKey,password, tcp_socket):
    padded = str(password).zfill(20)
    encrypted = ""
    for c in padded:
        encrypted += "{0:04x}".format(apply_key(pubKey, ord(c)))
    tcp_socket.sendall(encrypted.encode())


def get_public_key(key_pair):
    """
    Pulls the public key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (e,n)
    """
    return (key_pair[0], key_pair[2])


def get_private_key(key_pair):
    """
    Pulls the private key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (d,n)
    """

    return (key_pair[1], key_pair[2])


def create_keys_interactive():
    """
    Create new public keys

    :return: the private key (d, n) for use by other interactive methods
    """

    key_pair = create_keys()
    pub = get_public_key(key_pair)
    priv = get_private_key(key_pair)
    print("Public key: ")
    print(pub)
    print("Private key: ")
    print(priv)
    return priv


def compute_checksum_interactive():
    """
    Compute the checksum for a message, and encrypt it
    """

    priv = create_keys_interactive()
    message = input("Please enter the message to be checksummed: ")
    hash = compute_checksum(message)
    print("Hash:", "{0:04x}".format(hash))
    cipher = apply_key(priv, hash)
    print("Encrypted Hash:", "{0:04x}".format(cipher))


def verify_checksum_interactive():
    """
    Verify a message with its checksum, interactively
    """

    pub = enter_public_key_interactive()
    message = input("Please enter the message to be verified: ")
    recomputed_hash = compute_checksum(message)

    string_hash = input("Please enter the encrypted hash (in hexadecimal): ")
    encrypted_hash = int(string_hash, 16)
    decrypted_hash = apply_key(pub, encrypted_hash)
    print("Recomputed hash:", "{0:04x}".format(recomputed_hash))
    print("Decrypted hash: ", "{0:04x}".format(decrypted_hash))
    if recomputed_hash == decrypted_hash:
        print("Hashes match -- message is verified")
    else:
        print("Hashes do not match -- has tampering occured?")


def encrypt_message_interactive():
    """
    Encrypt a message
    """

    message = input("Please enter the message to be encrypted: ")
    pub = enter_public_key_interactive()
    encrypted = ""
    for c in message:
        encrypted += "{0:04x}".format(apply_key(pub, ord(c)))
    print("Encrypted message:", encrypted)


def decrypt_message_interactive(priv=None):
    """
    Decrypt a message
    """

    encrypted = input("Please enter the message to be decrypted: ")
    if priv is None:
        priv = enter_key_interactive("private")
    message = ""
    for i in range(0, len(encrypted), 4):
        enc_string = encrypted[i: i + 4]
        enc = int(enc_string, 16)
        dec = apply_key(priv, enc)
        if dec >= 0 and dec < 256:
            message += chr(dec)
        else:
            print("Warning: Could not decode encrypted entity: " + enc_string)
            print("         decrypted as: " + str(dec) + " which is out of range.")
            print("         inserting _ at position of this character")
            message += "_"
    print("Decrypted message:", message)


def break_key_interactive():
    """
    Break key, interactively
    """

    pub = enter_public_key_interactive()
    priv = break_key(pub)
    print("Private key:")
    print(priv)
    decrypt_message_interactive(priv)


def enter_public_key_interactive():
    """
    Prompt user to enter the public modulus.

    :return: the tuple (e,n)
    """

    print("(Using public exponent = " + str(PUBLIC_EXPONENT) + ")")
    string_modulus = input("Please enter the modulus (decimal): ")
    modulus = int(string_modulus)
    return (PUBLIC_EXPONENT, modulus)


def enter_key_interactive(key_type):
    """
    Prompt user to enter the exponent and modulus of a key

    :param key_type: either the string 'public' or 'private' -- used to prompt the user on how
                     this key is interpretted by the program.
    :return: the tuple (e,n)
    """
    string_exponent = input("Please enter the " + key_type + " exponent (decimal): ")
    exponent = int(string_exponent)
    string_modulus = input("Please enter the modulus (decimal): ")
    modulus = int(string_modulus)
    return (exponent, modulus)


def compute_checksum(string):
    """
    Compute simple hash

    Given a string, compute a simple hash as the sum of characters
    in the string.

    (If the sum goes over sixteen bits, the numbers should "wrap around"
    back into a sixteen bit number.  e.g. 0x3E6A7 should "wrap around" to
    0xE6A7)

    This checksum is similar to the internet checksum used in UDP and TCP
    packets, but it is a two's complement sum rather than a one's
    complement sum.

    :param str string: The string to hash
    :return: the checksum as an integer
    """

    total = 0
    for c in string:
        total += ord(c)
    total %= 0x8000  # Guarantees checksum is only 4 hex digits
    # How many bytes is that?
    #
    # Also guarantees that the checksum will
    # always be less than the modulus.
    return total


# ---------------------------------------
# Do not modify code above this line
# ---------------------------------------

# Remeber to use the named constants as you write your code
# MAX_PRIME = 0b11111111  The maximum value a prime number can have
# MIN_PRIME = 0b11000001  The minimum value a prime number can have
# PUBLIC_EXPONENT = 17  The default public exponent

e = 17
def create_keys():
    """
    Create the public and private keys.

    :return: the keys as a three-tuple: (e,d,n)
    """

    primes = prime_generator_ex.generate_primes(100, 254)
    p = random.choice(primes)
    q = random.choice(primes)
    n = p * q
    lcm = math.lcm((p - 1), (q - 1))
    done = False
    d= 1
    while not done:
        if (e * d) % lcm == 1:
            done = True
        else: d = d + 1
    return e, d, n


def apply_key(key, m):
    """
    Apply the key, given as a tuple (e,n) or (d,n) to the message.

    This can be used both for encryption and decryption.

    :param tuple key: (e,n) or (d,n)
    :param int m: the message as a number 1 < m < n (roughly)
    :return: the message with the key applied. For example,
             if given the public key and a message, encrypts the message
             and returns the ciphertext.
    """
    a, n = key
    return pow(m,a) % n



def break_key(pub):
    """
    Break a key.  Given the public key, find the private key.
    Factorizes the modulus n to find the prime numbers p and q.

    You can follow the steps in the "optional" part of the in-class
    exercise.

    :param pub: a tuple containing the public key (e,n)
    :return: a tuple containing the private key (d,n)
    """
    e, n = pub
    p = 0
    q = 0
    primes = prime_generator_ex.generate_primes(1,int(n/2))
    for i in reversed(primes):
        for j in primes:
            if j * i == n:
                p = j
                q = i
                lcm = math.lcm((p-1), (q-1))
                done = False
                d = 1
                while not done:
                    if (e * d) % lcm == 1:
                        done = True
                        return (d,n)
                    else:
                        d = d + 1



if __name__ == "__main__":
    main()
