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
    print("Groupaddress= ", groupaddress)
    socket.connect(f"tcp://{groupaddress}")
    outmessage= f"Join {username}"
    socket.send(outmessage.encode())
    print("REached here?")
    inmessage= socket.recv()
    print("But here?")
    print(inmessage.decode())
    if inmessage.decode().split(" ")[0] == "SUCCESS":
        return inmessage.decode().split(" ")[1]
    return "FAILED"


if __name__=="__main__":
    groupmap= {}
    username= input("Enter username: ")
    while True:
        print("MENU")
        print("1. Get group list")
        print("2. Join a group")
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
                requestedgroup= input("Enter group name:")
                if requestedgroup in groupmap:
                    groupaddress= groupmap[requestedgroup]
                    print("groupaddress: "+ str(groupaddress))
                    newport= JoinGroup(groupaddress)
                    if(newport == "FAILED"):
                        print("Unable to connect to the group")
                    else:
                        print(groupmap[requestedgroup])
                        groupmap[requestedgroup]= groupmap[requestedgroup].split(":")[0]+":"+newport
                        print(groupmap[requestedgroup])
                        print("Joined group succesfully")
