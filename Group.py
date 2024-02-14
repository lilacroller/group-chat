import zmq
import socket
from threading import Thread
import time
import datetime

context= zmq.Context()
usertele= set()
messagehistory= [] #stores tuple of form (timestamp, uuid, message)
currentusers= set()
nextport= 1201

def MessageServer(name, ip):
    socket= context.socket(zmq.REQ)
    socket.connect("tcp://localhost:1233")
    outmessage= f"{name} - {ip}"
    socket.send(outmessage.encode())
    inmessage= socket.recv()
    print(inmessage)

def addtoGroup(uuid):
    success= False
    if uuid not in usertele:
        usertele.add(uuid)
        success= True
    return success

def removefromGroup(uuid):
    success= False
    if uuid in usertele:
        usertele.remove(uuid)
        success= True
    return success

#send message format: Send <UUID> - message contents
def sendMessage(uuid, message):
    success= False
    content= message.split(" - ")[1]
    if uuid in usertele:
        messagehistory.append((int(time.time()), uuid, content))
        success= True
    return success

#get message format: Get <UUID> timestamp:HH:MM:SS
def getMessage(uuid, message):
    if uuid not in usertele:
        return "FAILED"
    i= message.find("timestamp:")
    if i==-1:
        msgs=""
        for a in messagehistory:
            msgs= msgs+", " + str(a)
        return msgs
    time_string= message[i+10:i+18]
    epoch_time = int(datetime.datetime.strptime(time_string, "%H:%M:%S").timestamp())
    msgs= ""
    for a in messagehistory:
        if a[0]<=epoch_time:
            msgs= msgs+", " +  str(a)
    
    return msgs
                
def chat(port):
    socket= context.socket(zmq.REP)
    socket.bind(f"tcp://*:{port}")
    while True:
        inmessage= socket.recv()
        uuid= inmessage.decode().split(" ")[1]

        if (inmessage.startswith(b"Send")):
            print(f"MESSAGE SEND FROM {uuid}")
            if sendMessage(uuid, inmessage.decode()):
                outmessage= "SUCCESS"
                socket.send(outmessage.encode())
            else: socket.send("FAILED".encode())
        
        elif inmessage.startswith(b"Get"):
            print(f"MESSAGE REQUEST FROM {uuid}")
            outmessage= getMessage(uuid, inmessage.decode())
            socket.send(outmessage.encode())
        
        elif inmessage.startswith(b"Leave"):
            print(f"LEAVE REQUEST FROM {uuid}")
            if uuid in usertele:
                usertele.remove(uuid)
                socket.send("SUCCESS".encode())
                break
            socket.send("FAILED".encode())

def groupSpawner():
    global nextport
    socket= context.socket(zmq.REP)
    socket.bind("tcp://*:1200")
    while True:
        inmessage= socket.recv()
        if inmessage.startswith(b"Join"):
            uuid= inmessage.decode().split(" ")[1]
            if uuid not in usertele:
                usertele.add(uuid)
                outmessage= f"SUCCESS {nextport}"
                socket.send(outmessage.encode())
                chatThread= Thread(target=chat, args=(nextport,))
                chatThread.start()
                nextport= nextport+1
            else: socket.send("FAILED".encode())



def check4usrRequests():
    socket= context.socket(zmq.REP)
    socket.bind("tcp://*:1200")
    while True:
        inmessage= socket.recv()
        uuid= inmessage.decode().split(" ")[1]
        if (inmessage.startswith(b"Join")):
            print(f"JOIN REQUEST FROM {uuid}")
            if addtoGroup(uuid) is True:
                outmessage= "SUCCESS"
                socket.send(outmessage.encode())
#               chatThread= Thread(target=chat, args=(socket,))
#               chatThread.start()  
            else: socket.send("FAILED".encode())

        elif (inmessage.startswith(b"Leave")):
            print(f"LEAVE REQUEST FROM {uuid}")
            if removefromGroup(uuid):
                outmessage= "SUCCESS"
                socket.send(outmessage.encode())
            else: socket.send("FAILED".encode())

        elif (inmessage.startswith(b"Send")):
            print(f"MESSAGE SEND FROM {uuid}")
            if sendMessage(uuid, inmessage.decode()):
                outmessage= "SUCCESS"
                socket.send(outmessage.encode())
            else: socket.send("FAILED".encode())
        
        elif (inmessage.startswith(b"Get")):
            print(f"MESSAGE REQUEST FROM {uuid}")
            outmessage= getMessage(uuid, inmessage.decode())
            socket.send(outmessage.encode())


if __name__=="__main__":
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    MessageServer(hostname, IPAddr)
    usrrequstThread= Thread(target=groupSpawner)
    usrrequstThread.start()