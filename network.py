import socket
import pickle

class Network:
    def __init__ (self, server_ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip #ip address of server
        print(self.server)
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect (self):
            try:
                self.client.connect(self.addr)
                return pickle.loads(self.client.recv(2048)) 
            except Exception as e:
                 print("Connection error: ", e)
                 return None
            
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print("Socket error: ", e)
            return None
            