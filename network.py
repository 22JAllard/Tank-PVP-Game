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
            self.client.connect(self.addr)
            self.client.settimeout(10.0)  #10 second timeout
            self.connected = True
            print("Connected successfully")

            
            # Send client colour
            colour_and_scale = (client_colour, scale)
            self.client.send(pickle.dumps(colour_and_scale)) ####THE ISSUE WAS SCALE IS THE PROTOCOL
            
            # Receive initial data
            data = self.client.recv(4096)
            if not data:
                print("No initial data received")
                return False

            print("initial data", pickle.loads(data))
            return pickle.loads(data)
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
            data = self.client.recv(8192)
            if data:
                return pickle.loads(data)
            else:
                print("No data received from server")
                return None
        except Exception as e:
            print("Error receiving map number:", e)
            return None
        
    def send(self, data): #sends tank
        if not self.connected:
            return None
            
        try:
            # Send player data
            # print("Sending data, ", data)
            self.client.send(pickle.dumps(data))
            self.client.setblocking(True)
            received_data = self.client.recv(4096)
            # print("Received_data = ", pickle.loads(received_data))


            if not received_data:
                print("No data received from server")
                self.disconnect()
                return None
  
            return pickle.loads(received_data) #contains both tanks and bullets
        except socket.timeout:
            print("Send/receive timed out")
            self.disconnect()
            return None
        except socket.error as error:
            print(f"Send error:", error)
            self.disconnect()
            return None
        except Exception as error:
            print(f"Unexpected error: {error}")
            self.disconnect()
            return None

        
    def disconnect(self):
        self.connected = False
        try:
            self.client.close()
        except:
            pass

    # def send_bullet(self, data):
    #     if not self.connected:
    #         return None
            
<<<<<<< HEAD
    #     try:
    #         # Send bullet data
    #         bullet_data = ("Bullet", data)
    #         self.client.send(pickle.dumps(bullet_data))
    #         received_data = self.client.recv(4096)
    #         # print("Bullet received data = ", pickle.loads(received_data))
    #         if not received_data:
    #             print("No data received from server")
    #             self.disconnect()
    #             return None
    #         return pickle.loads(received_data)
=======
        try:
            # Send bullet data
            bullet_data = ("Bullet", data)
            self.client.send(pickle.dumps(bullet_data))
            received_data = self.client.recv(4096)
            if not received_data:
                print("No data received from server")
                self.disconnect()
                return None
            return pickle.loads(received_data)
>>>>>>> 746f84841987cf91e8867704d9b0cdf338c35540

    #     except socket.timeout:
    #         print("Send/receive timed out (bullet)")
    #         self.disconnect()
    #         return None
    #     except socket.error as error:
    #         print(f"Send error (bullet):", error)
    #         self.disconnect()
    #         return None
    #     except Exception as error:
    #         print(f"Unexpected error (bullet):", error)
    #         self.disconnect()
    #         return None