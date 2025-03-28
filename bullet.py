import time
import pygame
pygame.init()

#bullet class

class Bullet:
    def __init__(self, x, y, colour, angle, ):
        self.x = x
        self.y = y
        self.radius = 3
        self.colour = colour
        self.bullet_speed = 0.25
        self.bullet_diagonal_speed = ((2 ** 0.5) ** -2) * self.bullet_speed #1 should be hypotenuse, and x/y less than 1
        self.firetime = 60
        self.angle = angle #known as rotation in the tank class
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)
        self.last_redraw_time = time.time()
        #self.player = player
        self.created = True


#draw function
    def draw(self, win, scale):

        if self.firetime > 0:
            pygame.draw.circle(win, self.colour, (self.x * scale, self.y * scale), self.radius)
            print(self.firetime)

#move function
    def move(self, wall_rects, scale):
        dx = 0
        dy = 0

        if self.created:
            self.created = False
            self.last_redraw_time = time.time()
            return

        self.delta_time = time.time() - self.last_redraw_time
        self.last_redraw_time = time.time()


        factored_speed = self.delta_time / self.bullet_speed
        # factored_speed = self.bullet_speed
        factored_diagonal_speed = self.delta_time / self.bullet_speed
        # factored_diagonal_speed =  self.bullet_speed
        #print("welcome to bullet move")
        if self.angle == 0: 
            dy = factored_speed #self.bullet_speed
            # self.y += self.bullet_speed
        elif self.angle == 45:
            dx = factored_diagonal_speed
            dy = factored_diagonal_speed
            # self.x += self.bullet_diagonal_speed
            # self.y += self.bullet_diagonal_speed
        elif self.angle == 90:
            dx = factored_speed
            # self.x += self.bullet_speed
        elif self.angle == 135:
            dx = factored_diagonal_speed
            dy = -factored_diagonal_speed
            # self.x += self.bullet_diagonal_speed
            # self.y -= self.bullet_diagonal_speed
        elif self.angle == 180:
            dy = -factored_speed
            # self.y -= self.bullet_speed
        elif self.angle == 225:
            dx = -factored_diagonal_speed
            dy = -factored_diagonal_speed
            # self.x -= self.bullet_diagonal_speed
            # self.y -= self.bullet_diagonal_speed
        elif self.angle == 270:
            dx = -factored_speed
            # self.x -= self.bullet_speed
        elif self.angle == 315:
            dx = -factored_diagonal_speed
            dy = factored_diagonal_speed
            # self.x -= self.bullet_diagonal_speed
            # self.y += self.bullet_diagonal_speed
        #self.draw()

        self.scaled_rect = self.rect
        self.scaled_rect[0] = self.rect[0] * scale 
        self.scaled_rect[1] = self.rect[1] * scale
        self.scaled_rect[2] = scale 
        self.scaled_rect[3] = scale
        self.collision_rect = self.scaled_rect.move(dx * scale, dy * scale) 
        if any(self.scaled_rect.colliderect(wall) for wall in wall_rects):
            self.firetime = 0
        else:
            self.x += dx
            self.y += dy
        
        self.rect.x = self.x
        self.rect.y = self.y

#lifetime function
    def firetimer(self, wall_rects, scale):
        if self.firetime > 0:
            self.move(wall_rects, scale)
            self.firetime -= 1
        return self.firetime > 0

    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)

    def is_solid_tile(self, tile):
        try:
            color = tile[0].get_at((0, 0))
            return color[0] > 100
        
        except:
            return False
        