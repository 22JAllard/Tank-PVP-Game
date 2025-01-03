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
    def __init__ (self, x, y, width, height, coloura, colourb, text, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.coloura = coloura
        self.colourb = colourb
        self.text = text
        self.font = pygame.font.SysFont(font, self.height - 20)

        self.rect = (self.x, self.y, self.width, self.height)

        self.label = self.font.render(self.text, True, self.colourb)

    def draw(self, window):
        pygame.draw.rect(window, self.coloura, self.rect)
        window.blit(self.label, (screen_width//2 - self.label.get_width()//2, self.y + 10))

    # def clicked(self):
    #     pass

class CenteredButton(Button):
    def __init__ (self, x, y, width, height, coloura, colourb, text, font):
        self.x = screen_width//2 - width//2
        self.y = y
        self.width = width
        self.height = height
        self.coloura = coloura
        self.colourb = colourb
        self.text = text
        self.font = pygame.font.SysFont(font, self.height - 20)

        self.rect = (self.x, self.y, self.width, self.height)
        self.label = self.font.render(self.text, True, self.colourb)

class CenteredText():
    def __init__ (self, y, colour, message, size, font):
        self.x = screen_width//2
        self.y = y
        self.colour = colour
        self.message = message
        self.size = size

        self.font = pygame.font.SysFont(font, self.size)

        self.text = self.font.render(self.message, True, self.colour)
    
    def draw(self, window):
        window.blit(self.text, (self.x - self.text.get_width()//2, self.y)) 

def main_menu():
    window.blit(menu_bg, (0,0))

    #text
    title_text = CenteredText(30, (255,255,255), "Tank PVP Game", 100, "Arial")
    title_text.draw(window)

    #buttons
    test = CenteredButton(0, 200, 300, 100, (255,255,255),(0,0,0), "Button", "Arial")
    test.draw(window)
    
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
        
