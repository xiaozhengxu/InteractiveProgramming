import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN
import time
from random import choice
import numpy 

player_speed = 5 #a value from 1 to 10
# plank_speed = 5 #a value from 1 to 10


white = (255, 255, 255)
black = (0, 0, 0)
green = (79, 191, 44)
red = (255, 0, 0)
blue = (13, 0, 145)

clock = pygame.time.Clock()

pygame.font.init()
fontsmall = pygame.font.SysFont('UbuntuMono',20)
fontlarge = pygame.font.SysFont('UbuntuMono',100)
fontmedium = pygame.font.SysFont('UbuntuMono',40)
fonttiny = pygame.font.SysFont('UbuntuMono', 15)

fast_plank = pygame.image.load('fast_plank.png')
flip_plank = pygame.image.load('flip_plank.png')
heart_plank = pygame.image.load('heart_plank.png')
spike_plank = pygame.image.load('spike_plank.png')
slow_plank = pygame.image.load('slow_plank.png')
regular_plank = pygame.image.load('regular_plank.png')
player_cupcake =pygame.image.load('cupcake.png')

player_cupcake=pygame.transform.scale(player_cupcake,(140,180))
regular_plank=pygame.transform.scale(regular_plank,(140,28))
fast_plank=pygame.transform.scale(fast_plank,(140,28))
slow_plank=pygame.transform.scale(slow_plank,(140,28))
flip_plank=pygame.transform.scale(flip_plank,(140,28))
heart_plank=pygame.transform.scale(heart_plank,(140,28))
spike_plank=pygame.transform.scale(spike_plank,(140,32))

class Plank(object):
    """ Represents a plank in our Fall game """
    def __init__(self, left, top, width, height, plank_type):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.plank_type = plank_type
        # self.color = choice(["red", "green", "orange", "blue", "purple"])
        if plank_type == "regular":    
            self.image=regular_plank 
        elif plank_type == 'spike':
            self.image=spike_plank
        elif plank_type == 'flip':
            self.image=flip_plank
        elif plank_type == 'heart':
            self.image=heart_plank
        elif plank_type == 'fast':
            self.image=fast_plank
        elif plank_type == 'slow':
            self.image=slow_plank

        self.rect = pygame.Rect(left, top, width, height)

    def movey(self):
        self.rect.move_ip(0,-1)

class Player(object):
    """ Represents the player in our Fall game """
    def __init__(self, left, top, width, height):
        """ Initialize the player with the specified geometry """
        self.rect = pygame.Rect(left, top, width, height)
        self.speed = (10 - player_speed)/3.0 + 0.3
        self.dx=0
        self.dy=0
        self.image=player_cupcake

    def movex(self, dx):
        '''Moves player side ways by an integer value of dx!
        Checks for the walls and stops player from moving outside the walls'''
        if self.rect.left<=20:
            if self.dx>0:
                self.rect.move_ip(self.dx,0)
        elif self.rect.left>=480-self.rect.width-20:
            if self.dx<0:
                self.rect.move_ip(self.dx,0)
        else:
            self.rect.move_ip(self.dx,0)

    def movey(self,dy):
        self.rect.move_ip(0,dy)

class FallModel(object):
    """ Stores the game state for our Fall game """
    def __init__(self,start_time):
        self.controller = PyGameKeyboardController(self)
        self.time_on_flip=0 #time on a flip plank
        self.start_time=start_time
        self.time=start_time
        self.make_plank_time=0 # times that new plank is made
        self.move_plank_time=0 #Times that planks are moved
        self.move_player_time=0
        self.fall_time=0 #Time that a player falls down from a plank 
        # self.move_plank_speed=(10 - plank_speed)/2+1  # The smaller this is, the faster the planks move up
        self.score=0
        self.move_plank_speed=4 # The smaller this is, the faster the planks move up

        self.WALL_THICKNESS=20
        self.top_wall=Wall(0,0,480,self.WALL_THICKNESS)
        self.left_wall=Wall(0,0,self.WALL_THICKNESS,640)
        self.right_wall=Wall(480-self.WALL_THICKNESS,0,self.WALL_THICKNESS,640)

        self.PLAYER_WIDTH = 30
        self.PLAYER_HEIGHT = 30
        self.plank_types = ['fast','slow',"spike", "flip",'heart',"regular", "regular", "regular", "regular"]
        self.planks = []
        self.PLANK_WIDTH = 140
        self.PLANK_HEIGHT = 28
        first_plank=Plank(480/2, 400,self.PLANK_WIDTH, self.PLANK_HEIGHT, "regular")
        self.planks.append(first_plank)

        self.on_plank=False
        self.beside_plank=False
        self.current_plank = first_plank

        self.life = 500
        self.player = Player(480/2+30, 400 - self.PLAYER_HEIGHT-15, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)


    def is_dead(self):
        return self.player.rect.top>=640 or self.player.rect.top<=0 or self.life <= 0

    def make_planks(self):
    #Make new planks from the bottom 
        new_plank_x=choice(range(20,480-20-self.PLANK_WIDTH))
        new_plank=Plank(new_plank_x, 640, self.PLANK_WIDTH, self.PLANK_HEIGHT, choice(self.plank_types))
        
        self.planks.append(new_plank)

    def move_planks(self):
        '''move planks up and removes the ones that are outside the screen'''
        for p in self.planks:
            p.movey()
            if p.rect.bottom<0:
                self.planks.remove(p)

    def check_on_plank(self):
        for p in self.planks:
            # if self.player.rect.colliderect(p):
            #Check if the player is on the plank (exactly)
            if self.player.rect.right>=p.rect.left and self.player.rect.left<=p.rect.right:
                if self.player.rect.bottom<p.rect.top+3 and self.player.rect.bottom>=p.rect.top-15:
                    self.on_plank=True
                    self.current_plank = p
                    self.fall_time=0
            #Check if the player is beside a plank:
                if self.player.rect.top<=p.rect.bottom and self.player.rect.bottom>=p.rect.top+3: 
                    self.beside_plank=True
                    self.player.dx=0

    def update(self):
        #check if player is on a plank and make it fall if otherwise
        self.score=int(self.time/500)

        #Continuously increase game speed
        if self.score<200:
            self.move_plank_speed=4-self.score*4.0/200
        elif self.score>=200:
            self.move_plank_speed=0

        self.time=pygame.time.get_ticks()-self.start_time
        move_plank=False
        self.on_plank=False

        #Move the player in the x direction
        self.player.dx=0
        self.controller.handle_event()
        self.check_on_plank() # check if the player is on a plank and whether the player is beside a plank, changes the boolean self.on_plank and self.beside_plank
        
        if self.time-self.move_player_time>self.player.speed:
            self.player.movex(int(self.player.dx))
            self.move_player_time=self.time

        #Move planks and player in the y direction if time interval is reached
        if self.time-self.move_plank_time>self.move_plank_speed:
            self.move_planks()
            move_plank=True
            self.move_plank_time=self.time

        #Make the player fall, recover life, increment/reset times
        if not self.on_plank:
            self.time_on_flip=0
            self.fall_time+=1
            #uncomment following if want to recover life:
            # if self.life<500:
            #     self.life+=.3
            #use the following if want accelerated falling(gravity):
            self.player.movey(int(self.fall_time/200+1))
            #use the following if want constant fall speed:
            # self.player.movey(1)

        #Make the player move up with plank, carry out plank effects
        if self.on_plank and move_plank:
            self.player.movey(-1)
            self.fall_time=0
            if self.current_plank.plank_type == 'spike':
                self.life -= 0.8
            if self.current_plank.plank_type == 'flip':
                self.time_on_flip += 1
                if self.time_on_flip >= 50:
                    self.planks.remove(self.current_plank)
            if self.current_plank.plank_type == 'heart':
                self.life+=1
            if self.current_plank.plank_type == 'fast':
                if self.player.speed<=0:
                    self.player.speed=0
                else:
                    self.player.speed-=0.01
            if self.current_plank.plank_type == 'slow':
                if self.player.speed<3:
                    self.player.speed+=0.02
        #make new planks:
        # time_interval=choice(range(int(self.move_plank_speed*35+100),int(self.move_plank_speed*55+101)))
        # time_interval=(self.move_plank_speed*150)+100
        time_interval=400
        if self.time-self.make_plank_time>=time_interval:
            self.make_planks()
            self.make_plank_time=self.time

class Wall(object):
    """ Represents the walls in our game """
    def __init__(self, left, top, width, height):
        """ Initializes the wall with the specified width """
        # self.left=left
        # self.top=top
        # self.width = width
        # self.height=height
        self.rect = pygame.Rect(left, top, width, height)


class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model

    def handle_event(self):
        """ Look for left and right keypresses to
            modify the x position of the player """
        keys = pygame.key.get_pressed() #Returns a tuple of 0s corresponding to every key on the keyboard 
        if keys[pygame.K_LEFT]:
            self.model.player.dx=-1
        if keys[pygame.K_RIGHT]:
            self.model.player.dx=1
            
class PyGameMouseController(object):
    def __init__(self, model):
        self.model = model

    def handle_event(self):
        """ Look for mouse movements and respond appropriately """
        self.model.player.dx = numpy.sign(pygame.mouse.get_pos()[0]-240.0)


class PygameFallView(object):
    """ Visualizes aFall game in a pygame window """
    def __init__(self, model, screen):
        """ Initialize the view with the specified model
            and screen. """
        self.model = model
        self.screen = screen
        self.text_start = 140

    def draw(self):
        """ Draw the game state to the screen """
        self.screen.fill(pygame.Color('white'))
        # draw walls to screen
        tw=self.model.top_wall.rect
        lw=self.model.left_wall.rect
        rw=self.model.right_wall.rect

        pygame.draw.rect(self.screen, pygame.Color('pink'), tw)
        pygame.draw.rect(self.screen, pygame.Color('pink'), lw)
        pygame.draw.rect(self.screen, pygame.Color('pink'), rw)

        # draw the planks to the screen
        for plank in self.model.planks:
            self.screen.blit(plank.image, plank.rect)

        # draw the player to the screen
        p = self.model.player
        self.screen.blit(p.image,p.rect)

        # displays the life
        myfont = pygame.font.SysFont("monospace", 40) 

        life_display=int(self.model.life/100)

        label = myfont.render("Life " + str(life_display), 1, (255,255,0)) 
        screen.blit(label, (100, 100))

        score = myfont.render("Score {}".format(self.model.score), 1, (255,255,0)) 
        screen.blit(score, (100, 150))

        pygame.display.update() 

    def display_text(self, msg, font, color, x, y):
        """Writes text on screen"""
        text = font.render(msg, True, color)
        self.screen.blit(text, [x, y])

    def start_menu(self):
        """Shows starting menu"""

        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]: #single player mode
            return '1'
        if keys[pygame.K_2]: #multi player mode
            return '2'
        if keys[pygame.K_3]: #double player mode
            return '3'
        self.screen.fill(white)
        self.display_text("FALL", fontlarge, pygame.Color(178,238,238), 100, 120)
        self.display_text("1. Solo", fontmedium, black, self.text_start, 270)
        self.display_text("2. Controls", fontmedium, black, self.text_start, 310)
        self.display_text("3. Quit", fontmedium, black, self.text_start, 350)
        clock.tick(15)
        pygame.display.update()
        return '0'

    def instruct(self):
        self.screen.fill(white)
        instructions1 = "Move the cupcake left to right to stay on "
        instructions2='planks and survive.'
        instructions3 = "Keyboard control: left and right keys"
        instructions4 = "Mouse control: place mouse in left and right"
        instructions5= "halves of the screen to move cupcake"
        instructions6 = "Webcam control: move face from left to right facing"
        instructions7="the camera to move cupcake"
        instructions8 = "Press 'Q' to go back."

        self.display_text(instructions1, fontsmall, black, 30, 250)
        self.display_text(instructions2, fontsmall, black, 30, 270)
        self.display_text(instructions3, fonttiny, black, 30, 300)
        self.display_text(instructions4, fonttiny, black, 30, 330)
        self.display_text(instructions5, fonttiny, black, 30, 350)
        self.display_text(instructions6, fonttiny, black, 30, 380)
        self.display_text(instructions7, fonttiny, black, 30, 400)
        self.display_text(instructions8, fonttiny, black, 30, 430)

        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]: #single player mode
            return '0'
        else:
            return '2'
    def score(self):
        self.screen.fill(white)
        score_text='Score:{}'.format(scores[-1])
        msg1='Press q to go back'
        msg2='Press 1 to restart'
        self.display_text(score_text,fontlarge,black, 10,230)
        self.display_text(msg1,fontmedium,black, 10,340)
        self.display_text(msg2,fontmedium,black, 10,380)
        pygame.display.update()
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_q] or pygame.mouse.get_pressed()[0]==True: #single player mode
            return '0'
        elif keys[pygame.K_1]:
            return '1'
        else:
            return '4'

if __name__ == '__main__':
    pygame.init()
    size = (480, 640)
    screen = pygame.display.set_mode(size)
    model=FallModel(pygame.time.get_ticks())
    view=PygameFallView(model,screen)
    scores=[]
    #controller = PyGameMouseController(model)
    running = True
    res='0'

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        if res=='0':
            res=view.start_menu()
        elif res=='1':
            #Play the game
            view.draw() 
            model.update()
            if model.is_dead():
                res='4'
                scores.append(model.score)
        elif res=='2':
            res=view.instruct()
        elif res=='3':
            running=False 
        elif res=='4':
            res=view.score()
            model=FallModel(pygame.time.get_ticks())
            view=PygameFallView(model,screen)
            



