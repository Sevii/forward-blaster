import random
import math
import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, GRAY, PURPLE, ORANGE, DARK_GRAY, BROWN, CYAN


class HomingMissile:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.width = 12
        self.height = 6
        self.speed = 3
        self.target_x = target_x
        self.target_y = target_y
        self.homing_strength = 0.1  # How aggressively it homes in
        self.vel_x = 0
        self.vel_y = 0
        self.lifetime = 0
        self.max_lifetime = 4000  # 8 seconds before self-destruct
        
    def update(self, player_x, player_y):
        # Update target to current player position
        self.target_x = player_x
        self.target_y = player_y
        
        # Calculate direction to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            target_vel_x = (dx / distance) * self.speed
            target_vel_y = (dy / distance) * self.speed
            
            # Smoothly adjust velocity towards target
            self.vel_x += (target_vel_x - self.vel_x) * self.homing_strength
            self.vel_y += (target_vel_y - self.vel_y) * self.homing_strength
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Update lifetime
        self.lifetime += 16  # Assuming 60 FPS
        
    def is_expired(self):
        return self.lifetime >= self.max_lifetime
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        # Draw missile as a red triangle pointing towards movement direction
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)
        
        # Calculate angle based on velocity
        angle = math.atan2(self.vel_y, self.vel_x)
        
        # Draw main body
        pygame.draw.circle(screen, RED, (center_x, center_y), 4)
        
        # Draw nose pointing in direction of travel
        nose_length = 8
        nose_x = center_x + int(nose_length * math.cos(angle))
        nose_y = center_y + int(nose_length * math.sin(angle))
        pygame.draw.line(screen, ORANGE, (center_x, center_y), (nose_x, nose_y), 3)
        
        # Draw small exhaust trail
        trail_x = center_x - int(6 * math.cos(angle))
        trail_y = center_y - int(6 * math.sin(angle))
        pygame.draw.circle(screen, YELLOW, (trail_x, trail_y), 2)


class JumpingBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_y = y
        self.width = 80
        self.height = 60
        self.speed = 1.5
        self.health = 5  # Takes 5 hits to kill
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_power = -18
        self.on_ground = False
        self.jump_timer = 0
        self.jump_delay = random.uniform(2000, 4000)  # 2-4 seconds between jumps
        self.last_missile = 0
        self.missile_delay = random.uniform(3000, 5000)  # 3-5 seconds between missiles
        self.flash_timer = 0
        self.hit_flash = False
        self.ground_y = SCREEN_HEIGHT - 140
        
    def update(self):
        self.x -= self.speed
        
        # Apply gravity
        self.vel_y += self.gravity
        
        # Update vertical position
        self.y += self.vel_y
        
        # Ground collision
        if self.y + self.height >= self.ground_y:
            self.y = self.ground_y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Handle jumping
        current_time = pygame.time.get_ticks()
        if self.on_ground and current_time - self.jump_timer > self.jump_delay:
            self.vel_y = self.jump_power
            self.on_ground = False
            self.jump_timer = current_time
            self.jump_delay = random.uniform(2000, 4000)  # Reset jump delay
        
        # Handle hit flash
        if self.hit_flash:
            if current_time - self.flash_timer > 200:  # Flash for 200ms
                self.hit_flash = False
        
    def take_damage(self):
        self.health -= 1
        self.hit_flash = True
        self.flash_timer = pygame.time.get_ticks()
        return self.health <= 0
        
    def can_fire_missile(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_missile > self.missile_delay:
            self.last_missile = current_time
            self.missile_delay = random.uniform(3000, 5000)  # Reset delay
            return True
        return False
        
    def fire_missile(self, target_x, target_y):
        missile_x = self.x + self.width // 2
        missile_y = self.y + self.height // 2
        return HomingMissile(missile_x, missile_y, target_x, target_y)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        # Draw main body (large, intimidating boss)
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)
        
        # Choose color based on health and flash state
        if self.hit_flash:
            body_color = (255, 100, 100)  # Red flash when hit
        elif self.health <= 2:
            body_color = (150, 50, 50)  # Dark red when heavily damaged
        elif self.health <= 3:
            body_color = (120, 60, 60)  # Medium red when moderately damaged
        else:
            body_color = (100, 40, 40)  # Dark reddish-brown when healthy
            
        # Draw main body (large rectangle with rounded edges effect)
        pygame.draw.ellipse(screen, body_color, (self.x, self.y, self.width, self.height))
        
        # Draw mechanical legs/springs (to show jumping capability)
        leg_width = 8
        leg_height = 15
        left_leg_x = self.x + 15
        right_leg_x = self.x + self.width - 15 - leg_width
        leg_y = self.y + self.height - 5
        
        # Springs effect
        spring_color = DARK_GRAY
        pygame.draw.rect(screen, spring_color, (left_leg_x, leg_y, leg_width, leg_height))
        pygame.draw.rect(screen, spring_color, (right_leg_x, leg_y, leg_width, leg_height))
        
        # Draw coils on springs
        for i in range(3):
            coil_y = leg_y + i * 4
            pygame.draw.line(screen, GRAY, (left_leg_x, coil_y), (left_leg_x + leg_width, coil_y), 2)
            pygame.draw.line(screen, GRAY, (right_leg_x, coil_y), (right_leg_x + leg_width, coil_y), 2)
        
        # Draw missile launchers on shoulders
        launcher_size = 12
        left_launcher_x = self.x + 8
        right_launcher_x = self.x + self.width - 8 - launcher_size
        launcher_y = self.y + 10
        
        pygame.draw.rect(screen, BLACK, (left_launcher_x, launcher_y, launcher_size, launcher_size))
        pygame.draw.rect(screen, BLACK, (right_launcher_x, launcher_y, launcher_size, launcher_size))
        
        # Draw launcher barrels
        barrel_color = ORANGE
        pygame.draw.circle(screen, barrel_color, (left_launcher_x + launcher_size//2, launcher_y + launcher_size//2), 3)
        pygame.draw.circle(screen, barrel_color, (right_launcher_x + launcher_size//2, launcher_y + launcher_size//2), 3)
        
        # Draw menacing eyes
        eye_size = 6
        pygame.draw.circle(screen, RED, (center_x - 12, center_y - 8), eye_size)
        pygame.draw.circle(screen, RED, (center_x + 12, center_y - 8), eye_size)
        pygame.draw.circle(screen, BLACK, (center_x - 12, center_y - 8), 3)
        pygame.draw.circle(screen, BLACK, (center_x + 12, center_y - 8), 3)
        
        # Draw health indicator (small bars above boss)
        health_bar_width = self.width - 20
        health_bar_height = 6
        health_bar_x = self.x + 10
        health_bar_y = self.y - 15
        
        # Background (red)
        pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health (green)
        health_width = int((self.health / 5) * health_bar_width)
        pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, health_width, health_bar_height))
        
        # Border
        pygame.draw.rect(screen, BLACK, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
