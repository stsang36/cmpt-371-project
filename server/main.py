import game_server as gs
import signal
import sys
import socket

server_socket = None

def handle_sigint(sig, frame):
    if server_socket is not None:
        server_socket.close()

signal.signal(signal.SIGINT, handle_sigint)

# TODO: This function needs to handle any updates sent from the client. The handler must take a client class and a connection class.
def handle_client(client, conn):
    try:
        while True:
            data = client.receive()
            print(data)

            client.send("back at you!")

    except Exception as e:
        print(f"Client Error: {e}")
    finally:
        client.close()
        print(f"There is now {conn.get_active()} active connections.")

    pass


try:
    c = gs.init_host()
    server_socket = c.socket
    
    print(c)
    c.accept_clients(handle_client) # this is a blocking call.


except Exception as e:
    print(e)
    exit(1)

finally:
    if server_socket is not None:
        server_socket.close()
    print("Server closed.")


