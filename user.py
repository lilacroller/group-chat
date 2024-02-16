import zmq

context= zmq.Context()
username=""


def GetGroupList(uuid):
    address= "tcp://34.131.197.76:1234"
    socket= context.socket(zmq.REQ)
    socket.connect(address)
    socket.send(f"{uuid}".encode())
    inmessage= socket.recv()
    return inmessage.decode()

def JoinGroup(groupaddress):
    global username
    socket= context.socket(zmq.REQ)
    socket.connect(f"tcp://{groupaddress}")
    outmessage= f"Join {username}"
    socket.send(outmessage.encode())
    inmessage= socket.recv()
    print(inmessage.decode())
    if inmessage.decode().split(" ")[0] == "SUCCESS":
        return inmessage.decode().split(" ")[1]
    return "FAILED"

def LeaveGroup(groupaddress):
    global username
    socket= context.socket(zmq.REQ)
    socket.connect(f"tcp://{groupaddress}")
    outmessage= f"Leave {username}"
    socket.send(outmessage.encode())
    inmessage= socket.recv()
    print(inmessage.decode())

def GetMessage(groupaddress, timestamptag):
    global username
    socket=context.socket(zmq.REQ)
    socket.connect(f"tcp://{groupaddress}")
    outmessage= f"Get {username} {timestamptag}"
    socket.send(outmessage.encode())
    inmessage= socket.recv()
    return inmessage.decode()



def SendMessage(groupaddress, msg):
    global username
    socket=context.socket(zmq.REQ)
    socket.connect(f"tcp://{groupaddress}")
    outmessage= f"Send {username} - {msg}"
    socket.send(outmessage.encode())
    inmessage= socket.recv()
    return inmessage.decode()

if __name__=="__main__":
    groupmap= {}
    username= input("Enter username: ")
    while True:
        print("MENU")
        print("1. Get group list")
        print("2. Join a group")
        print("3. Leave a group")
        print("4. Get messages")
        print("5. Send message")
        x= input()
        match x:
            case "1":
                grouplist= GetGroupList(username)
                groups= grouplist.split(", ")
                if len(groups[-1])==0:
                    groups.pop()
                for a in groups:
                    print(a)
                    x= a.split(" - ")
                    groupname= x[0]
                    groupipaddress= x[1]
                    groupmap[groupname]= groupipaddress
            case "2":
                grouplist= GetGroupList(username)
                groups= grouplist.split(", ")
                if len(groups[-1])==0:
                    groups.pop()
                for a in groups:
                    print(a)
                    x= a.split(" - ")
                    groupname= x[0]
                    groupipaddress= x[1]
                    groupmap[groupname]= groupipaddress
                
                requestedgroup= input("Enter group name:")
                if requestedgroup in groupmap:
                    groupaddress= groupmap[requestedgroup]
                    newport= JoinGroup(groupaddress)
                    if(newport == "FAILED"):
                        print("Unable to connect to the group")
                    else:
                        print(groupmap[requestedgroup])
                        groupmap[requestedgroup]= groupmap[requestedgroup].split(":")[0]+":"+newport
                        print(groupmap[requestedgroup])
                        print("Joined group succesfully")
            case "3":
                grouptoleave= input("Enter group name to leave:")
                if grouptoleave in groupmap:
                    groupaddress= groupmap[grouptoleave]
                    LeaveGroup(groupaddress)
            case "4":
                sender= input("From which group do you want to get messages:")
                m= input("Do you want all the message(y/n): ")
                
                tstag= ""
                if(m=="n"):
                    date= input("Enter date in DD/MM/YYYY format: ")
                    time= input("Enter  in HH:MM:SS format: ")
                    timestamp= date + " " + time
                    tstag= "timestamp: " + timestamp
                senderAddress= groupmap[sender]
                msgdata= GetMessage(senderAddress, tstag)
                print(msgdata)
            case "5":
                sendee= input("Whom do you want to send the message:")
                message= input("Enter your message:")
                sendeeAddress= groupmap[sendee]
                success= SendMessage(sendeeAddress, message)
                print(success)
