import pygame, sys, random,json
from itertools import cycle


pygame.init()
data={"screen_width": 1280, "screen_height": 720, "scr": ["1280x720"], "speed": 90}  
try:
    with open('settings.txt') as setfile:
        data=json.load(setfile)
except:
    pass

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


WIN_SIZE = [data["screen_width"],data["screen_height"]]
MAX_FRAME_RATE = data['speed']
SPEED_RATE = MAX_FRAME_RATE / 30
BALL_INITIAL_SPEED = [SPEED_RATE, -SPEED_RATE]
PADDLE_INITIAL_SPEED = SPEED_RATE *2
COL_BACKGROUND = 0, 0, 0
MAX_PLAYER_LIFE = 2
TITLE_BLINK_EVENT = pygame.USEREVENT + 0


WIDTH = 1280
HEIGHT =720
WIN_SIZE=[WIDTH,HEIGHT]

FONT = pygame.font.SysFont("Consolas", int(WIDTH/20))

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong!")

CLOCK = pygame.time.Clock()

window = pygame.display.set_mode(WIN_SIZE)



# Paddles
def play_pong():
    RUNNING=True

    player = pygame.Rect(0, 0, 10, 100)
    player.center = (WIDTH-100, HEIGHT/2)

    opponent = pygame.Rect(0, 0, 10, 100)
    opponent.center = (100, HEIGHT/2)

    player_score=0
    opponent_score = 0
    win_point=10

    # Ball

    ball = pygame.Rect(0, 0, 20, 20)
    ball.center = (WIDTH/2, HEIGHT/2)

    x_speed, y_speed = 1, 1

    while RUNNING:
        if player_score or opponent_score >= win_point:
            is_game_over=True
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_SPACE]:
            if not ball.moving:
                ball.moving = True

        if keys_pressed[pygame.K_UP]:
            if player.top > 0:
                player.top -= 2
        if keys_pressed[pygame.K_DOWN]:
            if player.bottom < HEIGHT:
                player.bottom += 2
        if keys_pressed[pygame.K_w]:
            if opponent.top > 0:
                    opponent.top -= 2
        if keys_pressed[pygame.K_s]:
            if opponent.bottom < HEIGHT:
                opponent.bottom += 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if ball.y >= HEIGHT:
            y_speed = -1
        if ball.y <= 0:
            y_speed = 1
        if ball.x <= 0:
            player_score += 1
            ball.center = (WIDTH/2, HEIGHT/2)
            x_speed, y_speed = random.choice([1, -1]), random.choice([1, -1])
        if ball.x >= WIDTH:
            opponent_score += 1
            ball.center = (WIDTH/2, HEIGHT/2)
            x_speed, y_speed = random.choice([1, -1]), random.choice([1, -1])
        if player.x - ball.width <= ball.x <= player.right and ball.y in range(player.top-ball.width, player.bottom+ball.width):
            x_speed = -1
        if opponent.x - ball.width <= ball.x <= opponent.right and ball.y in range(opponent.top-ball.width, opponent.bottom+ball.width):
            x_speed = 1

        player_score_text = FONT.render(str(player_score), True, "white")
        opponent_score_text = FONT.render(str(opponent_score), True, "white")


        ball.x += x_speed * 2
        ball.y += y_speed * 2

        SCREEN.fill("Black")

        pygame.draw.rect(SCREEN, "white", player)
        pygame.draw.rect(SCREEN, "white", opponent)
        pygame.draw.circle(SCREEN, "white", ball.center, 10)

        SCREEN.blit(player_score_text, (WIDTH/2+50, 50))
        SCREEN.blit(opponent_score_text, (WIDTH/2-50, 50))

        pygame.display.update()
        CLOCK.tick(300)

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
            CLOCK.tick(MAX_FRAME_RATE)

    except FileNotFoundError:
        print("Couldn't load font files.")
        return
    except Exception as gi_e:
        print("Unknown Error occured! Error: " + str(gi_e))
        return


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


def game_over():
    global is_game_intro
    global is_game_over
    global is_highscore

    # stop music
    pygame.mixer.music.stop()

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
            CLOCK.tick(MAX_FRAME_RATE)

    except Exception as go_e:
        print("Unknown Error occured! Error: " + str(go_e))
        return



def play():
    while is_running:
        if is_game_intro:
            # start screen
            game_intro()

        if is_game:
            # main game loop
            play_pong()
            #end screen
        if is_game_over:
            game_over()

    pygame.quit()