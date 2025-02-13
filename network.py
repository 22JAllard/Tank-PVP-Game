import socket
import pickle

class Network:
    def __init__ (self, server_ip, client_colour):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip #ip address of server
        print("Connecting to server: ", self.server)
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connected = False
        self.initial_data = self.connect(client_colour)

    def connect (self, client_colour):
        try:
            self.client.connect(self.addr)
            self.client.settimeout(5.0)  # 5 second timeout
            self.connected = True
            print("Connected successfully")
            
            # Send client color
            self.client.send(pickle.dumps(client_colour))
            
            # Receive initial data
            data = self.client.recv(2048)
            if not data:
                print("No initial data received")
                return False
                
            initial_data = pickle.loads(data)
            print(f"Received initial data: {initial_data}")
            return initial_data
        except socket.timeout:
            print("Connection timed out")
            self.disconnect()
            return False
        except Exception as error:
            print("Connection error:", error)
            self.disconnect()
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
        if not self.connected:
            return None
            
        try:
            # Send player data
            self.client.send(pickle.dumps(data))
            
            # Receive updated game state
            received_data = self.client.recv(2048)
            if received_data:
                return pickle.loads(received_data)
            return None
        except Exception as error:
            print(f"Sending error: {error}")
            self.disconnect()
            return None
                
        except socket.timeout:
            print("Send/receive timed out")
            self.disconnect()
            return None
        except socket.error as error:
            print(f"Send error:", error)
            self.disconnect()
            return None
        except Exception as error:
            print(f"Unexpected error:", error)
            self.disconnect()
            return None
        
    def disconnect(self):
        self.connected = False
        try:
            self.client.close()
        except Exception as e:
            print(f"Error during disconnect: {e}")