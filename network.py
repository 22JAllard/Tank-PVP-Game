#import libraries
import socket
import pickle

class Network:
    def __init__ (self, server_ip, client_colour, scale):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a TCP socket for the client (AF_INET = IPv4, SOCK_STREAM = TCP)
        self.server = server_ip #ip address of server
        print("Connecting to server: ", self.server)
        self.port = 5555 #same port as the server is using
        self.addr = (self.server, self.port) #create a tuple with the server ip and port
        self.initial_data = self.connect(client_colour, scale) #call the class' connect function with colour and scale

    def connect (self, client_colour, scale):
        try:
            self.client.connect(self.addr) #connect to the IP and port
            self.client.settimeout(10.0)  #10 second timeout
            self.connected = True #if the network is able to connect
            print("Connected successfully")

            colour_and_scale = (client_colour, scale) #create a tuple with the colour and scale
            self.client.send(pickle.dumps(colour_and_scale)) #send the colour and scale to server, serialised

            data = self.client.recv(4096) #receieve data from the server
            if not data: #if there is no data 
                print("No initial data received")
                return False

            return pickle.loads(data) #returns the data which was received
        
        except socket.timeout: #if there is an error/timeout, disconnect 
            print("Connection timed out")
            self.disconnect()
            return False
        except Exception as error:
            print("Connection error:", error)
            self.disconnect()
            return False
            
    def receive_map_number(self): 
        try:
            data = self.client.recv(8192) #receive and store data 
            if data:
                return pickle.loads(data) #return the unserialised data
            else:
                print("No data received from server") 
                return None
            
        except Exception as e:
            print("Error receiving map number:", e)
            return None
        
    def send(self, data): 
        if not self.connected: #only runs if the network is connected
            return None
            
        try:
            self.client.send(pickle.dumps(data)) #send the data passed into the function to server
            self.client.setblocking(True) #sets the socket to blocking mode, means send and receive calls wait until data is available
            received_data = self.client.recv(4096) #receive and store data from the client

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
            self.client.close() #close the connection
        except:
            pass