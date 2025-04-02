#import libraries
import socket
from _thread import *
import pickle 
import random
from os import path
from tank import Tank
from bullet import Bullet

#define server and ports, server is set to a placeholder
server = "0.0.0.0"
port = 5555

#gets the server ip and prints 
hostname = socket.gethostname()
addresses = socket.getaddrinfo(hostname, None)
for addr in addresses:
    if addr[0] == socket.AF_INET:  
        print(f"Server IP addresses:  {addr[4][0]}")

#define variable
maplimit = 2 #number of available maps
mapnumber = random.randint(1,maplimit) #selecting a random map number
print("Selected map number", mapnumber) 
players = {} #create empty dictionaries to add instances to later
bullets = {}
response_bullets = {}
bullet_count = 0
current_id = 0
client_bullet_count = 0

#the possible spawn co-ordinates for each player, based off the 50x50 grid
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
    x, y = player_positions[position_index] #getting the x and y spawn values using the calculated position_index and the pre-set list in player_positions
    player_id = current_id #which number is the player

    new_tank = Tank(x, y, client_colour, scale, player_id) #creates a new tank instance  
    players[current_id] = new_tank #stores the new tank data in the servers player array
    current_id += 1 #increments the current_id
    return player_id #return the player number

def tank_fired(player_id, bullet_data): #only run if fire_data being sent is not none
    if player_id in players: #if the players id can be found in the players list
        for bullet_id in bullets: #for each bullet_id in the bullets list
            if bullet_id.startswith(f"{player_id}_"): #checks if the bullet id starts with the players id and then a _
                return None #returns nothing if it does
            
        tank = players[player_id] #stores the tank instance at position player_id in players in the tank variable
        bullet_x, bullet_y, bullet_angle, bullet_colour = bullet_data #splits up bullet data to store the x, y, angle and colour seperately
        new_bullet = Bullet(bullet_x, bullet_y, bullet_colour, bullet_angle) #creates a new instance of the bullet using the data that has just been stored
        bullet_id = f"{player_id}_{len(bullets)}" #creates an ID for the bullet using the player_id who fired it, and also how many bullets have been fired
        bullets[bullet_id] = new_bullet #stores the new bullet that has been created in the bullets list, with the bullet_id
        print(f"Created new bullet {bullet_id} for player {player_id}")
        return bullet_id
    return None

def loadlevel():
    level_file = f'map{mapnumber}.txt' #saving the map file in level_file
    if path.exists(level_file): #checking that the map file can be found
        with open(level_file, 'rb') as f: #opens the level file in binary read mode, as f
            return pickle.load(f) #return the data from the file, and pickle it
    return None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates a TCP socket, AF_INET sets it as an IPv4 address, and SOCK_STREAM that the socket will use TCP

try:
    s.bind((server,port)) #connecting the socket to a specific IP/server and port

except socket.error as e: 
    print("Bind failed..", str(e))
    exit()

s.listen(6) #sets the maximum number of connections which can join in the server lifetime
print("Server Started\nWaiting for connections...")

TANK_IMAGES = {}

def client_thread(conn):
    global players, current_id, response_data, response_bullets
    sent_bullets = set() #creates an empty set which can be used to track bullets which have been sent to clients
    try:
        print("Sending map data, map number = ", mapnumber)

        colour_and_scale_data = pickle.loads(conn.recv(4096)) #receive data from the clients and store it
        client_colour = colour_and_scale_data[0] #split the received data into colour and scale, and store seperately
        client_scale = colour_and_scale_data[1]
        print("Connected clients colour: ",client_colour)
        print("Connected clients scale: ", client_scale)
        player_id = player_connected(client_colour, client_scale) #calls the player_connected function, sending it both the received colour and scale, and stores the returned data in player_id
        print(f"New player connected. ID: {player_id}")
        
        initial_data = { #creates a dictionary with the initial data to send back to client
            "map_number": mapnumber,
            "player_id": player_id,
            "tank": players[player_id] #only send the connecting clients tank, which is in the players list with the player_id
        }
        conn.sendall(pickle.dumps(initial_data)) #send the created dictionary back to client

        while True: #main server loop
            try:
                conn.setblocking(True) #sets the socket to blocking mode, means send and receive calls wait until data is available

                player_count = len(players) #calculates how many players are in the players list

                data = conn.recv(4096) #receive data, still pickled 
                if not data: #if the data received is empty
                    print(f"Client {player_id} sent empty data, closing the connection")
                    break
                recieved_data = pickle.loads(data) #unpickle the data and store it

                if isinstance(recieved_data, tuple) and recieved_data[0] == "Bullet": #check if the received data is a tuple, and that there is an element which is a bullet
                    bullet_data = recieved_data[1] #stores the bullet data from the received data variable
                    tank_fired(player_id, bullet_data) #calls the tank_fired function and sends the player_id and bullet data
                elif isinstance(recieved_data, dict): #if the recieved data is a dictionary
                    if 'players' in recieved_data: #if there is a players key
                        players[player_id] = recieved_data['players'] #store the data after the player key in received data in the players dictionary, with the player_id
                    else:
                        players[player_id] = recieved_data #store all the received data in the players list
                    
                    if 'bullets' in recieved_data and recieved_data['bullets'] and not (isinstance(recieved_data['bullets'], tuple) and len(recieved_data['bullets']) == 0): #checks for a bullets key, that the bullets section is not empty, checks that the bullets section is not an empty tuple
                        global client_bullet_count
                        bullet_data = recieved_data['bullets'] #store the values in the bullets key from the recieved data dictionary
                        new_bullet_x, new_bullet_y, new_bullet_angle, new_bullet_colour = bullet_data #split up the contents of the bullet_data into x, y, angle and colour
                        new_bullet = Bullet(new_bullet_x, new_bullet_y, new_bullet_colour, new_bullet_angle) #create a new instance of the Bullet class, using the new split data
                        global bullet_count
                        bid = (f"{player_id}_{bullet_count}") #create a bullet id based on the player_id of the player who fired it, and what number bullet it is
                        print("Created new bullet, ID:", bid)
                        bullet_count += 1 #increment bullet count
                        response_bullets[bid] = new_bullet #store the new bullet instance in the response_bullets dictionary with the bullet id as key
                        client_bullet_count = player_count #store the player count in the client_bullet_count variable

                else:
                    players[player_id] = recieved_data #store all the received data in the players dictionary with the player id key

                response_data = { #create a dictionary with players and bullets keys
                    "players": players,
                    "bullets": response_bullets
                } 

                conn.sendall(pickle.dumps(response_data)) #send the newly created response data dictionary to client
                if client_bullet_count > 0: #if the client_bullet_count is more than 0, subtract one
                    client_bullet_count -= 1
                if client_bullet_count == 0: #if the client_bullet_count is 0, make response_bullets and empty dictionary
                    response_bullets = {}

            except ConnectionError as e:
                print(f"Connection error for {player_id}: {e}")
                break
            except Exception as e:
                print(f"Unexpected error for {player_id}: {e}")
                break
        
    except Exception as e:
        print("Initial connection error: ", e)

    finally:

        if player_id in players: #checks if the player exists in the players dictionary
            del players[player_id] #if it does, remove said player from the dictionary
            bullets_removing = [bid for bid in bullets if bid.startswith(f"{player_id}_")] #find all of the bullets for that player, and add them to bullets_removing
            for bid in bullets_removing: #delete the bullets in bullets_removing
                del bullets[bid]
            print(f"Player {player_id} disconnected")
        conn.close() #close that connection

while True:

    conn, addr = s.accept() #accept incoming connections, and store the connection object and address
    print(f"Connected from: {addr}")
    start_new_thread(client_thread, (conn,)) #create a new thread to handle the client connection