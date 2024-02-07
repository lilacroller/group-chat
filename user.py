import zmq


def GetGroupList():
    context= zmq.Context()
    socket= context.socket(zmq.REQ)
    socket.connect("tcp://localhost:1234")
    outmessage= "mridank"
    socket.send(outmessage.encode())
    inmessage= socket.recv()
    print(inmessage)

if __name__ == "__main__":
    GetGroupList()
