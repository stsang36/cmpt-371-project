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
        - players: dict of Player objects with keys as player IDs
        - game_lock: threading lock for game state
        - paused: boolean indicating if the game is paused
        - ended: boolean to see if the game has ended
        - scoreboard: dict that contains the current score of upper and lower sides
    Methods:
        - add_player() to add a player to the game state
        - remove_player() to remove a player from the game state
        - get_player_list() to get a list of players with empty slots too
        - get_scoreboard() to get the current scoreboard
        - update_scoreboard() to update the scoreboard
        - pause() to pause the game
        - unpause() to unpause the game
        - end() to end the game
        - is_paused() to check if the game is paused
        - is_ended() to check if the game has ended
        - reset_game() to reset the game state
    '''
    class Ball:
        '''
        The Game State Ball object contains the following:
            - x: x pos
            - y: y pos
            - xFac: x factor
            - yFac: y factor
            - WIDTH: width of the game area
            - HEIGHT: height of the game area
            - paddle_width: width of the paddle
            - paddle_height: height of the paddle
            - scoreboard_ref: reference to the scoreboard
            - last_touched_player: the player who last touched the ball

        Methods:
            - printing the object will return the position and side.
            - update(x, y, side): updates the ball position and side.
            - reset(): resets the ball to the center with a random direction.
            - score(side, x, y): updates the scoreboard based on the side and position of the ball.
            - update(players): updates the ball position and checks for collisions.
            - hitWall(): checks if the ball hits a wall
            - hitPlayer(players): checks if the ball has hit any player's paddle
            - get_side(): returns the side of the ball
            
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

        def score(self, side: Side, x: float, y: float):

            #print(f"Scoring for side: {side}")

            curr_scoreboard = self.scoreboard_ref
            
            if curr_scoreboard is None:
                raise ValueError("Scoreboard reference is not set.")
            
            hit_top = y <= 0
            hit_bottom = y >= self.HEIGHT
            hit_left = x <= 0
            hit_right = x >= self.WIDTH
            print(side)
            if side == Side.UPPER:
                if hit_top or hit_left:
                    # own goal upper hits top or left side
                    curr_scoreboard["lower_score"] += 1
                else:
                    curr_scoreboard["upper_score"] += 1

            elif side == Side.LOWER:
                if hit_bottom or hit_right:
                    # own goal lower hits bottom or right side
                    curr_scoreboard["upper_score"] += 1
                    
                else:
                    curr_scoreboard["lower_score"] += 1
            
            print(f"Scoreboard updated: {curr_scoreboard}")
            
        
        def update(self, players = None):
            '''
            Updates the ball position and side.
            '''
            self.x += self.xFac * 5
            self.y += self.yFac * 5
            self.hitWall()
            if players:
                self.hitPlayer(players)
             
        def hitWall(self):
            '''
            Checks if the ball hits any edge and resets the ball if it does and gives a point to a side.
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
            checks if the ball has hit any player's paddle.
            If it has, it will return the player ID of the player who hit the ball.
            '''
            for player_slot, player in players.items():
                if player.id is None:  # Skip empty slots
                    continue
                    
                match player.position:
                    case Position.LEFT:
                        if (self.x <= player.x + self.paddle_width and
                            self.x >= player.x and
                            player.y <= self.y <= player.y + self.paddle_height and
                            self.xFac < 0):  
                            self.xFac *= -1
                            self.side = Side.UPPER
                            self.last_touched_player = player_slot
                            return player.id
                    
                    case Position.RIGHT:
                        if (self.x + 5 >= player.x and
                            self.x <= player.x + self.paddle_width and
                            player.y <= self.y <= player.y + self.paddle_height and
                            self.xFac > 0):  
                            self.xFac *= -1
                            self.side = Side.LOWER
                            self.last_touched_player = player_slot
                            return player.id

                    case Position.TOP:
                        if (self.y <= player.y + self.paddle_width and
                            self.y >= player.y and
                            player.x <= self.x <= player.x + self.paddle_height and
                            self.yFac < 0):  
                            self.yFac *= -1
                            self.side = Side.UPPER 
                            self.last_touched_player = player_slot
                            return player.id

                    case Position.BOTTOM:
                        if (self.y + 5 >= player.y and
                            self.y <= player.y + self.paddle_width and
                            player.x <= self.x <= player.x + self.paddle_height and
                            self.yFac > 0):  
                            self.yFac *= -1
                            self.side = Side.LOWER  
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
        Methods:
            - printing the object will return the position and side.
            - update(x, y): updates the player position.
        '''

        def __init__(self, uuid: Optional[str], side=Side.NONE, x=0.0, y=0.0, position=None):

            self.id: Optional[str] = uuid
            self.side = side
            self.x = x
            self.y = y
            self.position = position

        def __str__(self):
            return f"Player {self.id} at ({self.x}, {self.y}), side: {self.side}, position: {self.position}"
        
        def update(self, x, y):
            '''
            Updates the player position.
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
            self.ended = True
            self.paused = True

    def is_paused(self):
        with self.game_lock:
            return self.paused
        
    def is_ended(self):
        with self.game_lock:
            return self.ended
        
   

    
    def reset_game(self):
        '''
        Resets the game.
        '''
        with self.game_lock:
            self.scoreboard = {
                "upper_score": 0,
                "lower_score": 0
            }
            self.paused = False
            self.ended = False
            self.ball = self.Ball(scoreboard_ref=self.scoreboard)
            self.ball.reset()
    


    




