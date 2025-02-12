import socket
import pickle

class Network:
    def __init__ (self, server_ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip #ip address of server
        print("Connecting to server: ", self.server)
        self.port = 5555
        self.addr = (self.server, self.port)
        self.initial_data = self.connect()
        self.player_id = self.initial_data["player_id"]
        self.player = self.initial_data["tank"]

    def connect (self):
            try:
                self.client.connect(self.addr)
                print("Connected successfully")
                return pickle.loads(self.client.recv(2048))
            except Exception as error:
                print("Connection error:", error)
                return False
            
    def receive_map_number(self):
        try:
            data = self.client.recv(4096)
            if data:
                return pickle.loads(data)
            else:
                print("No data received from server")
                return None
        except Exception as e:
            print("Error receiving map number:", e)
            return None
        
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)
            return None