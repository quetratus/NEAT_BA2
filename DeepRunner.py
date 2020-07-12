# hintergrund ist noch immer langsamer als andere objekte
# sprunggeschwindigkeit muss mit (gamespeed - walkspeed) multipliziert werden => effekt: man kann mit walkspeed weiter springen

# mal IMMER schneemänner spawnen lassen, alle 2000 MS: prüfen, ob so bei gamespeed 18 noch "schaffbar"

# der bug war eine fehlende geschlossene klammer in der zeile drüber

# 40 auf 60 FPS: alle modulos mal 1.5
# Zeilen, in denen Modulo gezogen wird:
# 234, 239, 249, 262, 283, 284, 304, 305, 329, 332, 334, 578
# => alle durchgehen und mit 1,5 malnehemen, DANACH DANEBEN KOMMENTAR SETZEN DASS ANGEGLICHEN!

# ALS ALLERERSTES TO DO:
# textausgabe im intro-screen:
# eingaben (1 - 4 = hintergründe, 5 = easy, 6 = hard mode)
# UND DRUNTER: Highscore
# UND NOCHMAL DRUNTER: debugging-wertausgaben (frames, indizes...)
#
# save-funktion: https://stackoverflow.com/questions/6420311/how-to-make-save-load-game-functions-in-pygame
# textausgabe: https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame

# Sliding: Mehrere Frames/Animation
# Hohe Hindernisse: Neu zeichnen (Vögel)
# Out of index-Fehler (Modulo 4?)
# Sound-Effekte
# Animationsgeschwindigkeit
# Titelscreen zeichnen
# Bonusitems zeichnen
# Bonusitems programmieren
# Score erfassen
# Score anzeigen
# (Schneemänner: Transparenz angleichen (Augen sind transparent))
# 1. im titelscreen highscore anzeigen
# 2. "1 for easy, 2 for hard"
# 3. im game over screen "space to replay, esc to go to title screen"
# 4. im game over screen high score anzeigen

import pygame
from pygame import *
from pygame.locals import *
import os
import random

# start up pygame
pygame.init()

# sound
pygame.mixer.init()
pygame.mixer.music.load("titelscreen.mp3")
pygame.mixer.music.play(loops=-1)

# set up screen size, FPS, colors...
scr_size = (width, height) = (852, 610)
screen = pygame.display.set_mode(scr_size)
pygame.display.set_caption("DeepRunner_V2")

FPS = 40
black = (0, 0, 0)
white = (255, 255, 255)
background_col = (230, 230, 235)

# set gravity and highscore
gravity = 0.6
highscore = 0

# start clock
clock = pygame.time.Clock()

# sets intervall for obstacles

global startgamespeed
startgamespeed = 4
global gamespeed
gamespeed = 4

if gamespeed == 0:
    pygame.time.set_timer(USEREVENT + 1, random.randrange(2000, 3500))
if gamespeed > 0:
    pygame.time.set_timer(USEREVENT + 1, int(random.randrange(2000, 3500) / (gamespeed/startgamespeed)))

    # start gamespeed = 4. if gamespeed is twice as fast, obstacles appear twice as often
    # TODO: Notieren: Wieviele Punkte hat man wenn man ohne schneller laufen zum ersten mal gamespeed = maximum hat?
    # ab dieser punktezahl wird die variable boost, die zuvor auf 1 stand, auf einen wert über 1 gesetzt: tempo erhöht sich weiter
    # => es kommen öfter gegner
    # prüfen: worst case, wenn die zufallszahlen ungünstig fallen: kann man überhaupt noch allem ausweichen?
    # evtl. über frames machen?

# create graphical objects (non-animated and animated respectively)
def load_image(name: object, sizex: object = -1, sizey: object = -1, colorkey: object = None, ) -> object:
    fullname = os.path.join('img', name)
    image = pygame.image.load(fullname)
    image = image.convert()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return (image, image.get_rect())


def load_sprite_sheet(sheetname, nx, ny, scalex=-1, scaley=-1, colorkey=None, ):
    fullname = os.path.join('img', sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0, ny):
        for j in range(0, nx):
            rect = pygame.Rect((j*sizex, i*sizey, sizex, sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet, (0, 0), rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image, (scalex, scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites, sprite_rect

# game over screen
def gameOver_message(gameover_image):
    gameover_rect =gameover_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height * 0.35

    screen.blit(gameover_image, gameover_rect)

# show score
def show_score(score, x, y):
    font = pygame.font.Font('freesansbold.ttf', 20)
    score_value = font.render("Score : " + str(score), True, (255, 255, 255))
    screen.blit(score_value, (x, y))

def show_highscore(highscore, x, y):
    font = pygame.font.Font('freesansbold.ttf', 20)
    highscore_value = font.render("Highscore : " + str(highscore), True, (255, 255, 255))
    screen.blit(highscore_value, (x, y))

# show debug stuff
def show_debug(walkspeed, gamespeed, startgamespeed, x, y):
    font = pygame.font.Font('freesansbold.ttf', 20)
    walkspeed_value = font.render("Walkspeed : " + str(walkspeed), True, (255, 255, 255))
    gamespeed_value = font.render("Gamespeed: " + str(gamespeed), True, (255, 255, 255))
    startgamespeed_value = font.render("Startgamespeed: " + str(startgamespeed), True, (255, 255, 255))
    screen.blit(walkspeed_value, (x, y))
    screen.blit(gamespeed_value, (x, y + 20))
    screen.blit(startgamespeed_value, (x, y + 40))

# show background
class Background():
    def __init__(self, gamespeed):
        if bground == "Snow_Night2.png":
            self.image, self.rect = load_image(bground, -1, -1)
            self.image1, self.rect1 = load_image(bground, -1, -1)
        if bground != "Snow_Night2.png":
            self.image, self.rect = load_image(bground, -1, -1, 1)
            self.image1, self.rect1 = load_image(bground, -1, -1, 1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = gamespeed

    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right

# Player character
class Penguin():
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = load_sprite_sheet('jump5+die1.png', 6, 1, sizex, sizey, -1)
        self.images1, self.rect1 = load_sprite_sheet('slide_die.png', 3, 1, sizex, sizey, -1)

        # positions character
        self.rect.bottom = int(0.83*height)
        self.rect.left = width/15
        # animation
        self.image = self.images[0]
        self.image1 = self.images1[0]
        self.index = 0
        self.frame = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.movement = [0, 0]
        self.jumpSpeed = 12
        # if gamespeed <= 17:
        #     self.jumpSpeed = 12
        # if gamespeed > 17:
        #     self.jumpSpeed = 10
        self.gotFish = False

        # size of penguin
        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    # draw self & show score
    def draw(self):
        screen.blit(self.image, self.rect)
        show_score(self.score, 10, 10)
        if highscore != 0:
            show_highscore(highscore, 10, 40)
        # Debug
        if debug == 1:
            show_debug(walkspeed, gamespeed, startgamespeed, 10, 60)

    # collision detection with ground
    def checkbounds(self):
        if self.rect.bottom > int(0.83*height):
            self.rect.bottom = int(0.83*height)
            self.isJumping = False

    # status checks (collect item, jump...)
    def update(self):
        if self.gotFish:
            self.score+=50
            self.gotFish = False

        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0

        # ducking
        elif self.isDucking:
            self.index = (self.index +1) % 2
            self.index = 1

        # walking animation
        else:
            if self.frame % 5 == 0:
                self.index = (self.index + 1) % 5

        # hit animation
        if self.isDead:
            if not self.isDucking:
                self.index = 5
            if self.isDucking:
                self.index = 2

        # normal animation
        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width

        else:
            self.image = self.images1[self.index]
            self.rect1.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        # score increases every 1/4 second
        if not self.isDead and self.frame % 10 == 0:
            self.score += difficulty

        # advances frame counter every time character is updated (= 40 times per second as per FPS set and clock)
        self.frame = (self.frame + 1)

# Title screen graphics
class Titelpingi(Penguin):
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = load_sprite_sheet('neutitle.png', 7, 1, sizex, sizey, -1)
        self.rect.bottom = height
        self.rect.left = int(1)
        self.image = self.images[0]
        self.index = 0
        self.frame = 0

    def draw(self):
        screen.blit(self.image, self.rect)

# Blinking of Pingi
    def update(self):
        if self.frame % 50 == 0:
            self.index = (self.index + 1) % 7
            self.image = self.images[self.index]
        self.frame = (self.frame + 1)

# Ground enemy
class Snowman(pygame.sprite.Sprite):
    def __init__(self, gamespeed, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('snowman4.png', 4, 1, sizex, sizey, -1)
        self.rect.bottom = int(0.83 * height)
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.index = 0
        self.frame = 0
        self.movement = [-1 * gamespeed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.frame % 10 == 0:
            self.index = (self.index + 1) % 3
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.frame = (self.frame + 1)
        if self.rect.right < 0:
            self.kill()

# Flying enemy
class Bird (pygame.sprite.Sprite):
    def __init__(self, gamespeed, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('vogel3.png', 4, 1, sizex, sizey, -1)
        self.bird_height = [height * 0.80, height * 0.90]
        self.rect.bottom = self.bird_height[random.randrange(0, 2)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-1 * gamespeed, 0]
        self.index = 0
        self.frame = 0

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.frame % 6 == 0:
                # low birds have 1 frame of animation more
                if self.rect.bottom == (height * 0.90):
                    self.index = (self.index + 1) % 4
                if self.rect.bottom != (height * 0.90):
                    self.index = (self.index + 1) % 3
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.frame = (self.frame + 1)
        if self.rect.right < 0:
            self.kill()

# Bonus item
class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image('fisch3.png', x, y, -1)
        self.fish_height = [height * 0.59, height * 0.75, height * 0.82]
        self.rect.bottom = self.fish_height[random.randrange(0, 3)]
        self.rect.left = width + self.rect.width
        self.speed = 18
        self.movement = [-1 * self.speed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


def introscreen():

    # initialize clock
    clock.tick(FPS)
    global bground
    global boost
    boost = 1
    global musicfile
    global debug
    debug = 0

    # get random stage if none is selected
    musicselect = random.randint(1, 4)
    if musicselect == 1:
        bground = "bg_happy.png"
        musicfile = "happy.mp3"
    if musicselect == 2:
        bground = "bg_somber.png"
        musicfile = "somber.mp3"
    if musicselect == 3:
        bground = "cropped_gif.gif"
        musicfile = "rock.mp3"
    if musicselect == 4:
        bground = "Snow_Night2.png"
        musicfile = "nacht2.mp3"

    # screen size
    titelpinguin = Titelpingi(852, 610)

    global difficulty
    global sfx
    sfx = 0
    difficulty = 1
    schwerer = 0

    gameStart = False

    while not gameStart:
        if pygame.display.get_surface() == None:
            print('Fehler beim Laden auf des Spiels. Versuchen Sie es bitte nochmal')
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(musicfile)
                        pygame.mixer.music.play(loops=-1)
                        pygame.event.wait()
                        difficulty += schwerer
                        gameStart = True
                    if event.key == pygame.K_1:
                            bground = "bg_happy.png"
                            musicfile = "happy.mp3"
                    if event.key == pygame.K_2:
                            bground = "bg_somber.png"
                            musicfile = "somber.mp3"
                    if event.key == pygame.K_3:
                            bground = "cropped_gif.gif"
                            musicfile = "rock.mp3"
                    if event.key == pygame.K_4:
                            bground = "Snow_Night2.png"
                            musicfile = "nacht2.mp3"
                    if event.key == pygame.K_e:
                        schwerer = 0
                    if event.key == pygame.K_d:
                        schwerer = 0.5
                    if event.key == pygame.K_n:
                        sfx = 0
                    if event.key == pygame.K_s:
                        sfx = 1
                    if event.key == pygame.K_x:
                        debug = 1
                    if event.key == pygame.K_h:
                        show_highscore()


        titelpinguin.update()

        # if all can be loaded, display it
        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            titelpinguin.draw()
            pygame.display.update()

def gameplay():
    global gamespeed
    gamespeed = 4
    global highscore
    #if debug == 1:
    gameOver = False
    global walkspeed
    walkspeed = 0.5
    gameQuit = False
    playerPenguin = Penguin(72, 64)
    # scrolling of background to the left
    scrollingBg = Background(-1*gamespeed)
    frame = 0

    # define elements on screen
    snowman = pygame.sprite.Group()
    Snowman.containers = snowman
    flyingBird = pygame.sprite.Group()
    Bird.containers = flyingBird
    fish = pygame.sprite.Group()
    Fish.containers = fish
    gameover_image, gameover_rect = load_image('gameover1.png', -1, -1, -1)

    while not gameQuit:
        while not gameOver:
            if pygame.display.get_surface() == None:
                print("Fehler aufgetreten")
                gameQuit = True
                gameOver = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = True

                    if event.type == pygame.KEYDOWN:
                        # langsamer laufen
                        if event.key == pygame.K_LEFT:
                            if walkspeed >= 0.5:
                                walkspeed -= 0.5
                                gamespeed -= 0.5

                        # schneller laufen
                        if event.key == pygame.K_RIGHT:
                            if walkspeed <= 3.5:
                                walkspeed += 0.5
                                gamespeed += 0.5
                                if gamespeed > (12 * difficulty):
                                    gamespeed = (12 * difficulty)

                        if event.key == pygame.K_ESCAPE:
                            gameQuit = True
                            gameOver = True

                        if event.key == pygame.K_SPACE:
                            if playerPenguin.rect.bottom == int(0.83*height):
                                if sfx == 1:
                                    effect = pygame.mixer.Sound("jump.wav")
                                    effect.play()

                                global jumpSpeed
                                # if gamespeed < 7:
                                #     playerPenguin.jumpSpeed = 25
                                # if 7 >= gamespeed < 16:
                                #     playerPenguin.jumpSpeed = 12
                                # if 16 <= gamespeed <= 17:
                                #     playerPenguin.jumpSpeed = 11
                                # if gamespeed > 17:
                                #     playerPenguin.jumpSpeed = 10
                                playerPenguin.isJumping = True
                                playerPenguin.movement[1] = -1*playerPenguin.jumpSpeed

                        if event.key == pygame.K_DOWN:
                            if not (playerPenguin.isJumping and playerPenguin.isDead):
                                playerPenguin.isDucking = True

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN:
                            playerPenguin.isDucking = False

                    # event trigger
                    if event.type == USEREVENT + 1:
                        r = random.randrange(0, 5)
                        if 0 <= r <= 1:
                            Snowman(gamespeed, 64, 64)
                        if r == 2:
                            Fish(45, 25)
                        if r == 3:
                            Bird(gamespeed, 78, 94)
                        if r == 4:
                            pass
            # loop for each snowman
            for s in snowman:
                s.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(playerPenguin, s):
                    playerPenguin.isDead = True

            # loop for each bird
            for b in flyingBird:
                b.movement[0] = -1 * gamespeed
                if pygame.sprite.collide_mask(playerPenguin, b):
                    playerPenguin.isDead = True

            # loop for each fish
            for f in fish:
                f.movement[0] = -3 * gamespeed
                if pygame.sprite.collide_mask(playerPenguin, f):
                    fish.remove(f)
                    playerPenguin.gotFish = True

            scrollingBg.update()
            playerPenguin.update()
            fish.update()
            flyingBird.update()
            snowman.update()


            if pygame.display.get_surface() != None:
                screen.fill(background_col)
                scrollingBg.draw()
                fish.draw(screen)
                flyingBird.draw(screen)
                playerPenguin.draw()
                snowman.draw(screen)

                pygame.display.update()
            clock.tick(FPS)

            if playerPenguin.isDead:
                gameOver = True
                pygame.mixer.init()
                pygame.mixer.music.stop()
                pygame.mixer.music.load("gameover2.mp3")
                pygame.mixer.music.play(loops=1)

                if playerPenguin.isDead:
                    gameOver = True
                    if playerPenguin.score > highscore:
                        highscore = playerPenguin.score

            # increase speed by time
            if frame%800 == 799:
                gamespeed += difficulty
                if gamespeed > (12 * difficulty):
                    gamespeed = (12 * difficulty)
                # TODO: Die Häufigkeit, mit der Hindernisse abgerufen werden, muss sich erhöhen, weil: Wenn die
                # Gegner sich superschnell bewegen, kommen sie gefühlt viel seltener, da länger garkeine im Bild
                # sind.
            frame = (frame + 1)

        if gameQuit:
            break

        while gameOver:
            if pygame.display.get_surface() == None:
                print("Fehler aufgetreten")
                gameQuit = True
                gameOver = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = False

                    else:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pygame.mixer.music.stop()
                                gameQuit = False
                                gameOver = False
                                playerPenguin.isDead = False
                                introscreen()

                            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                                gameOver = False
                                pygame.mixer.music.stop()
                                pygame.mixer.music.load(musicfile)
                                pygame.mixer.music.play(loops=-1)
                                gameplay()
                                
            if pygame.display.get_surface() != None:
                gameOver_message(gameover_image)
                pygame.display.update()
            clock.tick(FPS)

    pygame.quit()
    quit()

def main():
    isGameQuit = introscreen()
    if not isGameQuit:
        gameplay()

main()


