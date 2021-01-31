from setup import *
import os
import neat
import random
import math


# create graphical objects (non-animated and animated respectively)
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

    sizex = sheet_rect.width / nx
    sizey = sheet_rect.height / ny

    for i in range(0, ny):
        for j in range(0, nx):
            rect = pygame.Rect((j * sizex, i * sizey, sizex, sizey))
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


# show score
def show_score(score, penguins):
    font = pygame.font.Font('freesansbold.ttf', 18)
    score_value = font.render("Score : " + str(score), True, WHITE)
    screen.blit(score_value, (10, 10))
    score_value = font.render("Gens: " + str(GENERATION - 1), True, WHITE)
    screen.blit(score_value, (10, 30))
    score_value = font.render("Alive: " + str(len(penguins)), True,WHITE)
    screen.blit(score_value, (10, 50))


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
class Background:
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
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = load_sprite_sheet('jump6.png', 6, 1, sizex, sizey, -1)
        self.images1, self.rect1 = load_sprite_sheet('slide_die.png', 3, 1, sizex, sizey, -1)

        # positions character
        self.rect.bottom = GROUND_LEVEL
        self.rect.left = X_POSITION
        # animation
        self.image = self.images[0]
        self.image1 = self.images1[0]
        self.index = 0
        self.frame = 0
        self.isJumping = False
        self.movement = [0, 0]
        self.jumpSpeed = 10.5
        # size of penguin
        # self.stand_pos_width = self.rect.width
        # self.duck_pos_width = self.rect1.width

    # draw self & show score
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    # collision detection with ground
    def checkbounds(self):
        if self.rect.bottom > GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.isJumping = False

    # status checks (collect item, jump...)
    def walk(self):
        # walking animation
        if self.frame % 5 == 0:
            self.index = (self.index + 1) % 5
        self.image = self.images[self.index]
        # self.rect.width = self.stand_pos_width
        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        # advances frame counter every time character is updated (= 40 times per second as per FPS set and clock)
        self.frame = (self.frame + 1)

    def jump(self):
        self.movement[1] = -1 * self.jumpSpeed
        self.isJumping = True

    def update(self):
        if self.isJumping:
            self.index = 0
            self.movement[1] = self.movement[1] + GRAVITY

        # elf.rect = self.rect.move(self.movement)
        self.checkbounds()

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


# Ground enemy
class Snowman(pygame.sprite.Sprite):
    def __init__(self, gamespeed, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self)
        self.images, self.rect = load_sprite_sheet('snowman4.png', 4, 1, sizex, sizey, -1)
        self.rect.bottom = GROUND_LEVEL
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.index = 0
        self.frame = 0
        self.movement = [-1 * gamespeed, 0]
        self.passed = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def walk(self):
        if self.frame % 10 == 0:
            self.index = (self.index + 1) % 3
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.frame = (self.frame + 1)
        if self.rect.right < 0:
            self.kill()

    def collide(self, penguin):
        # Checking for collision using get mask function
        player_mask = penguin.get_mask()
        obj_mask = pygame.mask.from_surface(self.image)
        obj_offset = (self.rect.x - penguin.rect.x, self.rect.y - round(penguin.rect.y))
        collision_point = player_mask.overlap(obj_mask, obj_offset)
        if collision_point:
            return True
        return False


def draw_window(penguins, snowmen, obj_ind, score):
    for snowman in snowmen:
        snowman.draw(screen)
        snowman.update()
    for penguin in penguins:
        penguin.draw(screen)
        penguin.update()
        if DRAW_LINES:
            try:
                pygame.draw.line(screen, GREEN, (penguin.rect.right, penguin.rect.centery),
                                 snowmen[obj_ind].rect.midtop,
                                 2)
            finally:
                pass
        # draw bird
    show_score(score, penguins)

    pygame.display.update()


def main(genomes, config):
    global GENERATION
    GENERATION += 1
    gamespeed = 4

    penguins = []
    nets = []
    ge = []

    score = 0

    # scrolling of background to the left
    scrollingBg = Background(-1 * gamespeed)

    # List of Genomes
    # we need the underscore to loop through the indexes of the genomes
    for _, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        penguin = (Penguin(72, 64))
        penguins.append(penguin)
        genome.fitness = 0  # start with fitness level of 0
        ge.append(genome)

    # Creating list of obstacle class objects
    snowmen = [Snowman(gamespeed, 64, 64)]

    run = True
    while run:
        clock.tick(FPS)
        # frame = 0
        # frame += 1
        # score increases every 1/4 second
        # if frame % 10 == 0:
        # score += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # snowman index is 0
        obj_ind = 0
        if len(penguins) > 0:
            # to check which snowman; if penguin passes the first snowman then change index to 1
            if len(snowmen) > 1 and penguins[0].rect.x > snowmen[0].rect.x + snowmen[0].rect.x:
                obj_ind = 1
        else:
            break

        for x, penguin in enumerate(penguins):  # give each penguin a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            penguin.walk()

            # check for the distance between penguin and the snowman
            output = nets[penguins.index(penguin)].activate((penguin.rect.x,
                                                             abs(penguin.rect.right - snowmen[obj_ind].rect.left)))

            if output[0] > 0.5:
                penguin.jump()

        add_obs = False
        rem = []

        for snowman in snowmen:
            snowman.walk()

            # check for collision
            for x, penguin in enumerate(penguins):
            # for x, penguin in enumerate(penguins):
                if snowman.collide(penguin):
                    # every time penguin collides we reduce the fitness by -1
                    # ge[penguins.index(penguin)].fitness -= 1
                    # nets.pop(penguins.index(penguin))
                    # ge.pop(penguins.index(penguin))
                    # penguins.pop(penguins.index(penguin))
                    ge[x].fitness -= 1
                    # remove the penguin object
                    penguins.pop(x)
                    # remove the neural network associated to this penguin
                    nets.pop(x)
                    # remove the neural network associated to this penguuin
                    ge.pop(x)

            # for removing the obs
            if snowman.rect.right < 0:
                rem.append(snowman)

            # to see if obs has crossed the player
            if not snowman.passed and snowman.rect.x < penguin.rect.x:
                snowman.passed = True
             #   add_obs = True

           # if add_obs:
                score += 1
                for g in ge:
                    g.fitness += 5
                snowmen.append(Snowman(gamespeed, 64, 64))

            snowman.walk()

            # removing obstacles which has crossed
            for r in rem:
                snowmen.remove(r)

            for x, penguin in enumerate(penguins):
                if penguin.rect.top > 605:
                    nets.pop(x)
                    ge.pop(x)
                    penguins.pop(x)

        # penguin.update()

        scrollingBg.draw()
        scrollingBg.update()
        draw_window(penguins, snowmen, obj_ind, score)
        # for penguin in penguins:
        # penguin.update()
        # penguin.draw(screen)
        # snowman.draw(screen)
        # show_score(score, 10, 10)

        pygame.display.update()

        # increase speed by time
        # if frame % 800 == 799:
        #    frame = (frame + 1)


def run(config_path):
   # runs the NEAT algorithm to train the neural network, and sets location for the config file
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # set up population based on the config file
    p = neat.Population(config)

    # set output for the statistics
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # call the fitness function and config file for 50 generations
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
