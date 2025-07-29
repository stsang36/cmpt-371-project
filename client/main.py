import connect
import pygame
import time
import sys, os
import pong_setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import packet
from Striker import striker
from Ball import ball
from typing import cast

IDLE_TIME = 1

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

            if len(data) < 8:
                continue

            unloaded_data = packet.unload_packet(data)
            #print(f"Received Data: {unloaded_data}")
            status = packet.Status(unloaded_data["status"])


            



            match status:
                case packet.Status.BALL_POS:
                    x = unloaded_data["x"]
                    y = unloaded_data["y"]
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        Ball.posx = float(x)
                        Ball.posy = float(y)
                case packet.Status.MOVE:
                    uuid = unloaded_data["uuid"]
                    x = unloaded_data["x"]
                    y = unloaded_data["y"]

                    p = None
                    with conn.player_list_lock:
                        for s, d in conn.player_list.items():
                            #print(f"Checking player {s} with uuid {d['uuid']}")
                            if d['uuid'] == uuid:
                                p = d['player']
                                break

                    if p is not None:
                        p = cast(striker, p)
                        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                            p.posx = float(x)
                            p.posy = float(y)
                            p.updatePos()

                case packet.Status.PLAYER_LIST:
                    p1 = unloaded_data["p1"]
                    p2 = unloaded_data["p2"]
                    p3 = unloaded_data["p3"]
                    p4 = unloaded_data["p4"]

                    with conn.player_list_lock:
                        conn.player_list["1"]["uuid"] = p1
                        conn.player_list["2"]["uuid"] = p2
                        conn.player_list["3"]["uuid"] = p3
                        conn.player_list["4"]["uuid"] = p4


        except Exception as e:
            print(f"Socket Error: {e}")
            
        

    conn.close()


try:
    c = connect.init_connection()
    
    print(c)

    pygame.init()

    id = c.receive().decode()
    c.set_id(id)
    print(f"Connected with ID: {id}")

    current_slot = packet.unload_packet(c.receive())
    
    c.player_slot = current_slot["slot"]
    print(f"Player Slot: {c.player_slot}")

    if c.player_slot in [1, 2]:
        is_vertical = True
    else:
        is_vertical = False
    
    c.start_recieving(recv_handler)

    while c.player_slot is None:
        time.sleep(IDLE_TIME)


    
    
    #Run pong game

    # vertical strikers
    player1 = striker(20, (pong_setup.HEIGHT / 2) - 50, 10, 100, 10, pong_setup.GREEN)
    player2 = striker(pong_setup.WIDTH - 30, (pong_setup.HEIGHT / 2) - 50, 10, 100, 10, pong_setup.RED)
    
    # horizontal strikers
    player3 = striker((pong_setup.WIDTH/2)-50, 20, 100, 10, 10, pong_setup.GREEN)
    player4 = striker((pong_setup.WIDTH/2)-50, pong_setup.HEIGHT-30, 100, 10, 10, pong_setup.RED)
    
    with c.player_list_lock:
        c.player_list["1"]["player"] = player1
        c.player_list["2"]["player"] = player2
        c.player_list["3"]["player"] = player3
        c.player_list["4"]["player"] = player4


        my_player = c.player_list[str(c.player_slot)]["player"]
    
    my_player = cast(striker, my_player)

    Ball = ball(pong_setup.WIDTH/2, pong_setup.HEIGHT/2, 7, 5, pong_setup.WHITE)
    running = True
    move = 0
    #event handling
    while running:
        pong_setup.screen.fill(pong_setup.BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if is_vertical:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        move = -1
                    if event.key == pygame.K_DOWN:
                        move = 1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        move = 0
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        move = 1
                    if event.key == pygame.K_LEFT:
                        move = -1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                        move = 0
        #update ball and player position
        if is_vertical:
            my_player.updateVert(move)
        else:
            my_player.updateHori(move)
        #send player's position and ball's position to the server
        data = {'uuid': c.get_id(), 'x': my_player.posx, 'y': my_player.posy}
        
        c.send(data, packet.Status.MOVE)
        
        with c.player_list_lock:
            for s, i in c.player_list.items():
                if i['uuid'] != "":
                    p = cast(striker, i['player'])
                    p.display()

                    if i['uuid'] == c.get_id():
                        p.display(is_current_player=True)

        Ball.display()
        pygame.display.update()
        pong_setup.clock.tick(pong_setup.FPS)
    pygame.quit()
except Exception as e:
    print(f"Client error: {e}")
    exit(1)


