'''This file runs the Fall Game using the pygame module
@author: Xiaozheng Xu, Rebecca Getto
March 2016  
'''
import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN
import time
from random import choice
import numpy 

#define fonts and colors 
white = (255, 255, 255)
black = (0, 0, 0)
pygame.font.init()
fontsmall = pygame.font.SysFont('UbuntuMono',20)
fontlarge = pygame.font.SysFont('UbuntuMono',100)
fontmedium = pygame.font.SysFont('UbuntuMono',40)
fonttiny = pygame.font.SysFont('UbuntuMono', 15)

#set up display in order to convert images
size = (480, 640)
screen = pygame.display.set_mode(size)
plank_size=(120,24)
#load images and scale them
fast_plank = pygame.image.load('fast_plank.png').convert_alpha() #converting the image to the same pixel type as the screen- makes the game much faster!
flip_plank = pygame.image.load('flip_plank.png').convert_alpha() #conver_alpha makes empty pixels transparent 
heart_plank = pygame.image.load('heart_plank.png').convert_alpha()
spike_plank = pygame.image.load('spike_plank.png').convert_alpha()
slow_plank = pygame.image.load('slow_plank.png').convert_alpha()
regular_plank = pygame.image.load('regular_plank.png').convert_alpha()
player_cupcake =pygame.image.load('cupcake.png').convert_alpha()
wall_image=pygame.image.load('wall.png').convert_alpha()
legend_image=pygame.image.load('legend.png').convert_alpha()

player_cupcake=pygame.transform.scale(player_cupcake,(40,40))
regular_plank=pygame.transform.scale(regular_plank,plank_size)
fast_plank=pygame.transform.scale(fast_plank,plank_size)
slow_plank=pygame.transform.scale(slow_plank,plank_size)
flip_plank=pygame.transform.scale(flip_plank,plank_size)
heart_plank=pygame.transform.scale(heart_plank,plank_size)
spike_plank=pygame.transform.scale(spike_plank,(plank_size[0],plank_size[1]+4))
legend_image=pygame.transform.scale(legend_image,(300,400))


class Plank(object):
    """ Represents a plank in our Fall game """
    def __init__(self, left, top, width, height, plank_type):
        self.rect = pygame.Rect(left, top, width, height)
        self.plank_type = plank_type
        if plank_type == "regular":    
            self.image=regular_plank 
        elif plank_type == 'spike':
            self.image=spike_plank
            self.rect.height+=4
        elif plank_type == 'flip':
            self.image=flip_plank
        elif plank_type == 'heart':
            self.image=heart_plank
        elif plank_type == 'fast':
            self.image=fast_plank
        elif plank_type == 'slow':
            self.image=slow_plank

    def movey(self):
        self.rect.move_ip(0,-1)

class Player(object):
    """ Represents the player in our Fall game """
    def __init__(self, left, top, width, height):
        """ Initialize the player with a rectangle, its moving speed and instantaneous velocity dx and dy """
        self.rect = pygame.Rect(left, top, width, height)
        self.speed = 2 # this value changes when the player lands on fast and slow planks in the model
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
        '''Moves the player up and down by integer value dy'''
        self.rect.move_ip(0,dy)

class FallModel(object):
    """ Stores the game state for our Fall game """
    def __init__(self,start_time):
        '''Initialize controller, time variables, player, planks list with first plank.

        Takes in start_time which is the time the model is initialized as variable.

        Defines types of plank and their probablity of ocurring'''
        self.controller = PyGameKeyboardController(self)
        self.time_on_flip=0 #time on a flip plank
        self.start_time=start_time 
        self.time=0
        self.make_plank_time=0 # times that new plank is made
        self.move_plank_time=0 #Times that planks are moved
        self.move_player_time=0
        self.fall_time=0 #Time that a player falls down from a plank 
        self.score=0
        self.move_plank_speed=4 # The smaller this is, the faster the planks move up. 4 is arbituary and pretty slow

        self.PLAYER_WIDTH = 40
        self.PLAYER_HEIGHT = 40
        self.plank_types = ['fast','slow',"spike", "flip",'heart',"regular", "regular", "regular", "regular"]
        self.planks = []
        self.PLANK_WIDTH = plank_size[0]
        self.PLANK_HEIGHT = plank_size[1]
        first_plank=Plank(480/2, 500,self.PLANK_WIDTH, self.PLANK_HEIGHT, "regular")
        self.planks.append(first_plank)

        self.on_plank=False
        self.beside_plank=False
        self.current_plank = first_plank

        self.life = 300
        self.player = Player(480/2+30, 500 - self.PLAYER_HEIGHT, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)
        self.color=(255,230,255)

    def is_dead(self):
        '''Return True if the player is shuffed to the top, fall through the bottom, or run out of life'''
        return self.player.rect.top>=640 or self.player.rect.top<=0 or self.life <= 0

    def make_planks(self):
        '''Make new planks in a random x position from the bottom'''
        new_plank_x=choice(range(20,480-20-self.PLANK_WIDTH))
        new_plank=Plank(new_plank_x, 640, self.PLANK_WIDTH, self.PLANK_HEIGHT, choice(self.plank_types))
        self.planks.append(new_plank)

    def move_planks(self):
        '''move planks up and removes the ones that are outside the screen from planks list'''
        for p in self.planks:
            p.movey()
            if p.rect.bottom<0:
                self.planks.remove(p)

    def check_on_plank(self):
        '''Use a costum collision logic to check if the player is on a plank or beside a plank.
            If player is on a plank: set self.current_plank to the plank the player is on.
            If player is beside a plank, set the player's velocity to 0 so the player doesn't collide into the plank.'''
        for p in self.planks:
            #Check if the player is on the plank (exactly)
            if self.player.rect.right>=p.rect.left and self.player.rect.left<=p.rect.right:
                if p.plank_type=='spike': 
                    plank_depth=7
                else:
                    plank_depth=0

                if self.player.rect.bottom<p.rect.top+plank_depth+3 and self.player.rect.bottom>=p.rect.top+plank_depth:
                    self.on_plank=True
                    self.current_plank = p
                    self.fall_time=0
            #Check if the player is beside a plank:
                if self.player.rect.top<=p.rect.bottom and self.player.rect.bottom>=p.rect.top+plank_depth+3: 
                    self.beside_plank=True
                    self.player.dx=0

    def update(self):
        '''Updates the model through each time step, including what planks are on the screen,
        the positions of planks, player, life, score and player speed.
        '''
        #check if player is on a plank and make it fall if otherwise
        self.score=int(self.time/500)
        self.time=pygame.time.get_ticks()-self.start_time

        #Continuously increase game speed starting from move_plank_speed=4
        if self.score<200:
            self.move_plank_speed=4-self.score*4.0/200
            # self.color=(255-self.time/500,255,255) #teal color changing
        elif self.score>=200:
            self.move_plank_speed=0

        #continuously change color
        if self.color[1]>=100:
            self.color=(255,230-self.time/400,255) #pink color changing 
        else:
            self.color=(139,0,139)
        # self.move_plank_speed=0

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
                if self.player.speed<=0.8:
                    self.player.speed=0.8
                else:
                    self.player.speed-=0.01
            if self.current_plank.plank_type == 'slow':
                if self.player.speed<2.5:
                    self.player.speed+=0.01
        #make new planks:
        #random interval:
        # time_interval=choice(range(int(self.move_plank_speed*35+100),int(self.move_plank_speed*55+101)))
        #set interval depending on move_plank_speed:
        time_interval=(self.move_plank_speed*100)+100
        #constant interval: (planks will become more sparse as the move_plank_speed increase)
        # time_interval=400
        if self.time-self.make_plank_time>=time_interval:
            self.make_planks()
            self.make_plank_time=self.time

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
        
        self.screen.fill(self.model.color) #fills the screen with a color from model
        self.screen.blit(wall_image,(0,0)) #displays the wall

        # draw the planks to the screen
        for plank in self.model.planks:
            self.screen.blit(plank.image, plank.rect)

        # draw the player to the screen
        p = self.model.player
        self.screen.blit(p.image,p.rect)

        # displays the life
        myfont = pygame.font.SysFont("monospace", 40) 
        life_display=int(self.model.life/100)
        label = myfont.render("Life " + str(life_display), 1, (186,85,211)) 
        screen.blit(label, (50, 50))
        #display the score 
        score = myfont.render("Score {}".format(self.model.score), 1, (176,196,222)) 
        screen.blit(score, (250, 50))
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
        if keys[pygame.K_4]: #double player mode
            return '4'
        self.screen.fill((255,220,255))
        # self.display_text("FALL", fontlarge, (178,238,238), 100, 120) #teal
        self.display_text("FALL", fontlarge, (176,196,222), 100, 120) #light steal (blue)
        # self.display_text("FALL", fontlarge, (189,183,107), 100, 120) #goldish color
        self.display_text("1. Solo", fontmedium, (186,85,211), self.text_start, 270)
        self.display_text("2. Controls", fontmedium, (186,85,211), self.text_start, 310)
        self.display_text("3. Legend", fontmedium, (186,85,211), self.text_start, 350)
        self.display_text("4. Quit", fontmedium, (186,85,211), self.text_start, 390)
        pygame.display.update()
        return '0'

    def controls(self):
        '''Shows the controls'''
        self.screen.fill((255,220,255))
        instructions1 = "Move the cupcake left to right to stay on "
        instructions2='planks and survive.'
        instructions3 = "Keyboard control: left and right keys"
        instructions4 = "Mouse control: place mouse in left and right"
        instructions5= "halves of the screen to move cupcake"
        instructions6 = "Webcam control(To be implemented): move face/color from"
        instructions7="left to right facing the camera to move cupcake"
        instructions8 = "Press 'Q' to go back."

        self.display_text(instructions1, fontsmall, (186,85,211), 30, 250)
        self.display_text(instructions2, fontsmall, (186,85,211), 30, 270)
        self.display_text(instructions3, fonttiny, (186,85,211), 30, 300)
        self.display_text(instructions4, fonttiny, (186,85,211), 30, 330)
        self.display_text(instructions5, fonttiny, (186,85,211), 30, 350)
        self.display_text(instructions6, fonttiny, (186,85,211), 30, 380)
        self.display_text(instructions7, fonttiny, (186,85,211), 30, 400)
        self.display_text(instructions8, fonttiny, (186,85,211), 30, 430)

        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]: #single player mode
            return '0'
        else:
            return '2'

    def legend(self):
        self.screen.fill((255,220,255))
        self.screen.blit(legend_image,(85,45))
        instructions8 = "Press 'Q' to go back."
        self.display_text(instructions8, fontsmall,(186,85,211), 100, 500)
        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]: #single player mode
            return '0'
        else:
            return '3'

    def score(self):
        '''Show the score page and allow the player to go back to menu or restart the game'''
        self.screen.fill((255,220,255))
        score_text='Score:{}'.format(scores[-1])
        msg1='Press q to go back'
        msg2='Press 1 to restart'
        self.display_text(score_text,fontlarge,(186,85,211), 10,230) #purple color
        self.display_text(msg1,fontmedium,(186,85,211), 10,340)
        self.display_text(msg2,fontmedium,(186,85,211), 10,380)
        pygame.display.update()
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_q] or pygame.mouse.get_pressed()[0]==True: #single player mode
            return '0'
        elif keys[pygame.K_1]:
            return '1'
        else:
            return '5'

if __name__ == '__main__':
    pygame.init()
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
                res='5'
                scores.append(model.score)
        elif res=='2':
            res=view.controls()
        elif res=='3':
            res=view.legend()
        elif res=='4':
            running=False 
        elif res=='5':
            res=view.score()
            model=FallModel(pygame.time.get_ticks())
            view=PygameFallView(model,screen)
            



