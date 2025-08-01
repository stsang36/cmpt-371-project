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
from button import Button

IDLE_TIME = 1

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
                case packet.Status.SCOREBOARD:
                    upper_score = unloaded_data["upper_score"]
                    lower_score = unloaded_data["lower_score"]
                    
                    if isinstance(upper_score, int) and isinstance(lower_score, int):
                        conn.update_scoreboard(upper_score, lower_score)

        except Exception as e:
            print(f"Socket Error: {e}")
            
        

    conn.close()


#main pong game
def pong(my_player: striker):
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

        with c.scoreboard_lock:
            pong_setup.displayText("Score:", c.scoreboard['upper_score'], pong_setup.WIDTH//2, 20, pong_setup.WHITE)
            pong_setup.displayText("Score:", c.scoreboard['lower_score'], pong_setup.WIDTH//2, pong_setup.HEIGHT - 20, pong_setup.WHITE)

        pygame.display.update()
        pong_setup.clock.tick(pong_setup.FPS)


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
    
    c.start_recieving(recv_handler)

    while c.player_slot is None:
        time.sleep(IDLE_TIME)

    pygame.display.set_caption("Menu")

    #font for menu
    menuFont = pygame.font.Font("freesansbold.ttf", 100)
    menuText = menuFont.render("PONG ROYALE", True, pong_setup.WHITE)
    menuRect = menuText.get_rect(center=(450, 100))

    buttonFont = pygame.font.Font("freesansbold.ttf", 75)
    exitButton = Button(None, 450, 400, "EXIT", buttonFont, pong_setup.WHITE, pong_setup.GREEN)

    waitFont = pygame.font.Font("freesansbold.ttf", 30)
    waitText = waitFont.render("Waiting for other players", True, pong_setup.WHITE)
    waitRect = waitText.get_rect(center=(450, 300))

    started = False
    ready_to_play = False

    while True:
        mousePos = pygame.mouse.get_pos()
        pong_setup.screen.fill(pong_setup.BLACK)

        pong_setup.screen.blit(menuText, menuRect)
        pong_setup.screen.blit(waitText,waitRect)

        for button in [exitButton]:
            button.changeColour(mousePos[0], mousePos[1])
            button.update(pong_setup.screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                        
                if exitButton.checkForInput(mousePos[0], mousePos[1]):
                    pygame.quit()

        #count number of player who are ready to join the game
        with c.player_list_lock:
            active_count = sum(1 for p in c.player_list.values() if p["uuid"])

        #if player has exited the game, close the game screen and disconnect the server
        if started:
            pygame.quit()
            exit()

        #if there are 4 players, start the game
        if active_count == 4 and started != True:
            ready_to_play = True
            started = True

        if ready_to_play:
            pong(my_player)
            ready_to_play = False


        pygame.display.update()

except Exception as e:
    print(f"Client error: {e}")
    exit(1)


