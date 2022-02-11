import socket
from pynput import keyboard
import time

TCP_IP = "172.16.1.2"

#TCP_IP = "192.168.50.170"

TCP_PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
 
mode = "pull"
MIN_VIBE = 100
MAX_VIBE = 200

def make_message(index):
    command_array = [MIN_VIBE, MIN_VIBE, MIN_VIBE, MIN_VIBE]
    command_array[index] = MAX_VIBE
    return f'/{command_array[0]}/{command_array[1]}/{command_array[2]}/{command_array[3]}'


pattern = '118'
if mode == "push":
    commands = {'up':make_message(1), 'down':make_message(0), 'left':make_message(3), 'right':make_message(2)}

if mode == "pull":    
    commands = {'up':make_message(0), 'down':make_message(1), 'left':make_message(2), 'right':make_message(3)}
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
        for i in range(0,10):
            s.send(f'{commands[k]}\n'.encode('ascii'))
            #recieved = s.recv(64).decode('ASCII')
            #print(recieved)
            #time.sleep(0.001)
    if k == 'space':
        for i in range(0,1):
            s.send(f'/150/150/150/150\n'.encode('ascii'))

            
 
    if k == 'q':    
        return False  # stoplistener; remove this if want more keys
 
listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keysup messsage
 
 
