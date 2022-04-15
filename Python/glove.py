from concurrent.futures import thread
import socket
from pynput import keyboard
from threading import Thread


class Haptic():

    def __init__(self, ip, port, mode="pull", max_strength=255):
        self.UP = [max_strength,150,150,150]
        self.DOWN = [150,max_strength,150,150]
        self.LEFT = [150,150,max_strength,150]
        self.RIGHT = [150,150,150,max_strength]
        self.OFF = [150,150,150,150]

        self.TCP_IP = ip
        self.TCP_PORT = port
        self.mode = mode
        
    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.TCP_IP, self.TCP_PORT))
    
    
    def make_message(self, vect):
        return f'/{vect[0]}/{vect[1]}/{vect[2]}/{vect[3]}\n'


    def listen_keyboard(self, keys = ['up', 'down', 'left', 'right']):
        self.keys = keys
        self.commands = {keys[0]: self.make_message(self.UP), keys[1]: self.make_message(self.DOWN), 
            keys[2]: self.make_message(self.LEFT), keys[3]: self.make_message(self.RIGHT)}
        self.board = keyboard.Controller()
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()  # start to listen on a separate thread
        self.listening = True
        self.listener.join()  # remove if main thread is polling self.keysup messsage

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.s.send(f'{self.make_message(self.OFF)}'.encode('ascii'))
            self.s.close()
            self.listening = False
            return False  # stop listener
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
    
        if k in self.keys:  # keys of interest
            print(self.commands[k])
            self.s.send(f'{self.commands[k]}'.encode('ascii'))
            self.s.send(f'{self.commands[k]}'.encode('ascii'))
            #for i in range(0,1):
                #self.s.send(f'{commands[k]}\n'.encode('ascii'))
                #recieved = s.recv(64).decode('ASCII')
                #print(recieved)
        if k == 'space':
            for i in range(0,1):
                print(self.make_message(self.OFF))
                self.s.send(f'{self.make_message(self.OFF)}'.encode('ascii'))
                self.s.send(f'{self.make_message(self.OFF)}'.encode('ascii'))
                #self.s.send(f'/buz4/118\n'.encode('ascii'))

if __name__ == "__main__":
    left_glove = Haptic("172.16.1.2", 8888)
    left_arm = Haptic("172.16.1.3", 8888, max_strength=255)

    left_glove.connect()
    left_arm.connect()

    left_glove_listen = Thread(target=left_glove.listen_keyboard)
    left_glove_listen.start()
    #left_arm_listen = Thread(target=left_arm.listen_keyboard)
    #left_glove.listen_keyboard()
    left_arm.listen_keyboard(keys=['w','a','s','d'])