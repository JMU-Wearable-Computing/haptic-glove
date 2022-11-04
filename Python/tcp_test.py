import socket 
verbose = True

def connect(TCP_IP, TCP_PORT):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        connected = True
        
        print('Succesfully connected')
        while True:
            mg = s.recv(4096).decode("ascii").split('\r')[0].split('\n')[0]
    except:
        if verbose:
            print(f'Failed to connect to ip {TCP_IP}')
    #return s

if __name__ == '__main__':
    device = connect('192.168.50.231', 8888)
    #device.send('test'.encode('ascii'))