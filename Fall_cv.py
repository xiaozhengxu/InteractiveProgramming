import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION
import time
from random import choice
import cv2

player_speed = 1 #a value from 1 to 10
# plank_speed = 5 #a value from 1 to 10


white = (255, 255, 255)
black = (0, 0, 0)
green = (79, 191, 44)
red = (255, 0, 0)
blue = (13, 0, 145)

clock = pygame.time.Clock()

pygame.font.init()
fontsmall = pygame.font.SysFont('UbuntuMono',40)
fontlarge = pygame.font.SysFont('UbuntuMono',100)
fonttiny = pygame.font.SysFont('UbuntuMono', 15)

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
            self.color=pygame.Color(178,238,238) # a teal color 
        elif plank_type == 'spike':
            self.color=pygame.Color('red')
        elif plank_type == 'flip':
            self.color = pygame.Color(0, 255, 0)
        self.rect = pygame.Rect(left, top, width, height)

    def movey(self):
        self.rect.move_ip(0,-1)

class Player(object):
    """ Represents the player in our Fall game """
    def __init__(self, left, top, width, height):
        """ Initialize the player with the specified geometry """
        self.rect = pygame.Rect(left, top, width, height)
        self.speed = (10 - player_speed)/10.0 + 0.3
        self.dx=0
        self.dy=0

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
    def __init__(self):
        self.controller = PyGameCvController(self)  
        self.time_on_flip=0 #time on a flip plank
        self.time=0 #total time since game started
        self.make_plank_time=0 # times that new plank is made
        self.move_plank_time=0 #Times that planks are moved
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

        self.planks = []
        self.PLANK_WIDTH = 100
        self.PLANK_HEIGHT = 20
        first_plank=Plank(480/2, 400,self.PLANK_WIDTH, self.PLANK_HEIGHT, "regular")
        self.planks.append(first_plank)

        self.on_plank=False
        self.beside_plank=False
        self.current_plank = first_plank

        self.life = 500
        self.player = Player(480/2, 400 - self.PLAYER_HEIGHT, self.PLAYER_WIDTH, self.PLAYER_HEIGHT)


    def is_dead(self):
        return self.player.rect.top>=640 or self.player.rect.top<=0 or self.life <= 0

    def make_planks(self):
    #Make new planks from the bottom 
        # if make_new_p:
        plank_types = ["regular", "regular", "regular", "regular", "spike", "flip"]
        new_plank_x=choice(range(20,480-20-self.PLANK_WIDTH))
        new_plank=Plank(new_plank_x, 640, self.PLANK_WIDTH, self.PLANK_HEIGHT, choice(plank_types))
        
        self.planks.append(new_plank)

    def move_planks(self):
        for p in self.planks:
                p.movey()

    def check_on_plank(self):
        for p in self.planks:
            # if self.player.rect.colliderect(p):
            #Check if the player is on the plank (exactly)
            if self.player.rect.right>=p.rect.left and self.player.rect.left<=p.rect.right:
                if self.player.rect.bottom<=p.rect.top+3 and self.player.rect.bottom>=p.rect.top:
                    self.on_plank=True
                    self.current_plank = p
                    self.fall_time=0
            #Check if the player is beside a plank:
                if self.player.rect.top<=p.rect.bottom and self.player.rect.bottom>=p.rect.top: 
                        self.beside_plank=True
                        self.player.dx=0

    def update(self):
        #check if player is on a plank and make it fall if otherwise
        self.score=len(self.planks)

        self.time=pygame.time.get_ticks()
        move_plank=False
        self.on_plank=False
        self.player.dx=0
        self.check_on_plank()
        self.controller.handle_event()
        #Move the player in the x direction
        self.player.movex(self.player.dx)
        #Move planks and player in the y direction
        if self.time-self.move_plank_time>self.move_plank_speed:
            self.move_planks()
            move_plank=True
            self.move_plank_time=self.time

        if not self.on_plank:
            self.time_on_flip=0
            self.fall_time+=1
            if self.life<500:
                self.life+=.1
            #use the following if want gravity:
            self.player.movey(int(self.fall_time/200+1))
                #use the following if want constant fall speed:
                # self.player.movey(1)
        self.controller.handle_event()
        if self.on_plank and move_plank:
            self.player.movey(-1)
            self.fall_time=0
            if self.current_plank.plank_type == 'spike':
                self.life -= 1
            if self.current_plank.plank_type == 'flip':
                self.time_on_flip += 1
                if self.time_on_flip >= 50:
                    self.planks.remove(self.current_plank)
        #make new planks:
        time_interval=choice(range(int(self.move_plank_speed*30+100),int(self.move_plank_speed*100+101)))
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

class PyGameCvController(object):
    def __init__(self,model):
        self.cap = cv2.VideoCapture(0)
        self.model=model
        self.face_cascade = cv2.CascadeClassifier('/home/xiaozheng/Softdes/ToolBox-ComputerVision/haarcascade_frontalface_alt.xml')

    def handle_event(self):
        ret, frame = self.cap.read()

        faces = self.face_cascade.detectMultiScale(frame, scaleFactor=1.2, minSize=(20,20))

        for (x,y,w,h) in faces:
            deltax=225-x
            self.model.player.dx=deltax/100
        # Display the resulting frame
        cv2.imshow('frame',frame)
        cv2.waitKey(1) 

    def closecv(self):
        self.cap.release()
        cv2.destroyAllWindows()


class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model
        self.move_player_time=0

    def handle_event(self):
        """ Look for left and right keypresses to
            modify the x position of the player """
        keys = pygame.key.get_pressed() #Returns a tuple of 0s corresponding to every key on the keyboard 
        if self.model.time-self.move_player_time>model.player.speed:
            if keys[pygame.K_LEFT]:
                self.model.player.dx=-1
            if keys[pygame.K_RIGHT]:
                self.model.player.dx=1
            self.move_player_time=self.model.time

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
        self.screen.fill(pygame.Color('black'))
        # draw walls to screen
        tw=self.model.top_wall.rect
        lw=self.model.left_wall.rect
        rw=self.model.right_wall.rect

        pygame.draw.rect(self.screen, pygame.Color('pink'), tw)
        pygame.draw.rect(self.screen, pygame.Color('pink'), lw)
        pygame.draw.rect(self.screen, pygame.Color('pink'), rw)

        # draw the planks to the screen
        for plank in self.model.planks:
            pygame.draw.rect(self.screen, plank.color, plank.rect)

        # draw the player to the screen
        p = self.model.player.rect
        # pos=(self.model.player.left, self.model.player.top)
        # pygame.draw.circle(self.screen, pygame.Color('red'), pos, self.model.player.radius, width=0)
        pygame.draw.rect(self.screen, pygame.Color('white'),p)
        # displays the life
        myfont = pygame.font.SysFont("monospace", 15) 

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
        self.display_text("1. Solo", fontsmall, black, self.text_start, 270)
        self.display_text("2. Controls", fontsmall, black, self.text_start, 310)
        self.display_text("3. Quit", fontsmall, black, self.text_start, 350)
        clock.tick(15)
        pygame.display.update()
        return '0'

    def instruct(self):
        self.screen.fill(white)
        instructions1 = "Player 1 is green snake and uses WASD to control."
        instructions2 = "Player 2 is blue snake and uses arrow keys to control."
        instructions3 = "Eat the apple to gain points before time runs out!"
        instructions4 = "Press 'Q' to go back."
        self.display_text(instructions1, fontsmall, black, self.text_start, 270)
        self.display_text(instructions2, fontsmall, black, self.text_start, 310)
        self.display_text(instructions3, fontsmall, black, self.text_start, 350)
        self.display_text(instructions4, fontsmall, black, self.text_start, 390)
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
        self.display_text(msg1,fontsmall,black, 10,380)
        self.display_text(msg2,fontsmall,black, 10,480)

        keys = pygame.key.get_pressed()
        pygame.display.update()
        if keys[pygame.K_q]: #single player mode
            return '0'
        elif keys[pygame.K_1]:
            return '1'
        else:
            return '4'

if __name__ == '__main__':
    pygame.init()
    size = (480, 640)
    screen = pygame.display.set_mode(size)
    scores=[]
    model=FallModel()
    view = PygameFallView(model, screen)
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
                model.controller.closecv()
                res='4'
                scores.append(model.score)
        elif res=='2':
            res=view.instruct()
        elif res=='3':
            running=False 
        elif res=='4':
            res=view.score()
            model=FallModel()
            view=PygameFallView(model,screen)



