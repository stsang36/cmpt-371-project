import connect
import time

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

            print(data)
        except Exception as e:
            print(f"Socket Error: {e}")
            break
        

    conn.close()


try:
    c = connect.init_connection()
    
    print(c)
    c.start_recieving(recv_handler)
    

    while True:
        ans = input("enter ur text: ")
        c.send(ans)    


except Exception as e:
    print(e)
    exit(1)


