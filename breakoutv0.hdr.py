import pygame
import random
import math

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 1)
pygame.init()
pygame.mixer.init()

# Window Setup
WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Breakout")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Game Variables
PADDLE_WIDTH = 60
PADDLE_HEIGHT = 10
PADDLE_Y = HEIGHT - 30
BALL_SIZE = 10
BRICK_WIDTH = 40
BRICK_HEIGHT = 20
BALL_SPEED_X = 8   # Adjusted for 30 fps
BALL_SPEED_Y = -8  # Adjusted for 30 fps
PADDLE_SPEED = 8
ROWS = 6
COLUMNS = WIDTH // BRICK_WIDTH

# Game State
running = True
paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = BALL_SPEED_X
ball_speed_y = BALL_SPEED_Y
bricks = []
for row in range(ROWS):
    for col in range(COLUMNS):
        brick_x = col * BRICK_WIDTH
        brick_y = row * BRICK_HEIGHT
        bricks.append(pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT))
score = 0

# --- NES Style Sound Generation ---
def generate_square_wave(frequency, duration, volume, duty_cycle=0.5):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    wave_samples = bytearray()
    for i in range(samples):
        t = i / sample_rate
        sample = int(volume * 32767 * (1 if (t * frequency) % 1 < duty_cycle else -1))
        sample = max(-32768, min(32767, sample))
        wave_samples += sample.to_bytes(2, byteorder='little', signed=True)
    return pygame.mixer.Sound(buffer=wave_samples)

def generate_triangle_wave(frequency, duration, volume):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    wave_samples = bytearray()
    for i in range(samples):
        t = i / sample_rate
        sample = int(volume * 32767 * (2 * abs(2*(t * frequency - math.floor(t*frequency + 0.5))) - 1))
        sample = max(-32768, min(32767, sample))
        wave_samples += sample.to_bytes(2, byteorder='little', signed=True)
    return pygame.mixer.Sound(buffer=wave_samples)
    
def generate_noise(duration, volume):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    noise_samples = bytearray()
    for _ in range(samples):
        sample = int(random.uniform(-1, 1) * volume * 32767)
        sample = max(-32768, min(32767, sample))
        noise_samples += sample.to_bytes(2, byteorder='little', signed=True)
    return pygame.mixer.Sound(buffer=noise_samples)
    
def generate_blip(frequency, duration, volume, decay_rate=0.8):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    wave_samples = bytearray()
    env_amp = 1
    for i in range(samples):
        t = i / sample_rate
        sample = int(volume * env_amp * 32767 * math.sin(2 * math.pi * frequency * t))
        sample = max(-32768, min(32767, sample))
        wave_samples += sample.to_bytes(2, byteorder='little', signed=True)
        env_amp *= decay_rate
    return pygame.mixer.Sound(buffer=wave_samples)

# --- Game Sounds ---
hit_sound = generate_blip(300, 0.05, 0.3, 0.6)
brick_sound = generate_square_wave(440, 0.05, 0.4, 0.25)
death_sound = generate_square_wave(100, 0.5, 0.6, 0.25)
wall_sound = generate_blip(600, 0.03, 0.2, 0.4)

def draw_text(text, x, y, font, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Game Font
font = pygame.font.Font(None, 36)

def handle_paddle_movement():
    global paddle_x
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= PADDLE_SPEED
    if keys[pygame.K_RIGHT] and paddle_x < WIDTH - PADDLE_WIDTH:
        paddle_x += PADDLE_SPEED

def handle_ball_movement():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, running, score
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Wall collision
    if ball_x <= 0 or ball_x >= WIDTH - BALL_SIZE:
        ball_speed_x *= -1
        wall_sound.play()
    if ball_y <= 0:
        ball_speed_y *= -1
        wall_sound.play()
    if ball_y >= HEIGHT:
        death_sound.play()
        running = False

    # Paddle collision
    paddle_rect = pygame.Rect(paddle_x, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball_rect = pygame.Rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE)
    if ball_rect.colliderect(paddle_rect) and ball_speed_y > 0:
        ball_speed_y *= -1
        hit_sound.play()

    # Brick collision
    for brick in list(bricks):
        if ball_rect.colliderect(brick):
            bricks.remove(brick)
            ball_speed_y *= -1
            score += 10
            brick_sound.play()
            break

# Game Loop
clock = pygame.time.Clock()
while running:
    screen.fill(BLACK)

    # Handle input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Game logic
    handle_paddle_movement()
    handle_ball_movement()

    # Draw everything
    pygame.draw.rect(screen, WHITE, (paddle_x, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))
    for brick in bricks:
        pygame.draw.rect(screen, BLUE, brick)
    draw_text(f"Score: {score}", WIDTH // 2, 20, font, WHITE)

    pygame.display.flip()
    clock.tick(30)  # Adjusted to 30 fps
pygame.quit()
