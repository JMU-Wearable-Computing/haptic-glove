import socket
from pynput import keyboard

TCP_IP = "172.16.1.2"
TCP_PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
 
commands = {'up':'/buz2/118', 'down':'/buz0/118', 'left':'/buz1/118', 'right':'/buz3/118'}
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
 
 
