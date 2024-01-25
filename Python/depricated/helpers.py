import socket

#Generate a local device IP given its decive_id
def find_device_ip(device_id):
    this_ip = socket.gethostbyname(socket.gethostname())
    ip_split = this_ip.split('.')[0:-1]
    device_ip = ip_split[0] + '.' + ip_split[1] + '.' + ip_split[2] + '.' + str(device_id)
    return device_ip
