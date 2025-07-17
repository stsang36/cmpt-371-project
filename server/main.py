import game_server as gs
import signal

server_socket = None

def handle_sigint(sig, frame):
    if server_socket is not None:
        server_socket.close()

signal.signal(signal.SIGINT, handle_sigint)

def handle_client(client: gs.client, conn: gs.server_connection):
    '''
    Function that each thread will run to handle a client connection. It will send an update to all clients.
    Requires: a client class and a server_connection class.

    MAKE SURE TO USE A MUTEX TO AVOID RACE CONDITIONS! This will modify the global gamestate after processing and updating the clients.
    '''
    try:
        while True:
            data = client.receive()
            print(data)

            if not data:
                break

            with conn.clients_lock:

                for aClient in conn.clients:
                    if aClient != client:
                        aClient.send(f"{client.id}:{data}")
            
            client.send("Data received by server.")

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


