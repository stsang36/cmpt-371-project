import game_server as gs
import signal
import sys
import socket

server_socket = None

def handle_sigint(sig, frame):
    if server_socket is not None:
        server_socket.close()

signal.signal(signal.SIGINT, handle_sigint)



try:
    c = gs.init_host()
    server_socket = c.socket
    
    print(c)
    c.accept_clients() # this is a blocking call.


except Exception as e:
    print(e)
    exit(1)

finally:
    if server_socket is not None:
        server_socket.close()
    print("Server closed.")


