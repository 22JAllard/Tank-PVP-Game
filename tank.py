import pygame

zerotank = pygame.image.load('0tank.png')
onetank = pygame.image.load('1tank.png')
twotank = pygame.image.load('2tank.png')
threetank = pygame.image.load('3tank.png')
fourtank = pygame.image.load('4tank.png')
fivetank = pygame.image.load('5tank.png')

class Tank:
    def __init__(self, x, y, colour, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.rect = pygame.Rect(x, y, width, height)
        self.vel = 3

    def draw(self, win):
        pygame.draw.rect(win, self.colour, self.rect) #modify to have tank graphic once we have a tank yk

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.vel

        if keys[pygame.K_RIGHT]:
            self.x += self.vel

        if keys[pygame.K_UP]:
            self.y -= self.vel

        if keys[pygame.K_DOWN]:
            self.y += self.vel

        self.update()
        
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)