import zmq
import socket
from threading import Thread
import time
import datetime
import requests

context= zmq.Context()
usertele= set()
messagehistory= [] #stores tuple of form (timestamp, uuid, message)
currentusers= set()

def MessageServer(name, ip, port):
    socket= context.socket(zmq.REQ)
    socket.connect("tcp://34.131.197.76:1233")
    outmessage= f"{name} - {ip}:{port}"
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

#get message format: Get <UUID> timestamp: DD/MM/YYYY HH:MM:SS
def getMessage(uuid, message):
    if uuid not in usertele:
        return "FAILED"
    i= message.find("timestamp:")
    if i==-1:
        msgs=""
        for a in messagehistory:
            msgs= msgs+", " + str(a)
        return msgs
    time_string= message[i+11:i+30]
    epoch_time = int(datetime.datetime.strptime(time_string, "%d/%m/%Y %H:%M:%S").timestamp())
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

def groupSpawner(port):
    socket= context.socket(zmq.REP)
    socket.bind(f"tcp://*:{port}")
    while True:
        inmessage= socket.recv()
        if inmessage.startswith(b"Join"):
            uuid= inmessage.decode().split(" ")[1]
            if uuid not in usertele:
                print(f"JOIN REQUEST FROM {uuid}")
                usertele.add(uuid)
                outmessage= f"SUCCESS {port+1}"
                socket.send(outmessage.encode())
                chatThread= Thread(target=chat, args=(port+1,))
                chatThread.start()
                port= port+1
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
    IPAddr = requests.get('https://checkip.amazonaws.com').text.strip()
    groupname= input("Enter group name:")
    port= int(input("Enter port no.: "))
    msthrd= Thread(target=MessageServer, args=(groupname, IPAddr, port))
    msthrd.start()
    usrrequstThread= Thread(target=groupSpawner, args=(port, ))
    usrrequstThread.start()
