import pygame
import random
from pygame import *
from pygame.locals import *
import os
import random
import sys


# start up pygame
pygame.init()

# sound
musicselect = random.randint(1,3)
# randomly determines music and background
# TODO
# einer von den hintergründen wird seltsam dargestellt; ich ruf dich da noch an
# sachen die noch "TODO" sind habe ich mit dem schlagwort markiert damit es leichter zu finden ist
# bei mir kommt der out of index fehler NUR wenn ich sterbe
if musicselect == 1:
    musicfile = "happy.mp3"
    bground = "bg_happy.png"
if musicselect == 2:
    musicfile = "somber.mp3"
    bground = "bg_somber.png"
if musicselect == 3:
    musicfile = "rock.mp3"
    bground = "cropped_gif.gif"
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(musicfile)
pygame.mixer.music.play(loops=-1)
pygame.event.wait()

# set up screen
scr_size = (width, height) = (852, 610)

FPS = 40
gravity = 0.6

black = (0, 0, 0)
white = (255, 255, 255)
background_col = (235, 235, 235)

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


class Background():
    def __init__(self, speed=-5):
        self.image, self.rect = load_image(bground, -1, -1, -1)
        self.image1, self.rect1 = load_image(bground, -1, -1, -1)
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


#class Ground(Background):
#    def __init__(self, speed):
#       self.image, self.rect = load_image('groundplatform.png', -1, -1, -1)#
#     self.image1, self.rect1 = load_image('groundplatform.png', -1, -1, -1)
#       self.speed = speed
#        self.rect.bottom = 610
#       self.rect1.bottom = 610


class Penguin():
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = load_sprite_sheet('jump5.png', 5, 1, sizex, sizey, -1)
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
            self.index = 4

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
            self.index = (self.index+1)%3
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.frame = (self.frame + 1)
        if self.rect.right < 0:
            self.kill()


class PlatformUp1 (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image('platformUp1_outline.png', 220, 95, -1)
        self.speed = 4
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1 * self.speed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


# TODO: Diese scheiß Platform wird irgendwie verkehrt dargestellt, er WILL die Outline einfach nicht darstellen ._.
class Platformup2 (PlatformUp1):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image('platformUp2_outline.png', 160, 100, -1)
        self.speed = 4
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1 * self.speed, 0]


def introscreen():
    temp_penguin = Penguin(144, 128)
    temp_penguin.isWaiting = True
    gameStart = False

    while not gameStart:
        if pygame.display.get_surface() == None:
            print('Fehler beim Laden auf des Spiels. Versuchen es Sie bitte nochmal')
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        temp_penguin.isJumping = True
                        temp_penguin.isWaiting = False
                        temp_penguin.movement[1] = -1*temp_penguin.jumpSpeed

        temp_penguin.update()

        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            temp_penguin.draw()

            pygame.display.update()

            clock.tick(FPS)
            if temp_penguin.isJumping == False and temp_penguin.isWaiting == False:
                gameStart = True


def gameplay():
    global highscore
    gamespeed = 4
    gameOver = False
    gameQuit = False
    playerPenguin = Penguin(72, 64)
    scrollingBg = Background(-1*gamespeed)
    frame = 0

    snowman = pygame.sprite.Group()
    Snowman.containers = snowman
    platformUp1 = pygame.sprite.Group()
    PlatformUp1.containers = platformUp1
    platformUp2 = pygame.sprite.Group()
    platformUp2.containers = platformUp2

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
                        if event.key ==pygame.K_SPACE:
                            if playerPenguin.rect.bottom == int(0.83*height):
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
                            PlatformUp1(width, int(0.59 * height))
                        elif r == 3:
                            Platformup2(width, int(0.59 * height))
                        elif r == 4:
                            pass

            for s in snowman:
                s.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(playerPenguin, s):
                    playerPenguin.isDead = True

            for p in platformUp1 or platformUp2:
                p.movement[0] = -1 * gamespeed
                if pygame.sprite.collide_mask(playerPenguin, p):
                    playerPenguin.isDead = True

            # if len(snowman) < 5 and random.randrange(0, 200) == 5:
               # Snowman(gamespeed, 64, 64)

           # if len(platformUp1) < 5 and random.randrange(0, 300) == 10 and frame > 100:
             #   PlatformUp1(width, int(0.59*height))

          #  if len(platformUp2) < 5 and random.randrange(0, 300) == 10:
           #     Platformup2(width, random.randrange(height / 5, height / 2))

            scrollingBg.update()
            playerPenguin.update()
            platformUp1.update()
            platformUp2.update()
            snowman.update()

            if pygame.display.get_surface() != None:
                screen.fill(background_col)
                scrollingBg.draw()
                platformUp1.draw(screen)
                platformUp2.draw(screen)
                playerPenguin.draw()
                snowman.draw(screen)

                pygame.display.update()
            clock.tick(FPS)

            if playerPenguin.isDead:
                gameOver = True

                if playerPenguin.isDead:
                    gameOver = True
                    if playerPenguin.score > highscore:
                        highscore = playerPenguin.score

            # increase speed by time
            if frame%800 == 799:
                gamespeed += 1
                # TODO
                # scorecounter += 1
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
                            gameplay()

            if pygame.display.get_surface() != None:
                pygame.display.update()
            clock.tick(FPS)

    pygame.quit()
    quit()

def main():
    isGameQuit = introscreen()
    if not isGameQuit:
        gameplay()

main()






