import socket
from _thread import *
import pickle 
import random
from os import path
from tank import Tank
from bullet import Bullet

server = "0.0.0.0"
port = 5555

hostname = socket.gethostname()
addresses = socket.getaddrinfo(hostname, None)
for addr in addresses:
    if addr[0] == socket.AF_INET:  
        print(f"Server IP addresses:  {addr[4][0]}")

maplimit = 1
mapnumber = random.randint(1,maplimit)
players = {}
bullets = {}
current_id = 0

player_positions = [

    (2,2),
    (45, 2),
    (2, 45),
    (45, 45),
    (2, 25),
    (25, 2)

]

def player_connected(client_colour):
    global current_id
    position_index = len(players) % len(player_positions)
    x, y = player_positions[position_index]
    
    # Create new tank
    new_tank = Tank(x, y, client_colour)  # Default red color
    players[current_id] = new_tank
    
    player_id = current_id
    current_id += 1
    return player_id

def tank_fired():
    #similar to player_connected
    #called when a tank has fired (f key press)
    #create a new instance of the bullet class, 
    # ^which will start at the tanks bulletx/y pos, be the same colour as the tank, and connected to the firing tank using their player id

    pass

def loadlevel():
    level_file = f'map{mapnumber}.txt'
    if path.exists(level_file):
        with open(level_file, 'rb') as f:
            return pickle.load(f)
    return None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server,port)) #connecting server and port

except socket.error as e: #in case stuff doesnt work
    print("Bind failed..", str(e))
    exit()

s.listen(6) #number dictates how many people can connect
print("Server Started\nWaiting for connections...")

TANK_IMAGES = {}

def client_thread(conn):
    try:
        print("Sending map data, map number = ", mapnumber)

        colour_and_scale_data = pickle.loads(conn.recv(2048))
        client_colour = colour_and_scale_data(0)
        client_scale = colour_and_scale_data(1)
        print(client_colour, client_scale)
        player_id = player_connected(client_colour)
        print(f"New player connected. ID: {player_id}")
        
        initial_data = {
            "map_number": mapnumber,
            "player_id": player_id,
            "tank": players[player_id]
        }
        conn.sendall(pickle.dumps(initial_data))
            

        while True:
            try:
                data = pickle.loads(conn.recv(2048))
                players[player_id] = data
                #add to send bullet data here?
                
                conn.sendall(pickle.dumps(players))
            except:
                break
        
    except Exception as e:
        print("Error: ", e)

    finally:

        if player_id in players:
            del players[player_id]
            print(f"Player {player_id} disconnected")
        conn.close()



while True:
    conn, addr = s.accept() #accept incoming connections, store stuff
    print(f"Connected from: {addr}")
    start_new_thread(client_thread, (conn,))