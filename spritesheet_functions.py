"""
This module is used to pull individual sprites from sprite sheets.
"""
import pygame

"""
Global constants
"""


# Colors
BLACK    = (   0,   0,   0) 
WHITE    = ( 255, 255, 255) 
BLUE     = (   0,   0, 255)
 
# Screen dimensions
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
 
class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """
 
    def __init__(self, file_name):
        """ Constructor. Pass in the file name of the sprite sheet. """
 
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert()
 
 
    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """
 
        # Create a new blank image
        image = pygame.Surface([width, height]).convert()
 
        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
 
        # Assuming black works as the transparent color
        image.set_colorkey(BLACK)
 
        # Return the image
        return image

PLAYER = (90, 0, 140, 110)
REGULAR_PLANK = (0, 480, 300, 540-480)
SPIKE_PLANK = (0, 140, 300, 70)
HEART_PLANK = (0, 570, 300, 70)
FLIP_PLANK = (0, 400, 300, 70)
FAST_PLANK = (0, 230, 300, 70)
SLOW_PLANK = (0, 320, 300, 70)

class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """
 
    def __init__(self, sprite_sheet_data):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this
            code. """
        super(Platform, self).__init__()
 
        sprite_sheet = SpriteSheet("sprite_sheet.png")
        # Grab the image for this platform
        self.image = sprite_sheet.get_image(sprite_sheet_data[0],
                                            sprite_sheet_data[1],
                                            sprite_sheet_data[2],
                                            sprite_sheet_data[3])
 
        self.rect = self.image.get_rect()

sprite_planks = pygame.sprite.Group()
sprite_planks.add(Platform(PLAYER))
sprite_planks.add(Platform(REGULAR_PLANK))
sprite_planks.add(Platform(SPIKE_PLANK))
sprite_planks.add(Platform(HEART_PLANK))
sprite_planks.add(Platform(FLIP_PLANK))
sprite_planks.add(Platform(FAST_PLANK))
sprite_planks.add(Platform(SLOW_PLANK))
all_images = pygame.image.load('sprite_sheet.png')