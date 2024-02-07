import zmq
from threading import Thread

# each cell contains a tuple of form (groupname-ipaddress)
GroupList= []

def GroupList2txt():
# returns list of group in text version
    result=""
    for cell in GroupList:
        result= result + str(cell[0])+ " - " +str(cell[1])+ ", "
    
    return result


def check4usrrequests():
# stays online and keeps checking for requests from user
    context= zmq.Context()
    socket= context.socket(zmq.REP)
    socket.bind("tcp://*:1234")

    while True:
        inmessage= socket.recv()
        print(f"GROUP LIST REQUEST FROM {inmessage.decode()}")
        outmessage= GroupList2txt()
        socket.send(outmessage.encode())

def check4grprequests():
    pass

if __name__=="__main__":
    GroupList= [("hinge", "12.30.40"), ("dingy", "12.32.12")]
    thread= Thread(target=check4usrrequests)
    thread.start()