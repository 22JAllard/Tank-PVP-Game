import socket
from _thread import *
import pickle

server = "172.20.10.2" #cmd ipconfig 
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.listen(6) #number dictates how many people can connect
print("Server Started\nWaiting for connections...")

try:
    s.bind((server,port)) #connecting server and port

except socket.error as e: #in case stuff doesnt work
    print(str(e))
    exit()

while True:
    conn, addr = s.accept() #accept incoming connections, store stuff
    print("Connected to:", addr)
