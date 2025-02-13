import pygame
pygame.init()

TANK_IMAGES = {
    (255,0,0): '0tank.png',
    (0,255,0): '1tank.png',
    (0,0,255): '2tank.png',
    (255,255,0): '3tank.png',
    (255,127,11): '4tank.png',
    (255,21,123): '5tank.png'
}

class Tank:
    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        self.width = self.x
        self.height = self.y
        self.colour = colour
        # self.rect = pygame.Rect(x, y, width, height)
        self.vel = 3
        
        self.image_path = TANK_IMAGES.get(self.colour)
    
    def load_image(self):
        if hasattr(self, 'image_path') and self.image_path:
            self.image = pygame.image.load(self.image_path)
            #self.image = pygame.transform.scale(self.image, (screen_height//50, screen_height//50))
        else:
            raise ValueError(f"No image path found for colour {self.colour}")

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('image', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.load_image()


    def draw(self, win):
        #pygame.draw.rect(win, self.colour, self.rect) #modify to have tank graphic once we have a tank yk
        win.blit(self.image,(self.x, self.y))

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

    def shrink(self, screen_height):
        self.image = pygame.transform.scale(self.image, (screen_height//50, screen_height//50))

    def scale(self, scale):
        self.width *= scale
        self.height *= scale