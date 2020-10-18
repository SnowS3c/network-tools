#!/bin/pyhon3

# python3 portscanner.py <ip>
# python3 portscanner.py <ip> <last_port>
# python3 portscanner.py <ip> <first_port> <last_port>

import sys
import socket
from datetime import datetime
import os
import threading
from queue import Queue


# Define the target
if len(sys.argv) == 2:
    target = socket.gethostbyname(sys.argv[1])  # Translate hostname to IPv4
    first_port = 1
    last_port = 100
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


# define portscan function
def portscan(port):
    try:
         #AF_INET IPv4 - SOCK_STREAM Port
         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         # it will take 1 second if the socket its not connecting
         # socket.setdefaulttimeout(1)

         # returns an error indicator
         # if port is open it return 0, if it is cloes is 1
         result = s.connect_ex((target, port))

         # print which port is checking
         # with print_lock:
         #    print("Checking port {}".format(port))

         if result == 0:
            with print_lock:
                print("Port {} is open".format(port))

         s.close()

    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit()

    except socket.gaierror:
        print("Hostname could not be resolved.")
        sys.exit()

    except socket.error:
        print("Couldn't connect to server.")
        sys.exit()

# The threader thread pulls a worker from the queue an processes it
def threader():
    while True:
        # gets a worker from the queue
        port = q.get()

        # run the example job with the avail worker in queue (thread)
        portscan(port)

        # completed with the job
        q.task_done()


# Add a pretty banner
print("-" * 50)
print("Scanning target " + target)
print("Time started: " + str(datetime.now()))
print("-" * 50)


# Check if the host is up
response = os.system("ping -c 1 " + target + " > /dev/null")
if response != 0:
    print("Host is down")
    sys.exit()

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


t2 = datetime.now()
total = t2 - t1
print("\nPorts scanned from " + str(first_port) + " to " + str(last_port))
print("Scanning completed in: " + str(total))

