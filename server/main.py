import game_server as gs
import signal
import sys, os
import game_track as gt
import time
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import packet

BALL_UPDATE_INTERVAL = 0.03
IDLE_TIME = 1
PLAYER_LIST_UPDATE_INTERVAL = 2

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

    '''

    #send UUID at initial connection between client and server.
    print(f"Sending UUID: {client.id}")
    try:
        client.send(str(client.id).encode())
    except Exception as e:
        print(f"Error sending UUID to client: {e}")
        client.close()
        return
    
    #add new player to the game state and send the new player slot to all clients.

    try:
        player_slot = conn.game_state.add_player(str(client.id))
    except ValueError as e:
        print(f"Error adding player: {e}")
        client.close()
        return



    if player_slot is None:
        print(f"Failed to add player {str(client.id)} to game state.")
        client.close()
        return
    
    print(f"Player {str(client.id)} added to slot {player_slot}.")

    new_send = packet.serialize({"uuid": str(client.id), "slot": int(player_slot[1:])}, packet.Status.PLAYER_NEW_SLOT)
    try:
        client.send(new_send)
        print(f"Sent new player slot to all clients: {client.id} in slot {player_slot}.")
    except Exception as e:
        print(f"Error Sending New player: {e}")


    
    #Ready up the client and send the player list.
    client.ready_up()
    conn.send_player_list()

    if conn.get_active() == 1 and conn.game_state.is_ended():
        # If this is the first client and the game has ended, reset the game state.
        conn.game_state.reset_game()
        conn.game_state.unpause()
        print("Game state reset for a new player.")


    #start the client receiving thread.
    try:
        while True:
            data = client.receive()
            if not data:
                # the client has disconnected.
                break

            unloaded_data = packet.unload_packet(data)
            
            #testing whether the packet was unloaded correctly
            #print(f"Unloaded Data: {unloaded_data}")

            status = packet.Status(unloaded_data["status"])
            to_send = None

            # Handle the different packet statuses
                
            match status:
                case packet.Status.MOVE:
                    with conn.game_state.game_lock:
                        for player in conn.game_state.players.values():
                            if player.id == str(client.id):
                                # Update the player's position
                                player.update(unloaded_data["x"], unloaded_data["y"])
                                to_send = packet.serialize({"uuid": str(client.id), "x": player.x, "y": player.y}, packet.Status.MOVE)
                
                case packet.Status.PAUSE:
                    conn.game_state.pause()
                    to_send = packet.serialize({}, packet.Status.PAUSE)


        # now send the updated data to all clients and the scoreboard.
        try:
            conn.update_clients(to_send)
            conn.send_scoreboard()
        except Exception as e:
            print(f"Error updating clients: {e}")

        
    except Exception as e:
        print(f"Client Error: {e}")

    # handle client disconnection
    finally:
        client.close()
        conn.game_state.remove_player(str(client.id))
        conn.send_player_list()
        print(f"There is now {conn.get_active()} active connections.")

    pass

def ball_updater_thread(conn: gs.server_connection):
    '''
    This thread will update the ball position every update_interval seconds.
    broadcast the new position to all clients.

    Requires a server_connection object.
    '''
    game_state = conn.game_state

    while True:
        #print(f"game_state.is_paused() = {game_state.is_paused()} conn.get_active() = {conn.get_active()} game_state.is_ended() = {game_state.is_ended()}")
        if not game_state.is_paused() and conn.get_active() > 0:
            with game_state.game_lock:
                game_state.ball.update(players = game_state.players)
                to_send = packet.serialize({"x": game_state.ball.x,"y": game_state.ball.y}, packet.Status.BALL_POS)

            try:
                #print(f"Sending Ball Position: {game_state.ball.x}, {game_state.ball.y}")
                conn.update_clients(to_send)
            except Exception as e:
                print(f"Ball Exception: {e}")

            with game_state.game_lock: 
                curr_scoreboard = game_state.ball.scoreboard_ref
                
                if not curr_scoreboard:
                    raise ValueError("Scoreboard not found in game state.")
                    
                upper_score = curr_scoreboard["upper_score"]
                lower_score = curr_scoreboard["lower_score"]
            
            if lower_score == 10 or upper_score == 10:
                game_state.end()
                    
                    
            if game_state.is_ended():
                print("Game has ended.")
                to_end = packet.serialize({"winner": game_state.ball.side.value}, packet.Status.END)
                conn.game_state.pause()
                try:
                    conn.update_clients(to_end)
                except Exception as e:
                    print(f"Error sending END packet: {e}")
        
        # If the game is paused or no clients are connected, wait for a while before checking again.
        if game_state.is_paused() or conn.get_active() < 1:
            time.sleep(IDLE_TIME)
        else:
            time.sleep(BALL_UPDATE_INTERVAL)
    
def player_list_updater_thread(conn: gs.server_connection):
    '''
    This thread will update the player list every 5 seconds.
    '''

    while True:
        
        try:
            if conn.get_active() > 0:
                conn.send_player_list()
        except Exception as e:
            print(f"Error sending player list: {e}")
            break
        
        time.sleep(PLAYER_LIST_UPDATE_INTERVAL)



def main():

    
    global server_socket

    # SIGNAL HANDLER because the server will not be able to interrupt while waiting for clients.
    signal.signal(signal.SIGINT, handle_sigint)

    ball_t = None
    player_list_t = None

    # initialize the socket and threads. 
    try:
        c = gs.init_host()
        server_socket = c.socket
        print(c)
        ball_t = threading.Thread(target=ball_updater_thread, args=(c, ), daemon=True)
        ball_t.start()
        player_list_t = threading.Thread(target=player_list_updater_thread, args=(c, ), daemon=True)
        player_list_t.start()

        c.accept_clients(handle_client) # this is a blocking call for this thread.

    except Exception as e:
        print(f"Server Exception occured: {e}")
        exit(1)

    finally:
        if server_socket is not None:
            server_socket.close()
        print("Server closed.")


if __name__ == "__main__":
    main()
    sys.exit(0)


