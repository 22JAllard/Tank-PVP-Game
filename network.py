import socket
import pickle
import pygame
import threading
import time

class Network:
    def __init__ (self, server_ip, client_colour, scale):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip #ip address of server
        print("Connecting to server: ", self.server)
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connected = False
        self.known_bullets = set()
        self.latest_data = None
        self.initial_data = self.connect(client_colour, scale)
        if self.connected:
            threading.Thread(target=self.receive_updates, daemon=True).start()

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
                self.connected = False
                return False

            return pickle.loads(data)
        except socket.timeout:
            print("Connection timed out")
            self.disconnect()
            return False
        except Exception as error:
            print("Connection error:", error)
            self.disconnect()
            return False
            
    def receive_updates(self):
        buffer = b""
        while True:
            if not self.connected:
                break
            try:
                received_data = self.client.recv(8192)
                if not received_data:
                    print("Server disconnected")
                    self.disconnect()
                    break
                buffer += received_data
                while True:
                    try:
                        received = pickle.loads(received_data)
                        buffer = b""
                        new_bullets = {bid: bullet for bid, bullet in received["bullets"].items()
                                    if bid not in self.known_bullets}
                        if new_bullets:
                            print(f"Client received new bullets: {new_bullets.keys()}")
                        self.known_bullets.update(new_bullets.keys())
                        self.latest_data = received
                        break
                    except pickle.UnpicklingError:
                        break
                    except Exception as e:
                        print(f"Receive error: {e}")
                        self.disconnect()
                        break
            except socket.error as e:
                print("Socket errror:", e)
                self.disconnect
                break

    def get_latest_data(self):  
        return self.latest_data

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
            self.client.send(pickle.dumps(data))
            return True
            # self.client.setblocking(True)
            # received_data = self.client.recv(4096)


            # if not received_data:
            #     print("No data received from server")
            #     self.disconnect()
            #     return None
  
            # return pickle.loads(received_data) #contains both tanks and bullets
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
        time.sleep(0.2)
        try:
            self.client.close()
        except:
            pass

    def send_bullet(self, data):
        if not self.connected:
            return None
            
        try:
            # Send bullet data
            bullet_data = ("Bullet", data)
            self.client.send(pickle.dumps(bullet_data))
            buffer = b""
            while True:
                data = self.client.recv(8192)
                if not data:
                    print("No data received from server (bullet)")
                    self.disconnect()
                    return None
                buffer += data
                try:
                    received = pickle.loads(buffer)
                    self.latest_data = received  # Update immediately
                    print(f"Send_bullet received: {received}")
                    break
                except pickle.UnpicklingError:
                    continue  # Wait for complete data
            return True

        except socket.timeout:
            print("Send/receive timed out (bullet)")
            self.disconnect()
            return None
        except socket.error as error:
            print(f"Send error (bullet):", error)
            self.disconnect()
            return None
        except Exception as error:
            print(f"Unexpected error (bullet):", error)
            self.disconnect()
            return None