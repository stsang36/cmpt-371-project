import connect
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import packet

# perhaps we need to make the client multithreaded to get and send game updates to the server. 
def send_thread(data):
    pass

def recv_handler(conn: connect.client_connection):
    '''
    This thread handler would take in a client_connection to recieve new updates from the server.
    It should modify and update the game state here on the client side.
    '''


    
    while True:

        try:
            data = conn.receive()
            if not data:
                break

            unloaded_data = packet.unload_packet(data)
            print(f"Received Data: {unloaded_data}")

        except Exception as e:
            print(f"Socket Error: {e}")
            break
        

    conn.close()


try:
    c = connect.init_connection()
    
    print(c)

    id = c.receive().decode()
    c.set_id(id)
    print(f"Connected with ID: {id}")

    c.start_recieving(recv_handler)
    
    # send a test packet MOVE for every 5 seconds
    while True:
        data = {'uuid': c.get_id(), 'x': 1.0, 'y': 2.0}

        p = packet.serialize(data, packet.Status.MOVE)
        c.send(p)
        time.sleep(5)
        


except Exception as e:
    print(e)
    exit(1)


