import pygame
import pong_setup

class ball:
    ''' Local storage of the Client side ball object contains the following:
        - posx: x position of the ball
        - posy: y position of the ball
        - radius: radius of the ball
        - color
        - ball: pygame circle object for the ball

        Methods:
        - .display(): display the ball.
    '''

    def __init__(self, posx: float, posy: float, radius: float, color: tuple[int, int, int]):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.color = color
        self.ball = pygame.draw.circle(
            pong_setup.screen, self.color, (self.posx, self.posy), self.radius)

    def __str__ (self) -> str:
        return f"Client object Ball at ({self.posx}, {self.posy})"
    
    def display(self) -> None:
        
        self.ball = pygame.draw.circle(
            pong_setup.screen, self.color, (self.posx, self.posy), self.radius)
