import connect
import pygame
import time
import sys, os
import pong_setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared import packet
from Striker import striker

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

def sendMovement(c, data):
    p = packet.serialize(data, packet.Status.MOVE)
    c.send(p)

try:
    c = connect.init_connection()
    
    print(c)

    pygame.init()

    id = c.receive().decode()
    c.set_id(id)
    print(f"Connected with ID: {id}")
    
    c.start_recieving(recv_handler)
    
    # send a test packet MOVE for every 5 seconds
    player = striker(pong_setup.WIDTH-20, 0, 10, 100, 10, pong_setup.GREEN)
    running = True
    move = 0
    while running:
        pong_setup.screen.fill(pong_setup.BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move = -1
                    data = {'uuid': c.get_id(), 'x': 0, 'y': -1}
                    sendMovement(c, data)
                if event.key == pygame.K_DOWN:
                    move = 1
                    data = {'uuid': c.get_id(), 'x': 0, 'y': 1}
                    sendMovement(c, data)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    move = 0
                    data = {'uuid': c.get_id(), 'x': 0, 'y': 0}
                    sendMovement(c, data)
        player.update(move)
        player.display()
        pygame.display.update()
        pong_setup.clock.tick(pong_setup.FPS)
    pygame.quit()
except Exception as e:
    print(e)
    exit(1)


