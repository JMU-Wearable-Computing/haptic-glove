""" Echo server script

Increments received ASCII character by 1 and sends it via TCP socket

Author: Will Bradford

Current implementation is broken with boards running Firmware V2.0. See issue #7 in repo.
- Jason Forsyth (7/11/24)

"""

import socket
import time

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to TCP server (ensure last digit of IP address is correct)
s.connect(("172.16.1.4", 8888))

# Packet variables for incrementing
old_packet = 'A'.encode('ascii')
new_packet = 'A'.encode('ascii')

# Ensures old_packet is sent first
count = 0
while True:
  if count == 0:
    s.sendall(old_packet)
    count += 1
  else:
    s.sendall(new_packet)

  # Allows enough time for message to be sent from Arduino
  time.sleep(2)

  # Recieve message and remove unneeded characters
  data = s.recv(1024).decode('ascii').split('\r')[0].split('\n')[0]

  # Print message
  print(f'{data}\n')

  # Increment ASCII number
  incr_packet = data.encode('ascii')[0] + 1
  new_packet = chr(incr_packet).encode('ascii')
