import socket
import pickle

class Network:
    def __init__ (self, server_ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip #ip address of server
        print("Connecting to server: ", self.server)
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect (self):
            try:
                self.client.connect(self.addr)
                print("Connected successfully")

                full_data = b""
                while True:
                    packet = self.client.recv(4096)
                    if not packet:
                        break
                    full_data += packet
                if full_data:
                    return pickle.loads(full_data)
                else:
                    print("Error: No data recieved from server")
                    return None 
                    
            except Exception as e:
                 print("Connection error: ", e)
                 return None
            
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))

            full_data = b""
            while True:
                packet = self.client.recv(4096)
                if not packet:
                    break
                full_data += packet

            if full_data:
                return pickle.loads(full_data)
            else:
                print("Error: No response from server")
                return None
        except socket.error as e:
            print("Socket error: ", e)
            return None
            