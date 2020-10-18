#!/bin/python3
# Must run with root privileges
# dont work with localhost
# python3 synportscanner.py <ip>
# python3 synportscanner.py <ip> <last_port>
# python3 synportscanner.py <ip> <first_port> <last_port>

import sys
from datetime import datetime
import os
import threading
from queue import Queue
from scapy.all import *


# Define the target
if len(sys.argv) == 2:
    target = socket.gethostbyname(sys.argv[1])  # Translate hostname to IPv4
    first_port = 1
    last_port = 1000
elif len(sys.argv) == 3 and 1 <= int(sys.argv[2]) <= 65535:
    target = socket.gethostbyname(sys.argv[1])  # Translate hostname to IPv4
    first_port = 1
    last_port = sys.argv[2]
elif len(sys.argv) == 4 and 1 <= int(sys.argv[2]) <= 65535 and 1 <= int(sys.argv[3]) <= 65535 and int(sys.argv[2]) < int(sys.argv[3]):
    target = socket.gethostbyname(sys.argv[1])  # Translate hostname to IPv4
    first_port = sys.argv[2]
    last_port = sys.argv[3]
else:
    print("Invalid amount of arguments.")
    print("Syntax:\tpython3 portscanner.py <ip>\n\tpython3 portscanner.py <ip> <last_port>\n\tpython3 portscanner.py <ip> <first_port> <last_port>")
    sys.exit()


def synportscan(port):
    result=sr1( IP(dst=target)/TCP(flags="S", dport=port), verbose=0)

    # print which port is checking
#     with print_lock:
#         print("Checking port {}".format(port))

    if result.getlayer(TCP).flags == "SA":
        with print_lock:
            print("Port {} is open".format(port))


# The threader thread pulls a worker from the queue an processes it
def threader():
    while True:
        # gets a worker from the queue
        port = q.get()

        # run the example job with the avail worker in queue (thread)
        synportscan(port)

        # completed with the job
        q.task_done()


# a print_lock is what is used to prevent "double" modification of shared variables.
# this is used so while one thread is using a variable, others cannot access
# it. Once done, the thread releases the print_lock.
# to use it, you want to specify a print_lock per thing you wish to print_lock.
print_lock = threading.Lock()

# Create the queue and threader
q = Queue()

# how many threads are we going to allow for
for x in range(30):
    t = threading.Thread(target=threader)

    # classifying as a daemon, so they will die when the main dies
    t.daemon = True

    # begins, must come after daemon definition
    t.start()

#start = time.

t1 = datetime.now()

# number of port assigned.
for port in range(int(first_port), int(last_port) + 1):
    q.put(port)

# wait untile the thread terminates.
q.join()

t2=datetime.now()
total = t2 - t1
print("\nPorts scanned from " + str(first_port) + " to " + str(last_port))
print("Scanning completed in: " + str(total))

# a=sr1( IP(dst="10.0.2.15")/TCP(flags="S", dport=7777) )
# print(a.getlayer(TCP).flags)

print("Done")
