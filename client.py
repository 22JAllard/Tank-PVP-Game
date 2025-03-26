#client
import pygame
from network import Network
import pickle
from os import path
from tank import Tank
from bullet import Bullet
import time
import ast
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
fireable = False
map_unloaded = True
bullets = []
send_data = {}
last_fire = False
username = "Type to enter username"
saved = False
loaded = False
save_button_colour = (255,255,255)
load_button_colour = (255,255,255)
loaded_username = None

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
    server_connect_text = CenteredText(350, (255,255,255), "Enter server IP", 50, "Arial")
    server_connect_text.draw(window)

    global entered_ip
    entered_ip = "192.168.1.137"
    entered_ip_text = CenteredText(400, (255,255,255), entered_ip, 30, "Arial")
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

def play_menu(): #ip entering screen
    global menu; menu = play_menu
    global network; global no_map_number

    menu_bg = pygame.image.load('menu_bg.png')
    window.blit(menu_bg, (0,0))

    back_button = Button(50, 50, 50, 50, (255,255,255), (0,0,0), "<", "Arial", 25, main_menu, play_menu)
    back_button.draw(window)
    back_button.click(event)

    server_ip = server_connect()
    global no_map_number
    if server_ip and no_map_number:
        try:
            print("Attempting to connect to server. IP: ", server_ip)
            global network
            network = Network(server_ip, client_colour, scale) #creates a new instance of the network class, also where the connecting stuff is

            global initial_data
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

    bullets = []
    last_fire = []

#Get player tank through network
    try:
        game_map = Map(map_data) #
        player = network.initial_data["tank"]
        # print("PLAYER: ",player)
        # send_data = player
        send_data['players'] = player
        # print(send_data)
        player.colour = client_colour
        
        #player.shrink(screen_height)
        global scale
        scale = int(scale)
        # player.scalee(scale) ####
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
            
            # #  player drawing
            # if 'players' in players:
            #     # print(players)
            #     for player_id, tank in players['players'].items():
            #         tank.draw(window, scale)
            
            keys = pygame.key.get_pressed()

            global fireable
            if keys[pygame.K_f] and not last_fire:
                if player.check_fireable():
                    fire_data = player.fired() #this then needs to be sent to the server to make a new instance of bullet
                    if fire_data:
                        try:
                            # bullet_x, bullet_y, angle, colour = fire_data
                            # new_bullet = Bullet(bullet_x, bullet_y, colour, angle)
                            # bullets.append(new_bullet)
                            # print(f"New bullet created at ({bullet_x}, {bullet_y}) with angle {angle}")
                            # network_reponse = network.send_bullet(fire_data)
                            # if network_reponse and 'bullets' in network_reponse:
                            #     server_bullets = list(network_reponse['bullets'].values())
                            #     for bullet in server_bullets:
                            #         if bullet not in bullets:
                            #             bullets.append(bullet)
                            #             print("Added server bullet", bullet)
                            # send_data = players
                            send_data["bullets"] = fire_data
                            # print(send_data)
                        except ValueError:
                            print("Invalid fire_data format")
                    last_fire = True
            elif not keys[pygame.K_f]:
                last_fire = False
                # send_data = players

            

# Send player data and get updated players

            # print("Send_data = ",send_data)
            # print(player)
            # print("Sending data: ",send_data)
            received_data = network.send(send_data)
            # print(received_data)
            if "players" in received_data:
                received_players = received_data["players"]
                for player_id, tank in received_players.items():
                    if player_id == initial_data["player_id"]:
                        mytank = tank
                    if hasattr(tank, 'draw'):  # Make sure it's a Tank object
                        tank.draw(window, scale)
                    else:
                        print(f"Invalid tank data for player {player_id}: {tank}")

            if "bullets" in received_data:
                received_bullets = received_data["bullets"]
                # print(received_bullets)
                for player_id, bullet in received_bullets.items():
                    if hasattr(bullet, 'draw'):  # Make sure it's a Tank object
                        # bullet.draw(window)
                        bullets.append(bullet)
                    else:
                        print(f"Invalid bullet data for player {player_id}: {bullet}")

            bullets_remove = []
            # print("Bullets: ", bullets)
            # print(len(bullets))
            for bullet in bullets[:]:
                # if hasattr(bullet, 'draw') and bullet.firetime > 0:
                if hasattr(bullet, 'draw'):
                    bullet.draw(window, scale) ##
                    bullet.firetimer(wall_rects, scale)

                    ######
                    # print(bullet.rect)
                    # print(tank.rect)
                    if (bullet.x >= mytank.x and bullet.x <= mytank.x + 1) and (bullet.y >= mytank.y and bullet.y <= mytank.y + 1):
                        # if tank.id != initial_data["player_id"]:
                        # pygame.display.quit()
                        # pygame.quit()
                        died_text = CenteredText(100, (255,0,0), "You got shot", 60, "Arial")
                        died_text.draw(window)
                        pygame.time.delay(3000)
                    # pygame.display.update()
                    
                    if bullet.firetime <= 0:
                        bullets_remove.append(bullet)
                else:
                    bullets_remove.append(bullet)

            for bullet in bullets_remove:
                if bullet in bullets:
                    bullets.remove(bullet)

            send_data['bullets'] = () 
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
 
    enter_username()

    colour_button = ColourButton(screen_width//2 + 50, 300, 550, 80, (0,0,0), "Colour", "Arial", 80, client_colour)
    colour_button.draw(window)
    colour_button.arrow_click()

    back_button = Button(50, 50, 50, 50, (255,255,255), (0,0,0), "<", "Arial", 25, main_menu, customise_menu)
    back_button.draw(window)
    back_button.click(event)

    load_button = Button(screen_width//2 -50 -150, screen_height - 125, 150, 60, load_button_colour, (0,0,0), "Load", "Arial", 35, load_preferences, customise_menu)
    load_button.draw(window)
    load_button.click(event)
    check_loaded()

    save_button = Button(screen_width//2 + 50, screen_height - 125, 150, 60, save_button_colour, (0,0,0), "Save", "Arial", 35, save_preferences, customise_menu)
    save_button.draw(window)
    save_button.click(event)

def enter_username(): 
    global username
    username_text = CenteredText(200, (0,0,0), username, 50, "Arial")
    username_text.draw(window)

    global input_active
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and input_active:
            if username == "Type to enter username":
                username = ""
                username = username + str(event.unicode)
            elif event.key == pygame.K_RETURN:
                input_active = False
                return username
            elif event.key == pygame.K_BACKSPACE:
                username = username[:-1]
            else:
                username = username + str(event.unicode)

def load_preferences():
    global client_colour, load_button_colour, loaded, loaded_username
    if username != "Type to enter username" and loaded == False:
        with open('preferences.txt', 'r') as file:
            records = file.readlines()
            for line in records:
                saved_user = line.split(',')[0].strip()
                if saved_user == username:
                    #load colour
                    saved_colour = line.split(',', 1)[1].strip()
                    client_colour = ast.literal_eval(saved_colour)
                    print("1", client_colour)
                    print(f"Loading Preferences...\nSaved Colour for {username}: {client_colour}")
                    load_button_colour = (0,255,0)
                    loaded_username = username
                    loaded = True

def check_loaded():
    global loaded, load_button_colour
    if loaded_username != username:
        loaded = False
        load_button_colour = (255,255,255)
        
def save_preferences():
    if username != "Type to enter username":
        global save_button_colour, saved
        with open('preferences.txt', 'r') as file:
            records = file.readlines()
        with open('preferences.txt', 'w') as file:
            for line in records:
                saved_user = line.split(',')[0].strip()
                if saved_user == username:
                    file.write(f'{username}, {client_colour}\n')
                    print(f"Updating Preferences for {username}...\nColour: {client_colour}")
                    save_button_colour = (0,255,0)
                    saved = True
                else:
                    file.write(line)
        if not saved:
            print(f"Saving Preferences...\nUsername: {username}, Colour: {client_colour}")
            with open('preferences.txt', 'a') as file:
                file.write(f'{username}, {client_colour}\n')
                save_button_colour = (0,255,0)
                saved = True

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
        self.click_width = height
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
            if pygame.mouse.get_pos()[0] > self.x and pygame.mouse.get_pos()[0] < (self.x + self.click_width) and pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < (self.y + self.height):
                if colour_pos == 0:
                    colour_pos = 5
                else:
                    colour_pos -= 1
            elif pygame.mouse.get_pos()[0] > (self.x  + self.width - self.click_width) and pygame.mouse.get_pos()[0] < (self.x + self.width) and pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < (self.y + self.height):
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