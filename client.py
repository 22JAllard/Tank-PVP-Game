#client
import pygame

pygame.init()
run = True

window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

#stores info about client screen size
display = pygame.display.Info()
screen_width = display.current_w
screen_height = display.current_h

#load images etc
menu_bg = pygame.image.load('menu_bg.png')

class Button():
    def __init__ (self, x, y, width, height, colour):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.rect = (x, y, width, height)

    def draw(self, window):
        pygame.draw.rect(window, self.colour, self.rect)

    # def clicked(self):
    #     pass

class CenteredText():
    def __init__ (self, y, colour, message, size, font):
        self.x = screen_width//2
        self.y = y
        self.colour = colour
        self.message = message
        self.size = size
        self.font = font

        self.font = pygame.font.SysFont(self.font, size)

        self.text = self.font.render(self.message, True, self.colour)
    
    def draw(self, window):
        window.blit(self.text, (self.x - self.text.get_width()//2, self.y)) 

def main_menu():
    window.blit(menu_bg, (0,0))
    text1 = CenteredText(30, (0,0,0), "Menu", 100, "Arial")
    
while run:
    main_menu()

    pygame.display.flip()

    key = pygame.key.get_pressed()
    if key[pygame.K_ESCAPE]:
        run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
        
