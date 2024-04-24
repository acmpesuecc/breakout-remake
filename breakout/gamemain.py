import sys
import pygame
import LevelDefines
from numpy import *
import json
from itertools import cycle

data={"screen_width": 1280, "screen_height": 720, "scr": ["1280x720"], "speed": 90}  
try:
    with open('settings.txt') as setfile:
        data=json.load(setfile)
except:
    pass

# CONSTANTS AND GLOBAL VARS

WIN_SIZE = [data["screen_width"],data["screen_height"]]
MAX_FRAME_RATE = data['speed']
SPEED_RATE = MAX_FRAME_RATE / 30
BALL_INITIAL_SPEED = [SPEED_RATE, -SPEED_RATE]
PADDLE_INITIAL_SPEED = SPEED_RATE *2
COL_BACKGROUND = 0, 0, 0
MAX_PLAYER_LIFE = 2

# bias for collision checks
BALL_RECT_BIAS = 2

# init sprites
ball_paddle_sprites = pygame.sprite.Group()
brick_sprites = pygame.sprite.Group()

# init sound mixer
pygame.mixer.init()
# music
'''add shit here'''
# set sound effects
bounce_effect = pygame.mixer.Sound("res/sound/bounce.wav")
brick_effect = pygame.mixer.Sound("res/sound/brick.wav")
# actual music volume
music_volume = 1.0
# init pygame and set window mode
pygame.init()
pygame.display.set_caption('Brick Slayer')
window = pygame.display.set_mode(WIN_SIZE)

# set clock for game ticks
clock = pygame.time.Clock()
# timers for rotate and blinking text
last_time_rotate = clock.get_time()
last_time_blink = clock.get_time()


# init stats
bricks_count = 0
bricks_gone = 0

# brick id matrix and static brick position matrices
brick_position_matrix_x = zeros((LevelDefines.BRICK_LAYOUT_ROWS, LevelDefines.BRICK_LAYOUT_COLS), dtype='int')
brick_position_matrix_y = zeros((LevelDefines.BRICK_LAYOUT_ROWS, LevelDefines.BRICK_LAYOUT_COLS), dtype='int')
brick_id_matrix = zeros((LevelDefines.BRICK_LAYOUT_ROWS, LevelDefines.BRICK_LAYOUT_COLS), dtype='int')

# actual level
actual_level_num = 3

# blink event
TITLE_BLINK_EVENT = pygame.USEREVENT + 0


# bools for menu handling
is_game_over = False
is_game_intro = True
is_running = True
is_game = False

# colors for cycle on title text
title_colors = cycle([(234, 178, 114), (229, 71, 68), (165, 68, 229), (68, 84, 221), (196, 221, 68)])
active_color = next(title_colors)
next_color = next(title_colors)
current_color = active_color
col_cycle_step = 1

# set window icon
try:
    icon = pygame.image.load("res/img/iCoffee.png").convert_alpha()
    pygame.display.set_icon(icon)
except FileNotFoundError:
    print("Couldn't load window icon! File not found.")
except Exception:
    print("Unknown error while trying to load icon.")


# CLASSES
class Player:
    def __init__(self):
        self.life = MAX_PLAYER_LIFE
        self.score = 0

    def update_score(self, score):
        self.score = score


class Ball(pygame.sprite.Sprite):
    """
    Class for a ball object. (Sprite)
    """

    # constructor
    def __init__(self, initial_pos):
        # initialize sprite class object
        pygame.sprite.Sprite.__init__(self)
        # assign image for ball
        self.image = pygame.image.load("res/img/ball.png").convert_alpha()
        self.rect = self.image.get_rect()
        # initial speed
        self.speed = BALL_INITIAL_SPEED
        # set initial position
        self.rect.x = initial_pos[0]
        self.rect.y = initial_pos[1]
        # check whether ball is in initial_pos or not
        self.moving = False
        # add ball sprite to sprite group
        ball_paddle_sprites.add(self)

    # update sprite
    def update(self):
        if self.moving:
            pos = self.rect.move(self.speed)
            self.rect = pos

    # collision check with walls
    def check_bounds(self):
        """
        Checks if the ball hits the walls of the game field.

        :return: True if ball hits a boundary, False if not.
        """
        # check left/right walls
        if self.rect.left < 0 or self.rect.right > WIN_SIZE[0]:
            self.speed[0] = -self.speed[0]
            bounce_effect.play()
        # check top/bottom walls
        if self.rect.top < 0 or self.rect.bottom > WIN_SIZE[1]:
            self.speed[1] = -self.speed[1]
            bounce_effect.play()

    # collision check with paddle
    def check_collision_paddle(self, paddle):
        """
        Checks collision of the ball with the paddle.

        :param paddle: the paddle object.
        :return: True if ball collides with paddle, False if not.
        """
        # shortcuts for side checks
        left_side = self.rect.right + self.rect.width / 2 >= paddle.rect.left
        right_side = self.rect.left + self.rect.width / 2 >= paddle.rect.right
        above_paddle = self.rect.bottom > paddle.rect.top > self.rect.bottom - self.rect.height / 2
        below_paddle = self.rect.bottom - self.rect.height / 2 >= paddle.rect.top
        corner_left = self.rect.right >= paddle.rect.left >= self.rect.right - self.rect.width / 2
        corner_right = self.rect.left <= paddle.rect.right <= self.rect.left + self.rect.width / 2
        from_left = self.speed[0] > 0
        from_right = self.speed[0] < 0

        # check if collision with paddle happened
        if pygame.sprite.collide_rect(self, paddle):
            # side checks
            if above_paddle:
                # collision at corner of the paddle
                if (corner_left and from_left) or (corner_right and from_right):
                    self.speed[0] = -self.speed[0]
                self.speed[1] = -self.speed[1]
            # collision at sides of paddle
            elif below_paddle:
                if left_side or right_side:
                    self.speed[0] = -self.speed[0]
            return True
        return False

    def check_ball_out(self, paddle):
        """
        Checks whether the ball went out or not.

        :param paddle: the paddle object.
        :return: True if the ball is below the paddle, False if not.
        """
        if self.rect.bottom - self.rect.height / 2 >= paddle.rect.bottom:
            return True
        return False

    def check_collision_brick(self, brick):
        """
        Checks if the ball hit any brick(s).

        :param brick: the brick object to test collision for.
        :return: True if collision happened, False if not.
        """
        if pygame.sprite.collide_rect(self, brick):

            global bricks_gone

            # skip detection if brick was already destroyed
            if brick.status == LevelDefines.BRICK_DESTR:
                return False

            # shortcuts for (possible) ball positions
            from_left_right = (self.rect.x + self.rect.width - BALL_RECT_BIAS <= brick.rect.x
                               or self.rect.x + BALL_RECT_BIAS >= brick.rect.x + brick.rect.width) \
                              and (brick.rect.y <= self.rect.y <= brick.rect.y + brick.rect.height)

            from_top_bottom = (self.rect.y <= brick.rect.y
                               or self.rect.y + BALL_RECT_BIAS >= brick.rect.y + brick.rect.height) \
                              and (brick.rect.x <= self.rect.x <= brick.rect.x + brick.rect.width)

            # check ball reflection direction
            if from_top_bottom:
                self.speed[1] *= -1
            elif from_left_right:
                self.speed[0] *= -1
            else:
                self.speed[0] *= -1
                self.speed[1] *= -1

            # play sound
            brick_effect.play()

            # delete brick
            if not brick.status >= LevelDefines.BRICK_UNDESTR:
                if not brick.status > LevelDefines.BRICK_NORMAL:
                    bricks_gone += 1
                brick.change_status(brick.status - 1)
                return True
            return False


class Brick(pygame.sprite.Sprite):
    """
    Class for a brick object. (Sprite)
    """

    def __init__(self, brick_type, position, brick_id):
        # initialize sprite class object
        pygame.sprite.Sprite.__init__(self)
        # assign image for brick
        # types --> 0 = destroyed
        #           1 = normal
        #           2 = advanced
        #           3 = undestroyable
        #           4 = special
        self.image = pygame.transform.scale(pygame.image.load(LevelDefines.BRICK_IMAGE[brick_type]).convert_alpha(),(75,25))
        # if type == 'normal':
        # self.image = pygame.image.load("res/img/BrickBlue.png").convert_alpha()
        self.rect = self.image.get_rect()
        # position of rect
        self.pos = position
        # actual status of the brick
        self.status = brick_type
        # assign id
        self.id = brick_id
        # add ball sprite to sprite group
        # all_sprites.add(self)
        brick_sprites.add(self)

    def update(self):
        # self.rect = self.pos
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def change_status(self, new_status):
        self.status = new_status
        self.image = pygame.transform.scale(pygame.image.load(LevelDefines.BRICK_IMAGE[new_status]).convert_alpha(),(75,25))


class Paddle(pygame.sprite.Sprite):
    """
    Class for the paddle object. (Sprite)
    """

    def __init__(self):
        # initialize sprite class object
        pygame.sprite.Sprite.__init__(self)
        # assign image for paddle
        self.image = pygame.image.load("res/img/PaddleBlueMiddle.png").convert_alpha()
        self.rect = self.image.get_rect()
        # initial position
        self.rect.x = WIN_SIZE[0] / 2
        self.rect.y = 4 / 5 * WIN_SIZE[1]
        # initial speed
        self.speed = PADDLE_INITIAL_SPEED
        # add to sprites
        ball_paddle_sprites.add(self)
        # set change
        self.change_x = self.rect.x
        # save previous pos
        self.prev_x = self.rect.x

    def can_move_right(self):
        return self.rect.right < WIN_SIZE[0]

    def can_move_left(self):
        return self.rect.left > 0

    def update(self):
        self.prev_x = self.rect.x
        self.rect.x = self.change_x


# GLOBAL GAME METHODS
def init_bricks(level_num):
    """
    Initializes the bricks of the actual level.

    :param level_num: the actual level.
    """
    # check if level number is valid
    if not 0 <= level_num <= LevelDefines.LEVEL_NUM:
        return

    global bricks_count
    global bricks_gone
    global brick_id_matrix
    global brick_position_matrix_x
    global brick_position_matrix_y

    brick_count_row = 0
    row_count = 0
    bricks_count = 0
    bricks_gone = 0

    # initial height and width of bricks
    brick_height = pygame.image.load(LevelDefines.BRICK_IMAGE[0]).get_rect().height
    brick_width = pygame.image.load(LevelDefines.BRICK_IMAGE[0]).get_rect().width

    # brick offset according to window size and brick defines
    brick_offset_x = ((WIN_SIZE[0] -
                       ((brick_width * LevelDefines.BRICKS_PER_ROW)
                        + (LevelDefines.BRICK_SPACE[0] * LevelDefines.BRICKS_PER_ROW))) / 2) + 3

    id_count = 0

    for brick_type in LevelDefines.BRICK_LAYOUTS[level_num]:
        # calculate position of entire brick
        pos_x = brick_offset_x + (brick_width * brick_count_row) + (LevelDefines.BRICK_SPACE[0] * brick_count_row)
        pos_y = (brick_height * 4) + (LevelDefines.BRICK_SPACE[1] * row_count) + (brick_height * row_count)

        # assign positions to position matrices
        brick_position_matrix_x[row_count][brick_count_row] = pos_x
        brick_position_matrix_y[row_count][brick_count_row] = pos_y

        # assign id to brick id matrix
        brick_id_matrix[row_count][brick_count_row] = id_count
        # create instance of Brick
        brick = Brick(brick_type, [pos_x, pos_y], id_count)
        # update stats
        if brick_type > 0:
            bricks_count += 1
        if brick.status >= LevelDefines.BRICK_UNDESTR:
            bricks_gone += 1
        # next row
        if brick_count_row == LevelDefines.BRICKS_PER_ROW - 1:
            brick_count_row = 0
            row_count += 1
        else:
            brick_count_row += 1
        id_count += 1
        brick_sprites.add(brick)

    print(
        "Bricks added. Level Num: " + str(level_num) + ", count: " + str(bricks_count) + ", gone: " + str(bricks_gone))


def cycle_title_color():
    """
    Fades between different RGB values for certain game
    screen titles.
    """
    global col_cycle_step
    global next_color
    global active_color
    global current_color

    col_cycle_step += 1
    if col_cycle_step < MAX_FRAME_RATE:
        # (y-x)/MAX_FRAME_RATE calculates the amount of change per step required to
        # fade one channel of the old color to the new color
        # source: https://stackoverflow.com/questions/51973441/how-to-fade-from-one-colour-to-another-in-pygame
        current_color = [x + (((y - x) / MAX_FRAME_RATE) * col_cycle_step) for x, y in
                         zip(active_color, next_color)]

    else:
        col_cycle_step = 1
        active_color = next_color
        next_color = next(title_colors)

# GAME SCREENS
def game_intro():
    """
    Game Intro screen.
    """
    global is_game_intro
    global is_game
    global is_game_over
    global current_color


    # reset bools
    is_game_over = False

    try:

        # load font and render text
        title_font = pygame.font.Font("res/font/Game_Played.otf", 30)
        title_on = title_font.render("PRESS ENTER", True, (102, 101, 206), COL_BACKGROUND).convert_alpha()
        # create surfaces for title text on/off for blinking animation
        blink_rect = title_on.get_rect()
        title_off = pygame.Surface(blink_rect.size)
        # cycle through both surfaces
        blink_surfaces = cycle([title_on, title_off])
        blink_surface = next(blink_surfaces)
        pygame.time.set_timer(TITLE_BLINK_EVENT, MAX_FRAME_RATE * 10)

        # get title text height and width
        text_width = title_on.get_width()
        text_height = title_on.get_height()

        # load title image
        title_img = pygame.image.load("res/img/title.png")
        title_img_rect = title_img.get_rect()
        # initial position
        title_img_rect.x = WIN_SIZE[0] / 2 - title_img_rect.width / 2
        title_img_rect.y = WIN_SIZE[1] / 3 - title_img_rect.height

        # help text and images
        arr_left_img = pygame.image.load("res/img/arrLeft.png")
        arr_right_img = pygame.image.load("res/img/arrRight.png")
        arr_left_img_rect = arr_left_img.get_rect()
        arr_right_img_rect = arr_right_img.get_rect()

        help_font = pygame.font.Font("res/font/Game_Played.otf", 18)

        help_caption_move = help_font.render("MOVE: ", True, (102, 101, 175), COL_BACKGROUND).convert_alpha()
        help_caption_exit = help_font.render("QUIT: ", True, (102, 101, 175), COL_BACKGROUND).convert_alpha()
        help_caption_start = help_font.render("START: ", True, (102, 101, 175), COL_BACKGROUND).convert_alpha()
        help_descr_exit = help_font.render("ESC", True, (102, 101, 225), COL_BACKGROUND).convert_alpha()
        help_descr_start = help_font.render("SPACE", True, (102, 101, 225), COL_BACKGROUND).convert_alpha()

        arr_left_img_rect.x = WIN_SIZE[0] / 2
        arr_left_img_rect.y = WIN_SIZE[1] - 100

        arr_right_img_rect.x = arr_left_img_rect.x + arr_left_img_rect.width
        arr_right_img_rect.y = arr_left_img_rect.y

        while is_game_intro:
            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == TITLE_BLINK_EVENT:
                    blink_surface = next(blink_surfaces)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()
            # key events
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_RETURN]:
                is_game_intro = False
                is_game = True

            window.fill(COL_BACKGROUND)

            # display blinking title text
            window.blit(blink_surface, (WIN_SIZE[0] / 2 - text_width / 2, WIN_SIZE[1] / 2 - text_height / 2))

            # display title image
            pygame.draw.rect(window, COL_BACKGROUND, title_img_rect)
            window.blit(title_img, title_img_rect)
            # draw help
            text_pos_x = arr_left_img_rect.x - help_caption_move.get_width() - 10
            window.blit(help_caption_move, (text_pos_x, arr_left_img_rect.y))
            pygame.draw.rect(window, COL_BACKGROUND, arr_left_img_rect)
            window.blit(arr_left_img, arr_left_img_rect)
            pygame.draw.rect(window, COL_BACKGROUND, arr_right_img_rect)
            window.blit(arr_right_img, arr_right_img_rect)
            window.blit(help_caption_start, (text_pos_x, arr_left_img_rect.y + help_caption_move.get_height() +3))
            window.blit(help_descr_start,
                        (arr_right_img_rect.x - 10, arr_left_img_rect.y + help_caption_move.get_height()+3 ))
            window.blit(help_caption_exit, (text_pos_x, arr_left_img_rect.y + help_caption_move.get_height()+27))
            window.blit(help_descr_exit,
                        (arr_right_img_rect.x - 10, arr_left_img_rect.y + help_caption_move.get_height()+27))

            # update screen
            pygame.display.update()
            clock.tick(MAX_FRAME_RATE)

    except FileNotFoundError:
        print("Couldn't load font files.")
        return
    except Exception as gi_e:
        print("Unknown Error occured! Error: " + str(gi_e))
        return


def game_loop():
    """
    Game Loop.
    """
    global actual_level_num
    global is_game_over
    global is_game

    # set run bool
    running = True

    # set key events on repeat
    pygame.key.set_repeat()

    # init class instances
    paddle = Paddle()
    ball_pos = [paddle.rect.x + paddle.rect.width / 2, paddle.rect.y ]
    ball = Ball(ball_pos)
    player = Player()

    # collision counter
    collision_tick = 0
    collision = False

    # setup bricks
    init_bricks(actual_level_num)

    # main loop
    while running:
        # check if level up
        if bricks_gone >= bricks_count:
            ball.moving = False
            actual_level_num += 1
            brick_sprites.empty()
            if actual_level_num >= LevelDefines.LEVEL_NUM:
                is_game_over = True
                is_game = False

                break;
            else:
                init_bricks(actual_level_num)

        # check if ball out
        if ball.check_ball_out(paddle):
            ball.moving = False
            ball.speed[0] = SPEED_RATE
            ball.speed[1] = -SPEED_RATE
            player.life -= 1
            if player.life < 1:
                is_game_over = True
                is_game = False

        # leave ball at paddle before start
        if not ball.moving:
            ball.rect.x = paddle.rect.x + paddle.rect.width / 2
            ball.rect.y = paddle.rect.y - 10

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # music playback
            # volume controle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()

        # key events
        pressed = pygame.key.get_pressed()
        # move paddle
        if pressed[pygame.K_RIGHT]:
            if paddle.can_move_right():
                paddle.change_x += paddle.speed
        if pressed[pygame.K_LEFT]:
            if paddle.can_move_left():
                paddle.change_x -= paddle.speed
        # start ball
        if pressed[pygame.K_SPACE]:
            if not ball.moving:
                ball.moving = True

        # show score and lives
        font = pygame.font.Font("res/font/Game_Played.otf", 12)
        lives = font.render("LIVES:", True, (216, 210, 195), COL_BACKGROUND).convert_alpha()
        score = font.render("SCORE:", True, (216, 210, 195), COL_BACKGROUND).convert_alpha()
        score_text = font.render(str(player.score), False, (216, 210, 195), COL_BACKGROUND).convert_alpha()
        text_lives_height = lives.get_height()
        text_score_height = score.get_height()

        # rotate bricks according to rotate scheme
        # ball movement
        ball.check_bounds()

        ''' Check if ball collided with paddle
            within Framerate. This prevents 
            pygame sprite.collide to fire
            again, causing weird behaviour.'''
        if collision:
            if collision_tick == MAX_FRAME_RATE:
                collision_tick = 0
                collision = False
            else:
                collision_tick += 1

        if not collision:
            # check collision with paddle
            if ball.check_collision_paddle(paddle):
                collision = True
                bounce_effect.play()

            # check collision with bricks
            for brick in brick_sprites:
                if ball.check_collision_brick(brick):
                    collision_brick = True
                    player.score += 1

        # update objects
        ball_paddle_sprites.update()
        brick_sprites.update()

        # deprecated
        # brick_hit_list = pygame.sprite.spritecollide(ball, brick_sprites, False)

        # draw sprites
        window.fill(COL_BACKGROUND)
        brick_sprites.draw(window)
        ball_paddle_sprites.draw(window)
        # draw status text
        window.blit(lives, (10, WIN_SIZE[1] - 20 - text_lives_height / 2))
        window.blit(score, (WIN_SIZE[0] - score.get_width() - 40, WIN_SIZE[1] - 20 - text_score_height / 2))
        window.blit(score_text, (WIN_SIZE[0] - 20, WIN_SIZE[1] - 20 - text_score_height / 2))

        # draw life sprites
        if player.life >= 1:
            life_img = pygame.image.load("res/img/lives.png").convert_alpha()
            life_img = pygame.transform.scale(life_img, (12, 14))
            life_img_rect = life_img.get_rect()

            for i in range(player.life):
                life_img_rect.x = lives.get_width() + 20 + i * 20
                life_img_rect.y = WIN_SIZE[1] - lives.get_height() - 14
                window.blit(life_img, life_img_rect)

        # cap framerate
        clock.tick(MAX_FRAME_RATE)

        # finally update display
        pygame.display.update()

        # end loop if game over
        if is_game_over:
            highscore = player.score
            print("Game Over...Highscore: " + str(highscore))
            del player
            del ball
            del paddle
            running = False


def game_over():
    global is_game_intro
    global is_game_over
    global is_highscore

    # stop music
    pygame.mixer.music.stop()

    # empty sprites
    ball_paddle_sprites.empty()
    brick_sprites.empty()

    try:

        while is_game_over:
            # load font and render text
            font = pygame.font.Font("res/font/Game_Played.otf", 20)
            go_title = font.render("GAME OVER", True, current_color, COL_BACKGROUND).convert_alpha()
            go_descr = font.render("PRESS SPACE", True, (244, 131, 66), COL_BACKGROUND).convert_alpha()

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()
            # key events
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE]:
                is_game_intro = True
                is_game_over = False

            cycle_title_color()

            window.fill(COL_BACKGROUND)

            # display blinking title text
            window.blit(go_title,
                        (WIN_SIZE[0] / 2 - go_title.get_width() / 2, WIN_SIZE[1] / 3 - go_title.get_height() / 2))

            window.blit(go_descr,
                        (WIN_SIZE[0] / 2 - go_descr.get_width() / 2, WIN_SIZE[1] / 2 + go_title.get_height() * 2))

            # update screen
            pygame.display.update()
            clock.tick(MAX_FRAME_RATE)

    except Exception as go_e:
        print("Unknown Error occured! Error: " + str(go_e))
        return


# main logic
def main():
    while is_running:
        if is_game_intro:
            # start screen
            game_intro()

        if is_game:
            # main game loop
            game_loop()

        if is_game_over:
            game_over()

    pygame.quit()
