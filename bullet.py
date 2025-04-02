#import libraries and intialise pygame
import time
import pygame
pygame.init()

class Bullet:
    def __init__(self, x, y, colour, angle):
        self.x = x
        self.y = y
        self.radius = 3
        self.colour = colour
        self.bullet_speed = 0.25
        self.bullet_diagonal_speed = ((2 ** 0.5) ** -2) * self.bullet_speed #calculate how much x and y need to increase by if the bullet is moving diagonally
        self.firetime = 60
        self.angle = angle 
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius) #create the rect for the circle
        self.last_redraw_time = time.time() #stores the current time (epoch)
        self.created = True

    def draw(self, win, scale):
        if self.firetime > 0: #only draws the bullet if the firetime is above zero
            pygame.draw.circle(win, self.colour, (self.x * scale, self.y * scale), self.radius) #draws a circle to window, in the tank that fired's colour

    def move(self, wall_rects, scale):
        dx = 0 #potential movement
        dy = 0

        if self.created: #if True
            self.created = False
            self.last_redraw_time = time.time() #stores the time
            return

        self.delta_time = time.time() - self.last_redraw_time #calculates the time difference between now and when it was last redrawn (seconds)
        self.last_redraw_time = time.time() #store the time (epoch)

        factored_speed = self.delta_time / self.bullet_speed #how much the bullet should move, based on the time since last redraw
        factored_diagonal_speed = self.delta_time / self.bullet_speed

        #calculating how much the bullet should move depending on its angle
        if self.angle == 0: #down
            dy = factored_speed 
        elif self.angle == 45: #down right
            dx = factored_diagonal_speed
            dy = factored_diagonal_speed
        elif self.angle == 90:#right
            dx = factored_speed
        elif self.angle == 135: #up right
            dx = factored_diagonal_speed
            dy = -factored_diagonal_speed
        elif self.angle == 180: #up
            dy = -factored_speed
        elif self.angle == 225: #up left
            dx = -factored_diagonal_speed
            dy = -factored_diagonal_speed
        elif self.angle == 270: #left
            dx = -factored_speed
        elif self.angle == 315: #down left
            dx = -factored_diagonal_speed
            dy = factored_diagonal_speed

        self.scaled_rect = self.rect #creating a collision rect based on client pixels rather than server co-ordinates
        self.scaled_rect[0] = self.rect[0] * scale #x
        self.scaled_rect[1] = self.rect[1] * scale #y
        self.scaled_rect[2] = scale #width
        self.scaled_rect[3] = scale #height

        self.collision_rect = self.scaled_rect.move(dx * scale, dy * scale) #creating a new collision rect based on scaled values

        if any(self.scaled_rect.colliderect(wall) for wall in wall_rects): #checks for collision against a wall, if there is set lifetime to 0
            self.firetime = 0
        else: #if theres no collision, move the bullet based on it's potential movement
            self.x += dx
            self.y += dy
        
        self.rect.x = self.x #update rect
        self.rect.y = self.y

    #lifetime function
    def firetimer(self, wall_rects, scale):#calculate bullet firetime
        if self.firetime > 0: #while its alive
            self.move(wall_rects, scale) #move the bullet
            self.firetime -= 1 #decrease the firetime
        return self.firetime > 0 #return True or False

    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius) #update the rect

    def is_solid_tile(self, tile): #checks the tiles to see if they are solid, cannot be collided with
        try:
            color = tile[0].get_at((0, 0)) #gets the RGB colour of the top left pixel from the tile
            return color[0] > 100 #return True/False depending whether the red value is above 100 or not
        
        except:
            return False
        