import pygame
import sys
import random
import math
import os
from os import getenv
from os.path import expanduser, join
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Set screen size, title, and clock
width = 800
height = 600

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Don't get mad")
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Load font
font = pygame.font.Font(None, 36)

# Load background image
background_image = pygame.image.load("assets\\bg.png").convert()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\\player.png")
        
        # Set desired width and height
        desired_width = 70
        desired_height = 70

        # Scale the image to the desired dimensions
        self.image = pygame.transform.scale(self.image, (desired_width, desired_height))
        
        self.rect = self.image.get_rect()
        self.rect.x = 380
        self.rect.y = 520
        self.lives = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= 5
        if keys[K_RIGHT] and self.rect.x < 800 - self.rect.width:
            self.rect.x += 5

    def lose_life(self):
        self.lives -= 1

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=-1):
        super().__init__()
        self.image = pygame.Surface((5, 20))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = 10 * direction

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0 or self.rect.top > 600:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    speed_increase = 0.01
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\\enemy.png")
        
        # Set desired width and height
        desired_width = 70
        desired_height = 70

        # Scale the image to the desired dimensions
        self.image = pygame.transform.scale(self.image, (desired_width, desired_height))
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 760)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.randint(2, 5)
        self.speed_x = random.choice([-1, 1]) * random.randint(1, 3)
        self.dodge_threshold = 4
        self.dodge_speed = 10
        self.attack_probability = 0.01
        self.attack_speed = 70

    def update(self):
        # Increase speed over time
        self.speed_y += Enemy.speed_increase
        
        # Check if the enemy should attack the player
        if random.random() < self.attack_probability:
            if self.rect.x < player.rect.x:
                self.rect.x += self.attack_speed
            else:
                self.rect.x -= self.attack_speed

            self.rect.y += self.speed_y
        else:
            # Dodge bullets if the enemy's speed is above the dodge threshold
            if self.speed_y >= self.dodge_threshold:
                nearest_bullet = None
                min_distance = float("inf")

                for bullet in bullets:
                    distance = abs(bullet.rect.y - self.rect.y)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_bullet = bullet

                # If the nearest bullet is within a certain distance, move sideways to dodge it
                if nearest_bullet and min_distance < 100:
                    if self.rect.x < nearest_bullet.rect.x:
                        self.rect.x -= self.dodge_speed
                    else:
                        self.rect.x += self.dodge_speed
                else:
                    self.rect.y += self.speed_y
            else:
                self.rect.y += self.speed_y

        # Keep the enemy inside the screen bounds and change direction when hitting the borders
        if self.rect.x <= 0:
            self.rect.x = 0
            self.dodge_speed = abs(self.dodge_speed)
        elif self.rect.x >= 760:
            self.rect.x = 760
            self.dodge_speed = -abs(self.dodge_speed)

        # Reset the enemy position if it goes off the bottom of the screen
        if self.rect.y > 600:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, 760)

# smart enemy class - lmilodi
class SmartEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\\senemy.png")
        
        # Set desired width and height
        desired_width = 70
        desired_height = 70

        # Scale the image to the desired dimensions
        self.image = pygame.transform.scale(self.image, (desired_width, desired_height))

        self.rect = self.image.get_rect()
        
        self.speed_y = random.randint(3, 6)
        self.dodge_threshold = 0
        self.dodge_speed = 40  # Increase dodge speed
        self.attack_probability = 0.1  # Increase attack probability
        self.shoot_probability = 0.1  # Increase shoot probability
        self.last_shot = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > 1000:  # Shoot every 1 second (1000 ms)
            self.last_shot = now
            enemy_bullet = Bullet(self.rect.x + 17, self.rect.y, direction=1)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)

    def update(self):
        super().update()
        if random.random() < self.shoot_probability:
            self.shoot()

class AdvancedEnemy(SmartEnemy): # serghini
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\\aenemy.png")

        # Set desired width and height
        desired_width = 70
        desired_height = 70

        # Scale the image to the desired dimensions
        self.image = pygame.transform.scale(self.image, (desired_width, desired_height))

        self.rect = self.image.get_rect()
        
        self.prediction_window = 50

    def update(self):
        super().update()

        # Analyze player movement and predict their future position
        player_future_x = player.rect.x

        if abs(self.rect.x - player.rect.x) < self.prediction_window:
            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                player_future_x -= 5 * 10  # Predict the player's position in 10 frames
            elif keys[K_RIGHT]:
                player_future_x += 5 * 10  # Predict the player's position in 10 frames

            # Clamp the predicted position within screen boundaries
            player_future_x = max(0, min(player_future_x, 800 - self.rect.width))

            # Move towards the predicted player position
            if self.rect.x < player_future_x:
                self.rect.x += self.attack_speed
            else:
                self.rect.x -= self.attack_speed

# Boss enemy class - lkbichi
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\\boss.png")
        
        # Set desired width and height
        desired_width = 150
        desired_height = 150

        # Scale the image to the desired dimensions
        self.image = pygame.transform.scale(self.image, (desired_width, desired_height))
        
        self.rect = self.image.get_rect()
        self.rect.x = 325
        self.rect.y = -200
        self.lives = 40
        self.speed_y = 6
        self.speed_x = 8
        self.shoot_probability = 1
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        if self.rect.y < 50:
            self.rect.y += self.speed_y
        else:
            self.rect.x += self.speed_x
            if self.rect.left < 0 or self.rect.right > 800:
                self.speed_x *= -1

        # Shoot bullets
        if random.random() < self.shoot_probability:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > 400:  # Shoot every 0.5 seconds (500 ms)
            self.last_shot = now
            bullet1 = Bullet(self.rect.centerx, self.rect.bottom, direction=1)
            bullet2 = Bullet(self.rect.centerx, self.rect.bottom, direction=1)
            bullet2.speed_y = bullet1.speed_y * math.sin(math.radians(30))
            bullet2.speed_x = -bullet1.speed_y * math.cos(math.radians(30))
            bullet3 = Bullet(self.rect.centerx, self.rect.bottom, direction=1)
            bullet3.speed_y = bullet1.speed_y * math.sin(math.radians(30))
            bullet3.speed_x = bullet1.speed_y * math.cos(math.radians(30))
            
            all_sprites.add(bullet1, bullet2, bullet3)
            enemy_bullets.add(bullet1, bullet2, bullet3)

    def lose_life(self):
        self.lives -= 1

# Heart class
class Heart(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\\heart.png")
        
        # Set desired width and height
        desired_width = 30
        desired_height = 30

        # Scale the image to the desired dimensions
        self.image = pygame.transform.scale(self.image, (desired_width, desired_height))
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = random.randint(-height, -self.rect.height)
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > height:
            self.kill()

# Add boss enemy variable
boss_enemy = None
boss_spawned = False
boss_defeated = False

player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
hearts = pygame.sprite.Group()

for _ in range(10):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Initialize score
score = 0

# Load heart image
heart_image = pygame.Surface((20, 20))
heart_image.fill(RED)

def draw_hearts(lives):
    for i in range(lives):
        screen.blit(heart_image, (760 - i * 25, 10))

def show_home_screen():
    home_screen = True

    # Load the background image
    background_image = pygame.image.load("assets\\mbg.jpg")
    background_image = pygame.transform.scale(background_image, (width, height))

    # Set up the font and text
    font = pygame.font.Font(None, 36)
    start_button_text = font.render("Start", True, WHITE)
    exit_button_text = font.render("Exit", True, WHITE)

    # Create 'Welcome to the Game' text
    welcome_font = pygame.font.Font(None, 48)
    welcome_text = welcome_font.render("MeaW", True, WHITE)
    welcome_text_rect = welcome_text.get_rect(center=(width // 2, 100))

    # Create 'Start' and 'Exit' buttons
    start_button = pygame.Rect(325, 200, 150, 50)
    exit_button = pygame.Rect(325, 450, 150, 50)

    while home_screen:
        # Draw the background image
        screen.blit(background_image, (0, 0))

        # Draw 'Welcome to the Game' text
        screen.blit(welcome_text, welcome_text_rect)

        # Draw 'Start' and 'Exit' buttons
        pygame.draw.rect(screen, BLUE, start_button)
        pygame.draw.rect(screen, RED, exit_button)
        screen.blit(start_button_text, (start_button.x + 50, start_button.y + 10))
        screen.blit(exit_button_text, (exit_button.x + 50, exit_button.y + 10))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.collidepoint(mouse_pos):
                    home_screen = False
                elif exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

def show_game_over_screen(score):
    game_over = True

    # Create 'Restart' and 'Exit' buttons
    restart_button = pygame.Rect(325, 300, 150, 50)
    exit_button = pygame.Rect(325, 400, 150, 50)

    # Button text
    restart_button_text = font.render("Restart", True, WHITE)
    exit_button_text = font.render("Exit", True, WHITE)

    while game_over:
        screen.fill((0, 0, 0))

        # Display 'You lost' text and score
        game_over_text = font.render("You lost!", True, WHITE)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(game_over_text, (340, 200))
        screen.blit(score_text, (355, 250))

        # Draw 'Restart' and 'Exit' buttons
        pygame.draw.rect(screen, BLUE, restart_button)
        pygame.draw.rect(screen, RED, exit_button)
        screen.blit(restart_button_text, (restart_button.x + 45, restart_button.y + 10))
        screen.blit(exit_button_text, (exit_button.x + 50, exit_button.y + 10))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button.collidepoint(mouse_pos):
                    game_over = False
                elif exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

hscore = ''.join([getenv('APPDATA') , '\\high_score.txt'])
def load_high_score():
    try:
        with open(hscore, "r") as file:
            high_score = int(file.read())
    except FileNotFoundError:
        high_score = 0

    return high_score

def save_high_score(high_score):
    with open(hscore, "w") as file:
        file.write(str(high_score))

# Show home screen before starting the game
show_home_screen()

# Game loop
running = True
spawn_heart_time = pygame.time.get_ticks()
while running:
    clock.tick(60)
    current_time = pygame.time.get_ticks()
    if current_time - spawn_heart_time > 10000:  # 10 seconds (10000 ms)
        heart = Heart()
        all_sprites.add(heart)
        hearts.add(heart)
        spawn_heart_time = current_time

    # Load high score
    high_score = load_high_score()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                bullet = Bullet(player.rect.x + 17, player.rect.y)
                all_sprites.add(bullet)
                bullets.add(bullet)
    
    # Draw background
    screen.blit(background_image, (0, 0))
    
    # Draw sprites
    all_sprites.update()
    all_sprites.draw(screen)
    
    # Spawn boss enemy after reaching a certain score
    if score >= 40 and not boss_spawned:
        boss_enemy = BossEnemy()
        all_sprites.add(boss_enemy)
        boss_spawned = True

    # Check for bullet-boss collisions
    if boss_spawned and not boss_defeated:
        boss_hit = pygame.sprite.spritecollide(boss_enemy, bullets, True)
        for _ in boss_hit:
            boss_enemy.lose_life()
            if boss_enemy.lives <= 0:
                boss_defeated = True
                boss_enemy.kill()
                score += 10
    
    # Check for bullet-enemy collisions
    collisions = pygame.sprite.groupcollide(bullets, enemies, True, True)
    for collision in collisions:
        score += 1  # Increase score by 1 for each enemy hit

        if score >= 20:
            spawn_probability = 0.3  # Adjust the probability of spawning a SmartEnemy
            advanced_enemy_probability = 0.2  # Adjust the probability of spawning an AdvancedEnemy

            rand_value = random.random()
            if rand_value < advanced_enemy_probability:
                advanced_enemy = AdvancedEnemy()
                all_sprites.add(advanced_enemy)
                enemies.add(advanced_enemy)
            elif rand_value < spawn_probability:
                smart_enemy = SmartEnemy()
                all_sprites.add(smart_enemy)
                enemies.add(smart_enemy)
            else:
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
        else:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

    # Check for player-enemy collisions
    player_hit = pygame.sprite.spritecollide(player, enemies, False)
    for enemy in player_hit:
        player.lose_life()
        enemy.rect.y = random.randint(-100, -40)
        enemy.rect.x = random.randint(0, 760)
    
    # Check for bullet-player collisions
    player_hit_by_bullet = pygame.sprite.spritecollide(player, enemy_bullets, True)
    player_touching_heart = pygame.sprite.spritecollide(player, hearts, True)
    if player_touching_heart:
        player.lives += 1

    if player_hit_by_bullet:
        player.lose_life()

    # End the game if the player has no lives left
    if player.lives <= 0:
        show_game_over_screen(score)
        break

    all_sprites.draw(screen)

    # Display score
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Display high score
    high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
    screen.blit(high_score_text, (10, 40))

    # Draw hearts representing lives
    draw_hearts(player.lives)
    
    # Update and save high score
    if score > high_score:
        high_score = score
        save_high_score(high_score)

    pygame.display.flip()

# Restart the game
if __name__ == "__main__":
    import sys
    exec(open(sys.argv[0]).read())