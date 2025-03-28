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
response_bullets = {}
bullet_count = 0
current_id = 0
client_bullet_count = 0

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
    
    player_id = current_id #which number is the player


    # Create new tank
    new_tank = Tank(x, y, client_colour, scale, player_id)  
    players[current_id] = new_tank #stores the new tank data in the servers player array. as a tuple with x co-ordinate, y co-ordinate, the colour, and the scale value for the client
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
        #new_bullet.move()
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
    global players, current_id, response_data, response_bullets
    sent_bullets = set()
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

                player_count = len(players)
                # print(player_count)

                data = conn.recv(4096) #just all the tank pos
                if not data:
                    print(f"Client {player_id} sent empty data, closing the connection")
                    break
                recieved_data = pickle.loads(data)
                # print("Received data = ",recieved_data)

                if isinstance(recieved_data, tuple) and recieved_data[0] == "Bullet":
                    bullet_data = recieved_data[1] #might need to be a [1:]??
                    tank_fired(player_id, bullet_data)
                elif isinstance(recieved_data, dict):
                    if 'players' in recieved_data:
                        players[player_id] = recieved_data['players']
                    else:
                        players[player_id] = recieved_data
                    
                    if 'bullets' in recieved_data and recieved_data['bullets'] and not (isinstance(recieved_data['bullets'], tuple) and len(recieved_data['bullets']) == 0):
                        global client_bullet_count
                        bullet_data = recieved_data['bullets']
                        # tank_fired(player_id, bullet_data)
                        # print(bullet_data) #(45.2, 97, 0, (255, 0, 0))
                        new_bullet_x, new_bullet_y, new_bullet_angle, new_bullet_colour = bullet_data
                        new_bullet = Bullet(new_bullet_x, new_bullet_y, new_bullet_colour, new_bullet_angle)
                        #add bid vv (bullet id)
                        global bullet_count
                        bid = (f"{player_id}_{bullet_count}")
                        print("Created new bullet, ID:", bid)
                        bullet_count += 1
                        response_bullets[bid] = new_bullet #this should be right but is dependent on ^^
                        client_bullet_count = player_count

                        # print(response_bullets)
                else:
                    players[player_id] = recieved_data

                    #print(f"Receied tank data from {player_id}")
                
                # response_bullets = {bid: bullet for bid, bullet in bullets.items() 
                #                   if bid not in sent_bullets}

                # print(players) #currently {0: {'players': <tank.Tank object at 0x00000120DF6A0FA0>}, 1: <tank.Tank object at 0x00000120DF6A0700>} #should be 0: <tank.Tank>, 1: <tank.Tank>
                # send_bullets = bullets
                # print("Send_bullets: ", send_bullets)

                # if response_bullets != "()":
                response_data = {
                    "players": players,
                    "bullets": response_bullets
                }
                # else:
                #     response_data = {
                #         "players": players
                #     }
                # print(response_data)
                # print("Sending data: ",response_data)
                conn.sendall(pickle.dumps(response_data)) #this is sending the bullet again every single time, needs to send once and delete.
                if client_bullet_count > 0:
                    client_bullet_count -= 1
                if client_bullet_count == 0:
                    response_bullets = {}
                # sent_bullets.update(response_bullets.keys())


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