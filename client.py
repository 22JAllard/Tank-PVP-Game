#client
import pygame

pygame.init()
run = True

window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

#stores info about client screen size
display = pygame.display.Info()
screen_width = display.current_w
screen_height = display.current_h

def play_menu():
    global menu; menu = play_menu
    print("play")

def customise_menu():
    global menu; menu = customise_menu
    customise_bg = pygame.image.load('warehouse.png')
    customise_bg = pygame.transform.scale(customise_bg, (screen_width, screen_height))
    window.blit(customise_bg, (0,0))

    customise_text = CenteredText(30, (0,0,0), "Customise", 100, "Arial")
    customise_text.draw(window)

def settings_menu():
    global menu; menu = settings_menu
    print("settings")

def quit_menu():
    global menu; menu = quit_menu
    print("exit")

class Button(): 
    def __init__ (self, x, y, width, height, coloura, colourb, text, font, size, function):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.coloura = coloura
        self.colourb = colourb
        self.text = text
        self.size = size
        self.font = pygame.font.SysFont(font, self.size)
        self.function = function

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.label = self.font.render(self.text, True, self.colourb)

    def draw(self, window):
        pygame.draw.rect(window, self.coloura, self.rect)
        window.blit(self.label, (self.x + (self.width - self.label.get_width())//2, self.y + (self.height - self.label.get_height())//2))
    
    def click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.function()

class CenteredButton(Button):
    def __init__(self, x, y, width, height, coloura, colourb, text, font, size, function):
        super().__init__(screen_width // 2 - width // 2, y, width, height, coloura, colourb, text, font, size, function)

class Text():
    def __init__ (self, x, y, colour, message, size, font):
        self.x = x
        self.y = y
        self.colour = colour
        self.message = message
        self.size = size

        self.font = pygame.font.SysFont(font, self.size)
        self.text = self.font.render(self.message, True, self.colour)
    
    def draw(self, window):
        window.blit(self.text, (self.x - self.text.get_width()//2, self.y)) 

class CenteredText(Text):
    def __init__(self, y, colour, message, size, font):
        x = screen_width //2
        super().__init__(x, y, colour, message, size, font)

def main_menu():
    menu_bg = pygame.image.load('menu_bg.png')
    window.blit(menu_bg, (0,0))

    #text
    title_text = CenteredText(30, (255,255,255), "Tank PVP Game", 100, "Arial")
    title_text.draw(window)

    global buttons
    buttons = [
        CenteredButton(0, 150, 400, 100, (255,255,255),(0,0,0), "Play", "Arial", 80, play_menu),
        CenteredButton(0, screen_height - 200, 400, 100, (255,255,255), (0,0,0), "Customise", "Arial", 80, customise_menu),
        Button(screen_width - 150, screen_height - 150, 100, 100, (255, 255, 255), (0,0,0), "Exit", "Arial", 25, quit_menu),
        Button(50, screen_height - 150, 100, 100, (255,255,255), (0,0,0), "Settings", "Arial", 25, settings_menu)
    ]

    for button in buttons:
        button.draw(window)
    
    return buttons

menu = main_menu
while run:
    menu()

    pygame.display.flip()

    key = pygame.key.get_pressed()
    if key[pygame.K_ESCAPE]:
        run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        for button in buttons:
                button.click(event)

    pygame.display.update()
pygame.display.quit()
pygame.quit()
        
