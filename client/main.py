import connect
import pygame
import time
import sys, os
import pong_setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import packet
from Striker import striker
from ball import Ball

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

#send data
def sendData(c, data, status):
    if status == 'M':
        p = packet.serialize(data, packet.Status.MOVE)
    if status == 'B':
        p = packet.serialize(data, packet.Status.BALL_POS)
    c.send(p)

try:
    c = connect.init_connection()
    
    print(c)

    pygame.init()

    id = c.receive().decode()
    c.set_id(id)
    print(f"Connected with ID: {id}")
    player_slot = packet.unload_packet(c.receive())
    print(f"Player Slot: {player_slot}")
    c.start_recieving(recv_handler)
    
    #Run pong game
    player = striker(pong_setup.WIDTH-20, 0, 10, 100, 10, pong_setup.GREEN)
    ball = Ball(pong_setup.WIDTH/2, pong_setup.HEIGHT/2, 7, 5, pong_setup.WHITE)
    running = True
    move = 0
    #event handling
    while running:
        pong_setup.screen.fill(pong_setup.BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move = -1
                if event.key == pygame.K_DOWN:
                    move = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    move = 0
        #collision detection
        if pygame.Rect.colliderect(ball.getRect(), player.getRect()):
            ball.hitX()
        #update ball and player position
        player.update(move)
        point = ball.update()
        #send data to the server
        if point:   
            ball.reset()
        #send player's position and ball's position to the server
        data = {'uuid': c.get_id(), 'x': player.posx, 'y': player.posy}
        ballData =  {'uuid': c.get_id(), 'x': ball.posx, 'y': ball.posy}
        sendData(c, data, 'M')
        sendData(c, ballData, 'B')
        player.display()
        ball.display()
        pygame.display.update()
        pong_setup.clock.tick(pong_setup.FPS)
    pygame.quit()
except Exception as e:
    print(e)
    exit(1)


