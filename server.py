import socket
from _thread import *
import pickle 
import random
from os import path

host = socket.gethostname()
server = socket.gethostbyname(host)
print (server)
port = 8888

maplimit = 1
mapnumber = random.randint(1,maplimit)

def loadlevel():
    if path.exists(f'map{mapnumber}.txt'):
        pickle_in = open(f'level{mapnumber}.txt', 'rb')
        map_data = pickle.load(pickle_in)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server,port)) #connecting server and port

except socket.error as e: #in case stuff doesnt work
    print(str(e))
    exit()

s.listen(6) #number dictates how many people can connect
print("Server Started\nWaiting for connections...")

while True:
    conn, addr = s.accept() #accept incoming connections, store stuff
    print("Connected to:", addr)