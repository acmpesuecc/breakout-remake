import sys, json, random, math
import pygame
from pygame.locals import *
import LevelDefines as level

# Initialize Pygame and load settings
pygame.init()
pygame.display.init()

# Load settings
data = {"screen_width": 1280, "screen_height": 720, "scr": "1280x720", "fps": 30}
try:
    with open('settings.txt') as setfile:
        data = json.load(setfile)
except:
    pass

scrw = data['screen_width']
scrh = data['screen_height']
screen = pygame.display.set_mode((scrw, scrh), DOUBLEBUF | HWSURFACE)
pygame.display.set_caption('Brick-slayer')

# Sprite Groups for efficient rendering and collision detection
all_sprites = pygame.sprite.Group()
brick_sprites = pygame.sprite.Group()
ball_sprites = pygame.sprite.Group()
paddle_sprites = pygame.sprite.Group()
powerup_sprites = pygame.sprite.Group()

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, strength):
        super().__init__()
        self.strength = strength
        self.images = {
            1: pygame.transform.scale(pygame.image.load("assets/red.png").convert_alpha(), (115, 35)),
            2: pygame.transform.scale(pygame.image.load("assets/gold.png").convert_alpha(), (115, 35)),
            3: pygame.transform.scale(pygame.image.load("assets/blue.png").convert_alpha(), (115, 35)),
            4: pygame.transform.scale(pygame.image.load("assets/purple.png").convert_alpha(), (115, 35)),
            5: pygame.transform.scale(pygame.image.load("assets/green.png").convert_alpha(), (115, 35))
        }
        self.image = self.images[strength]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def damage(self):
        self.strength -= 1
        if self.strength > 0:
            self.image = self.images[self.strength]
        else:
            self.kill()
        return 10  # Score for hitting brick

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/paddle.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.reset()
        
    def reset(self):
        self.rect.width = 114
        self.rect.height = 30
        self.rect.x = int((scrw / 2) - (self.rect.width / 2))
        self.rect.y = scrh - (self.rect.height * 2)
        self.direction = 0
        
    def update(self):
        mouse_x, _ = pygame.mouse.get_pos()
        self.rect.x = mouse_x - self.rect.width // 2
        
        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > scrw:
            self.rect.right = scrw

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/ball.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.reset(x, y)
        self.mask = pygame.mask.from_surface(self.image)  # Pixel-perfect collisions
        
    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 5
        self.speed_y = -5
        self.speed_max = 6
        self.active = True
        
    def update(self):
        if not self.active:
            return
            
        # Update position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Wall collisions
        if self.rect.left <= 0 or self.rect.right >= scrw:
            self.speed_x *= -1
        if self.rect.top <= 0:
            self.speed_y *= -1
        if self.rect.bottom >= scrh:
            self.active = False
            return
            
        # Paddle collision - using sprite collide
        paddle_hit = pygame.sprite.spritecollide(self, paddle_sprites, False)
        if paddle_hit:
            paddle = paddle_hit[0]
            self.speed_y *= -1
            # Adjust x speed based on where ball hits paddle
            hit_pos = (self.rect.centerx - paddle.rect.left) / paddle.rect.width
            self.speed_x = (hit_pos - 0.5) * 10
            
        # Brick collision - using sprite collide
        brick_hits = pygame.sprite.spritecollide(self, brick_sprites, False)
        for brick in brick_hits:
            score = brick.damage()
            if random.random() < 0.01:  # 1% chance for power-up
                PowerUp(brick.rect.centerx, brick.rect.bottom)
            
            # Determine collision side and bounce accordingly
            if self.speed_y > 0 and self.rect.bottom > brick.rect.top:
                self.speed_y *= -1
            elif self.speed_y < 0 and self.rect.top < brick.rect.bottom:
                self.speed_y *= -1
            
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (10, 10), 10)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        powerup_sprites.add(self)
        all_sprites.add(self)
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > scrh:
            self.kill()
        
        # Check for paddle collection
        if pygame.sprite.spritecollide(self, paddle_sprites, False):
            self.activate()
            self.kill()
            
    def activate(self):
        # Spawn 5 new balls
        paddle = paddle_sprites.sprites()[0]
        angles = [0.4, 0.6, 0.8, 1.0, 1.2]
        for angle in angles:
            new_ball = Ball(paddle.rect.centerx, paddle.rect.top)
            new_ball.speed_x = math.cos(angle) * 5
            new_ball.speed_y = math.sin(angle) * -5
            ball_sprites.add(new_ball)
            all_sprites.add(new_ball)

def create_level(level_number):
    # Clear existing bricks
    brick_sprites.empty()
    
    matrix = level.BRICK_LAYOUTS[level_number - 1]
    brick_width = 115
    brick_height = 35
    
    for row_index, row in enumerate(matrix):
        for col_index, strength in enumerate(row):
            if strength > 0:
                brick = Brick(col_index * brick_width, row_index * brick_height, strength)
                brick_sprites.add(brick)
                all_sprites.add(brick)

def main():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('typewriter', 70)
    score = 0
    level_number = 1
    game_over = False
    
    # Create initial game objects
    paddle = Paddle()
    paddle_sprites.add(paddle)
    all_sprites.add(paddle)
    
    ball = Ball(paddle.rect.centerx, paddle.rect.top)
    ball_sprites.add(ball)
    all_sprites.add(ball)
    
    create_level(level_number)
    
    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_SPACE and not ball.active:
                    ball.reset(paddle.rect.centerx, paddle.rect.top)
                elif event.key == K_RETURN and len(brick_sprites) == 0:
                    level_number += 1
                    create_level(level_number)
                    ball.reset(paddle.rect.centerx, paddle.rect.top)
        
        # Update
        all_sprites.update()
        
        # Check win/lose conditions
        if len(brick_sprites) == 0:
            game_over = True
        if not any(ball.active for ball in ball_sprites):
            game_over = True
        
        # Draw
        screen.fill((9, 10, 24))
        all_sprites.draw(screen)
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        if game_over:
            if len(brick_sprites) == 0:
                text = "Press RETURN for next level"
            else:
                text = "Press SPACE to restart"
            game_over_text = font.render(text, True, (255, 255, 0))
            text_rect = game_over_text.get_rect(center=(scrw//2, scrh//2))
            screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
        clock.tick(data["fps"])

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()