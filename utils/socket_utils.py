# from the user Jamieson Becker:
# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib

import socket
import platform

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# what is the IP?
IP = get_ip()
