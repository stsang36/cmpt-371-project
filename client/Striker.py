import pygame
import pong_setup
class striker:
    ''' Striker class contains the following:
        - posx: x position of the striker
        - posy: y position of the striker
        - width: width of the striker
        - height: height of the striker
        - speed: speed of the striker
        - color: color of the striker
        - pRect: pygame.Rect object for the striker
        - pDraw: pygame.draw.rect object for the striker

        Methods:
        Printing the striker object will return the position and color of the striker.
        - display: display the striker.
        - updateVert: update the vertical position.
        - updateHori: update the horizontal position.
        - updatePos: update the position of the striker using server data.
        - displayScore: display the text score.
        - getRect: return the pygame.Rect object of the striker.

    '''


    
    def __init__(self, posx: float, posy: float, width: int, height: int, speed: float, 
                 color: tuple[int, int, int]):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.pRect = pygame.Rect(posx, posy, width, height)
        self.pDraw = pygame.draw.rect(pong_setup.screen, self.color, self.pRect)

    def __str__ (self) -> str:
        return f"{self.color} Striker at ({self.posx}, {self.posy})"    
    
    # Used to display the object on the screen
    def display(self, is_current_player:bool=False) -> None:
        self.pDraw = pygame.draw.rect(pong_setup.screen, self.color, self.pRect)

        if is_current_player:
            pygame.draw.rect(pong_setup.screen, (255, 255, 0), self.pRect, width=3)


    def updateVert(self, yFac: float) -> None:
        ''' Update the vertical position of the striker
            # if yFac == -1 ==> The object is moving upwards
            # if yFac == 1 ==> The object is moving downwards
            # if yFac == 0 ==> The object is not moving
        
        '''
        self.posy = self.posy + self.speed*yFac

        if self.posy <= 0:
            self.posy = 0
        elif self.posy + self.height >= pong_setup.HEIGHT:
            self.posy = pong_setup.HEIGHT-self.height
    
    def updateHori(self, xFac: float) -> None:
        ''' Update the horizontal position of the striker
            # if xFac == -1 ==> The object is moving left
            # if xFac == 1 ==> The object is moving right
            # if xFac == 0 ==> The object is not moving
        '''
        
        self.posx = self.posx + self.speed*xFac

        if self.posx <= 0:
            self.posx = 0
        elif self.posx + self.width >= pong_setup.WIDTH:
            self.posx = pong_setup.WIDTH-self.width

    def updatePos(self):
        '''
        Update the position of the striker using server data.
        '''
        self.pRect = pygame.Rect(self.posx, self.posy, self.width, self.height)


    def displayScore(self, text, score, x, y, color):
        text = pong_setup.font20.render(text+str(score), True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)

        pong_setup.screen.blit(text, textRect)

    def getRect(self) -> pygame.Rect:
        return self.pRect