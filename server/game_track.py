
from enum import Enum
import threading
from typing import Optional

class Side(Enum):
    '''
    Represents the side of the game.
    '''
    LEFT = 'L'
    RIGHT = 'R'
    NONE = 'N'

class Position(Enum):
    '''
    Represents the position of the player.
    '''
    LEFT = 'L'
    RIGHT = 'R'
    TOP = 'T'
    BOTTOM = 'B'



class Game_State:
    '''
    The Game State object contains the following:
        - ball: Ball object
        - players: dictionary of Player objects with keys as player IDs
        - game_lock: threading lock for synchronizing access to the game state by multiple clients
    '''
    class Ball:
        '''
        The Game State Ball object contains the following:
            - x: x pos
            - y: y pos
            - side: side of the ball (LEFT, RIGHT, NONE)

        Methods:
            - printing the object will return the position and side.
            - update(x, y, side): updates the ball position and side.
            

        '''
        def __init__ (self, x = 450, y = 300, xFac = 1, yFac = 1, WIDTH = 900, HEIGHT = 600, paddle_width = 10, paddle_height = 100):
            self.x = x
            self.y = y
            self.xFac = xFac
            self.yFac = yFac
            self.side = Side.NONE
            self.WIDTH = WIDTH
            self.HEIGHT = HEIGHT
            self.paddle_width = paddle_width
            self.paddle_height = paddle_height
        def __str__(self):
            return f"Ball at position ({self.x}, {self.y}, {self.side})"
        
        def update(self, players = None):
            '''
            Updates the ball position and side.
            '''
            self.x += self.xFac * 5
            self.y += self.yFac * 5
            self.hitWall()
            if players:
                self.hitPlayer(players)

        #if the ball hit the wall, it results into reflection
        def hitWall(self):
            if self.y <= 0 or self.y >= self.HEIGHT:
                self.yFac *= -1
            if self.x <= 0 or self.x >= self.WIDTH:
                self.xFac *= -1
        #If it hit the paddle, it result into reflection and change side of the ball
        def hitPlayer(self, players: dict):
            '''
            Checks if the ball has hit any player.
            If it hits, reflect the ball and optionally change its direction slightly.
            '''
            for player in players.values():
                match player.position:
                    case Position.LEFT:
                        if (self.x <= player.x + self.paddle_width and
                            self.x >= player.x and
                            player.y <= self.y <= player.y + self.paddle_height):
                            self.xFac *= -1
                            self.side = Side.LEFT
                            return player.id
                    
                    case Position.RIGHT:
                        if (self.x + 5 >= player.x and
                            self.x <= player.x + self.paddle_width and
                            player.y <= self.y <= player.y + self.paddle_height):
                            self.xFac *= -1
                            self.side = Side.RIGHT
                            return player.id

                    case Position.TOP:
                        if (self.y <= player.y + self.paddle_width and
                            self.y >= player.y and
                            player.x <= self.x <= player.x + self.paddle_height):
                            self.yFac *= -1
                            self.side = Side.LEFT
                            return player.id

                    case Position.BOTTOM:
                        if (self.y + 5 >= player.y and
                            self.y <= player.y + self.paddle_width and
                            player.x <= self.x <= player.x + self.paddle_height):
                            self.yFac *= -1
                            self.side = Side.RIGHT
                            return player.id
            return None

        def get_side(self):
            return self.side
    
    class Player:
        '''
        The Player object contains the following:
            - uuid: unique identifier for the player
            - side: side of the player (LEFT, RIGHT, NONE)
            - x: x pos
            - y: y pos
            - position: position of the player (LEFT, RIGHT, TOP, BOTTOM)
        '''

        def __init__(self, uuid: Optional[str], side=Side.NONE, x=0.0, y=0.0, position=None):
            '''
            The Player object contains the following:
                - uuid: unique identifier for the player
                - side: side of the player (LEFT, RIGHT, NONE)
                - x: x pos
                - y: y pos
            '''
            self.id: Optional[str] = uuid
            self.side = side
            self.x = x
            self.y = y
            self.position = position

        def __str__(self):
            return f"Player {self.id} at ({self.x}, {self.y}), side: {self.side}, position: {self.position}"
        
        def update(self, x, y):
            '''
            Updates the player position and side.
            '''
            self.x = x
            self.y = y

    
    def __init__(self):
        self.ball = self.Ball()
        self.players = {
            "p1": self.Player(uuid=None, side=Side.LEFT, position=Position.LEFT),
            "p2": self.Player(uuid=None, side=Side.RIGHT, position=Position.RIGHT),
            "p3": self.Player(uuid=None, side=Side.LEFT, position=Position.TOP),
            "p4": self.Player(uuid=None, side=Side.RIGHT, position=Position.BOTTOM)
        }
        self.game_lock = threading.Lock()
        self.paused = False
        self.ended = False

    def __str__(self):
        return f"({self.ball.x}, {self.ball.y}, paused: {self.paused}), players: {self.players}"
    
    def add_player(self, new_id:str, x=0.0, y=0.0,):
        '''
        Adds a player to the game state.
        '''
        MAX_PLAYERS = 4

        with self.game_lock:
            count = 0
            for player in self.players.values():
                if player.id == new_id:
                    raise ValueError(f"Player {new_id} already exists.")
                if player.id is not None:
                    count += 1
            
            if count >= MAX_PLAYERS:
                raise ValueError(f"Maximum number of players {MAX_PLAYERS} reached.")
        
            

            for key, slot in self.players.items():
                if slot.id is None:
                    slot.id = new_id
                    slot.x = x
                    slot.y = y
                    return key
        
        return None
    
    def remove_player(self, remove_id: str) -> Optional[str]:
        '''
        Removes a player from the game state.
        '''
        with self.game_lock:
                for player in self.players.values():
                    if player.id == remove_id:

                        player.id = None
                        player.x = 0.0
                        player.y = 0.0
                        
                        print(f"Player {remove_id} removed from game state.")
                        return

        return None




    def pause(self):
        with self.game_lock:
            self.paused = True
        
    def unpause(self):
        with self.game_lock:
            self.paused = False
    
    def end(self):
        with self.game_lock:
            self.ended = False

    def is_paused(self):
        with self.game_lock:
            return self.paused
    


    




