import pygame
import pong_setup

class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac = 1
        self.yFac = -1
        self.ball = pygame.draw.circle(
            pong_setup.screen, self.color, (self.posx, self.posy), self.radius)
        self.beenHit = 0
        self.lastHit = 0

    def display(self):
        self.ball = pygame.draw.circle(
            pong_setup.screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        self.posx += self.speed*self.xFac
        self.posy += self.speed*self.yFac

        # If the ball hits the surfaces, 
        # with no players hiting it
        # it results in a reflection
        if self.posy <= 0 or self.posy >= pong_setup.HEIGHT:
            self.yFac *= -1
        if self.posx <= 0 or self.posx >= pong_setup.WIDTH:
            self.xFac *= -1

        # Hit on strikers

        if self.posx <= 0 and self.beenHit:
            return self.lastHit
        elif self.posx >= pong_setup.WIDTH and self.beenHit:
            return self.lastHit
        elif self.posy <= 0 and self.beenHit:
            return self.lastHit
        elif self.posy >= pong_setup.HEIGHT and self.beenHit:
            return self.lastHit
        else:
            return 0

    def reset(self):
        self.posx = pong_setup.WIDTH//2
        self.posy = pong_setup.HEIGHT//2
        self.xFac *= -1
        self.beenHit = 0
        self.lastHit = 0

    # Used to reflect the ball along the X-axis
    def hitX(self):
        # Update beenHit bool to true
        self.beenHit = 1

        # Check wich VertiStriker hit
        if self.posx < pong_setup.WIDTH/2:
            self.lastHit = 1 # geek1
        else:
            self.lastHit = 2 # geek2
        self.xFac *= -1

    # Used to reflect the ball along the Y-axis
    def hitY(self):
        # Update beenHit bool to true
        self.beenHit = 1

        # Check wich HoriStriker hit
        if self.posy < pong_setup.HEIGHT/2:
            self.lastHit = 3 # geek3
        else:
            self.lastHit = 4 # geek4
        self.yFac *= -1

    def getRect(self):
        return self.ball