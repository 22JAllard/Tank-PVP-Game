#import libraries
import pygame
pygame.init()
from bullet import Bullet

TANK_IMAGES = { #create a dictionary with all the tank images in, with the colour as key
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
        self.image_path = TANK_IMAGES.get(self.colour) #gets the path for the image based on the colour given to the client (colour is key)
        self.rect = pygame.Rect(x, y, self.width, self.height) #create a rectangle for the tank using the x, y, width and height values
        self.scale = scale
        self.bullet_x_start = self.x 
        self.bullet_y_start = self.y 
        self.fireable = True
        self.load_image() #calls function to store the image itself in self.image
        self.firetimer = 0
        self.fire_cooldown = 60
        self.id = id
    
    def load_image(self):
        if hasattr(self, 'image_path') and self.image_path: #check if the image path exists
            self.image = pygame.image.load(self.image_path)

        else:
            raise ValueError(f"No image path found for colour {self.colour}")

    def __getstate__(self): 
        state = self.__dict__.copy() #create a copy of the object's attribute dictionary
        state.pop('image', None) #remove the image attribute from the state if it exists
        return state

    def __setstate__(self, state):
        self.__dict__.update(state) #restore the objects attributes from the unpickled version
        self.load_image() #reload the image after deserialisation
 
    def draw(self, win, scale):
        self.image = pygame.transform.scale(self.image, (scale *(0.6), scale)) #scale the tank image so that it fits in a map tile (scale x scale)
        self.image = pygame.transform.rotate(self.image, self.rotation) #rotate the tank image using it's self.rotation value
        win.blit(self.image,(self.x * scale, self.y * scale)) #draw the image to the screen, with x and y being multiplied by scale so it fits client screens pixels, rather than server co-ordinates

    def move(self, map_grid, scale, wall_rects):
        keys = pygame.key.get_pressed() #check for a key press
        dx = 0 #set potential movement to 0
        dy = 0

        if keys[pygame.K_UP] and keys[pygame.K_RIGHT]: #checks for multiple keys being pressed first, moves diagonal
            self.rotation = 135 #down is 0, 90 degrees to right, 45 for the diagonal
            dx = self.vel #set the potential movement from the velocity
            dy = -self.vel
            self.bullet_x = self.x + 1 + 1 #edit bullet x and y to match the correct start point for bullets
            self.bullet_y = self.y - 1

        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]: 
            self.rotation = 45 #down is 0, only adding 45 for the diagonal
            dx = self.vel #set the potential movement from the velocity
            dy = self.vel
            self.bullet_x_start = self.x + 1 + 1 #edit bullet x and y to match the correct start point for bullets
            self.bullet_y_start = self.y + 1 + 1

        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            self.rotation = 315 #adds 270 to face left, plus 45 for diagonal
            dx = -self.vel #set the potential movement from the velocity
            dy = self.vel
            self.bullet_x_start = self.x - 1 #edit bullet x and y to match the correct start point for bullets
            self.bullet_y_start = self.y + 1 + 1

        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            self.rotation = 225 #adds 180 to face up, and 45 for diagonal
            dx = -self.vel #set the potential movement from the velocity
            dy = -self.vel
            self.bullet_x_start = self.x - 1 #edit bullet x and y to match the correct start point for bullets
            self.bullet_y_start = self.y - 1

        elif keys[pygame.K_LEFT]:
            dx = -self.vel #set the potential movement from the velocity
            self.rotation = 270 #faces left
            self.bullet_x_start = self.x -1 #edit bullet x and y to match the correct start point for bullets
            self.bullet_y_start = self.y + 0.3

        elif keys[pygame.K_RIGHT]:
            dx = self.vel #set the potential movement from the velocity
            self.rotation = 90 #faces right
            self.bullet_x_start = self.x + 1 +1 #edit bullet x and y to match the correct start point for bullets
            self.bullet_y_start = self.y + 0.3

        elif keys[pygame.K_UP]:
            dy = -self.vel #set the potential movement from the velocity
            self.rotation = 180 #faces up
            self.bullet_x_start = self.x + 0.3 #edit bullet x and y to match the correct start point for bullets
            self.bullet_y_start = self.y -1

        elif keys[pygame.K_DOWN]:
            dy = self.vel #set the potential movement from the velocity
            self.rotation = 0 #faces down, 0 is no rotation
            self.bullet_x_start = self.x + 0.3 #edit bullet x and y to match the correct start point for bullets
            self.bullet_y_start = self.y + 1 + 1

        self.scaled_rect = self.rect #changing the rect from based on the servers 50x50 grid to the clients scaled window
        self.scaled_rect[0] = self.rect[0] * scale #x
        self.scaled_rect[1] = self.rect[1] * scale #y
        self.scaled_rect[2] = scale #width, both need to fit in one tile, which is scale x scale
        self.scaled_rect[3] = scale #height
        self.collision_rect = self.scaled_rect.move(dx * scale, dy * scale) #make a new rect based on the scaling for testing collisions

        self.scaled_x = self.collision_rect[0] 
        self.scaled_y = self.collision_rect[1] #get the x and y co ordinates based off map tile grid

        if not any(self.collision_rect.colliderect(wall) for wall in wall_rects): #if the tank won't collide with anything, add the potential movement
            self.x += dx
            self.y += dy

        self.update() #update the tank

    def fired(self):
        if self.check_fireable(): #call the check_fireable function to see if the tank can fire
            self.fire_data = (self.bullet_x_start, self.bullet_y_start, self.rotation, self.colour) #create a tuple called fire_data with the bullet x and y start co-ordinates, the rotation, and the colour
            self.firetimer = self.fire_cooldown 
            return self.fire_data
        return None
        
    def update(self): #updates the tank
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) #updates the tank with the new rect
        if self.firetimer > 0: #decreases the firetimer if its more than 0
            self.firetimer -= 1

    def shrink(self, screen_height):
        self.image = pygame.transform.scale(self.image, (screen_height//50, screen_height//50)) #scales the image down to fit a tile
    
    def is_solid_tile(self, tile): #checks the tiles to see if they are solid, cannot be collided with
        try:
            color = tile[0].get_at((0, 0)) #gets the RGB colour of the top left pixel from the tile 
            return color[0] > 100 #return True/False depending whether the red value is above 100 or not
        
        except:
            return False
        
    def check_fireable(self):
        return self.firetimer <= 0 #returns True/False