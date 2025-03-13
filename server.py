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

maplimit = 2
mapnumber = random.randint(1,maplimit)
print("Selected map number", mapnumber)
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

def player_connected(client_colour, scale):
    global current_id
    position_index = len(players) % len(player_positions) #working out which position to give the new tank
    x, y = player_positions[position_index] #where the tank spawns
    
    # Create new tank
    new_tank = Tank(x, y, client_colour, scale)  
    players[current_id] = new_tank #stores the new tank data in the servers player array. as a tuple with x co-ordinate, y co-ordinate, the colour, and the scale value for the client
    
    player_id = current_id #which number is the player
    current_id += 1
    return player_id

def tank_fired(player_id, bullet_data): #only run if fire_data being sent is not none
    #print("Player ID, ", player_id, "\n PLayers: ", players)
    if player_id in players:
        for bullet_id in bullets:
            if bullet_id.startswith(f"{player_id}_"):
                #print(f"Player {player_id} already has an active bullet: ", bullet_id)
                return None
            
        tank = players[player_id]
        bullet_x, bullet_y, bullet_angle, bullet_colour = bullet_data
        new_bullet = Bullet(bullet_x, bullet_y, bullet_colour, bullet_angle)
        bullet_id = f"{player_id}_{len(bullets)}"
        bullets[bullet_id] = new_bullet
        print(f"Created new bullet {bullet_id} for player {player_id}")
        new_bullet.move()
        return bullet_id
    return None

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
    global players, current_id
    try:
        print("Sending map data, map number = ", mapnumber)

        colour_and_scale_data = pickle.loads(conn.recv(4096))#
        client_colour = colour_and_scale_data[0] #this bits new and above below
        client_scale = colour_and_scale_data[1]#
        print("Connected clients colour: ",client_colour)
        print("Connected clients scale: ", client_scale)
        player_id = player_connected(client_colour, client_scale) 
        #something which calls the bullet function
        print(f"New player connected. ID: {player_id}")
        
        initial_data = {
            "map_number": mapnumber,
            "player_id": player_id,
            "tank": players[player_id]
        }
        conn.sendall(pickle.dumps(initial_data))

        while True:
            try:
                conn.setblocking(True)

                data = conn.recv(4096) #just all the tank pos
                if not data:
                    print(f"Client {player_id} sent empty data, closing the connection")
                    break
                recieved_data = pickle.loads(data)

                if isinstance(recieved_data, tuple) and recieved_data[0] == "Bullet":
                    bullet_data = recieved_data[1] #might need to be a [1:]??
                    tank_fired(player_id, bullet_data)
                else:
                    players[player_id] = recieved_data
                    #print(f"Receied tank data from {player_id}")

                response_data = {
                    "players": players,
                    "bullets": bullets
                }
                conn.sendall(pickle.dumps(response_data))

            except ConnectionError as e:
                print(f"Connection error for {player_id}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error for {player_id}: {e}")
                break
        
    except Exception as e:
        print("Initial connection error: ", e)

    finally:

        if player_id in players:
            del players[player_id]
            bullets_removing = [bid for bid in bullets if bid.startswith(f"{player_id}_")]
            for bid in bullets_removing:
                del bullets[bid]
            print(f"Player {player_id} disconnected")
        conn.close()

while True:
    conn, addr = s.accept() #accept incoming connections, store stuff
    print(f"Connected from: {addr}")
    start_new_thread(client_thread, (conn,))