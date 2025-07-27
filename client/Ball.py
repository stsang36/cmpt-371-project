import pygame
import pong_setup

class ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.color = color
        self.ball = pygame.draw.circle(
            pong_setup.screen, self.color, (self.posx, self.posy), self.radius)

    def display(self):
        self.ball = pygame.draw.circle(
            pong_setup.screen, self.color, (self.posx, self.posy), self.radius)
