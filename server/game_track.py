
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
        def __init__ (self, x=0.0, y=0.0, xFac = 1, yFac = 1, WIDTH = 900, HEIGHT = 600):
            self.x = x
            self.y = y
            self.xFac = xFac
            self.yFac = yFac
            self.side = Side.NONE
            self.WIDTH = WIDTH
            self.HEIGHT = HEIGHT
            

        def __str__(self):
            return f"Ball at position ({self.x}, {self.y}, {self.side})"
        
        def update(self, x: float, y: float, side: Side=Side.NONE):
            '''
            Updates the ball position and side.
            '''
            self.x += self.xFac * 5
            self.y += self.yFac * 5
            self.side = side
            self.hitWall()

        def hitWall(self):
            if self.y <= 0 or self.y >= self.HEIGHT:
                self.yFac *= -1
            if self.x <= 0 or self.x >= self.WIDTH:
                self.xFac *= -1
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
    
    def add_player(self, new_id:str, x=0.0, y=0.0,):
        '''
        Adds a player to the game state.
        '''
        with self.game_lock:
            for player in self.players.values():
                if player.id == new_id:
                    raise ValueError(f"Player {new_id} already exists.")
            

            for key, slot in self.players.items():
                if slot.id is None:
                    slot.id = new_id
                    slot.x = x
                    slot.y = y
                    return key
        
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


    




