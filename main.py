import pygame
import random
import csv
import time
import numpy as np
import pandas as pd
import tensorflow as tf

model = tf.keras.models.load_model('pong_game_model.h5')

pygame.display.set_caption("PongAI")
pygame.font.init()


WIDTH, HEIGHT = 500, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
BLACK = (0, 0, 0)
FPS = 60
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 20
WHITE = (255, 255, 255)
BALL_SIDE = 10
PADDLE_VEL = 4
BALL_VEL = 2
VICT = 5
SCORE = 0
POINT_UP = pygame.USEREVENT + 1
POINT_DOWN = pygame.USEREVENT + 2
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def draw_window(paddle_up, paddle_down, ball, paddle_up_score_text, paddle_down_score_text):
    WIN.fill(BLACK)
    pygame.draw.rect(WIN, RED, paddle_up)
    pygame.draw.rect(WIN, BLUE, paddle_down)
    pygame.draw.rect(WIN, WHITE, ball)
    WIN.blit(paddle_up_score_text, (10, HEIGHT//2 - paddle_up_score_text.get_height()//2))
    WIN.blit(paddle_down_score_text, (WIDTH - 10 - paddle_down_score_text.get_width(), HEIGHT//2 - paddle_down_score_text.get_height()//2))

    pygame.display.update()

def handle_movement_up(paddle_up, keys_pressed):
    if keys_pressed[pygame.K_a] and paddle_up.x - PADDLE_VEL > 0:
        paddle_up.x -= PADDLE_VEL
    if keys_pressed[pygame.K_d] and paddle_up.x + PADDLE_VEL + paddle_up.width < WIDTH:
        paddle_up.x += PADDLE_VEL

def handle_movement_down(paddle_down, keys_pressed):
    if keys_pressed[pygame.K_LEFT] and paddle_down.x - PADDLE_VEL > 0:
        paddle_down.x -= PADDLE_VEL
    if keys_pressed[pygame.K_RIGHT] and paddle_down.x + PADDLE_VEL + paddle_down.width < WIDTH:
        paddle_down.x += PADDLE_VEL

def handle_movement_ball_x(ball, ball_vel_x):
    ball.x += ball_vel_x

    if ball.x <= 0:
        ball_vel_x = -ball_vel_x
    if ball.x + ball.width >= WIDTH:
        ball_vel_x = -ball_vel_x
    
    ball.x += ball_vel_x

    return ball_vel_x

def handle_movement_ball_y(paddle_up, paddle_down, ball, ball_vel_y):
    ball.y += ball_vel_y

    if ball.colliderect(paddle_up) or ball.colliderect(paddle_down):
        ball_vel_y = -ball_vel_y

    return ball_vel_y

def return_def_position(paddle_up, paddle_down, ball):
    ball.x = WIDTH//2 - BALL_SIDE//2
    ball.y = HEIGHT//2 - BALL_SIDE//2
    paddle_up.x = WIDTH//2 - PADDLE_WIDTH//2
    paddle_up.y = 0 + PADDLE_HEIGHT
    paddle_down.x = WIDTH//2 - PADDLE_WIDTH//2
    paddle_down.y = HEIGHT - 2*PADDLE_HEIGHT

def point_made(ball, paddle_up, paddle_down):
    if ball.y <= 0 + PADDLE_HEIGHT:
        return_def_position(paddle_up, paddle_down, ball)
        pygame.event.post(pygame.event.Event(POINT_DOWN))
        pygame.time.delay(1000)
        return 'POINT_DOWN'
    if ball.y >= HEIGHT - 2*PADDLE_HEIGHT:
        return_def_position(paddle_up, paddle_down, ball)
        pygame.event.post(pygame.event.Event(POINT_UP))
        pygame.time.delay(1000)
        return 'POINT_UP'
    else:
        return 'GAME_GOING'
    

def write_vel():
    x = random.choice([-1, 1])
    y = random.choice([-1, 1])
    ball_vel_x = x * BALL_VEL
    ball_vel_y = y * BALL_VEL

    return ball_vel_x, ball_vel_y

def save_game_state_to_csv(ball, ball_vel_x, ball_vel_y, paddle_up, paddle_down, point, keys_pressed, filename):
    csv_file = filename
    header = ['ball_x', 'ball_y', 'ball_vel_x', 'ball_vel_y', 'paddle_up_x', 'paddle_up_y', 'paddle_up_vel', 'paddle_down_x', 'paddle_down_y', 'point', 'key_up', 'key_down']
    key_up = ''
    key_down = ''
    
    if keys_pressed[pygame.K_a]:
        key_up = 'a'
    if keys_pressed[pygame.K_d]:
        key_up = 'd'
    if keys_pressed[pygame.K_LEFT]:
        key_down = 'LEFT'
    if keys_pressed[pygame.K_RIGHT]:
        key_down = 'RIGHT'

    try:
        with open(csv_file, 'r') as f:
            pass
    except FileNotFoundError:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([ball.x, ball.y, ball_vel_x, ball_vel_y, paddle_up.x, paddle_up.y, PADDLE_VEL, paddle_down.x, paddle_down.y, point, key_up, key_down])

def handle_movement_model(paddle_up, action):
    if action == 0:
        if paddle_up.x - PADDLE_VEL > 0:
            paddle_up.x -= PADDLE_VEL
    if action == 1:
        if paddle_up.x + PADDLE_VEL + paddle_up.width < WIDTH:
            paddle_up.x += PADDLE_VEL


def main():
    start_time = time.time()
    paddle_up = pygame.Rect(WIDTH//2 - PADDLE_WIDTH//2, 0 + PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_down = pygame.Rect(WIDTH//2 - PADDLE_WIDTH//2, HEIGHT - 2*PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH//2 - BALL_SIDE//2, HEIGHT//2 - BALL_SIDE//2, BALL_SIDE, BALL_SIDE)
    ball_vel_x, ball_vel_y = write_vel()
    paddle_up_score = 0
    paddle_down_score = 0
    
    clock = pygame.time.Clock()
    run = True
    while run:
        point = 'GAME_GOING'
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == POINT_UP:
                paddle_up_score += 1
                ball_vel_x, ball_vel_y = write_vel()

            if event.type == POINT_DOWN:
                paddle_down_score += 1
                ball_vel_x, ball_vel_y = write_vel()

        paddle_up_score_text = pygame.font.SysFont("comicsans", 30).render(f"{paddle_up_score}", 1, RED)
        paddle_down_score_text = pygame.font.SysFont("comicsans", 30).render(f"{paddle_down_score}", 1, BLUE)
        
        keys_pressed = pygame.key.get_pressed()



        
        game_state = np.array([ball.x, ball.y, ball_vel_x, ball_vel_y, paddle_up.x, paddle_up.y, PADDLE_VEL, paddle_down.x, paddle_down.y])
        game_state = game_state.reshape(1, -1).astype('float32')
        predicted_action = model.predict(game_state)
        action = np.argmax(predicted_action)
        handle_movement_model(paddle_up, action)
        

        # handle_movement_up(paddle_up, keys_pressed)
        handle_movement_down(paddle_down, keys_pressed)
        handle_movement_ball_x(ball, ball_vel_x)
        ball_vel_x = handle_movement_ball_x(ball, ball_vel_x)
        handle_movement_ball_y(paddle_up, paddle_down, ball, ball_vel_y)
        ball_vel_y = handle_movement_ball_y(paddle_up, paddle_down, ball, ball_vel_y)
        point = point_made(ball, paddle_up, paddle_down)
        

        if time.time() - start_time >= 1:
            save_game_state_to_csv(ball, ball_vel_x, ball_vel_y, paddle_up, paddle_down, point, keys_pressed, filename='game_states.csv')
            start_time = time.time()  

        draw_window(paddle_up, paddle_down, ball, paddle_up_score_text, paddle_down_score_text)

if __name__ == "__main__":
    main()