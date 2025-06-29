import random
import math
import pygame

from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WHITE,
    BLACK,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    GRAY,
    PURPLE,
    ORANGE,
    DARK_GRAY,
    BROWN,
    CYAN,
)


class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 20
        self.speed_x = random.uniform(-1, 1)  # Slight horizontal drift
        self.speed_y = 2  # Slow falling speed
        self.rotation = 0

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rotation += 3  # Rotate as it falls

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        # Draw bomb as a dark circle with a fuse
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)
        pygame.draw.circle(screen, BLACK, (center_x, center_y), self.width // 2)
        pygame.draw.circle(screen, DARK_GRAY, (center_x, center_y), self.width // 2 - 2)

        # Draw fuse (small line sticking out)
        fuse_x = center_x + int(6 * math.cos(math.radians(self.rotation)))
        fuse_y = center_y + int(6 * math.sin(math.radians(self.rotation)))
        pygame.draw.line(screen, ORANGE, (center_x, center_y), (fuse_x, fuse_y), 2)


class BossEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_y = y
        self.width = 60
        self.height = 45
        self.speed = random.uniform(1, 2)  # Slower than regular flying enemies
        self.health = 2  # Takes 2 hits to kill
        self.sway_amplitude = random.uniform(40, 80)
        self.sway_frequency = random.uniform(0.01, 0.03)  # Slower sway
        self.time_offset = random.uniform(0, 2 * math.pi)
        self.time = 0
        self.last_bomb = 0
        self.bomb_delay = random.uniform(2000, 4000)  # 2-4 seconds between bombs
        self.flash_timer = 0
        self.hit_flash = False

    def update(self):
        self.x -= self.speed
        self.time += self.sway_frequency
        # Create swaying motion using sine wave
        self.y = self.start_y + self.sway_amplitude * math.sin(
            self.time + self.time_offset
        )

        # Keep within screen bounds
        self.y = max(50, min(SCREEN_HEIGHT - 200, self.y))

        # Handle hit flash
        if self.hit_flash:
            current_time = pygame.time.get_ticks()
            if current_time - self.flash_timer > 200:  # Flash for 200ms
                self.hit_flash = False

    def take_damage(self):
        self.health -= 1
        self.hit_flash = True
        self.flash_timer = pygame.time.get_ticks()
        return self.health <= 0

    def can_drop_bomb(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_bomb > self.bomb_delay:
            self.last_bomb = current_time
            self.bomb_delay = random.uniform(2000, 4000)  # Reset delay
            return True
        return False

    def drop_bomb(self):
        bomb_x = self.x + self.width // 2
        bomb_y = self.y + self.height
        return Bomb(bomb_x, bomb_y)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        # Draw main body (larger, darker bird)
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)

        # Choose color based on health and flash state
        if self.hit_flash:
            body_color = (255, 100, 100)  # Red flash when hit
        elif self.health == 1:
            body_color = (100, 50, 50)  # Darker red when damaged
        else:
            body_color = (80, 40, 40)  # Dark reddish-brown

        # Draw body (larger oval)
        pygame.draw.ellipse(
            screen, body_color, (self.x, self.y, self.width, self.height)
        )

        # Draw wings (larger, more menacing)
        wing_size = 15
        # Left wing
        left_wing = [
            (center_x - wing_size, center_y),
            (center_x - wing_size - 20, center_y - wing_size),
            (center_x - wing_size - 20, center_y + wing_size),
        ]
        pygame.draw.polygon(screen, DARK_GRAY, left_wing)

        # Right wing
        right_wing = [
            (center_x + wing_size, center_y),
            (center_x + wing_size + 20, center_y - wing_size),
            (center_x + wing_size + 20, center_y + wing_size),
        ]
        pygame.draw.polygon(screen, DARK_GRAY, right_wing)

        # Draw eyes (larger, more menacing)
        eye_size = 5
        pygame.draw.circle(screen, RED, (center_x - 8, center_y - 5), eye_size)
        pygame.draw.circle(screen, RED, (center_x + 8, center_y - 5), eye_size)
        pygame.draw.circle(screen, BLACK, (center_x - 8, center_y - 5), 2)
        pygame.draw.circle(screen, BLACK, (center_x + 8, center_y - 5), 2)

        # Draw beak (sharp, menacing)
        beak = [
            (center_x, center_y + 5),
            (center_x - 8, center_y + 15),
            (center_x + 8, center_y + 15),
        ]
        pygame.draw.polygon(screen, ORANGE, beak)
