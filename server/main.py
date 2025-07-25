import game_server as gs
import signal
import sys, os
import game_track as gt
import time
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import packet

BALL_UPDATE_INTERVAL = 0.03 

server_socket = None

def handle_sigint(sig, frame):
    '''
    Handles the SIGINT shut down the server because it would not be able to interrupt while waiting for clients.
    '''
    global server_socket
    if server_socket is not None:
        server_socket.close()



def handle_client(client: gs.client, conn: gs.server_connection):
    '''
    Function that each thread will run to handle a client connection. It will send an update to all clients.
    Requires: a client class and a server_connection class.

    MAKE SURE TO USE A MUTEX TO AVOID RACE CONDITIONS! This will modify the global gamestate after processing and updating the clients.
    '''

    #send UUID at initial connection between client and server.
    print(f"Sending UUID: {client.id}")
    client.send(str(client.id).encode())

    #add new player to the game state
    player_slot = conn.game_state.add_player(str(client.id))



    if player_slot is None:
        print(f"Failed to add player {str(client.id)} to game state.")
        client.close()
        return
    
    print(f"Player {str(client.id)} added to slot {player_slot}.")

    new_send = packet.serialize({"uuid": str(client.id), "slot": int(player_slot[1:])}, packet.Status.PLAYER_NEW_SLOT)
    try:
        conn.update_clients(new_send)
    except Exception as e:
        print(f"Error Sending New player: {e}")


    try:
        while True:
            data = client.receive()
            print(data)

            if not data:
                # the client has disconnected.
                break

            unloaded_data = packet.unload_packet(data)
            
            #testing whether the packet was unloaded correctly
            print(f"Unloaded Data: {unloaded_data}")

            status = packet.Status(unloaded_data["status"])
            to_send = None
            with conn.game_state.game_lock:
                
                match status:
                    case packet.Status.MOVE:

                        for player in conn.game_state.players.values():
                            if player.id == str(client.id):
                                # Update the player's position
                                player.update(unloaded_data["x"], unloaded_data["y"])
                                to_send = packet.serialize({"uuid": str(client.id), "x": player.x, "y": player.y}, packet.Status.MOVE)
                   
                    case packet.Status.PAUSE:
                        conn.game_state.pause()
                        to_send = packet.serialize({"uuid": client.id}, packet.Status.PAUSE)
                    case packet.Status.END:
                        conn.game_state.end()
                        to_send = packet.serialize({"uuid": client.id}, packet.Status.END)

            try:
                conn.update_clients(to_send)
            except Exception as e:
                print(f"Error updating clients: {e}")

        
    except Exception as e:
        print(f"Client Error: {e}")
    finally:
        client.close()
        print(f"There is now {conn.get_active()} active connections.")

    pass

def ball_updater_thread(conn: gs.server_connection):
    '''
    This thread will update the ball position every update_interval seconds.
    broadcast the new position to all clients.
    '''
    game_state = conn.game_state

    #TODO: BALL LOGIC HERE
    new_side = gt.Side.NONE

    while True:
        with game_state.game_lock:
            game_state.ball.update(players = game_state.players)
            # Optionally: broadcast ball position to clients
            to_send = packet.serialize({"x": game_state.ball.x,"y": game_state.ball.y}, packet.Status.BALL_POS)

            try:
                conn.update_clients(to_send)
            except Exception as e:
                print(f"Ball Exception: {e}")

        time.sleep(BALL_UPDATE_INTERVAL)

def main():

    
    global server_socket

    signal.signal(signal.SIGINT, handle_sigint)


    try:
        c = gs.init_host()
        server_socket = c.socket
        print(c)
        ball_t = threading.Thread(target=ball_updater_thread, args=(c, ), daemon=True)
        ball_t.start()

        c.accept_clients(handle_client) # this is a blocking call.


    except Exception as e:
        print(e)
        exit(1)

    finally:
        
        if server_socket is not None:
            server_socket.close()
        print("Server closed.")


if __name__ == "__main__":
    main()
    sys.exit(0)


