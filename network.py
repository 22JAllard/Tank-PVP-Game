import socket
import pickle
import pygame

class Network:
    def __init__ (self, server_ip, client_colour, scale):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip #ip address of server
        print("Connecting to server: ", self.server)
        self.port = 5555
        self.addr = (self.server, self.port)
        self.initial_data = self.connect(client_colour, scale)

    def connect (self, client_colour, scale):
        try:
            print("1")
            self.client.connect(self.addr)
            self.client.settimeout(5.0)  # 5 second timeout
            self.connected = True
            print("Connected successfully")
            
            print("2")
            # Send client colour
            colour_and_scale = (client_colour, scale)
            self.client.send(pickle.dumps(colour_and_scale)) ####THE ISSUE WAS SCALE IS THE PROTOCOL
            
            print("3")
            # Receive initial data
            data = self.client.recv(4096)
            if not data:
                print("No initial data received")
                return False

            print("4")
            return pickle.loads(data)
        except socket.timeout:
            print("Connection timed out")
            self.disconnect()
            return False
        except Exception as error:
            print("Connection error:", error)#
            self.disconnect()
            return False
            
    def receive_map_number(self):
        try:
            data = self.client.recv(8192)
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
            received_data = self.client.recv(4096)
            if not received_data:
                print("No data received from server")
                self.disconnect()
                return None
                
            return pickle.loads(received_data)
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
        except:
            pass