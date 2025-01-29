#client
import pygame
from network import Network
from map import Map

pygame.init()
run = True

window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

#stores info about client screen size
display = pygame.display.Info()
screen_width = display.current_w
screen_height = display.current_h

entered_ip = ""
colour_pos = 0
tank_colours = [(255,0,0), (0,255,0), (0,0,255), (255,255,0)]
client_colour = tank_colours[colour_pos]

def server_connect():
    server_connect_text = CenteredText(350, (0,0,0), "Enter server IP", 50, "Arial")
    server_connect_text.draw(window)

    global entered_ip
    entered_ip_text = CenteredText(400, (0,0,0), entered_ip, 30, "Arial")
    entered_ip_text.draw(window)

    input_active = True
    if event.type == pygame.KEYDOWN and input_active:
        if event.key == pygame.K_RETURN:
            input_active = False
            #try connect to said ip
        elif event.key == pygame.K_BACKSPACE:
            entered_ip = entered_ip[:-1]
        else:
            entered_ip += event.unicode
        pygame.display.update

def play_menu():
    global menu; menu = play_menu
    menu_bg = pygame.image.load('menu_bg.png')
    window.blit(menu_bg, (0,0))

    server_connect()

def customise_menu():
    global menu; menu = customise_menu
    customise_bg = pygame.image.load('warehouse.png')
    customise_bg = pygame.transform.scale(customise_bg, (screen_width, screen_height))
    window.blit(customise_bg, (0,0))

    customise_text = CenteredText(30, (0,0,0), "Customise", 100, "Arial")
    customise_text.draw(window)

    colour_button = ColourButton(screen_width//2 + 50, 200, 550, 80, (0,0,0), "Colour", "Arial", 80, client_colour)
    colour_button.draw(window)

    colour_button.arrow_click()

def settings_menu():
    global menu; menu = settings_menu
    print("settings")

def quit_menu():
    global menu; menu = quit_menu
    print("exit")

class ColourButton():
    def __init__ (self, x, y, width, height, text_colour, text, font, size, selected_colour):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.button_colour = selected_colour
        self.text_colour = text_colour
        self.text = text
        self.size = size
        self.font = pygame.font.SysFont(font, self.size)

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.label = self.font.render(self.text, True, self.text_colour)

    def draw(self, window):
        pygame.draw.rect(window, self.button_colour, self.rect)

        self.arrow_left = self.font.render("<", True, self.text_colour)
        self.arrow_right = self.font.render(">", True, self.text_colour)

        window.blit(self.arrow_left, (self.x + 10, self.y + (self.height - self.label.get_height())//2))
        window.blit(self.arrow_right, (self.x + self.width - 10 - self.arrow_right.get_width(), self.y + (self.height - self.label.get_height())//2))

        window.blit(self.label, (self.x + (self.width - self.label.get_width())//2, self.y + (self.height - self.label.get_height())//2))
    
    def arrow_click(self):
        global colour_pos
        if pygame.mouse.get_pressed()[0] == 1:
            if pygame.mouse.get_pos()[0] > self.x and pygame.mouse.get_pos()[0] < (self.x + 10 + self.arrow_left.get_width()) and pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < (self.y + self.arrow_left.get_width()):
                if colour_pos == 0:
                    colour_pos = 3
                else:
                    colour_pos -= 1
            elif pygame.mouse.get_pos()[0] > (self.x + self.width - 10 - self.arrow_right.get_width()) and pygame.mouse.get_pos()[0] < (self.x + self.width) and pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < (self.y + self.arrow_left.get_width()):
                if colour_pos == 3:
                    colour_pos = 0
                else:
                    colour_pos += 1
            global client_colour
            client_colour = tank_colours[colour_pos]

class Button(): 
    def __init__ (self, x, y, width, height, button_colour, text_colour, text, font, size, function, what_menu):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.button_colour = button_colour
        self.text_colour = text_colour
        self.text = text
        self.size = size
        self.font = pygame.font.SysFont(font, self.size)
        self.function = function
        self.menu = what_menu

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.label = self.font.render(self.text, True, self.text_colour)

    def draw(self, window):
        pygame.draw.rect(window, self.button_colour, self.rect)
        window.blit(self.label, (self.x + (self.width - self.label.get_width())//2, self.y + (self.height - self.label.get_height())//2))
    
    def click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and menu == self.menu:
            if self.rect.collidepoint(event.pos):
                self.function()

class CenteredButton(Button):
    def __init__(self, y, width, height, button_colour, text_colour, text, font, size, function, what_menu):
        x = screen_width // 2 - width // 2
        super().__init__(x, y, width, height, button_colour, text_colour, text, font, size, function, what_menu)

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
        CenteredButton(150, 400, 100, (255,255,255),(0,0,0), "Play", "Arial", 80, play_menu, main_menu),
        CenteredButton(screen_height - 150, 400, 100, (255,255,255), (0,0,0), "Customise", "Arial", 80, customise_menu, main_menu),
        #Button(screen_width - 150, screen_height - 150, 100, 100, (255, 255, 255), (0,0,0), "Exit", "Arial", 25, quit_menu, main_menu),
        #Button(50, screen_height - 150, 100, 100, (255,255,255), (0,0,0), "Settings", "Arial", 25, settings_menu, main_menu)
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