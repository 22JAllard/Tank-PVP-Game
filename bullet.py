import pygame
pygame.init()

#bullet class

class Bullet:
    def __init__(self, x, y, colour, angle, ):
        self.x = x
        self.y = y
        self.radius = 3
        self.colour = colour
        self.bullet_speed = 4
        self.bullet_diagonal_speed = ((2 ** 0.5) ** -2) * self.bullet_speed #1 should be hypotenuse, and x/y less than 1
        self.firetime = 60
        self.angle = angle #known as rotation in the tank class
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)
        #self.player = player


#draw function
    def draw(self, win):
        print("drawing")
        if self.firetime > 0:
            pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius)

#move function
    def move(self, wall_rects):
        dx = 0
        dy = 0
        #print("welcome to bullet move")
        if self.angle == 0: 
            dy = self.bullet_speed
            # self.y += self.bullet_speed
        elif self.angle == 45:
            dx = self.bullet_diagonal_speed
            dy = self.bullet_diagonal_speed
            # self.x += self.bullet_diagonal_speed
            # self.y += self.bullet_diagonal_speed
        elif self.angle == 90:
            dx = self.bullet_speed
            # self.x += self.bullet_speed
        elif self.angle == 135:
            dx = self.bullet_diagonal_speed
            dy = -self.bullet_diagonal_speed
            # self.x += self.bullet_diagonal_speed
            # self.y -= self.bullet_diagonal_speed
        elif self.angle == 180:
            dy = -self.bullet_speed
            # self.y -= self.bullet_speed
        elif self.angle == 225:
            dx = -self.bullet_diagonal_speed
            dy = -self.bullet_diagonal_speed
            # self.x -= self.bullet_diagonal_speed
            # self.y -= self.bullet_diagonal_speed
        elif self.angle == 270:
            dx = -self.bullet_speed
            # self.x -= self.bullet_speed
        elif self.angle == 315:
            dx = -self.bullet_diagonal_speed
            dy = self.bullet_diagonal_speed
            # self.x -= self.bullet_diagonal_speed
            # self.y += self.bullet_diagonal_speed
        #self.draw()

        if any(self.rect.colliderect(wall) for wall in wall_rects):
            self.firetime = 0
        else:
            self.x += dx
            self.y += dy
        
        self.rect.x = self.x
        self.rect.y = self.y

#lifetime function
    def firetimer(self, wall_rects):
        if self.firetime > 0:
            self.move(wall_rects)
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
        