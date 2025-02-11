import socket
from _thread import *
import pickle 
import random
from os import path

host = socket.gethostname()
server = socket.gethostbyname(host)
print ("Server IP: ", server)
port = 5555

maplimit = 1
mapnumber = random.randint(1,maplimit)

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

def client_thread(conn):
    try:
        print("Sending map data, map number = ", mapnumber)
        data = pickle.dumps(mapnumber)
        conn.sendall(data)
    except Exception as e:
        print("Error: ", e)
    finally:
        conn.close()

while True:
    conn, addr = s.accept() #accept incoming connections, store stuff
    print(f"Connected from: {addr}")
    start_new_thread(client_thread, (conn,))