import pygame

pygame.init()

# Font that is used to render the text
font20 = pygame.font.Font('freesansbold.ttf', 20)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
# Used to adjust the frame rate
clock = pygame.time.Clock()
FPS = 30

def displayText(text:str, score:int, x:float, y:float, color:tuple[int, int, int]) -> None:
    t = font20.render(text+ " " + str(score), True, color)
    textRect = t.get_rect()
    textRect.center = (x, y)
    
    screen.blit(t, textRect)