import random
import math
import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, GRAY, PURPLE, ORANGE, DARK_GRAY, BROWN, CYAN

class FlyingEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_y = y
        self.width = 25
        self.height = 25
        self.speed = random.uniform(2, 4)
        self.health = 1
        self.sway_amplitude = random.uniform(30, 60)  # How much it sways up/down
        self.sway_frequency = random.uniform(0.02, 0.05)  # How fast it sways
        self.time_offset = random.uniform(0, 2 * math.pi)  # Random phase offset
        self.time = 0
        
    def update(self):
        self.x -= self.speed
        self.time += self.sway_frequency
        # Create swaying motion using sine wave
        self.y = self.start_y + self.sway_amplitude * math.sin(self.time + self.time_offset)
        
        # Keep within screen bounds
        self.y = max(50, min(SCREEN_HEIGHT - 150, self.y))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        # Draw main body (purple circle)
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)
        pygame.draw.circle(screen, PURPLE, (center_x, center_y), self.width // 2)
        
        # Draw wings (orange triangles)
        wing_size = 8
        # Left wing
        left_wing = [
            (center_x - wing_size, center_y),
            (center_x - wing_size - 10, center_y - wing_size),
            (center_x - wing_size - 10, center_y + wing_size)
        ]
        pygame.draw.polygon(screen, ORANGE, left_wing)
        
        # Right wing
        right_wing = [
            (center_x + wing_size, center_y),
            (center_x + wing_size + 10, center_y - wing_size),
            (center_x + wing_size + 10, center_y + wing_size)
        ]
        pygame.draw.polygon(screen, ORANGE, right_wing)
        
        # Draw eyes
        eye_size = 3
        pygame.draw.circle(screen, WHITE, (center_x - 5, center_y - 3), eye_size)
        pygame.draw.circle(screen, WHITE, (center_x + 5, center_y - 3), eye_size)
        pygame.draw.circle(screen, BLACK, (center_x - 5, center_y - 3), 1)
        pygame.draw.circle(screen, BLACK, (center_x + 5, center_y - 3), 1)
