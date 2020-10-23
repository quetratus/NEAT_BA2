import pygame
from pygame.locals import *
import os
import random
import neat
import math
import sys

# start up pygame
pygame.init()
clock = pygame.time.Clock()


# set up screen size, FPS, colors...
WINDOW_SIZE = (width, height) = (852, 604)
screen = pygame.display.set_mode(WINDOW_SIZE)
display = pygame.Surface(WINDOW_SIZE)
pygame.display.set_caption("DeepRunner_V2")

font = pygame.font.Font('freesansbold.ttf', 20)

GROUND_LEVEL = int(WINDOW_SIZE[1]*0.83)
ground_rect = pygame.Rect(0, GROUND_LEVEL, WINDOW_SIZE[0], WINDOW_SIZE[1])

# (Draw lines between the game character and obstacles to see what the AI sees)
DRAW_LINES = False

FPS = 40

# set gravity and highscore
gravity = 0.6
highscore = 0

startgamespeed = 4
gamespeed = 4

generation = 0

# sets intervall for obstacles
if gamespeed == 0:
    pygame.time.set_timer(USEREVENT + 1, random.randrange(1500, 3000))
if gamespeed > 0:
    pygame.time.set_timer(USEREVENT + 1, int(random.randrange(1500, 3000) / (gamespeed / startgamespeed)))


def load_image(name, sizex=-1, sizey=-1, colorkey=None, ):
    fullname = os.path.join('img', name)
    image = pygame.image.load(fullname)
    image = image.convert()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return image, image.get_rect()


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
    gameover_rect = gameover_image.get_rect()
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
    alive_text = font.render(f'Number alive: {len(penguins)}', True, (255, 255, 255))
    generation_text = font.render(f'Generation: {generation}', True, (255, 255, 255))

    screen.blit(walkspeed_value, (x, y))
    screen.blit(gamespeed_value, (x, y + 20))
    screen.blit(startgamespeed_value, (x, y + 40))
    screen.blit(alive_text, (x, y + 50))
    screen.blit(generation_text, (x, y + 60))


# show background
class Background():
    def __init__(self, gamespeed):
        self.image, self.rect = load_image('bg_happy.png', -1, -1, 1)
        self.image1, self.rect1 = load_image('bg_happy.png', -1, -1, 1)
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
class Penguin:
    def __init__(self, x, y, sizex, sizey):
        self.images, self.rect = load_sprite_sheet('jump6.png', 6, 1, sizex, sizey, -1)
        self.images1, self.rect1 = load_sprite_sheet('slide_die.png', 3, 1, sizex, sizey, -1)
        self.sizex = -1
        self.sizey = -1
        # character positions
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, sizex, sizey)
        #self.rect.bottom = GROUND_LEVEL
        #self.rect.left = width/15
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
        # self.gotFish = False
        # setting the closest snowman to the leftmost snowman
        self.last_closest_pipe = snowmen[0]

        # size of penguin
        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    # draw self & show score
    def draw(self):
        screen.blit(self.image, self.rect)

    # collision detection with ground
    def checkbounds(self):
        if self.rect.bottom > GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.isJumping = False

    # status checks (collect item, jump...)
    def update(self):
        self.x, self.y = self.rect.x, self.rect.y  # Updating position atributes
#        self.movement()

        #  if self.gotFish:
       #     self.score += 50
       #     self.gotFish = False
        if self.isJumping:
            self.movement = self.movement[1] + gravity

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

        #self.rect = self.rect.move(self.movement)
        self.checkbounds()

        # advances frame counter every time character is updated (= 40 times per second as per FPS set and clock)
        self.frame = (self.frame + 1)


# Ground enemy
class Snowman:
    def __init__(self, x, y, sizex, sizey, gamespeed):
        self.images, self.rect = load_sprite_sheet('snowman4.png', 4, 1, sizex, sizey, -1)
        self.sizex = -1
        self.sizey = -1
        self.x = x
        self.y = y
        self.rect.bottom = GROUND_LEVEL
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.index = 0
        self.frame = 0
        self.gamespeed = 4
        self.movement = [-1 * gamespeed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.frame % 10 == 0:
            self.index = (self.index + 1) % 3
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.x -= self.gamespeed  # Moves snowman to the left
        self.rect.x, self.rect.y = self.x, self.y  # Update position atributes
        self.frame = (self.frame + 1)
        if self.rect.right < 0:
            self.kill()


# Flying enemy
#class Bird (pygame.sprite.Sprite):
#    def __init__(self, gamespeed, sizex=-1, sizey=-1):
#        pygame.sprite.Sprite.__init__(self, self.containers)
#        self.images, self.rect = load_sprite_sheet('vogel3.png', 4, 1, sizex, sizey, -1)
#        self.bird_height = [height * 0.80, height * 0.90]
#       self.rect.bottom = self.bird_height[random.randrange(0, 2)]
#        self.rect.left = width + self.rect.width
#        self.image = self.images[0]
#        self.movement = [-1 * gamespeed, 0]
#        self.index = 0
#        self.frame = 0

#    def draw(self):
#        screen.blit(self.image, self.rect)

#    def update(self):
#        if self.frame % 6 == 0:
#            # high birds have 1 frame of animation less for the old version
#            if self.rect.bottom == (height * 0.90):
#                self.index = (self.index + 1) % 4
#            if self.rect.bottom != (height * 0.90):
#                self.index = (self.index + 1) % 3
#        self.image = self.images[self.index]
#        self.rect = self.rect.move(self.movement)
#        self.frame = (self.frame + 1)
#        if self.rect.right < 0:
#            self.kill()

# Bonus item
#class Fish(pygame.sprite.Sprite):
#    def __init__(self, x, y):
#        pygame.sprite.Sprite.__init__(self, self.containers)
#        self.image, self.rect = load_image('fisch3.png', x, y, -1)
#        self.fish_height = [height * 0.59, height * 0.75, height * 0.82]
#        self.rect.bottom = self.fish_height[random.randrange(0, 3)]
#        self.rect.left = width + self.rect.width
#        self.speed = 18
#        self.movement = [-1 * self.speed, 0]
#
#    def draw(self):
#        screen.blit(self.image, self.rect)
#
#    def update(self):
#        self.rect = self.rect.move(self.movement)
#        if self.rect.right < 0:
#            self.kill()

def get_distance(first_pos, second_pos):
    # Distance formula
    dx = first_pos[0] - second_pos[0]
    dy = first_pos[1] - second_pos[1]
    return math.sqrt(dx**2 + dy**2)


def remove_penguin(index):
    # 'Kills' the penguin and its corresponding genome and nn
    penguins.pop(index)
    ge.pop(index)
    nets.pop(index)


def draw():
    pygame.draw.line(display, (255, 255, 255), (0, GROUND_LEVEL), (WINDOW_SIZE[0], GROUND_LEVEL), 3)

    for penguin in penguins:
        penguin.draw()
        if DRAW_LINES:
            pygame.draw.line(
                display,
                (50, 200, 75),
                (penguin.rect.right, penguin.rect.centery),
                penguin.last_closest_pipe.rect.midtop,
                2
            )
    for s in snowmen:
        s.draw()

    screen.blit(display, (0, 0))

    pygame.display.update()


def main(genomes, config):
    global gamespeed, walkspeed
    gamespeed = 4
    walkspeed = 0.5

    global snowmen, penguins, nets, ge, generation
    generation += 1

    score = 0
    # scrolling of background to the left
    scrollingBg = Background(-1*gamespeed)
    frame = 0

    # define elements on screen
   # snowman = pygame.sprite.Group()
  #  Snowman.containers = snowman
   # flyingBird = pygame.sprite.Group()
 #   Bird.containers = flyingBird
 #   fish = pygame.sprite.Group()
 #   Fish.containers = fish

    #create lists for the genomes, the pengions, the neural network
    penguins = []
    nets = []
    ge = []
    snowmen = [Snowman(WINDOW_SIZE[0] + 668, GROUND_LEVEL, 64, 64, gamespeed)]

  #  for _, genome in genomes:
    for genome_id, genome in genomes:
    # set up neural network
    #start with fitness level of 0
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        #keep track on fitness
        penguins.append(Penguin(40, GROUND_LEVEL, 40, 64))
        ge.append(genome)

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            # quit the game if no penguin left
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Break if all the penguins die
        if len(penguins) <= 0:
            break

        # add new snowman
        for event in pygame.event.get():
            # event trigger
            if event.type == USEREVENT + 1:
                r = random.randrange(0, 2)
                if 0 <= r <= 1:
                    snowmen.append(Snowman(WINDOW_SIZE[0] + 668, GROUND_LEVEL, 64, 64, gamespeed))                # if r == 2:
                #     Fish(45, 25)
                # if r == 3:
                #    Bird(gamespeed, 75, 90)
                # if r == 4:
                #   pass

        for s in snowmen:
            s.update()
            s.movement[0] = -1 * gamespeed
            if s.x < -100:
                snowmen.remove(s)
            for i, penguin in enumerate(penguins):
                if pygame.sprite.collide_mask(penguin, s):
                    ge[i].fitness -= 3
                    remove_penguin(i)

        for i, penguin in enumerate(penguins):
                penguin.update()
                # Check if the penguin passed a snowman
                # Getting the closest snowman by finding the leftmost snowman that is to the right of the penguin
                penguin.closest_pipe = [s for s in snowmen if s.rect.x > penguin.x - penguin.sizex][0]
                # Checking if the penguin passed a snowman by comparing it to the closest snowman in the last frame and seeing if there is a change
                if penguin.closest_pipe != penguin.last_closest_pipe:
                    ge[i].fitness += 1
                penguin.last_closest_pipe = penguin.closest_pipe

                # Giving all penguins a little fitness for staying alive
                ge[i].fitness += 0.05

                output = nets[i].activate(
                    (
                        penguin.y,
                        get_distance((penguin.x, penguin.y), penguin.closest_pipe.rect.midtop)
                        #penguin.x, abs(penguin.x - snowmen[obj_ind].x)
                    )
                )

                if output[0] > 0.5:
                    penguin.isJumping = True
                 #   penguin.movement[1] = -1 * penguin.jumpSpeed

        # send penguin location, top snowman location and determine from network whether to jump or not
          #  output = nets[penguins.index(penguin)].activate((penguin, abs(penguin-s)))

            # loop for each bird
          #  for b in flyingBird:
          #      b.movement[0] = -1 * gamespeed
           #     if pygame.sprite.collide_mask(playerPenguin, b):
            #        playerPenguin.isDead = True

            # loop for each fish
          #  for f in fish:
           #     f.movement[0] = -3 * gamespeed
            #    if pygame.sprite.collide_mask(playerPenguin, f):
             #       fish.remove(f)
              #      playerPenguin.gotFish = True

        scrollingBg.update()

        draw()

            # increase speed by time
        if frame % 800 == 799:
            gamespeed = + 1
        frame = (frame + 1)


def run(config_file):
    #include subheadings from the config file and set the path for configuration file
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )

    #set up population based on the config file
    p = neat.Population(config)

    #set output for the statistics
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)


#call the fitness function and config file 50times
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)