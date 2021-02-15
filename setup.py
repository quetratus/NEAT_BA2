import pygame
from pygame.locals import *
import random
import os

# start up pygame
pygame.init()
clock = pygame.time.Clock()

# set up screen size, FPS, colors...
WINDOW_SIZE = (width, height) = (852, 604)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("DeepRunnerAI")

font = pygame.font.Font('freesansbold.ttf', 20)

GROUND_LEVEL = round(height * 0.83)
X_POSITION = round(width / 15)

# Define colours
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FPS = 40

# set gravity and highscore
GRAVITY = 0.5
GENERATION = 0