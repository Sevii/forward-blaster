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


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.speed = random.uniform(1, 3)
        self.health = 1

    def update(self):
        self.x -= self.speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.get_rect())
        # Draw simple face
        eye_size = 4
        pygame.draw.circle(screen, WHITE, (int(self.x + 8), int(self.y + 10)), eye_size)
        pygame.draw.circle(
            screen, WHITE, (int(self.x + 22), int(self.y + 10)), eye_size
        )
