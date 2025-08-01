class Button():
    
    def __init__(self, image, posx, posy, textInput, font, baseColr, hoveringColr):
        self.image = image
        self.posx = posx
        self.posy = posy
        self.font = font
        self.baseColr = baseColr
        self.hoveringColr = hoveringColr
        self.textInput = textInput
        self.text = self.font.render(self.textInput, True, self.baseColr)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.posx, self.posy))
        self.textRect = self.text.get_rect(center=(self.posx, self.posy))

    # Displays image/text onto screen
    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.rect)

    # Checks if button is being clicked
    def checkForInput(self, posx, posy):
        if posx in range (self.rect.left, self.rect.right) and posy in range (self.rect.top, self.rect.bottom):
            return True
        return False
    
    # Changes button colour when being hovered by mouse
    def changeColour(self, posx, posy):
        if posx in range (self.rect.left, self.rect.right) and posy in range (self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.textInput, True, self.hoveringColr)
        else:
            self.text = self.font.render(self.textInput, True, self.baseColr)
