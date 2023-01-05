import socket
import threading
import rsa
import zlib
import json

class Config:
    def __init__(self):
        with open('server.json')as file: config_file=json.load(file)
        self.config={
            'ip': config_file['ip'],
            'port': config_file['port'],
            'buffer': config_file['buffer'],
        }

class RSA:
    def __init__(self, pub_key, priv_key):
        self.public_key = pub_key
        self.private_key = priv_key

    def encrypt(self, msg: str):
        return rsa.encrypt(msg, self.public_key)

    def decrypt(self, msg: bytes):
        return rsa.decrypt(msg, self.private_key)

class Client:
    def __init__(self):

        self.ip=Config().config['ip']
        self.port=int(Config().config['port'])
        self.buffer=int(Config().config['buffer'])

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.ip, self.port))

        self.private_key=rsa.PrivateKey.load_pkcs1(zlib.decompress(self.server.recv(self.buffer)))
        self.public_key=rsa.PublicKey.load_pkcs1(zlib.decompress(self.server.recv(self.buffer)))

        self.RSA = RSA(self.public_key,self.private_key)

        print('''
███████╗███████╗ ██████╗     ██████╗██╗     ██╗███████╗███╗   ██╗████████╗
██╔════╝██╔════╝██╔════╝    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝
███████╗█████╗  ██║         ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   
╚════██║██╔══╝  ██║         ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   
███████║███████╗╚██████╗    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   
╚══════╝╚══════╝ ╚═════╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   
                        Socket encrypted chat                                                                                                                      
        ''')
        threading.Thread(target=self.recv_thread, args=(self.server, self.buffer)).start()

        while True:
            msg = input('')
            self.server.send( self.RSA.encrypt(msg.encode()) )

    def recv_thread(self, sv, buffer):
        while True:
            print(self.RSA.decrypt(sv.recv(buffer)).decode())

Client()
