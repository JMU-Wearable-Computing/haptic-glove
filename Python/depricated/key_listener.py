import socket
from pynput import keyboard

TCP_IP = "172.16.1.2"

#TCP_IP = "192.168.50.170"

TCP_PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
 
mode = "pull"

pattern = '118'
if mode == "push":
    commands = {'up':f'/buz2/{pattern}', 'down':f'/buz0/{pattern}', 'left':f'/buz1/{pattern}', 'right':f'/buz3/{pattern}key'}

if mode == "pull":    
    commands = {'up':f'/buz0/{pattern}', 'down':f'/buz2/{pattern}', 'left':f'/buz3/{pattern}', 'right':f'/buz1/{pattern}'}
board = keyboard.Controller()
 
def on_press(key):
    if key == keyboard.Key.esc:
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
 
    if k in ['up', 'down', 'left', 'right']:  # keys of interest
        print(commands[k])
        for i in range(0,1):
            s.send(f'{commands[k]}\n'.encode('ascii'))
            #recieved = s.recv(64).decode('ASCII')
            #print(recieved)
    if k == 'space':
        for i in range(0,1):
            s.send(f'/buz4/118\n'.encode('ascii'))

            
 
    if k == 'q':    
        return False  # stoplistener; remove this if want more keys
 
listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keysup messsage
 
 
