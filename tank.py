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
    def __init__(self, x, y, colour, scale, id):

        self.x = x
        self.y = y
        self.width = 50  
        self.height = 50  
        self.colour = colour
        self.vel = 0.2
        self.rotation = 0
        self.image_path = TANK_IMAGES.get(self.colour)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.scale = scale
        self.bullet_x_start = self.x 
        self.bullet_y_start = self.y 
        self.fireable = True
        self.load_image()
        self.firetimer = 0
        self.fire_cooldown = 60
        self.id = id
    
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
        win.blit(self.image,(self.x * scale, self.y * scale))

    def move(self, map_grid, scale, wall_rects):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            self.rotation = 135
            dx = self.vel
            dy = -self.vel
            self.bullet_x = self.x + 1 + 1
            self.bullet_y = self.y - 1

        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            self.rotation = 45
            dx = self.vel
            dy = self.vel
            self.bullet_x_start = self.x + 1 + 1
            self.bullet_y_start = self.y + 1 + 1

        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            self.rotation = 315
            dx = -self.vel
            dy = self.vel
            self.bullet_x_start = self.x - 1
            self.bullet_y_start = self.y + 1 + 1

        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            self.rotation = 225
            dx = -self.vel
            dy = -self.vel
            self.bullet_x_start = self.x - 1
            self.bullet_y_start = self.y - 1

        elif keys[pygame.K_LEFT]:
            dx = -self.vel
            self.rotation = 270
            self.bullet_x_start = self.x -1 
            self.bullet_y_start = self.y + 0.3

        elif keys[pygame.K_RIGHT]:
            dx = self.vel
            self.rotation = 90
            self.bullet_x_start = self.x + 1 +1
            self.bullet_y_start = self.y + 0.3

        elif keys[pygame.K_UP]:
            dy = -self.vel
            self.rotation = 180
            self.bullet_x_start = self.x + 0.3 
            self.bullet_y_start = self.y -1

        elif keys[pygame.K_DOWN]:
            dy = self.vel
            self.rotation = 0
            self.bullet_x_start = self.x + 0.3
            self.bullet_y_start = self.y + 1 + 1


        originalx = self.x
        originaly = self.y

        self.scaled_rect = self.rect
        self.scaled_rect[0] = self.rect[0] * scale 
        self.scaled_rect[1] = self.rect[1] * scale
        self.scaled_rect[2] = scale 
        self.scaled_rect[3] = scale
        self.collision_rect = self.scaled_rect.move(dx * scale, dy * scale) 

        self.scaled_x = self.collision_rect[0] 
        self.scaled_y = self.collision_rect[1] #get the x and y co ordinates based off map tile grid.

        # print(wall_rects)
        if not any(self.collision_rect.colliderect(wall) for wall in wall_rects):
            self.x += dx
            self.y += dy

        # self.x += dx
        # self.y += dy
        self.update()

    def fired(self):
        if self.check_fireable():
            self.fire_data = (self.bullet_x_start, self.bullet_y_start, self.rotation, self.colour)
            self.firetimer = self.fire_cooldown
            return self.fire_data
        return None
        
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if self.firetimer > 0:
            self.firetimer -= 1

    def shrink(self, screen_height):
        self.image = pygame.transform.scale(self.image, (screen_height//50, screen_height//50))

    # def scalee(self, scale):
    #     self.x = scale * self.x
    #     self.y = scale * self.y
    #     self.width = scale
    #     self.height = scale
    #     self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_solid_tile(self, tile):
        try:
            color = tile[0].get_at((0, 0))
            return color[0] > 100
        
        except:
            return False
        
    def check_fireable(self):
        return self.firetimer <= 0