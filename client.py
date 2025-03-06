#client
import pygame
from network import Network
import pickle
from os import path
from tank import Tank
from bullet import Bullet
#from map import Map

pygame.init()
run = True
network = None

window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

#stores info about client screen size
display = pygame.display.Info()
screen_width = display.current_w
screen_height = display.current_h
scale = screen_height//50

clock = pygame.time.Clock()
mapnumber = None
input_active = True
no_map_number = True
entered_ip = ""
colour_pos = 0
tank_colours = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,127,11), (255,21,123)]
client_colour = tank_colours[colour_pos]
wall_rects = []
bullet_fireable = True
map_unloaded = True

zerotank = pygame.image.load('0tank.png')
onetank = pygame.image.load('1tank.png')
twotank = pygame.image.load('2tank.png')
threetank = pygame.image.load('3tank.png')
fourtank = pygame.image.load('4tank.png')
fivetank = pygame.image.load('5tank.png')

class Map:
    def __init__(self, data):
        self.tile_list = []
        self.tile_size = screen_height //50

        try:
            self.wood_block_image = pygame.image.load('0.png')
            self.dirt_path_image = pygame.image.load('1.png')
        except pygame.error as error:
            print(f"Error loading images: {error}")
            return

        global wall_rects
        for row_index, row in enumerate(data):
            for col_index, char in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size

                if char == '0':
                    img = pygame.transform.scale(self.wood_block_image, (self.tile_size, self.tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = x
                    img_rect.y = y
                    self.tile_list.append((img, img_rect))
                    wall_rects.append(img_rect)

                elif char == '1':
                    img = pygame.transform.scale(self.dirt_path_image, (self.tile_size, self.tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = x
                    img_rect.y = y
                    self.tile_list.append((img, img_rect))

    def draw(self, window):
        for tile, rect in self.tile_list:
            window.blit(tile, rect)

def server_connect():
    global input_active
    server_connect_text = CenteredText(350, (0,0,0), "Enter server IP", 50, "Arial")
    server_connect_text.draw(window)

    global entered_ip
    entered_ip_text = CenteredText(400, (0,0,0), entered_ip, 30, "Arial")
    entered_ip_text.draw(window)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_RETURN:
                input_active = False
                return entered_ip
            elif event.key == pygame.K_BACKSPACE:
                entered_ip = entered_ip[:-1]
            else:
                entered_ip = entered_ip + str(event.unicode)

def load_level():
    map_file = f'map{mapnumber}.txt'
    with open(map_file, 'r') as file:
        map_data = [list(line.strip()) for line in file]
    print(f"Loaded map data")
    return map_data

def play_menu():
    global menu; menu = play_menu
    global network; global no_map_number

    menu_bg = pygame.image.load('menu_bg.png')
    window.blit(menu_bg, (0,0))

    server_ip = server_connect()
    global no_map_number
    if server_ip and no_map_number:
        try:
            print("Attempting to connect to server. IP: ", server_ip)
            global network
            network = Network(server_ip, client_colour, scale) #creates a new instance of the network class, also where the connecting stuff is

            initial_data = network.initial_data
            if initial_data:
                global mapnumber 
                mapnumber = initial_data["map_number"] #searching the recieved data from the server for the value with "map_number"
                print("Selected map", mapnumber)
                no_map_number = False  
                
                global map_unloaded
                if map_unloaded:
                    map_unloaded = False
                    global world_data
                    world_data = load_level()
                
                if world_data:
                    game_map = Map(world_data)
                    game()  
                else:
                    print("Failed to load map data :(")
            else:
                print("Failed to receive initial data :(")

        except Exception as error:
            print("Failed to connect: ", error)

def game():
    global menu; menu = game
    global players, scale, world_data, wall_rects, network
    map_data = world_data
    game_map = Map(map_data)

    if not network or not network.connected:
        print("No network connected")
        menu = main_menu
        return
    
    if 'players' not in globals():
        players={}

#Get player tank through network
    try:
        game_map = Map(map_data) #
        player = network.initial_data["tank"]
        player.colour = client_colour
        
        #player.shrink(screen_height)
        global scale
        scale = int(scale)
        player.scalee(scale)
        running = True
        #Add network.connected check
        while network.connected and running:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    network.disconnect()
                    
            map_grid = game_map.tile_list 
            player.move(map_grid, scale, wall_rects)

            #send something about a bullet being fired??

            # Clear screen and draw map
            window.fill((0, 0, 0))
            game_map.draw(window)
            
            #  player drawing
            if 'players' in players:
                for player_id, tank in players['players'].items():
                    tank.draw(window, scale)
                    print(f"Drawing tank for player {player_id}: {tank}")
            
            #seems to just be drawing bullet as the tank? and even when there is no bullet. Also completely messes up the drawing of the tank so its ###
            # if 'bullets' in players is not None:
            #     for player_id, bullet in players['players'].items():
            #         bullet.draw(window, scale)
            #         print(f"Drawing bullet for player {player_id}: {tank}")

            bullets = []
            keys = pygame.key.get_pressed()

            if keys[pygame.K_f] and player.fireable:
                fire_data = player.fired() #this then needs to be sent to the server to make a new instance of bullet
                if fire_data:
                    bullet_x, bullet_y, angle, colour = fire_data
                    bullets.append(Bullet(bullet_x, bullet_y, angle, colour))
                    bullets = network.send_bullet(fire_data)

            for bullet in bullets[:]:
                bullet.draw(window)
                bullet.firetimer()
                if bullet.firetime <= 0:
                    bullets.remove(bullet)

# Send player data and get updated players
            
            players = network.send(player)
            pygame.display.update()
            
    except Exception as e:
        print(f"Error in game: {e}")
    finally:  # Added cleanup in finally block
        if network:
            network.disconnect()
        menu = main_menu
    
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

    back_button = Button(50, 50, 50, 50, (255,255,255), (0,0,0), "<", "Arial", 25, main_menu, customise_menu)
    back_button.draw(window)
    back_button.click(event)

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
                    colour_pos = 5
                else:
                    colour_pos -= 1
            elif pygame.mouse.get_pos()[0] > (self.x + self.width - 10 - self.arrow_right.get_width()) and pygame.mouse.get_pos()[0] < (self.x + self.width) and pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < (self.y + self.arrow_left.get_width()):
                if colour_pos == 5:
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
    global menu; menu = main_menu
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
    clock.tick(60)
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