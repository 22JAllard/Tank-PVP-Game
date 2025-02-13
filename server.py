import socket
from _thread import *
import pickle 
import random
from os import path
from tank import Tank

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
current_id = 0
player_id = None

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
    new_tank = Tank(x, y, client_colour, 40, 40)  # Default red color
    players[current_id] = new_tank
    
    player_id = current_id
    current_id += 1
    return player_id

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

        client_colour = pickle.loads(conn.recv(2048))
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