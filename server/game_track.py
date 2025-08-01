from enum import Enum
import threading
from typing import Optional
import random

MAX_PLAYERS = 4

class Side(Enum):
    '''
    Represents the side of the game.
    '''
    UPPER = 'u'
    LOWER = 'l'
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
        def __init__ (self, x = 450, y = 300, xFac = 1, yFac = 1, WIDTH = 900, HEIGHT = 600, paddle_width = 10, paddle_height = 100, scoreboard_ref = None):
            self.x = x
            self.y = y
            self.xFac = xFac
            self.yFac = yFac
            self.side = Side.NONE
            self.WIDTH = WIDTH
            self.HEIGHT = HEIGHT
            self.paddle_width = paddle_width
            self.paddle_height = paddle_height
            self.scoreboard_ref = scoreboard_ref
            self.last_touched_player = None

        def __str__(self):
            return f"Ball at position ({self.x}, {self.y}, {self.side})"
        
        def reset(self):
            '''
            Resets the ball to the center with a random direction.
            '''
            self.x = self.WIDTH / 2
            self.y = self.HEIGHT / 2
            self.side = Side.NONE
            # Random direction: choose xFac and yFac as either -1 or 1
            self.xFac = random.choice([-1, 1])
            self.yFac = random.choice([-1, 1])

        def score(self, side: Side, x: float, y: float): # change to pass ball coords

            #print(f"Scoring for side: {side}")

            curr_scoreboard = self.scoreboard_ref
            
            if curr_scoreboard is None:
                raise ValueError("Scoreboard reference is not set.")
            
            hit_top = y <= 0
            hit_bottom = y >= self.HEIGHT
            hit_left = x <= 0
            hit_right = x >= self.WIDTH

            if side == Side.UPPER:
                if hit_top or hit_left:
                    # own goal upper hits top or left side
                    self.scoreboard_ref["lower_score"] += 1
                else:
                    self.scoreboard_ref["upper_score"] += 1

            elif side == Side.LOWER:
                if hit_bottom or hit_right:
                    # own goal lower hits bottom or right side
                    self.scoreboard_ref["upper_score"] += 1
                    
                else:
                    self.scoreboard_ref["lower_score"] += 1
            
            print(f"Scoreboard updated: {self.scoreboard_ref}")
            
        
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
            '''
            Checks if the ball hits any edge. If it hits any edge after a paddle hit, reset the ball.
            Otherwise, reflect the ball for top/bottom edges (if no prior paddle hit).
            '''
            if self.y <= 0 or self.y >= self.HEIGHT or self.x <= 0 or self.x >= self.WIDTH:
                if self.side in [Side.UPPER, Side.LOWER]:
                    self.score(self.side, self.x, self.y)
                    self.reset()
                else:
                    if self.y <= 0 or self.y >= self.HEIGHT:
                        self.yFac *= -1
                    if self.x <= 0 or self.x >= self.WIDTH:
                        self.xFac *= -1
        
        def hitPlayer(self, players: dict):
            '''
            Checks if the ball has hit any player's paddle inner surface.
            If it hits, reflect the ball and update last touched player.
            Only counts hits on the inner surfaces of paddles.
            '''
            for player_slot, player in players.items():
                if player.id is None:  # Skip empty slots
                    continue
                    #made changes to only count hits on the inner surfaces of paddles (#todo:Cornercases to be tested)
                match player.position:
                    case Position.LEFT:
                        # Only count hits on the right surface (inner surface) of left paddle
                        if (self.x <= player.x + self.paddle_width and
                            self.x >= player.x and
                            player.y <= self.y <= player.y + self.paddle_height and
                            self.xFac < 0):  # Ball must be moving left to hit inner surface
                            self.xFac *= -1
                            self.side = Side.UPPER
                            self.last_touched_player = player_slot
                            return player.id
                    
                    case Position.RIGHT:
                        # Only count hits on the left surface (inner surface) of right paddle
                        if (self.x + 5 >= player.x and
                            self.x <= player.x + self.paddle_width and
                            player.y <= self.y <= player.y + self.paddle_height and
                            self.xFac > 0):  # Ball must be moving right to hit inner surface
                            self.xFac *= -1
                            self.side = Side.LOWER
                            self.last_touched_player = player_slot
                            return player.id

                    case Position.TOP:
                        # Only count hits on the bottom surface (inner surface) of top paddle
                        if (self.y <= player.y + self.paddle_width and
                            self.y >= player.y and
                            player.x <= self.x <= player.x + self.paddle_height and
                            self.yFac < 0):  # Ball must be moving up to hit inner surface
                            self.yFac *= -1
                            self.side = Side.UPPER  # You might want to adjust this logic
                            self.last_touched_player = player_slot
                            return player.id

                    case Position.BOTTOM:
                        # Only count hits on the top surface (inner surface) of bottom paddle
                        if (self.y + 5 >= player.y and
                            self.y <= player.y + self.paddle_width and
                            player.x <= self.x <= player.x + self.paddle_height and
                            self.yFac > 0):  # Ball must be moving down to hit inner surface
                            self.yFac *= -1
                            self.side = Side.LOWER  # You might want to adjust this logic
                            self.last_touched_player = player_slot
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
        self.players = {
            "p1": self.Player(uuid=None, side=Side.UPPER, position=Position.LEFT),
            "p2": self.Player(uuid=None, side=Side.LOWER, position=Position.RIGHT),
            "p3": self.Player(uuid=None, side=Side.UPPER, position=Position.TOP),
            "p4": self.Player(uuid=None, side=Side.LOWER, position=Position.BOTTOM)
        }
        self.game_lock = threading.Lock()
        self.paused = False
        self.ended = False
        self.scoreboard = {
            "upper_score": 0,
            "lower_score": 0
        }
        self.ball = self.Ball(scoreboard_ref=self.scoreboard)

    def __str__(self):
        return f"({self.ball.x}, {self.ball.y}, paused: {self.paused}), players: {self.players}"
    
    def add_player(self, new_id:str, x=0.0, y=0.0,):
        '''
        Adds a player to the game state.
        '''
        

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
    
    def get_player_list(self):
        '''
        Returns a list of players with empty slots too.
        '''
        with self.game_lock:
            return self.players


    def get_scoreboard(self):
        '''
        Returns the scoreboard.
        '''
        with self.game_lock:
            return self.scoreboard
        
    def update_scoreboard(self, upper_score: int, lower_score: int):
        '''
        Updates the scoreboard.
        '''
        with self.game_lock:
            self.scoreboard["upper_score"] = upper_score
            self.scoreboard["lower_score"] = lower_score



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
    


    




