import socket
import threading
import rsa
import zlib

clients_ip = []
clients = []

class Config:
    def __init__(self):
        self.config={
            'ip': '192.168.1.7',
            'port': 9001,
            'buffer': 2048
        }
    
class RSA:
    def __init__(self, pub_key, priv_key):
        self.public_key = pub_key
        self.private_key = priv_key

    def encrypt(self, msg: str):
        return rsa.encrypt(msg, self.public_key)

    def decrypt(self, msg: bytes):
        return rsa.decrypt(msg, self.private_key)

class Server:
    def __init__(self):

        self.ip=Config().config['ip']
        self.port=int(Config().config['port'])
        self.buffer=int(Config().config['buffer'])

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(100)

        print('''
███████╗███████╗ ██████╗    ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ 
██╔════╝██╔════╝██╔════╝    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
███████╗█████╗  ██║         ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
╚════██║██╔══╝  ██║         ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗
███████║███████╗╚██████╗    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
╚══════╝╚══════╝ ╚═════╝    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝    
                            Socket encrypted chat''')

        # generate keys
        self.public_key, self.private_key = self.create_keys()

        self.RSA = RSA(self.public_key,self.private_key)

        public_key_exported = rsa.PublicKey.save_pkcs1(self.public_key)
        public_key_exported = zlib.compress(public_key_exported, 7)

        private_key_exported = rsa.PrivateKey.save_pkcs1(self.private_key)
        private_key_exported = zlib.compress(private_key_exported, 7)
    
        while True:
            conn, addr = self.server.accept()

            # send keys
            conn.send(private_key_exported)

            conn.send(public_key_exported)
            
            client_ip = str(str(conn).split("laddr=('")[1]).split("'")[0]

            if conn in clients:
                conn.send(self.RSA.encrypt("You're already connected".encode()))
            else:
                conn.send(self.RSA.encrypt("Connected successfully".encode()))
                print('<'+client_ip+'> Hi!')
                clients.append(conn)
                
            threading.Thread(target=self.recv_thread, args=(client_ip, conn)).start()
            
    def recv_thread(self, client_ip, conn):
        while True:
            try:
                msg = '<'+client_ip+'> '+self.RSA.decrypt(conn.recv(self.buffer)).decode()
                for client in clients:
                    client.send(self.RSA.encrypt(msg.encode()))

            except Exception as e:
                print('[ error ] '+str(e))
                break

    def create_keys(self):
        public_key, private_key = rsa.newkeys(self.buffer)
        return public_key, private_key

Server()