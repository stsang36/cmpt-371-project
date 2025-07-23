import pygame

pygame.init()

# Font that is used to render the text
font20 = pygame.font.Font('freesansbold.ttf', 20)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

clock = pygame.time.Clock()    
FPS = 60

# Striker class

# Verticle Players

class VertiStriker:
        # Take the initial position, dimensions, speed and color of the object
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        # Rect that is used to control the position and collision of the object
        self.geekRect = pygame.Rect(posx, posy, width, height)
        # Object that is blit on the screen
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    # Used to display the object on the screen
    def display(self):
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def update(self, yFac):
        self.posy = self.posy + self.speed*yFac

        # Restricting the striker to be below the top surface of the screen
        if self.posy <= 0:
            self.posy = 0
        # Restricting the striker to be above the bottom surface of the screen
        elif self.posy + self.height >= HEIGHT:
            self.posy = HEIGHT-self.height

        # Updating the rect with the new values
        self.geekRect = (self.posx, self.posy, self.width, self.height)

    def displayScore(self, text, score, x, y, color):
        text = font20.render(text+str(score), True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)

        screen.blit(text, textRect)

    def getRect(self):
        return self.geekRect

# Horizontal Players

class HoriStriker:
        # Take the initial position, dimensions, speed and color of the object
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        # Rect that is used to control the position and collision of the object
        self.geekRect = pygame.Rect(posx, posy, width, height)
        # Object that is blit on the screen
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    # Used to display the object on the screen
    def display(self):
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def update(self, xFac):
        self.posx = self.posx + self.speed*xFac

        # Restricting the striker to be below the top surface of the screen
        if self.posx <= 0:
            self.posx = 0
        # Restricting the striker to be above the bottom surface of the screen
        elif self.posx + self.width >= WIDTH:
            self.posx = WIDTH-self.width

        # Updating the rect with the new values
        self.geekRect = (self.posx, self.posy, self.width, self.height)

    def displayScore(self, text, score, x, y, color):
        text = font20.render(text+str(score), True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)

        screen.blit(text, textRect)

    def getRect(self):
        return self.geekRect

# Ball class


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
            screen, self.color, (self.posx, self.posy), self.radius)
        self.beenHit = 0
        self.lastHit = 0

    def display(self):
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        self.posx += self.speed*self.xFac
        self.posy += self.speed*self.yFac

        # If the ball hits the surfaces, 
        # with no players hiting it
        # it results in a reflection
        if self.posy <= 0 or self.posy >= HEIGHT:
            self.yFac *= -1
        if self.posx <= 0 or self.posx >= WIDTH:
            self.xFac *= -1

        # Hit on strikers

        if self.posx <= 0 and self.beenHit:
            return self.lastHit
        elif self.posx >= WIDTH and self.beenHit:
            return self.lastHit
        elif self.posy <= 0 and self.beenHit:
            return self.lastHit
        elif self.posy >= HEIGHT and self.beenHit:
            return self.lastHit
        else:
            return 0

    def reset(self):
        self.posx = WIDTH//2
        self.posy = HEIGHT//2
        self.xFac *= -1
        self.beenHit = 0
        self.lastHit = 0

    # Used to reflect the ball along the X-axis
    def hitX(self):
        # Update beenHit bool to true
        self.beenHit = 1

        # Check wich VertiStriker hit
        if self.posx < WIDTH/2:
            self.lastHit = 1 # geek1
        else:
            self.lastHit = 2 # geek2
        self.xFac *= -1

    # Used to reflect the ball along the Y-axis
    def hitY(self):
        # Update beenHit bool to true
        self.beenHit = 1

        # Check wich HoriStriker hit
        if self.posy < HEIGHT/2:
            self.lastHit = 3 # geek3
        else:
            self.lastHit = 4 # geek4
        self.yFac *= -1

    def getRect(self):
        return self.ball

# Game Manager


def main():
    running = True

    # Defining the objects
    geek1 = VertiStriker(20, (HEIGHT/2)-50, 10, 100, 10, GREEN)
    geek2 = VertiStriker(WIDTH-30, (HEIGHT/2)-50, 10, 100, 10, GREEN)
    geek3 = HoriStriker((WIDTH/2)-50, 20, 100, 10, 10, GREEN)
    geek4 = HoriStriker((WIDTH/2)-50, HEIGHT-30, 100, 10, 10, GREEN)
    ball = Ball(WIDTH//2, HEIGHT//2, 7, 5, WHITE)

    VertiGeeks = [geek1, geek2]
    HoriGeeks = [geek3, geek4]

    # Initial parameters of the players
    geek1Score, geek2Score, geek3Score, geek4Score = 0, 0, 0, 0
    geek1YFac, geek2YFac, geek3XFac, geek4XFac = 0, 0, 0, 0

    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    geek2YFac = -1
                if event.key == pygame.K_DOWN:
                    geek2YFac = 1
                if event.key == pygame.K_w:
                    geek1YFac = -1
                if event.key == pygame.K_s:
                    geek1YFac = 1
                if event.key == pygame.K_RIGHT:
                    geek3XFac = 1
                if event.key == pygame.K_LEFT:
                    geek3XFac = -1
                if event.key == pygame.K_d:
                    geek4XFac = 1
                if event.key == pygame.K_a:
                    geek4XFac = -1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    geek2YFac = 0
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    geek1YFac = 0
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    geek3XFac = 0
                if event.key == pygame.K_d or event.key == pygame.K_a:
                    geek4XFac = 0

        # Collision detection
        for geek in VertiGeeks:
            if pygame.Rect.colliderect(ball.getRect(), geek.getRect()):
                ball.hitX()
        for geek in HoriGeeks:
            if pygame.Rect.colliderect(ball.getRect(), geek.getRect()):
                ball.hitY()

        # Updating the objects
        geek1.update(geek1YFac)
        geek2.update(geek2YFac)
        geek3.update(geek3XFac)
        geek4.update(geek4XFac)
        point = ball.update()

        # 1 -> Geek_1 has scored
        # 2 -> Geek_2 has scored
        # 3 -> Geek_3 has scored
        # 4 -> Geek_4 has scored
        #  0 -> None of them scored
        if point == 1:
            geek1Score += 1
        elif point == 2:
            geek2Score += 1
        elif point == 3:
            geek3Score += 1
        elif point == 4:
            geek4Score += 1

        # Someone has scored
        # a point and the ball is out of bounds.
        # So, we reset it's position
        if point:   
            ball.reset()

        # Displaying the objects on the screen
        geek1.display()
        geek2.display()
        geek3.display()
        geek4.display()
        ball.display()

        # Displaying the scores of the players
        geek1.displayScore("Geek_1 : ", 
                           geek1Score, 100, 20, WHITE)
        geek2.displayScore("Geek_2 : ", 
                           geek2Score, WIDTH-100, 20, WHITE)
        geek3.displayScore("Geek_3 : ", 
                           geek3Score, 100, HEIGHT-30, WHITE)
        geek4.displayScore("Geek_4 : ", 
                           geek4Score, WIDTH-100, HEIGHT-30, WHITE)

        pygame.display.update()
        clock.tick(FPS)     


if __name__ == "__main__":
    main()
    pygame.quit()