import pygame
import random
import math

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 1)  # Set mixer to 44100 Hz, 16-bit signed, mono
pygame.init()
pygame.mixer.init()

# Window Setup
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Oof Perfected Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Game States
MAIN_MENU = 0
GAME = 1
CREDITS = 2
ACHIEVEMENTS = 3
QUIT = 4
current_state = MAIN_MENU

# Game Variables
paddle_width = 10
paddle_height = 80
ball_size = 15
paddle_speed = 5
ball_speed_x = 3
ball_speed_y = 3
player_paddle_y = HEIGHT // 2 - paddle_height // 2
opponent_paddle_y = HEIGHT // 2 - paddle_height // 2
ball_x = WIDTH // 2 - ball_size // 2
ball_y = HEIGHT // 2 - ball_size // 2
player_score = 0
opponent_score = 0

# Achievements
achievements = {
    "First Win": False,
    "Perfect Game": False,
    "Unstoppable": False,
    "Oof Master": False,
}

# Synthesized Sound functions
def generate_beep(frequency, duration, volume):
    sample_rate = 44100  # Standard sample rate
    samples = int(sample_rate * duration)
    beep_samples = bytearray()
    for i in range(samples):
        t = i / sample_rate
        sample = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
        sample = max(-32768, min(32767, sample))  # Ensure sample is in 16-bit range
        beep_samples += sample.to_bytes(2, byteorder='little', signed=True)
    sound = pygame.mixer.Sound(buffer=beep_samples)
    return sound

oof_sound = generate_beep(200, 0.2, 0.3)  # Generate an Oof sound

def reset_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y
    ball_x = WIDTH // 2 - ball_size // 2
    ball_y = HEIGHT // 2 - ball_size // 2
    ball_speed_x = random.choice([-3, 3])
    ball_speed_y = random.choice([-3, 3])

def handle_paddle_movement():
    global player_paddle_y
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_paddle_y > 0:
        player_paddle_y -= paddle_speed
    if keys[pygame.K_DOWN] and player_paddle_y < HEIGHT - paddle_height:
        player_paddle_y += paddle_speed

def handle_opponent_movement():
    global opponent_paddle_y
    if ball_y < opponent_paddle_y + paddle_height // 2 and opponent_paddle_y > 0:
        opponent_paddle_y -= 2
    if ball_y > opponent_paddle_y + paddle_height // 2 and opponent_paddle_y < HEIGHT - paddle_height:
        opponent_paddle_y += 2

def handle_ball_movement():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, player_score, opponent_score
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    if ball_y <= 0 or ball_y >= HEIGHT - ball_size:
        ball_speed_y *= -1

    if ball_x <= paddle_width + 10 and player_paddle_y <= ball_y <= player_paddle_y + paddle_height:
        ball_speed_x *= -1

    if ball_x >= WIDTH - paddle_width - ball_size - 10 and opponent_paddle_y <= ball_y <= opponent_paddle_y + paddle_height:
        ball_speed_x *= -1

    if ball_x < 0:
        opponent_score += 1
        oof_sound.play()
        reset_ball()
    elif ball_x > WIDTH:
        player_score += 1
        reset_ball()

def draw_text(text, x, y, font, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def main_menu():
    screen.fill(BLACK)
    draw_text("Oof Perfected Pong", WIDTH // 2, HEIGHT // 4, title_font, WHITE)

    menu_options = ["Start Game", "Credits", "Achievements", "Quit"]
    y_offset = HEIGHT // 2
    button_height = 40
    button_spacing = 10
    buttons = []
    for i, option in enumerate(menu_options):
        button_rect = pygame.Rect(WIDTH // 2 - 100, y_offset + i * (button_height + button_spacing), 200, button_height)
        buttons.append((button_rect, option))
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        draw_text(option, button_rect.centerx, button_rect.centery, font, WHITE)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return QUIT
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for rect, option in buttons:
                if rect.collidepoint(mouse_pos):
                    if option == "Start Game":
                        return GAME
                    elif option == "Credits":
                        return CREDITS
                    elif option == "Achievements":
                        return ACHIEVEMENTS
                    elif option == "Quit":
                        return QUIT
    return MAIN_MENU

def game_screen():
    global player_paddle_y, opponent_paddle_y, ball_x, ball_y, ball_speed_x, ball_speed_y, player_score, opponent_score

    screen.fill(BLACK)

    # Draw game elements
    player_paddle = pygame.Rect(10, player_paddle_y, paddle_width, paddle_height)
    opponent_paddle = pygame.Rect(WIDTH - paddle_width - 10, opponent_paddle_y, paddle_width, paddle_height)
    ball = pygame.Rect(ball_x, ball_y, ball_size, ball_size)

    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, opponent_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    # Draw scores
    draw_text(f"Player: {player_score}", WIDTH // 4, 20, font, WHITE)
    draw_text(f"Opponent: {opponent_score}", WIDTH * 3 // 4, 20, font, WHITE)

    # Move paddles and ball
    handle_paddle_movement()
    handle_opponent_movement()
    handle_ball_movement()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return QUIT
    return GAME

def credits_screen():
    screen.fill(BLACK)

    credits_text = [
        "Game Created By:",
        "",
        "John Doe: Lead Programmer",
        "Jane Smith: Artist & Designer",
        "Random Person: Sound Designer"
    ]

    y_offset = HEIGHT // 4
    for line in credits_text:
        draw_text(line, WIDTH // 2, y_offset, font, WHITE)
        y_offset += 40

    back_button_rect = pygame.Rect(WIDTH // 2 - 80, y_offset + 40, 160, 40)
    pygame.draw.rect(screen, WHITE, back_button_rect, 2)
    draw_text("Back to Menu", back_button_rect.centerx, back_button_rect.centery, font, WHITE)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return QUIT
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if back_button_rect.collidepoint(mouse_pos):
                return MAIN_MENU
    return CREDITS

def achievements_screen():
    screen.fill(BLACK)

    achievements_text = ["Achievements:"]
    for name, unlocked in achievements.items():
        status = "Unlocked" if unlocked else "Locked"
        achievements_text.append(f"- {name}: {status}")

    y_offset = HEIGHT // 4
    for line in achievements_text:
        draw_text(line, WIDTH // 2, y_offset, font, WHITE)
        y_offset += 40

    back_button_rect = pygame.Rect(WIDTH // 2 - 80, y_offset + 40, 160, 40)
    pygame.draw.rect(screen, WHITE, back_button_rect, 2)
    draw_text("Back to Menu", back_button_rect.centerx, back_button_rect.centery, font, WHITE)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return QUIT
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if back_button_rect.collidepoint(mouse_pos):
                return MAIN_MENU
    return ACHIEVEMENTS

# Game Loop
clock = pygame.time.Clock()

running = True
while running:
    if current_state == MAIN_MENU:
        current_state = main_menu()
    elif current_state == GAME:
        current_state = game_screen()
    elif current_state == CREDITS:
        current_state = credits_screen()
    elif current_state == ACHIEVEMENTS:
        current_state = achievements_screen()
    elif current_state == QUIT:
        running = False

    clock.tick(60)

pygame.quit()
