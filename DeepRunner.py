from setup import *
import neat


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
def show_score(score, penguins, x_wert_p, x_wert_rect_p, x_wert_e, x_wert_rect_e, fehlercode):
    font = pygame.font.Font('freesansbold.ttf', 18)
    score_value = font.render("Score : " + str(score), True, WHITE)
    screen.blit(score_value, (10, 10))
    score_value = font.render("Gens: " + str(GENERATION - 1), True, WHITE)
    screen.blit(score_value, (10, 30))
    score_value = font.render("Alive: " + str(len(penguins)), True,WHITE)
    screen.blit(score_value, (10, 50))
    score_value = font.render("Penguin x: " + str(x_wert_p) + str(x_wert_rect_p), True, WHITE)
    screen.blit(score_value, (10, 70))
    score_value = font.render("Enemy x: " + str(x_wert_e) + str(x_wert_rect_e), True, WHITE)
    screen.blit(score_value, (10, 90))
    score_value = font.render("Fehlercode: " + str(fehlercode), True, WHITE)
    screen.blit(score_value, (10, 110))


# show background
class Background:
    def __init__(self, bg_speed):
        self.image, self.rect = load_image('bg_happy.png', -1, -1, 1)
        self.image1, self.rect1 = load_image('bg_happy.png', -1, -1, 1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = bg_speed

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
        self.rect.bottom = GROUND_LEVEL
        self.rect.left = X_POSITION
        # animation
        self.image = self.images[0]
        self.image1 = self.images1[0]
        self.index = 0
        self.frame = 0
        self.score = 0
        self.isJumping = False
        self.isDucking = False
        self.movement = [0, 0]
        self.jumpSpeed = 10
        self.x = self.rect.x
        self.y = self.rect.y
        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    # draw self
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, GREEN, self.rect, 2)

    def jump(self):
        if self.rect.bottom == GROUND_LEVEL:
            self.isJumping = True
            self.movement[1] = -1*self.jumpSpeed

    def duck(self):
        if not self.isJumping:
            self.isDucking = True

    def unduck(self):
        self.isDucking = False

    def checkbounds(self):
        if self.rect.bottom > GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.isJumping = False

    def move(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + GRAVITY

        if self.isJumping:
            self.index = 0
        # walking animation
        elif self.isDucking:
            self.index = (self.index + 1) % 2
            self.index = 1
        elif self.frame % 5 == 0:
                self.index = (self.index + 1) % 5

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()
        self.frame += 1

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Enemy:
    def __init__(self, gamespeed):
        if random.choice(range(6)) > 2:
            self.type_ = 1 # snowman
            self.images, self.rect = load_sprite_sheet('snowman4.png', 4, 1, 64, 64, -1)
            self.image = self.images[0]
            self.rect.bottom = GROUND_LEVEL
            self.rect.left = width + self.rect.width
        else:
            self.type_ = 2 # bird
            self.images, self.rect = load_sprite_sheet('vogel3.png', 4, 1, 75, 90, -1)
            self.image = self.images[0]
            #self.bird_height = [height * 0.80, height * 0.90]
            self.bird_height = [height * 0.80, height * 0.80, height * 0.80, height * 0.90]
            self.rect.bottom = self.bird_height[random.randrange(0, 4)]
            self.rect.left = width + self.rect.width
        self.index = 0
        self.frame = 0
        self.movement = [-1 * gamespeed, 0]
        self.passed = False
        self.x = self.rect.x
        self.y = self.rect.y

    def move(self):
        self.rect = self.rect.move(self.movement)

    def collide(self, penguin):
        # Checking for collision using get mask function
        player_mask = penguin.get_mask()
        obj_mask = pygame.mask.from_surface(self.image)
        obj_offset = (round(self.rect.x - penguin.rect.x), self.rect.y - round(penguin.rect.y))
        collision_point = player_mask.overlap(obj_mask, obj_offset)
        if collision_point:
            return True
        return False

    def draw(self, screen):
        self.image = self.images[self.index]
        if self.type_ == 1:
            if self.frame % 10 == 0:
                self.index = (self.index + 1) % 3

        if self.type_ == 2:
            if self.frame % 6 == 0:
                # high birds have 1 frame of animation less for the old version
                if self.rect.bottom == (height * 0.90):
                    self.index = (self.index + 1) % 4
                if self.rect.bottom != (height * 0.90):
                    self.index = (self.index + 1) % 3

        self.frame = (self.frame + 1)
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, RED, self.rect, 2)


# Bonus item
class Fish:
    def __init__(self, x, y):
        self.image, self.rect = load_image('fisch3.png', x, y, -1)
        self.fish_height = [height * 0.59, height * 0.75, height * 0.82]
        self.rect.bottom = self.fish_height[random.randrange(0, 3)]
        self.rect.left = width + self.rect.width
        self.speed = 18
        self.movement = [-1 * self.speed, 0]
        self.passed = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self):
        self.rect = self.rect.move(self.movement)


    def collide(self, penguin):
        # Checking for collision using get mask function
        player_mask = penguin.get_mask()
        obj_mask = pygame.mask.from_surface(self.image)
        obj_offset = (round(self.rect.x - penguin.rect.x), self.rect.y - round(penguin.rect.y))
        collision_point = player_mask.overlap(obj_mask, obj_offset)
        if collision_point:
            return True
        return False


def draw_window(scrollingBg, penguins, fishes, enemies, score, x_wert_p, x_wert_rect_p, x_wert_e, x_wert_rect_e, fehlercode):
    # define elements on screen
    scrollingBg.draw()
    for penguin in penguins:
        penguin.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)
        enemy.move()
    for fish in fishes:
        fish.draw(screen)
        fish.move()

    show_score(score, penguins, x_wert_p, x_wert_rect_p, x_wert_e, x_wert_rect_e, fehlercode)
    pygame.display.update()


def remove_penguin(index):
    penguins.pop(index)
    ge.pop(index)
    nets.pop(index)


def main(genomes, config):
    global penguins, nets, ge, snowmen, birds, fishes
    global GENERATION
    global x_wert_p, x_wert_rect_p, x_wert_e, x_wert_rect_e
    GENERATION += 1
    gamespeed = 4
    bg_speed = 4
    fehlercode = 0
    # scrolling of background to the left
    scrollingBg = Background(-1 * bg_speed)

    # penguins, neural network and genomes
    penguins = []
    nets = []
    ge = []


    # Create list of obstacle class objects
    enemies = [Enemy(gamespeed)]
    fishes = [Fish(45, 25)]

    frame = 0
    score = 0

    # List of Genomes
    # we need the underscore to loop through the indexes of the genomes
    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        penguin = (Penguin(72, 64))
        penguins.append(penguin)
        genome.fitness = 0  # start with fitness level of 0
        ge.append(genome)

    run = True
    while run and len(penguins):
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        for penguin in penguins:
            x_wert_p = str(penguin.x)
            x_wert_rect_p = str(penguin.rect.x)

        for enemy in enemies:
            x_wert_e = str(enemy.x)
            x_wert_rect_e = str(enemy.rect.x)

        for x, penguin in enumerate(penguins):
            penguin.move()
            ge[x].fitness += 0.1

            # enemy index and fish index is 0
            enemy_ind = 0
            fish_ind = 0
            if len(penguins) > 0:
                # to check which snowman; if penguin passes the first snowman then change index to 1
                if len(enemies) > 1 and penguins[0].rect.x > enemies[0].rect.x + enemies[0].rect.width:
                    enemy_ind = 1
                if len(fishes) > 1 and penguins[0].rect.x > fishes[0].rect.x + fishes[0].rect.width:
                    fish_ind = 1
            else:
                break

            # check for the distance between penguin and the snowman
            output = nets[penguins.index(penguin)].activate((penguin.rect.x,
                                                             abs(enemies[enemy_ind].rect.x - penguin.rect.x),
                                                             abs(enemies[enemy_ind].rect.y - penguin.rect.y),
                                                             abs(fishes[fish_ind].rect.x - penguin.rect.x),
                                                             abs(fishes[fish_ind].rect.y - penguin.rect.x)))

            if output[0] > 0.5:
                penguin.jump()
            if output[1] > 0.5:
                penguin.duck()
            else:
                penguin.unduck()

        rem = []

        for fish in fishes:
            for x, penguin in enumerate(penguins):
                if fish.collide(penguin):
                    ge[x].fitness += 50
                    score += 50
                    for fish in fishes:
                        fishes.remove(fish)
                        fishes.append(Fish(45, 25))
                elif fish.rect.right <= 0:
                        for fish in fishes:
                            fishes.remove(fish)
                            fishes.append(Fish(45, 25))

            #     if fish.passed and random.randrange(0, 50) == 3:
          #          fishes.append(Fish(45, 25))

            for r in rem:
                rem.remove(r)
                fehlercode = 1

        for enemy in enemies:
            enemy.move()
            for x, penguin in enumerate(penguins):
                if enemy.collide(penguin):
                    ge[x].fitness -= 1
                    remove_penguin(x)

             #   if enemy.passed and penguin.rect.x < enemy.rect.x:
                #if penguin.rect.x > enemy.rect.x:
              #      enemy.passed = True
               #     add_enemy = True

                if (enemy.rect.x) <= 0:
                 #   rem.append(enemy)
                    for enemy in enemies:
                        enemies.remove(enemy)
                        enemies.append(Enemy(gamespeed))
                        for g in ge:
                            g.fitness += 5

            enemy.move()

        for penguin in penguins:
            penguin.move()

        # score increases every 1/4 second
        if frame % 10 == 0:
            score += 1

        if frame % 800 == 799:
            bg_speed -= 1
            gamespeed += 1

        draw_window(scrollingBg, penguins, fishes, enemies, score, x_wert_p, x_wert_rect_p, x_wert_e, x_wert_rect_e, fehlercode)
        scrollingBg.update()
        frame += 1

        pygame.display.update()


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