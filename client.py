#import libraries
import pygame
from network import Network
import pickle
from os import path
from tank import Tank
from bullet import Bullet
import ast

#initialise pygame
pygame.init()

#set run to true as client is running, and network to none as the network is not currently connected to server
run = True
network = None

#set up the pygame window to styart at (0,0) (top left), and make it full screen
window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

#store info about client screen size
display = pygame.display.Info()
screen_width = display.current_w
screen_height = display.current_h
scale = screen_height//50

#define variables
clock = pygame.time.Clock() #set up the clock
mapnumber = None 
input_active = True  
no_map_number = True 
entered_ip = ""
colour_pos = 0
tank_colours = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,127,11), (255,21,123)] #define an array with all the colours of tanks available
client_colour = tank_colours[colour_pos] #selects the client colour based on the position of the position in the array
wall_rects = [] 
fireable = False
map_unloaded = True
bullets = []
send_data = {}
last_fire = False
username = "Type to enter username" #will later be set to an empty string to allow the user to type to it
saved = False
loaded = False
save_button_colour = (255,255,255)
load_button_colour = (255,255,255)
loaded_username = None

#load images for tanks
zerotank = pygame.image.load('0tank.png')
onetank = pygame.image.load('1tank.png')
twotank = pygame.image.load('2tank.png')
threetank = pygame.image.load('3tank.png')
fourtank = pygame.image.load('4tank.png')
fivetank = pygame.image.load('5tank.png')

class Map:
    def __init__(self, data):
        self.tile_list = [] #create an empty array with all the tiles in
        self.tile_size = screen_height //50 #calculate the size of each tile to fit the 50x50 tile grids on the screen

        try: #tries to load the two images for the map
            self.wood_block_image = pygame.image.load('0.png')
            self.dirt_path_image = pygame.image.load('1.png')
        except pygame.error as error: #prints error message if the images could not be loaded correctly.
            print(f"Error loading images: {error}")
            return

        global wall_rects 
        for row_index, row in enumerate(data): #for each row
            for col_index, char in enumerate(row): #for each character in the row
                x = col_index * self.tile_size #changes the x (left) of the tile to be drawn
                y = row_index * self.tile_size #changes the y (top corner) of the tile to be drawn

                if char == '0': #if the character is a 0
                    img = pygame.transform.scale(self.wood_block_image, (self.tile_size, self.tile_size)) #edits the size of the tile image
                    img_rect = img.get_rect() #creates the rectangle around the image
                    img_rect.x = x #sets the x and y (below) to the current x and y values
                    img_rect.y = y 
                    self.tile_list.append((img, img_rect)) #adds the tile to the tile list
                    wall_rects.append(img_rect) #adds the tile to the list of solid tiles (ie. causes collisions)

                elif char == '1':
                    img = pygame.transform.scale(self.dirt_path_image, (self.tile_size, self.tile_size)) #edits the size of the tile image
                    img_rect = img.get_rect() #creates the rectangle around the image
                    img_rect.x = x #sets the x and y (below) to the current x and y values 
                    img_rect.y = y 
                    self.tile_list.append((img, img_rect)) #adds the tile to the tile list


    def draw(self, window): 
        for tile, rect in self.tile_list: #for each tile in the tile_list
            window.blit(tile, rect) #draw it to the window, based on the tile's rect.

def server_connect():

    global input_active
    server_connect_text = CenteredText(350, (255,255,255), "Enter server IP", 50, "Arial") #create an instance of the CenteredText class, with y value 350, colour white, text as "Enter server IP", size 50 and font "Arial"
    server_connect_text.draw(window) #draw the instance to window

    global entered_ip
    entered_ip_text = CenteredText(400, (255,255,255), entered_ip, 30, "Arial") #create another instance of the CenteredText class which will have y value 400, colour white, text as the contents of entered_ip, size 30 and font "Arial"
    entered_ip_text.draw(window) #draw the instance to the window

    pygame.display.update() #update the pygame window

    for event in pygame.event.get(): #checks for an event 
        if event.type == pygame.KEYDOWN and input_active: #if there is an event, check if the event is a key being pressed and the input_active value is still true
            if event.key == pygame.K_RETURN: #if the key pressed if Return/Enter
                input_active = False #set input_active to false, and prevent any more keys being pressed
                return entered_ip
            elif event.key == pygame.K_BACKSPACE: 
                entered_ip = entered_ip[:-1] #if the key pressed is backspace, delete the last character in the entered_ip string
            else:
                entered_ip = entered_ip + str(event.unicode) #if the key pressed is not an enter or a backspace, add the button press to the entered_ip string

def load_level():
    map_file = f'map{mapnumber}.txt' #sets the map_file to the map number given (ie 'map1.txt')
    with open(map_file, 'r') as file: #open the file in read mode, to prevent any accidental changes to the file
        map_data = [list(line.strip()) for line in file] #store the map data, by reading through and stripping lines of enters
    print(f"Loaded map data") 
    return map_data

def play_menu(): #ip entering screen
    global menu; menu = play_menu
    global network; global no_map_number

    menu_bg = pygame.image.load('menu_bg.png')
    window.blit(menu_bg, (0,0)) #draw the menu image to the screen

    back_button = Button(50, 50, 50, 50, (255,255,255), (0,0,0), "<", "Arial", 25, main_menu, play_menu) #create an instance of the button class with x value 50, y 50, width 50. height 50, button colour white, text colour black, text "<" (as in an arrow), font "Arial", size 25, the function to be called if clicked as main_menu and the screen it is to be drawn on as play_menu
    back_button.draw(window) #draw instance of button
    back_button.click(event) #check for the button being clicked

    server_ip = server_connect() #call the clients server_connect function and store the returned value in server_ip
    global no_map_number
    if server_ip and no_map_number: #checks that there is a value in server and no_map_number
        try:
            print("Attempting to connect to server. IP: ", server_ip) #print the server ip the client is trying to connect to
            global network
            network = Network(server_ip, client_colour, scale) #creates a new instance of the network class

            global initial_data
            initial_data = network.initial_data #stores the initial_data as the contents of the networks intial data
            if initial_data: #if the contents of the initial_data is not empty
                global mapnumber 
                mapnumber = initial_data["map_number"] #searching the recieved data dictionary from the server for the value with "map_number"
                print("Selected map", mapnumber) 
                no_map_number = False  
                
                global map_unloaded
                if map_unloaded: 
                    map_unloaded = False
                    global world_data
                    world_data = load_level() #stores the returned data from the load_level function in world_data
                
                if world_data: #if world_data is not empty
                    game_map = Map(world_data) #creates an instance of the map class, sending it the world_data, and stores any returned data in game_map
                    game()  #calls the game function 
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
    game_map = Map(map_data) #creates a new instance of the map class, sending it the map data and storing returned data in game_map

    if not network or not network.connected: #if there is no network, or the network is not connected, return and set the active menu to main_menu
        print("No network connected")
        menu = main_menu
        return
    
    if 'players' not in globals(): 
        players={}

    bullets = []
    last_fire = [] #create bullets and last_fire as empty arrays

    #Get player tank through network
    try: 
        game_map = Map(map_data) #creates a new instance of the map class, sending it the map data and storing returned data in game_map
        player = network.initial_data["tank"] #store the value in the tank section of the intial data from network in players
        send_data['players'] = player #put the player in the data to be sent to the server, in the 'players' section
        player.colour = client_colour #set the players colour to the client colour
        
        global scale
        scale = int(scale) #makes the scale an integer
        running = True
        while network.connected and running: #while the network is connected and client running
            
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:
                    running = False
                    network.disconnect()
                    
            map_grid = game_map.tile_list #store the tile list in the map_grid variable
            player.move(map_grid, scale, wall_rects) #call the move function in the tank code

            # Clear screen and draw map
            window.fill((0, 0, 0)) #create a black backdrop on the pygame window
            game_map.draw(window) #draw the map data onto the window
            
            keys = pygame.key.get_pressed() #store the key if a key is pressed

            global fireable
            if keys[pygame.K_f] and not last_fire: #if the key pressed is f, and not last fire
                if player.check_fireable(): #check if the player can fire
                    fire_data = player.fired() #store the return from the fired function in fire_data
                    if fire_data: #if there is anything in fire_data
                        try:
                            send_data["bullets"] = fire_data #store the fire data in the send_data dictionary 'bullets' section
                        except ValueError:
                            print("Invalid fire_data format")
                    last_fire = True
            elif not keys[pygame.K_f]: #if the key pressed is not f, put last_fire to False
                last_fire = False

            received_data = network.send(send_data) #store the returned data from sending the send_data to server
            if "players" in received_data: #if 'players' are in the received_data
                received_players = received_data["players"] #store the values in the received data players section in recieved_players
                for player_id, tank in received_players.items(): #for player id and tank in the received_players
                    if player_id == initial_data["player_id"]: #if the players id of the player in received_players is matching to the clients personal player id, received in the initial data
                        mytank = tank #store that tanks data in mytank
                    if hasattr(tank, 'draw'):  #checks it is a tank object that can be drawn
                        tank.draw(window, scale) #if it is, draw it to the window, with the correct scale
                    else:
                        print(f"Invalid tank data for player {player_id}: {tank}")

            if "bullets" in received_data: #if 'bullets' are in the received_data
                received_bullets = received_data["bullets"] #store the values in the 'bullets' section of the received_data in received_bullets
                for player_id, bullet in received_bullets.items(): #for each player id and bullet in recieved bullets
                    if hasattr(bullet, 'draw'):  #checks it is a bullet object that can be drawn
                        bullets.append(bullet) #if it is, add it to the bullets list
                    else:
                        print(f"Invalid bullet data for player {player_id}: {bullet}")

            bullets_remove = []
            for bullet in bullets[:]:#checks for each bullet in a copy of the bullets list
                if hasattr(bullet, 'draw'): #if it is an instance of the bullet class and has the attribute draw
                    bullet.draw(window, scale) #draw the bullet to the screen
                    bullet.firetimer(wall_rects, scale) #call the bullet firetimer function, sending the wall_rects and also scale

                    if (bullet.x >= mytank.x and bullet.x <= mytank.x + 1) and (bullet.y >= mytank.y and bullet.y <= mytank.y + 1): #checks if the bullet collides with the clients own tank

                        died_text = CenteredText(100, (255,0,0), "You got shot", 60, "Arial") #create an instance of the CenteredText function, with y value 100, text colour red, text "You got shot", size 60 and font "Arial"
                        died_text.draw(window) #draw the instance to screen
                    
                    if bullet.firetime <= 0: #if the bullets firetime value is less than or equal to zero
                        bullets_remove.append(bullet) #add the bullet to the bullets_remove list
                else:
                    bullets_remove.append(bullet) #if it cannot be drawn, add it to the remove list anyway

            for bullet in bullets_remove: #searches through each bullet in the bullets remove list, and removes it
                if bullet in bullets:
                    bullets.remove(bullet)

            send_data['bullets'] = ()  #send an empty tuple in the bullets section
            pygame.display.update() #update the pygame window
            
    except Exception as e:
        print(f"Error in game: {e}")
    finally:  #once the try loop is exited
        if network: 
            network.disconnect() #disconnect from the network
        menu = main_menu #and set the menu back to main_menu
    
def customise_menu():
    global menu; menu = customise_menu
    customise_bg = pygame.image.load('warehouse.png') #load the background image
    customise_bg = pygame.transform.scale(customise_bg, (screen_width, screen_height)) #change the image size to the size of the client screen
    window.blit(customise_bg, (0,0)) #draw the image to screen

    customise_text = CenteredText(30, (0,0,0), "Customise", 100, "Arial") #create a new instance of the CenteredText class with y value 30, colour black, text "Customise", size 100 and font "Arial"
    customise_text.draw(window) #draw the text to screen
 
    enter_username() #call the enter username function

    colour_button = ColourButton(screen_width//2 + 50, 300, 550, 80, (0,0,0), "Colour", "Arial", 80, client_colour) #creates a new instance of the ColourButton class with x value half the screen width + 50, y value 300, width 550, height 80, colour black, text colour "Colour", font "Arial", size 80, and background colour the clients colour
    colour_button.draw(window) #draw the button to screen
    colour_button.arrow_click() #check for a click of the buttom

    back_button = Button(50, 50, 50, 50, (255,255,255), (0,0,0), "<", "Arial", 25, main_menu, customise_menu) #new instance of the Button class with x value 50, y value 50, width 50, height 50, background colour white, text colour black, text "<", font "Arial", size 25, calls main_menu and is drawn on the customise menu
    back_button.draw(window) #draw button
    back_button.click(event) #check for the button being clicked

    load_button = Button(screen_width//2 -50 -150, screen_height - 125, 150, 60, load_button_colour, (0,0,0), "Load", "Arial", 35, load_preferences, customise_menu) #new instance of Button class, with x value half screen width - 200, y value 125 less than screen height, width 150, height 60, colour of the contents of load_button_colour (either white or green), text colour black, text "Load", font "Arial", calls load_preferences function and on the customise menu
    load_button.draw(window) #draw button
    load_button.click(event) #check for click
    check_loaded() #check if preferences have been loaded to change colour of the button

    save_button = Button(screen_width//2 + 50, screen_height - 125, 150, 60, save_button_colour, (0,0,0), "Save", "Arial", 35, save_preferences, customise_menu) #new instance of Button, x value 50 plus the screen width, y 125 less than the screen height, width 150, height 60, colour of the contents of save_button_colour (white/green), text black, text "Save", font "Arial", calls save_preferences, on customise menu
    save_button.draw(window) #draw button
    save_button.click(event) #check for button click

def enter_username(): 
    global username
    username_text = CenteredText(200, (0,0,0), username, 50, "Arial") #create an instance of the CenteredText class, y value 200, colour black, text is contents of username, size 50 and font "Arial"
    username_text.draw(window) #draw username text

    global input_active
    for event in pygame.event.get(): #check for an event
        if event.type == pygame.KEYDOWN and input_active: #check if the event is a key press and if the input is active
            if username == "Type to enter username": #if the username is unchanged, clear it when a key is pressed
                username = ""
                username = username + str(event.unicode) #add the pressed key to the username string
            elif event.key == pygame.K_RETURN: #if enter is pressed, disable input active
                input_active = False
                return username
            elif event.key == pygame.K_BACKSPACE: #delete the most recent character if backspace is pressed
                username = username[:-1]
            else:
                username = username + str(event.unicode) #if none of the above apply, just add the pressed key to the username string

def load_preferences():
    global client_colour, load_button_colour, loaded, loaded_username
    if username != "Type to enter username" and loaded == False: #check if the username is changed, and preferences are not loaded
        with open('preferences.txt', 'r') as file: #read the preferences file to avoid accidental edits
            records = file.readlines() #store the contents in a records variable
            for line in records: #search each line in the records
                saved_user = line.split(',')[0].strip() #just check the first section before the ,
                if saved_user == username: #if the saved username matches the username the user has entered
                    saved_colour = line.split(',', 1)[1].strip() #get the saved colour, which is after the ,
                    client_colour = ast.literal_eval(saved_colour) #convert saved_colour string to client_colour
                    print(f"Loading Preferences...\nSaved Colour for {username}: {client_colour}")
                    load_button_colour = (0,255,0) #change the colour of the load button
                    loaded_username = username
                    loaded = True

def check_loaded():
    global loaded, load_button_colour
    if loaded_username != username: #if the username that existed when preferences were loaded doesnt match the current username, turn the load button white again
        loaded = False
        load_button_colour = (255,255,255)
        
def save_preferences():
    if username != "Type to enter username": #make sure the user has entered a new username
        global save_button_colour, saved
        with open('preferences.txt', 'r') as file: #open the file in read mode as it doesn't need to be changed
            records = file.readlines() #read each line and store it in records
        with open('preferences.txt', 'w') as file: #open the file in write mode
            for line in records: #search each line in the record
                saved_user = line.split(',')[0].strip() #check the username of each line (ie before the ,)
                if saved_user == username: #if the saved user matches the username which data is being saved for
                    file.write(f'{username}, {client_colour}\n') #overwrite the current saved data for that username
                    print(f"Updating Preferences for {username}...\nColour: {client_colour}")
                    save_button_colour = (0,255,0) #change colour of the save button
                    saved = True
                else:
                    file.write(line) #if there is not a record with that username, add one
        if not saved: #if its not saved but the button is clicked
            print(f"Saving Preferences...\nUsername: {username}, Colour: {client_colour}")
            with open('preferences.txt', 'a') as file: #open the file in append mode 
                file.write(f'{username}, {client_colour}\n') #save the username and colour to file
                save_button_colour = (0,255,0)
                saved = True

class ColourButton():
    def __init__ (self, x, y, width, height, text_colour, text, font, size, selected_colour): #define the values which are needed for a new instance of the class
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.click_width = height
        self.button_colour = selected_colour
        self.text_colour = text_colour
        self.text = text
        self.size = size
        self.font = pygame.font.SysFont(font, self.size) #change the size and font to an actual pygame font

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) #create the rectangle for the button based on the 
        self.label = self.font.render(self.text, True, self.text_colour) #create the label of text based on the font and text (and it's colour)

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

    title_text = CenteredText(30, (255,255,255), "Tank PVP Game", 100, "Arial")
    title_text.draw(window)

    global buttons
    buttons = [
        CenteredButton(150, 400, 100, (255,255,255),(0,0,0), "Play", "Arial", 80, play_menu, main_menu),
        CenteredButton(screen_height - 150, 400, 100, (255,255,255), (0,0,0), "Customise", "Arial", 80, customise_menu, main_menu),
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