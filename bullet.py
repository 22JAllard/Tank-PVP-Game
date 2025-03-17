import pygame
pygame.init()

#bullet class

class Bullet:
    def __init__(self, x, y, colour, angle, ):
        self.x = float(x)
        self.y = float(y)
        self.radius = 3
        self.colour = colour
        self.bullet_speed = 2
        self.bullet_diagonal_speed = ((2 ** 0.5) ** -2) * self.bullet_speed #1 should be hypotenuse, and x/y less than 1
        self.firetime = 60
        self.angle = angle #known as rotation in the tank class
        #self.player = player


#draw function
    def draw(self, win):
        if self.firetime > 0:
            try:
                pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius)
            except TypeError as e:
                print(f"Error drawing bullet - colour: {self.colour}, pos: ({self.x}, {self.y}), error: {e}")


#move function
    def move(self):
        #print("welcome to bullet move")
        if self.angle == 0: 
            self.y += self.bullet_speed
        elif self.angle == 45:
            self.x += self.bullet_diagonal_speed
            self.y += self.bullet_diagonal_speed
        elif self.angle == 90:
            self.x += self.bullet_speed
        elif self.angle == 135:
            self.x += self.bullet_diagonal_speed
            self.y -= self.bullet_diagonal_speed
        elif self.angle == 180:
            self.y -= self.bullet_speed
        elif self.angle == 225:
            self.x -= self.bullet_diagonal_speed
            self.y -= self.bullet_diagonal_speed
        elif self.angle == 270:
            self.x -= self.bullet_speed
        elif self.angle == 315:
            self.x -= self.bullet_diagonal_speed
            self.y += self.bullet_diagonal_speed
        #self.draw()

#lifetime function
    def firetimer(self):
        if self.firetime > 0:
            self.firetime -= 1

    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)