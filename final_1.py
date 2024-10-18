import sys, json, random, math
import pygame
from pygame.locals import *
from PIL import Image
import LevelDefines as level

data = {"screen_width": 1680, "screen_height": 1050, "scr": "1680x1050", "fps": 30}
try:
    with open('settings.txt') as setfile:
        data = json.load(setfile)
except:
    pass

pygame.init()
pygame.mixer.init()  # Initialize Pygame mixer
pygame.display.init()
scrw = data['screen_width']
scrh = data['screen_height']
background = pygame.Surface((scrw, scrh))
screen = pygame.display.set_mode((scrw, scrh), DOUBLEBUF | HWSURFACE)
pygame.display.set_caption('Brick-slayer')

# level
level_number = 1
matrix = level.BRICK_LAYOUTS[level_number-1]

# define font
font = pygame.font.SysFont('typewriter', 70)
speed = [5, -5]

# colours
bg = (9, 10, 24)
block_gold_outline = (255, 215, 0)
block_magenta_outline = (255, 0, 255)
block_teal_outline = (55, 255, 255)
paddle_col = (255, 255, 255)
paddle_outline = (105, 105, 105)
text_col = (255, 255, 255)

# define game variables
cols = 17
rows = 6
clock = pygame.time.Clock()
fps = data["fps"]
live_ball = False
game_over = 0
power_ups = []
score = 0

def draw_text(text, font, text_col, y):
    img = font.render(text, True, text_col)
    text_rect = img.get_rect(center=(scrw/2, y))
    screen.blit(img, text_rect)

class Wall():
    def __init__(self):
        self.width = 115
        self.height = 35
        self.blocks = []
        self.images = {
            1: pygame.transform.scale(pygame.image.load("assets/red.png").convert(), (115, 35)),
            2: pygame.transform.scale(pygame.image.load("assets/gold.png").convert(), (115, 35)),
            3: pygame.transform.scale(pygame.image.load("assets/blue.png").convert(), (115, 35)),
            4: pygame.transform.scale(pygame.image.load("assets/purple.png").convert(), (115, 35)),
            5: pygame.transform.scale(pygame.image.load("assets/green.png").convert(), (115, 35))
        }
        self.brick_sound = pygame.mixer.Sound('assets/brick.wav')

    def create_wall(self, matrix):
        for row_index, row_values in enumerate(matrix):
            block_row = []
            for col_index, strength in enumerate(row_values):
                if strength == 0:
                    continue
                block_x = col_index * self.width
                block_y = row_index * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                # Increase brick strength by multiplying it by 3
                block_individual = [rect, strength * 3]
                block_row.append(block_individual)
            self.blocks.append(block_row)
    def draw_wall(self, screen):
        for row in self.blocks:
            for block in row:
                strength = block[1]
                if strength == 0:
                    continue
                block_rect = block[0]
                if strength in self.images:
                    brick_image = self.images[strength]
                    img_rect = brick_image.get_rect(center=block_rect.center)
                    screen.blit(brick_image, img_rect)


def calculate_ball_speed(remaining_blocks):
    # Reduce ball speed by roughly 25%
    if remaining_blocks < 5:
        return 4
    elif remaining_blocks < 10:
        return 5
    elif remaining_blocks < 15:
        return 6
    else:
        return 7

class Paddle():
    def __init__(self):
        self.width = 114
        self.height = 30
        self.x = float((scrw / 2) - (self.width / 2))
        self.y = scrh - (self.height * 2)
        self.rect = pygame.Rect(int(self.x), self.y, self.width, self.height)
        self.image = pygame.image.load('assets/paddle.png').convert_alpha()
        self.paddle_sound = pygame.mixer.Sound('assets/paddle.wav')
        self.speed = 10  # Constant speed for keyboard movement
        self.direction = 0
        self.using_keyboard = False
        self.last_mouse_x = 0

    def move(self):
        keys = pygame.key.get_pressed()
        mouse_x, _ = pygame.mouse.get_pos()
        
        # Check for keyboard input
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.using_keyboard = True
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
                self.direction = -1
            elif keys[pygame.K_RIGHT]:
                self.x += self.speed
                self.direction = 1
        else:
            self.using_keyboard = False

        # Use mouse input only if keyboard is not being used
        if not self.using_keyboard:
            if mouse_x != self.last_mouse_x:  # Check if mouse has moved
                self.x = float(mouse_x - self.width / 2)
                self.direction = 1 if mouse_x > self.last_mouse_x else -1 if mouse_x < self.last_mouse_x else 0
                self.last_mouse_x = mouse_x
            else:
                self.direction = 0

        # Ensure paddle stays within screen bounds
        if self.x < 0:
            self.x = 0
            self.direction = 0
        if self.x > scrw - self.width:
            self.x = scrw - self.width
            self.direction = 0

        # Update the rect position
        self.rect.x = int(self.x)

    def draw(self):
        screen.blit(self.image, self.rect)

    def reset(self):
        self.x = float((scrw / 2) - (self.width / 2))
        self.rect.x = int(self.x)
        self.direction = 0
        self.using_keyboard = False
        self.last_mouse_x = pygame.mouse.get_pos()[0]
class GameBall():
    def __init__(self, x, y):
        self.reset(x, y)
        self.image = pygame.image.load('assets/ball.png').convert_alpha()
        self.brick_sound = pygame.mixer.Sound('assets/brick.wav')
        self.paddle_sound = pygame.mixer.Sound('assets/paddle.wav')
        self.remaining_blocks = sum(sum(1 for strength in row if strength > 0) for row in matrix)

    def move(self):
        collision_thresh = 5
        wall_destroyed = 1
        row_count = 0

        for row in wall.blocks:
            item_count = 0
            for item in row:
                if self.rect.colliderect(item[0]):
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1
                    if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                        self.speed_y *= -1
                    if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                        self.speed_x *= -1
                    if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                        self.speed_x *= -1

                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                        global score
                        # Reduce score increment to 5 points per hit
                        score += 5
                        self.brick_sound.play()
                    elif wall.blocks[row_count][item_count][1] == 1:
                        wall.blocks[row_count][item_count][1] -= 1
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)
                        score += 5
                        self.brick_sound.play()
                        self.remaining_blocks -= 1
                    if random.random() < 0.005:
                        powerup.spawn_power_ups()

                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                item_count += 1
            row_count += 1

        if wall_destroyed == 1:
            self.game_over = 1
        # Wall collision
        if self.rect.left < 0 or self.rect.right > scrw:
            self.speed_x *= -1
        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > scrh:
            self.game_over = -1
            self.live_ball = False

        # Paddle collision
        if self.rect.colliderect(player_paddle.rect):
            if abs(self.rect.bottom - player_paddle.rect.top) < collision_thresh and self.speed_y > 0:
                self.speed_y *= -1
                self.speed_x += player_paddle.direction  # Use the direction from the paddle
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
                self.paddle_sound.play()
            self.speed_max = calculate_ball_speed(self.remaining_blocks)

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def reset(self, x, y):
        self.ball_rad = 11
        self.x = x - self.ball_rad
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        # Reduce initial ball speed
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 5
        self.game_over = 0
        self.live_ball = True

    def collect_power_ups(self):
        for power_up in power_ups:
            if not power_up.is_collected() and self.rect.colliderect(
                pygame.Rect(power_up.x - power_up.radius, power_up.y - power_up.radius, 2 * power_up.radius, 2 * power_up.radius)
            ):
                power_up.collect()

    def is_off_screen(self):
        return self.rect.y > scrh

class powerup():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = (255, 0, 0)
        self.collected = False

    @staticmethod
    def spawn_power_ups():
        paddle_center_x = player_paddle.x + player_paddle.width // 2
        paddle_center_y = player_paddle.y - player_paddle.height // 2
        angles = [0.4, 0.6, 0.8, 1.0, 1.2]
        for angle in angles:
            distance_from_center = 30
            new_x = paddle_center_x + int(distance_from_center * math.cos(angle))
            new_y = paddle_center_y + int(distance_from_center * math.sin(angle))
            new_speed_x = math.cos(angle) * 5
            new_speed_y = math.sin(angle) * -5
            new_ball = GameBall(new_x, new_y)
            new_ball.speed_x = new_speed_x
            new_ball.speed_y = new_speed_y
            balls.append(new_ball)
            power_up = powerup(new_x, new_y)
            power_ups.append(power_up)

    @staticmethod
    def draw_power_ups():
        for power_up in power_ups:
            if not power_up.is_collected() and not power_up.is_off_screen():
                pygame.draw.circle(screen, power_up.color, (power_up.x, power_up.y), power_up.radius)

    def is_collected(self):
        return self.collected

    def is_off_screen(self):
        return self.y > scrh

    def collect(self):
        self.collected = True

def draw_score():
    score_font = pygame.font.SysFont('typewriter', 40)
    score_text = f"Score: {score}"
    draw_text(score_text, score_font, text_col, 10)

clock = pygame.time.Clock()
wall = Wall()
wall.create_wall(matrix)
player_paddle = Paddle()
balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
live_ball = False
start_image = pygame.image.load('assets/Untitled.png').convert_alpha()
logo_rect = start_image.get_rect()

waiting_for_input = True
selected_level = 1
while waiting_for_input:
    clock.tick(60)
    current_time = pygame.time.get_ticks()
    screen.blit(start_image, (scrw / 2 - logo_rect.width / 2, scrh // 2 - logo_rect.height / 2))
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            waiting_for_input = False
    pygame.display.update()

level_number = selected_level

waiting_for_input = True
while waiting_for_input:
    clock.tick(120)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
            if event.key == pygame.K_SPACE and not live_ball:
                live_ball = True
                balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
                player_paddle.reset()
                wall.create_wall(matrix)
                balls[0].reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
                clock = pygame.time.Clock()
                score = 0
            elif event.key == K_RETURN:
                level_number += 1
                live_ball = True
                balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
                player_paddle.reset()
                wall.create_wall(matrix)
                balls[0].reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
                clock = pygame.time.Clock()
            elif event.key == pygame.K_ESCAPE:
                score = 0
                with open('settings.txt', 'w') as setfile:
                    json.dump(data, setfile)
                pygame.quit()
                sys.exit(0)
        elif event.type == pygame.MOUSEBUTTONDOWN and not live_ball:
            live_ball = True
            balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
            player_paddle.reset()
            wall.create_wall(matrix)
            balls[0].reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
            clock = pygame.time.Clock()
            score = 0

    if live_ball:
        player_paddle.move()
        for ball in balls:
            ball.collect_power_ups()
            game_over = ball.move()

            if ball.is_off_screen() or game_over != 0:
                ball.live_ball = False

        # Check if all balls are not live
        if not any(ball.live_ball for ball in balls):
            live_ball = False
        screen.fill((0, 0, 0))
        # draw all objects
        wall.draw_wall(screen)
        player_paddle.draw()
        # Draw power-ups
        powerup.draw_power_ups()

        for ball in balls:
            ball.draw()

        # print player instructions
        if not live_ball:
            if game_over == 1:
                exit_image =  pygame.image.load('assets/exit.png').convert_alpha()
                exit_rect = exit_image.get_rect()
                draw_text("Press enter/return to play the next level ", font, "Yellow",600)
                screen.blit(exit_image, (scrw / 2 - logo_rect.width / 2, scrh // 2 - logo_rect.height / 2))
            elif game_over == -1:
                exit_image = pygame.image.load('assets/exit.png')
                exit_rect = exit_image.get_rect()
                screen.blit(exit_image, (scrw / 2 - logo_rect.width / 2, scrh // 2 - logo_rect.height / 2))
        draw_score()
        pygame.display.update()

pygame.display.quit()
pygame.quit()
