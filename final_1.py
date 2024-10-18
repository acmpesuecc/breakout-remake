import pygame
import sys
import json
import random
import math
from pygame.locals import *

# Load settings from settings.txt
data = {"screen_width": 1680, "screen_height": 1050, "scr": "1680x1050", "fps": 30}
try:
    with open('settings.txt') as setfile:
        data = json.load(setfile)
except:
    pass

pygame.init()
pygame.display.init()
scrw = data['screen_width']
scrh = data['screen_height']
background = pygame.Surface((scrw, scrh))
screen = pygame.display.set_mode((scrw, scrh), DOUBLEBUF | HWSURFACE)
pygame.display.set_caption('Brick-slayer')
clock = pygame.time.Clock()
fps = data['fps']

# Colours
bg = (9, 10, 24)
text_col = (255, 255, 255)

# Load assets for walls and power-ups
wall_image_map = {
    1: pygame.transform.scale(pygame.image.load("assets/red.png"), (115, 35)),
    2: pygame.transform.scale(pygame.image.load("assets/gold.png"), (115, 35)),
    3: pygame.transform.scale(pygame.image.load("assets/blue.png"), (115, 35)),
    4: pygame.transform.scale(pygame.image.load("assets/purple.png"), (115, 35)),
    5: pygame.transform.scale(pygame.image.load("assets/green.png"), (115, 35)),
}

# Load start page logo
start_image = pygame.image.load('assets/Untitled.png').convert_alpha()
logo_rect = start_image.get_rect()

# Define function for drawing text
def draw_text(text, font, color, y):
    img = font.render(text, True, color)
    text_rect = img.get_rect(center=(scrw / 2, y))
    screen.blit(img, text_rect)

# Paddle class as a Sprite
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/paddle.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.reset()

    def update(self):
        mouse_x, _ = pygame.mouse.get_pos()
        self.rect.x = mouse_x - self.rect.width // 2
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x + self.rect.width > scrw:
            self.rect.x = scrw - self.rect.width

    def reset(self):
        self.rect.x = scrw // 2 - self.rect.width // 2
        self.rect.y = scrh - 40

# Ball class as a Sprite
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/ball.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.speed_x = 5
        self.speed_y = -5
        self.reset(x, y)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left <= 0 or self.rect.right >= scrw:
            self.speed_x = -self.speed_x
        if self.rect.top <= 0:
            self.speed_y = -self.speed_y

    def reset(self, x, y):
        self.rect.x = x - self.rect.width // 2
        self.rect.y = y

# Brick class as a Sprite
class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, strength):
        super().__init__()
        self.image = wall_image_map[strength]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.strength = strength

# Wall class to create bricks
class Wall:
    def __init__(self):
        self.bricks = pygame.sprite.Group()

    def create_wall(self, matrix):
        self.bricks.empty()
        for row_index, row_values in enumerate(matrix):
            for col_index, strength in enumerate(row_values):
                if strength > 0:
                    brick_x = col_index * 115
                    brick_y = row_index * 35
                    brick = Brick(brick_x, brick_y, strength)
                    self.bricks.add(brick)

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (10, 10), 10)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > scrh:
            self.kill()

# Initialize game objects
wall = Wall()
paddle = Paddle()
ball = Ball(paddle.rect.centerx, paddle.rect.top)

# Sprite Groups
all_sprites = pygame.sprite.LayeredUpdates(paddle, ball)
power_up_group = pygame.sprite.Group()

# Create a new level
level_matrix = [
    [3, 2, 1, 1, 2, 3, 0, 3, 2, 1],
    [1, 2, 3, 1, 0, 1, 3, 2, 1, 2],
    [2, 1, 1, 2, 3, 3, 2, 1, 0, 1]
]
wall.create_wall(level_matrix)
all_sprites.add(wall.bricks)

# Landing page display
def display_landing_page():
    waiting_for_input = True
    while waiting_for_input:
        clock.tick(60)
        screen.fill((0, 0, 0))
        screen.blit(start_image, (scrw / 2 - logo_rect.width / 2, scrh // 2 - logo_rect.height / 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_input = False
        pygame.display.update()

# Run landing page before the game starts
display_landing_page()

# Initialize score
score = 0

# Main game loop
running = True
while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game state
    all_sprites.update()
    power_up_group.update()

    # Collision between ball and bricks
    hit_bricks = pygame.sprite.spritecollide(ball, wall.bricks, True)
    if hit_bricks:
        ball.speed_y *= -1
        score += 10

    # Collision between ball and paddle
    if pygame.sprite.collide_rect(ball, paddle):
        ball.speed_y = -abs(ball.speed_y)

    # Drawing only updated areas
    screen.fill(bg)
    all_sprites.draw(screen)
    power_up_group.draw(screen)
    draw_text(f"Score: {score}", pygame.font.SysFont('typewriter', 40), text_col, 30)

    pygame.display.flip()

pygame.quit()
sys.exit()
