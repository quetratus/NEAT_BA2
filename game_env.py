from utils import *
import random

# Credit "Tio Aimar @ opengameart.org" and "Art from GameArtGuppy.com"
# Credit shivamshekhar (https://github.com/shivamshekhar/Chrome-T-Rex-Rush)

# start up pygame
pygame.init()
clock = pygame.time.Clock()

# set up screen size, FPS, colors...
WINDOW_SIZE = (width, height) = (852, 604)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("DeepRunnerAI")

font = pygame.font.Font('freesansbold.ttf', 15)

# global variables
GROUND_LEVEL = round(height * 0.83)
X_POSITION = round(width / 15)

FPS = 40

GRAVITY = 0.5
highscore = 0
GENERATION = 0


# show background
class Background:
    def __init__(self, bg_speed):
        self.image, self.rect = load_image('Background_Petra3.png', -1, -1, 1)
        self.image1, self.rect1 = load_image('Background_Petra3.png', -1, -1, 1)
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
        self.image = self.images[0]
        self.image1 = self.images1[0]
        self.index = 0
        self.frame = 0
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

    def jump(self):
        if self.rect.bottom == GROUND_LEVEL:
            self.isJumping = True
            self.isDucking = False
            self.movement[1] = -1 * self.jumpSpeed

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
            self.image = self.images1[self.index]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()
        self.frame += 1

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Enemy:
    def __init__(self, gamespeed):
        if random.choice(range(6)) > 2:
            self.type_ = 1  # snowman
            self.images, self.rect = load_sprite_sheet('snowman.png', 4, 1, 64, 64, -1)
            self.image = self.images[0]
            self.rect.bottom = GROUND_LEVEL
            self.rect.left = width + self.rect.width
        else:
            self.type_ = 2  # bird
            self.images, self.rect = load_sprite_sheet('vogel.png', 4, 1, 95, 110, -1)
            self.image = self.images[0]
            # self.bird_height = [height * 0.80, height * 0.90]
            self.bird_height = [height * 0.80, height * 0.80, height * 0.80, height * 0.90]
            self.rect.bottom = self.bird_height[random.randrange(0, 4)]
            self.rect.left = width + self.rect.width
        self.index = 0
        self.frame = 0
        self.movement = [-1 * gamespeed, 0]
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
                    self.index = (self.index + 1) % 4

        self.frame = (self.frame + 1)
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, RED, self.rect, 2)


# Bonus item
class Fish:
    def __init__(self, x, y):
        self.image, self.rect = load_image('fisch.png', x, y, -1)
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