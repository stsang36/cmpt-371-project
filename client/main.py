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
import threading

IDLE_TIME = 1

# Global variables to track game end and winner
ended = False
end_lock = threading.Lock()
winner = ""

def recv_handler(conn: connect.client_connection) -> None:
    '''
    This thread handler would take in a client_connection to handle incoming packets from the server in a separate thread.
    It should process messages and update the local game state such as ball, movement, score and game end triggers.
    '''

    global ended, winner, end_lock

    while True:

        try:
            data = conn.receive()

            if not data:
                break

            if len(data) < 8:
                continue

            # Unload the packet data
            unloaded_data = packet.unload_packet(data)
            status = packet.Status(unloaded_data["status"])

            # Match packet status type to handled action
            match status:

                #ball position update
                case packet.Status.BALL_POS:
                    x = unloaded_data["x"]
                    y = unloaded_data["y"]
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        Ball.posx = float(x)
                        Ball.posy = float(y)

                #striker movement update
                case packet.Status.MOVE:
                    uuid = unloaded_data["uuid"]
                    x = unloaded_data["x"]
                    y = unloaded_data["y"]

                    p = None
                    with conn.player_list_lock:
                        for s, d in conn.player_list.items():
                            if d['uuid'] == uuid:
                                p = d['player']
                                break

                    if p is not None:
                        p = cast(striker, p)
                        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                            p.posx = float(x)
                            p.posy = float(y)
                            p.updatePos()
                #player slots/count update
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
                #update scoreboard
                case packet.Status.SCOREBOARD:
                    upper_score = unloaded_data["upper_score"]
                    lower_score = unloaded_data["lower_score"]
                    
                    if isinstance(upper_score, int) and isinstance(lower_score, int):
                        conn.update_scoreboard(upper_score, lower_score)

                case packet.Status.END:
                    
                    with end_lock:
                        ended = True


        except ConnectionResetError as e:
            print(f"Connection Exception: {e}")
            conn.close()

            with end_lock:
                ended = True
                winner = "Server Disconnected"
            return

        except ConnectionError as e:
            print(f"Connection Error: {e}")
            conn.close()
            with end_lock:
                ended = True
                winner = "Server Disconnected"
            return


        except ValueError as e:
            print(f"Value Error: {e}")

        except Exception as e:
            print(f"Exception: {e}")

            
        

    conn.close()

def pong(my_player: striker):
    '''
    Main game loop that handles input, updates player state, and renders game frames.
    '''
    global ended, winner
    running = True
    move = 0
    #event handling
    while running:
        pong_setup.screen.fill(pong_setup.BLACK)
        # Check if game has ended
        with end_lock:
            ended_copy = ended

        if ended_copy:
            running = False
            # Determine winner based on final score
            if c.scoreboard["upper_score"] > c.scoreboard["lower_score"]:
                with end_lock:
                    winner = "Upper Team"
            elif c.scoreboard["upper_score"] < c.scoreboard["lower_score"]:
                with end_lock:    
                    winner = "Lower team"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # handle key presses for player movement for horizontal or vertical strikers
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
        
        # draw all connected players
        with c.player_list_lock:
            for s, i in c.player_list.items():
                if i['uuid'] != "":
                    p = cast(striker, i['player'])
                    p.display()

                    if i['uuid'] == c.get_id():
                        p.display(is_current_player=True)
        # draw the ball
        Ball.display()
        # draw the scoreboard
        with c.scoreboard_lock:
            pong_setup.displayText("Score:", c.scoreboard['upper_score'], 150, 100, pong_setup.GREEN)
            pong_setup.displayText("Score:", c.scoreboard['lower_score'], pong_setup.WIDTH - 150, pong_setup.HEIGHT - 100, pong_setup.RED)

        pygame.display.update()
        pong_setup.clock.tick(pong_setup.FPS)

# Main Menu Handling
try:
    c = connect.init_connection()
    print(c)

    pygame.init()

    # Get unique player ID from server
    id = c.receive().decode()
    c.set_id(id)
    print(f"Connected with ID: {id}")

    # Get assigned player slot from server and assign player to position striker
    while c.player_slot is None:
        msg = c.receive()

        if not msg:
            raise ConnectionError("No slot received.")

        if len(msg) < 1:
            continue
        try:
            current_slot = packet.unload_packet(msg)
        except ValueError as e:
            print(f"{e}")
            continue

        if not isinstance(current_slot, dict):
            continue

        if not isinstance(current_slot["slot"], int):
            continue

        if current_slot.get("slot") is None:
            continue
        
        
        c.set_player_slot(current_slot["slot"])

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

    # intialize the ball
    Ball = ball(pong_setup.WIDTH/2, pong_setup.HEIGHT/2, 7, pong_setup.WHITE)
    
    #initialize the thread
    c.start_recieving(recv_handler)
    # wait for player slot to be assigned
    while c.player_slot is None:
        time.sleep(IDLE_TIME)

    pygame.display.set_caption("Menu")

    #font for menu
    menuFont = pygame.font.Font("freesansbold.ttf", 100)
    menuText = menuFont.render("PONG ROYALE", True, pong_setup.WHITE)
    menuRect = menuText.get_rect(center=(450, 100))

    buttonFont = pygame.font.Font("freesansbold.ttf", 30)
    exitButton = Button(None, 450, 400, "EXIT", buttonFont, pong_setup.WHITE, pong_setup.GREEN)

    waitFont = pygame.font.Font("freesansbold.ttf", 30)
    waitText = waitFont.render("Waiting for other players", True, pong_setup.WHITE)
    waitRect = waitText.get_rect(center=(450, 300))
    
    started = False
    ready_to_play = False

    while True:
        mousePos = pygame.mouse.get_pos()
        pong_setup.screen.fill(pong_setup.BLACK)

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

        #if game has ended, show which team won the game

        with end_lock:
            end_copy = ended

        if end_copy:
            with end_lock:

                if "Server Disconnected" in winner:
                    endText = waitFont.render(f"Disconnected!\nRelaunch the client.", True, pong_setup.RED)
                    pygame.display.set_caption("Disconnected")
                else:
                    winner = c.get_winner()
                    endText = waitFont.render(f"{winner} wins!", True, pong_setup.WHITE)
                    pygame.display.set_caption(f"{winner} wins!")
            endRect = endText.get_rect(center=(450, 250))
            pong_setup.screen.blit(endText,endRect)

        #if player has exited the game, close the game screen and disconnect the server
        elif started:
            pygame.quit()
            exit()
        #show main menu of the game
        else:
            pong_setup.screen.blit(menuText, menuRect)
            pong_setup.screen.blit(waitText,waitRect)
            # Display active player count
            playerCountText = waitFont.render(f"Players connected: {active_count}/4", True, pong_setup.WHITE)
            playerCountRect = playerCountText.get_rect(center=(450, 340))
            pong_setup.screen.blit(playerCountText, playerCountRect)

        #if there are 4 players, start the game
        if active_count == 4 and started != True:
            ready_to_play = True
            started = True
            pygame.display.set_caption("Pong Royale")

        if ready_to_play:
            pong(my_player)
            ready_to_play = False



        pygame.display.update()

except Exception as e:
    print(f"Client error: {e}")
    exit(1)


