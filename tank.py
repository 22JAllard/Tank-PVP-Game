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
        self.width = 30  
        self.height = 50  
        self.colour = colour
        self.vel = 2
        self.rotation = 0
        self.image_path = TANK_IMAGES.get(self.colour)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.wall_rects = []
        self.bullet_x = x
        self.bullet_y = y
    
    def load_image(self):
        if hasattr(self, 'image_path') and self.image_path:
            self.image = pygame.image.load(self.image_path)
            self.width = self.image.get_width()
            self.height = self.image.get_height()

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

            
    def tank_fire(self, win,scale):
        pygame.draw.circle(win, self.colour, (self.bullet_x, self.bullet_y), 2, 2)
        pygame.display.flip()

        print(scale)
        print(self.width, self.height)
        print(self.x, self.y)
        print(self.bullet_x, self.bullet_y)

        print("fired")

    def move(self, map_grid, scale, wall_rects, win):
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
            self.bullet_x = self.x + scale
            self.bullet_y = self.y + scale

        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            self.rotation = 315
            dx = -self.vel
            dy = self.vel
            self.bullet_x = self.x 
            self.bullet_y = self.y + scale

        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            self.rotation = 225
            dx = -self.vel
            dy = -self.vel
            self.bullet_x = self.x
            self.bullet_y = self.y

        elif keys[pygame.K_LEFT]:
            dx = -self.vel
            self.rotation = 270
            self.bullet_x = self.x 
            self.bullet_y = self.y + scale * 0.3

        elif keys[pygame.K_RIGHT]:
            dx = self.vel
            self.rotation = 90
            self.bullet_x = self.x + scale
            self.bullet_y = self.y + scale * 0.3

        elif keys[pygame.K_UP]:
            dy = -self.vel
            self.rotation = 180
            self.bullet_x = self.x + scale * 0.3
            self.bullet_y = self.y 

        elif keys[pygame.K_DOWN]:
            dy = self.vel
            self.rotation = 0
            self.bullet_x = self.x + scale * 0.3
            self.bullet_y = self.y +scale

        if keys[pygame.K_f]:
            self.tank_fire(win, scale)

        #self.collision_rect = pygame.Rect(self.rect.x, self.rect.y, self.width, self.height)
        self.collision_rect = self.rect.move(dx, dy)

        self.scaled_x = self.collision_rect[0]//scale 
        self.scaled_y = self.collision_rect[1]//scale #get the x and y co ordinates based off map tile grid.

        if not any(self.collision_rect.colliderect(wall) for wall in wall_rects):
            self.x += dx
            self.y += dy

        # print(map_grid[:1])

        
        # for i in range(0,50):
        #     map_numerical_grid = map_grid[i][1][:1]//scale
        #     print(map_numerical_grid)

        self.update()
        
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def scale(self, scale):
        self.x = scale * self.x
        self.y = scale * self.y
        self.width = scale * 0.6
        self.height = scale
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_solid_tile(self, tile,):
        try:
            color = tile[0].get_at((0, 0))
            return color[0] > 100
        
        except:
            return False
