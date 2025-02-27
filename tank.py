import pygame
pygame.init()
from bullet import Bullet

TANK_IMAGES = {
    (255,0,0): '0tank.png',
    (0,255,0): '1tank.png',
    (0,0,255): '2tank.png',
    (255,255,0): '3tank.png',
    (255,127,11): '4tank.png',
    (255,21,123): '5tank.png'
}

class Tank:
    def __init__(self, x, y, colour, scale):

        self.x = x
        self.y = y
        self.width = 50  
        self.height = 50  
        self.colour = colour
        self.vel = 1
        self.rotation = 0
        self.image_path = TANK_IMAGES.get(self.colour)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.scale = scale
        self.bullet_x_start = self.x + scale * 0.3
        self.bullet_y_start = self.y + scale
        self.fireable = True
    
    def load_image(self):
        if hasattr(self, 'image_path') and self.image_path:
            self.image = pygame.image.load(self.image_path)

        else:
            raise ValueError(f"No image path found for colour {self.colour}")

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('image', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.load_image()

    def draw(self, win, scale):
        #pygame.draw.rect(win, self.colour, self.rect) #modify to have tank graphic once we have a tank yk
        self.image = pygame.transform.scale(self.image, (scale *(0.6), scale))
        self.image = pygame.transform.rotate(self.image, self.rotation)
        win.blit(self.image,(self.x, self.y))

    def move(self, map_grid, scale, wall_rects):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            self.rotation = 135
            dx = self.vel
            dy = -self.vel
            self.bullet_x = self.x +scale
            self.bullet_y = self.y 

        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            self.rotation = 45
            dx = self.vel
            dy = self.vel
            self.bullet_x_start = self.x + scale
            self.bullet_y_start = self.y + scale

        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            self.rotation = 315
            dx = -self.vel
            dy = self.vel
            self.bullet_x_start = self.x 
            self.bullet_y_start = self.y + scale

        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            self.rotation = 225
            dx = -self.vel
            dy = -self.vel
            self.bullet_x_start = self.x
            self.bullet_y_start = self.y

        elif keys[pygame.K_LEFT]:
            dx = -self.vel
            self.rotation = 270
            self.bullet_x_start = self.x 
            self.bullet_y_start = self.y + scale * 0.3

        elif keys[pygame.K_RIGHT]:
            dx = self.vel
            self.rotation = 90
            self.bullet_x_start = self.x + scale
            self.bullet_y_start = self.y + scale * 0.3

        elif keys[pygame.K_UP]:
            dy = -self.vel
            self.rotation = 180
            self.bullet_x_start = self.x + scale * 0.3
            self.bullet_y_start = self.y 

        elif keys[pygame.K_DOWN]:
            dy = self.vel
            self.rotation = 0
            self.bullet_x_start = self.x + scale * 0.3
            self.bullet_y_start = self.y +scale

        

        originalx = self.x
        originaly = self.y

        self.collision_rect = self.rect.move(dx, dy)

        self.scaled_x = self.collision_rect[0]//scale 
        self.scaled_y = self.collision_rect[1]//scale #get the x and y co ordinates based off map tile grid.

        if not any(self.collision_rect.colliderect(wall) for wall in wall_rects):
            self.x += dx
            self.y += dy

        self.update()

    def fired(self):
        
        #wait for client to press f
        #return something to client which can then bounce to server through network to make a new bullet instance

        if self.fireable == True:
            self.fireable = False
            self.fire_data = (self.bullet_x_start, self.bullet_y_start, self.rotation, self.colour) #needs to have a value for bullet start poss
            return self.fire_data
        
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def shrink(self, screen_height):
        self.image = pygame.transform.scale(self.image, (screen_height//50, screen_height//50))

    def scalee(self, scale):
        self.x = scale * self.x
        self.y = scale * self.y
        self.width = scale
        self.height = scale
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_solid_tile(self, tile):
        try:
            color = tile[0].get_at((0, 0))
            return color[0] > 100
        
        except:
            return False