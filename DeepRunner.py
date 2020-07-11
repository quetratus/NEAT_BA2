# ALS ALLERERSTES TO DO:
# textausgabe im intro-screen:
# eingaben (1 - 4 = hintergründe, 5 = easy, 6 = hard mode)
# UND DRUNTER: Highscore
# UND NOCHMAL DRUNTER: debugging-wertausgaben (frames, indizes...)
# provisorischer code für textausgabe:
# def show_score(x, y):
#     score_value = 0
#     score = font.render("Score : " + str(score_value), True, (255, 255, 255))
#     screen.blit(score, (x, y))
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
# Game Over-Screen zeichnen
# Game Over-Screen programmieren
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

pygame.mixer.init()
pygame.mixer.music.load("titelscreen.mp3")
pygame.mixer.music.play(loops=-1)

# sound
# TODO
# einer von den hintergründen wird seltsam dargestellt; ich ruf dich da noch an
# sachen die noch "TODO" sind habe ich mit dem schlagwort markiert damit es leichter zu finden ist
# bei mir kommt der out of index fehler NUR wenn ich sterbe

# set up screen
scr_size = (width, height) = (852, 610)

FPS = 40
gravity = 0.6

black = (0, 0, 0)
white = (255, 255, 255)
background_col = (230, 230, 235)

screen = pygame.display.set_mode(scr_size)
pygame.display.set_caption("DeepRunner_V2")

highscore = 0

clock = pygame.time.Clock()

pygame.time.set_timer(USEREVENT + 1, random.randrange(1500, 3000))


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


def gameOver_message(gameover_image):
    gameover_rect =gameover_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height * 0.35

    screen.blit(gameover_image, gameover_rect)

#def show_score(score, x, y):
#    score_value = font.render("Score : " + str(score), True, (255, 255, 255))
#    screen.blit(score_value, (x, y))


class Background():
    def __init__(self, speed=-5):
        if bground == "Snow_Night2.png":
            self.image, self.rect = load_image(bground, -1, -1)
            self.image1, self.rect1 = load_image(bground, -1, -1)
        if bground != "Snow_Night2.png":
            self.image, self.rect = load_image(bground, -1, -1, 1)
            self.image1, self.rect1 = load_image(bground, -1, -1, 1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

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


class Penguin():
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = load_sprite_sheet('jump6.png', 6, 1, sizex, sizey, -1)  # 5 = wieviele objekte auf x-achse, 1 = y-achse, -1 = color-key-transparenz
        self.images1, self.rect1 = load_sprite_sheet('slide.png', 2, 1, sizex, sizey, -1)
        self.rect.bottom = int(0.83*height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.image1 = self.images1[0]
        self.index = 0
        self.frame = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isWaiting = False
        self.movement = [0, 0]
        self.jumpSpeed = 12

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self):
        screen.blit(self.image, self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.83*height):
            self.rect.bottom = int(0.83*height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping or self.isWaiting:
            self.index = 0

        elif self.isDucking:
            self.index = (self.index +1) % 2
            self.index = 1

        else:
            if self.frame % 5 == 0:
                self.index = (self.index + 3) % 4

        if self.isDead:
            if not self.isDucking:
                self.index = 5

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width

        else:
            self.image = self.images1[self.index]
            self.rect1.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and self.frame % 7 == 6 and self.isWaiting == False:
            self.score += 1

        self.frame = (self.frame + 1)


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

    def update(self):
        if self.frame % 100 == 0:
            self.index = (self.index + 1) % 7
            self.image = self.images[self.index]
        self.frame = (self.frame + 1)


class Snowman(pygame.sprite.Sprite):
    def __init__(self, speed=4, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('snowman4.png', 4, 1, sizex, sizey, -1)
        self.rect.bottom = int(0.83 * height)
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.index = 0
        self.frame = 0
        self.movement = [-1 * speed, 0]

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


class Bird (pygame.sprite.Sprite):
    def __init__(self, speed=4, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('vogel3.png', 4, 1, sizex, sizey, -1)
        self.bird_height = [height * 0.80, height * 0.90]
        self.rect.bottom = self.bird_height[random.randrange(0, 2)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-1 * speed, 0]
        self.index = 0
        self.frame = 0

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


class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image('fisch3.png', x, y, -1)
        self.fish_height = [height * 0.59, height * 0.75, height * 0.82]
        self.rect.bottom = self.fish_height[random.randrange(0, 3)]
        self.rect.left = width + self.rect.width
        self.speed = 20
        self.movement = [-1 * self.speed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


def introscreen():

    clock.tick(FPS)

    global bground
    global musicfile
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
        musicfile = "somber.mp3"

    titelpinguin = Titelpingi(852, 610)
    titelpinguin.isWaiting = True

    global difficulty
    global mac
    mac = 0
    difficulty = 1
    schwerer = 0

    gameStart = False

    # temp_ground, temp_ground_rect = load_image('groundplatform.png', -1, -1, -1) # -1? das ist doch die position
    # temp_ground_rect.left = width
    # temp_ground_rect.right = height*0.83

    while not gameStart:
        if pygame.display.get_surface() == None:
            print('Fehler beim Laden auf des Spiels. Versuchen es Sie bitte nochmal')
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.mixer.music.stop
                        pygame.mixer.music.load(musicfile)
                        pygame.mixer.music.play(loops=-1)
                        pygame.event.wait()
                        difficulty += schwerer
                        gameStart = True
                        titelpinguin.isWaiting = False
                        # temp_penguin.movement[1] = -1*temp_penguin.jumpSpeed
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
                            musicfile = "somber.mp3"
                    if event.key == pygame.K_e:
                        schwerer = 0
                    if event.key == pygame.K_d:
                        schwerer = 0.2
                    if event.key == pygame.K_n:
                        mac = 0
                    if event.key == pygame.K_s:
                        mac = 1

        titelpinguin.update()

        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            # screen.blit(temp_ground, temp_ground_rect)
            titelpinguin.draw()

            pygame.display.update()


def gameplay():
    global highscore
    gamespeed = 4
    gameOver = False
    walkspeed = 0.5
    gameQuit = False
    playerPenguin = Penguin(72, 64)
    scrollingBg = Background(-1*gamespeed)
    frame = 0

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
                            if walkspeed >= 0.1:
                                walkspeed -= 0.1
                                gamespeed -= 0.1

                        # schneller laufen
                        if event.key == pygame.K_RIGHT:
                            if walkspeed <= 0.9:
                                walkspeed += 0.1
                                gamespeed += 0.1

                        if event.key == pygame.K_SPACE:
                            if playerPenguin.rect.bottom == int(0.83*height):
                                if mac == 1:
                                    effect = pygame.mixer.Sound("jump.wav")
                                    effect.play()
                                playerPenguin.isJumping = True
                                playerPenguin.movement[1] = -1*playerPenguin.jumpSpeed

                        if event.key == pygame.K_DOWN:
                            if not (playerPenguin.isJumping and playerPenguin.isDead):
                                playerPenguin.isDucking = True

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN:
                            playerPenguin.isDucking = False

                    if event.type == USEREVENT + 1:
                        r = random.randrange(0, 5)
                        if 0 <= r <= 1:
                            Snowman(gamespeed, 64, 64)
                        if r == 2:
                            Fish(45, 25)
                        elif r == 3:
                            Bird(gamespeed, 84, 101)
                        elif r == 4:
                            pass

            for obstacle in snowman or flyingBird:
                obstacle.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(playerPenguin, obstacle):
                    playerPenguin.isDead = True

            for value in fish:
                value.movement[0] = -3 * gamespeed
                if pygame.sprite.collide_mask(playerPenguin, value):
                    playerPenguin.isDead = False
                    fish.remove(value)
                    # score += 1


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

             #   if highscore != 0:
             #       highscore.draw()
                playerPenguin.draw()
                snowman.draw(screen)

                pygame.display.update()
            clock.tick(FPS)

            if playerPenguin.isDead:
                gameOver = True
                pygame.mixer.init()
                pygame.mixer.music.stop
                pygame.mixer.music.load("gameover2.mp3")
                pygame.mixer.music.play(loops=1)

                if playerPenguin.isDead:
                    gameOver = True
                    if playerPenguin.score > highscore:
                        highscore = playerPenguin.score

            # increase speed by time
            if frame%800 == 799:
                gamespeed += difficulty
                # TODO: maximales gamespeed hier festlegen!!!!!!!!!!!
                # TODO
                # Müsste man halt nur noch irgendwo anzeigen...
                # if gamespeed = ?:
                    # gamespeed = (?-1)
                    # Maximalgeschwindigkeitsgrenze
                # TODO: ACHTUNG: Der Hintergrund muss sich auch schneller bewegen mit der Zeit,
                # sonst sieht es aus, als würden die Gegner "schliddern" (da sie sich schneller als der Hintergrund
                # bewegen).
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
                                gameQuit = True
                                gameOver = False

                            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                                gameOver = False
                                pygame.mixer.music.stop
                                pygame.mixer.music.load(musicfile)
                                pygame.mixer.music.play(loops=-1)
                                gameplay()
            # highsc.update(high_score)
            if pygame.display.get_surface() != None:
                gameOver_message(gameover_image)
              #  show_score(score, 10, 10)
                pygame.display.update()
            clock.tick(FPS)

    pygame.quit()
    quit()

def main():
    isGameQuit = introscreen()
    if not isGameQuit:
        gameplay()

main()


