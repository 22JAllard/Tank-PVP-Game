import pygame
tile_size = 50

class Map():
    def __init__(self, data):
        self.tile_list= []

        wood_block_image = pygame.image.load('0.png')
        dirt_path_image = pygame.image.load('1.png')
        row = 0
        for row in data:
            column = 0
            for tile in row:
                if tile == 0:
                    img = pygame.transform.scale(wood_block_image, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = column * tile_size
                    img_rect.y = row * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 1:
                    img = pygame.transform.scale(dirt_path_image, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = column * tile_size
                    img_rect.y = row * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                column += 1
            row += 1