import pygame
import random
import math

from monsters import Enemy, BossEnemy, FlyingEnemy, JumpingBoss
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, GRAY, PURPLE, ORANGE, DARK_GRAY, BROWN, CYAN
# Initialize Pygame
pygame.init()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -20
        self.gravity = 0.8
        self.on_ground = False
        self.crouching = False
        self.last_shot = 0
        self.shoot_delay = 200  # milliseconds
        self.max_hp = 100
        self.hp = self.max_hp
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1000  # milliseconds
        self.has_shotgun = False
        self.shotgun_timer = 0
        self.shotgun_duration = 15000  # 15 seconds
        self.has_machine_gun = False
        self.machine_gun_timer = 0
        self.machine_gun_duration = 7000  # 7 seconds
        self.has_penetrator = False
        self.penetrator_timer = 0
        self.penetrator_duration = 12000  # 12 seconds
        
    def update(self, keys, platforms, level=1):
        # Handle invulnerability
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False
        
        # Handle shotgun power-up timer
        if self.has_shotgun:
            current_time = pygame.time.get_ticks()
            if current_time - self.shotgun_timer > self.shotgun_duration:
                self.has_shotgun = False
        
        # Handle machine gun power-up timer
        if self.has_machine_gun:
            current_time = pygame.time.get_ticks()
            if current_time - self.machine_gun_timer > self.machine_gun_duration:
                self.has_machine_gun = False
        
        # Handle penetrator power-up timer
        if self.has_penetrator:
            current_time = pygame.time.get_ticks()
            if current_time - self.penetrator_timer > self.penetrator_duration:
                self.has_penetrator = False
        
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
            
        # Jumping
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            
        # Crouching
        self.crouching = keys[pygame.K_DOWN]
        
        # Apply gravity
        self.vel_y += self.gravity
        
        # Update horizontal position
        self.x += self.vel_x
        
        # Check platform collisions for horizontal movement
        player_rect = self.get_rect()
        for platform in platforms:
            if player_rect.colliderect(platform.get_rect()):
                if self.vel_x > 0:  # Moving right
                    self.x = platform.x - self.width
                elif self.vel_x < 0:  # Moving left
                    self.x = platform.x + platform.width
        
        # Update vertical position
        self.y += self.vel_y
        
        # Check platform collisions for vertical movement
        player_rect = self.get_rect()
        self.on_ground = False
        
        for platform in platforms:
            if player_rect.colliderect(platform.get_rect()):
                if self.vel_y > 0:  # Falling down
                    self.y = platform.y - self.get_rect().height
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping up
                    self.y = platform.y + platform.height
                    self.vel_y = 0
        
        # Ground collision (no floor on level 6)
        if level != 6:
            ground_y = SCREEN_HEIGHT - 100
            if self.y + self.height >= ground_y:
                self.y = ground_y - self.height
                self.vel_y = 0
                self.on_ground = True
        else:
            # Level 6 has no floor - player dies if they fall off screen
            if self.y > SCREEN_HEIGHT:
                self.hp = 0  # Kill player if they fall off
            
        # Screen boundaries
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            
    def take_damage(self, damage):
        if not self.invulnerable:
            self.hp -= damage
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            return True
        return False
    
    def is_alive(self):
        return self.hp > 0
    
    def pickup_shotgun(self):
        self.has_shotgun = True
        self.shotgun_timer = pygame.time.get_ticks()
    
    def pickup_machine_gun(self):
        self.has_machine_gun = True
        self.machine_gun_timer = pygame.time.get_ticks()
    
    def pickup_penetrator(self):
        self.has_penetrator = True
        self.penetrator_timer = pygame.time.get_ticks()
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        
        # Determine shoot delay based on active power-ups
        effective_delay = self.shoot_delay
        if self.has_machine_gun:
            effective_delay = 20
        
        if current_time - self.last_shot > effective_delay:
            self.last_shot = current_time
            bullets = []
            
            if self.has_penetrator and not self.has_machine_gun:
                # Penetrator - shoot 2 large penetrating bullets with horizontal offset
                bullet_x1 = self.x + self.width
                bullet_x2 = self.x + self.width + 10  # Horizontal offset
                bullet_y1 = self.y + self.height // 2 - 8
                bullet_y2 = self.y + self.height // 2 + 8
                bullets.append(PenetratingBullet(bullet_x1, bullet_y1, 0))
                bullets.append(PenetratingBullet(bullet_x2, bullet_y2, 0))
            elif self.has_shotgun and not self.has_machine_gun:
                # Shotgun - shoot 5 bullets in a cone
                bullet_x = self.x + self.width
                bullet_y = self.y + self.height // 2
                
                # Center bullet
                bullets.append(Bullet(bullet_x, bullet_y, 0))
                bullets.append(Bullet(bullet_x, bullet_y, -15))
                bullets.append(Bullet(bullet_x, bullet_y, -5))
                bullets.append(Bullet(bullet_x, bullet_y, 5))
                bullets.append(Bullet(bullet_x, bullet_y, 15))
            else:
                # Normal single bullet (or machine gun single bullet)
                bullet_x = self.x + self.width
                bullet_y = self.y + self.height // 2
                bullets.append(Bullet(bullet_x, bullet_y, 0))
                
            return bullets
        return []
    
    def auto_shoot_machine_gun(self):
        """Automatically fires machine gun without needing spacebar"""
        if not self.has_machine_gun:
            return []
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > 10:  # Very fast automatic firing
            self.last_shot = current_time
            bullet_x = self.x + self.width
            bullet_y = self.y + self.height // 2
            return [Bullet(bullet_x, bullet_y, 0)]
        return []
        
    def get_rect(self):
        height = self.height // 2 if self.crouching else self.height
        y = self.y + (self.height - height)
        return pygame.Rect(self.x, y, self.width, height)
        
    def draw(self, screen):
        rect = self.get_rect()
        # Flash red when invulnerable
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            pygame.draw.rect(screen, (255, 100, 100), rect)
        else:
            # Change color based on active power-ups
            if self.has_machine_gun:
                color = RED  # Red for machine gun
            elif self.has_penetrator:
                color = (150, 50, 255)  # Purple for penetrator
            elif self.has_shotgun:
                color = CYAN  # Cyan for shotgun
            else:
                color = BLUE  # Default blue
            pygame.draw.rect(screen, color, rect)
        
        # Draw gun (different appearance based on active power-ups)
        gun_x = self.x + self.width
        gun_y = self.y + self.height // 2
        
        if self.has_machine_gun:
            gun_color = YELLOW  # Bright yellow for machine gun
            gun_width = 30
            gun_height = 10
        elif self.has_penetrator:
            gun_color = (200, 100, 255)  # Purple for penetrator
            gun_width = 28
            gun_height = 12
        elif self.has_shotgun:
            gun_color = ORANGE  # Orange for shotgun
            gun_width = 25
            gun_height = 8
        else:
            gun_color = BLACK  # Default black
            gun_width = 20
            gun_height = 6
            
        if self.has_penetrator:
            # Draw dual barrels for penetrator
            barrel_height = 4
            pygame.draw.rect(screen, gun_color, (gun_x, gun_y - 8, gun_width, barrel_height))
            pygame.draw.rect(screen, gun_color, (gun_x, gun_y + 4, gun_width, barrel_height))
        else:
            pygame.draw.rect(screen, gun_color, (gun_x, gun_y - gun_height//2, gun_width, gun_height))

class Bullet:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 4
        self.speed = 10
        self.angle = angle  # Angle in degrees
        self.vel_x = self.speed * math.cos(math.radians(angle))
        self.vel_y = self.speed * math.sin(math.radians(angle))
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.get_rect())

class PenetratingBullet:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 8
        self.speed = 4  # Slower than regular bullets
        self.angle = angle  # Angle in degrees
        self.vel_x = self.speed * math.cos(math.radians(angle))
        self.vel_y = self.speed * math.sin(math.radians(angle))
        self.enemies_hit = []  # Track enemies hit for penetration
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        # Draw as a larger, purple/violet bullet with glow effect
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)
        
        # Outer glow
        pygame.draw.ellipse(screen, (150, 50, 255), (self.x - 2, self.y - 2, self.width + 4, self.height + 4))
        # Main bullet
        pygame.draw.ellipse(screen, (200, 100, 255), self.get_rect())
        # Inner core
        pygame.draw.ellipse(screen, WHITE, (self.x + 4, self.y + 2, self.width - 8, self.height - 4))

class PowerUp:
    def __init__(self, x, y, power_type="shotgun"):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.power_type = power_type
        self.collected = False
        self.bob_timer = 0
        self.bob_amplitude = 5
        self.original_y = y
        
    def update(self):
        # Make the power-up bob up and down
        self.bob_timer += 0.1
        self.y = self.original_y + math.sin(self.bob_timer) * self.bob_amplitude
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        if not self.collected:
            center_x = int(self.x + self.width // 2)
            center_y = int(self.y + self.height // 2)
            
            if self.power_type == "shotgun":
                # Draw shotgun power-up
                # Outer glow
                for i in range(3):
                    glow_color = (100 + i * 50, 200 + i * 20, 255)
                    pygame.draw.circle(screen, glow_color, (center_x, center_y), 18 - i * 3)
                
                # Main icon (shotgun shape)
                pygame.draw.rect(screen, ORANGE, (center_x - 8, center_y - 3, 16, 6))
                pygame.draw.rect(screen, BROWN, (center_x - 12, center_y - 2, 4, 4))
                
                # "S" for shotgun
                font = pygame.font.Font(None, 20)
                text = font.render("S", True, WHITE)
                text_rect = text.get_rect(center=(center_x, center_y))
                screen.blit(text, text_rect)
                
            elif self.power_type == "machine_gun":
                # Draw machine gun power-up
                # Outer glow (red/yellow theme)
                for i in range(3):
                    glow_color = (255, 200 - i * 30, 50 + i * 20)
                    pygame.draw.circle(screen, glow_color, (center_x, center_y), 18 - i * 3)
                
                # Main icon (machine gun shape - longer barrel)
                pygame.draw.rect(screen, YELLOW, (center_x - 10, center_y - 2, 20, 4))
                pygame.draw.rect(screen, RED, (center_x - 12, center_y - 3, 4, 6))
                
                # Draw small bullets/ammo indicator
                for j in range(3):
                    bullet_x = center_x - 6 + j * 4
                    pygame.draw.circle(screen, WHITE, (bullet_x, center_y + 6), 1)
                
                # "M" for machine gun
                font = pygame.font.Font(None, 20)
                text = font.render("M", True, WHITE)
                text_rect = text.get_rect(center=(center_x, center_y))
                screen.blit(text, text_rect)
                
            elif self.power_type == "penetrator":
                # Draw penetrator power-up
                # Outer glow (purple/violet theme)
                for i in range(3):
                    glow_color = (150 + i * 30, 50 + i * 20, 255)
                    pygame.draw.circle(screen, glow_color, (center_x, center_y), 18 - i * 3)
                
                # Main icon (dual barrel shape)
                pygame.draw.rect(screen, (200, 100, 255), (center_x - 8, center_y - 4, 16, 3))
                pygame.draw.rect(screen, (200, 100, 255), (center_x - 8, center_y + 1, 16, 3))
                pygame.draw.rect(screen, (150, 50, 255), (center_x - 12, center_y - 3, 4, 6))
                
                # "P" for penetrator
                font = pygame.font.Font(None, 20)
                text = font.render("P", True, WHITE)
                text_rect = text.get_rect(center=(center_x, center_y))
                screen.blit(text, text_rect)

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        # Draw platform with a nice gradient effect
        rect = self.get_rect()
        pygame.draw.rect(screen, (101, 67, 33), rect)  # Brown color
        # Add highlight on top
        pygame.draw.rect(screen, (139, 69, 19), (self.x, self.y, self.width, 4))
        # Add shadow on bottom
        pygame.draw.rect(screen, (62, 39, 35), (self.x, self.y + self.height - 4, self.width, 4))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Side-Scrolling Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.player = Player(50, SCREEN_HEIGHT - 160)
        self.bullets = []
        self.enemies = []
        self.flying_enemies = []
        self.boss_enemies = []
        self.jumping_bosses = []
        self.homing_missiles = []
        self.bombs = []
        self.platforms = []
        self.powerups = []
        self.score = 0
        self.level = 1
        self.max_level_reached = 1
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 2000  # milliseconds
        self.flying_enemy_spawn_timer = 0
        self.flying_enemy_spawn_delay = 3000  # milliseconds
        self.boss_enemy_spawn_timer = 0
        self.boss_enemy_spawn_delay = 8000  # 8 seconds between boss enemies
        self.jumping_boss_spawn_timer = 0
        self.jumping_boss_spawn_delay = 12000  # 12 seconds between jumping bosses
        self.powerup_spawn_timer = 0
        self.powerup_spawn_delay = 10000  # 10 seconds between power-ups
        self.game_over = False
        self.level_transition = False
        self.level_transition_timer = 0
        
        # Create platforms for level 1
        self.create_platforms()
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        
    def create_platforms(self):
        if self.level == 1:
            # Level 1 platforms (original)
            platforms = [
                Platform(200, 400, 120, 20),
                Platform(400, 350, 100, 20),
            ]
        elif self.level == 2:
            # Level 2 platforms (3 platforms)
            platforms = [
                Platform(300, 350, 150, 20),
                Platform(600, 250, 150, 20),
                Platform(150, 150, 150, 20),
            ]
        elif self.level == 3:
            # Level 3 platforms (4 platforms)
            platforms = [
                Platform(200, 400, 120, 20),
                Platform(500, 300, 120, 20),
                Platform(100, 200, 120, 20),
                Platform(700, 150, 120, 20),
            ]
        elif self.level == 4:
            # Level 4 platforms (5 platforms - more vertical challenge)
            platforms = [
                Platform(100, 450, 100, 20),
                Platform(300, 380, 120, 20),
                Platform(550, 300, 100, 20),
                Platform(750, 220, 120, 20),
                Platform(200, 150, 100, 20),
            ]
        elif self.level == 5:
            # Level 5 platforms (4 platforms)
            platforms = [
                Platform(150, 400, 140, 20),
                Platform(400, 300, 140, 20),
                Platform(650, 200, 140, 20),
                Platform(250, 150, 140, 20),
            ]
        elif self.level == 6:
            # Level 6 - Sky Level: No floor, 5 platforms, only flying enemies
            platforms = [
                Platform(50, 480, 120, 20),   # Bottom left
                Platform(250, 380, 130, 20),  # Mid-left
                Platform(450, 280, 140, 20),  # Center
                Platform(680, 380, 130, 20),  # Mid-right
                Platform(830, 480, 120, 20),  # Bottom right
            ]
        else:  # Level 7+ - Final Boss Level with all enemies
            # Default platforms for levels beyond 6
            platforms = [
                Platform(150, 400, 140, 20),
                Platform(400, 300, 140, 20),
                Platform(650, 200, 140, 20),
                Platform(250, 150, 140, 20),
            ]
        self.platforms = platforms
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over and not self.level_transition:
                        bullets = self.player.shoot()
                        self.bullets.extend(bullets)
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()
                        
    def restart_game(self):
        self.player = Player(50, SCREEN_HEIGHT - 160)
        self.bullets = []
        self.enemies = []
        self.flying_enemies = []
        self.boss_enemies = []
        self.jumping_bosses = []
        self.homing_missiles = []
        self.bombs = []
        self.powerups = []
        self.score = self.max_level_reached * 100
        self.level = self.max_level_reached
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 2000
        self.flying_enemy_spawn_timer = 0
        self.flying_enemy_spawn_delay = 3000
        self.boss_enemy_spawn_timer = 0
        self.boss_enemy_spawn_delay = 8000
        self.jumping_boss_spawn_timer = 0
        self.jumping_boss_spawn_delay = 12000
        self.powerup_spawn_timer = 0
        self.powerup_spawn_delay = 10000
        self.game_over = False
        self.level_transition = False
        self.level_transition_timer = 0
        self.create_platforms()
        
    def check_level_progression(self):
        if self.score >= 2000 and self.level == 6:
            self.level = 7
            self.max_level_reached = max(self.max_level_reached, 7)
            self.level_transition = True
            self.level_transition_timer = pygame.time.get_ticks()
            self.create_platforms()
            # Clear existing enemies when transitioning
            self.enemies.clear()
            self.flying_enemies.clear()
            self.boss_enemies.clear()
            self.jumping_bosses.clear()
            self.homing_missiles.clear()
            self.bombs.clear()
            self.powerups.clear()
            # Restore player health for new level
            self.player.hp = min(self.player.max_hp, self.player.hp + 70)
        elif self.score >= 1500 and self.level == 5:
            self.level = 6
            self.max_level_reached = max(self.max_level_reached, 6)
            self.level_transition = True
            self.level_transition_timer = pygame.time.get_ticks()
            self.create_platforms()
            # Clear existing enemies when transitioning
            self.enemies.clear()
            self.flying_enemies.clear()
            self.boss_enemies.clear()
            self.jumping_bosses.clear()
            self.homing_missiles.clear()
            self.bombs.clear()
            self.powerups.clear()
            # Restore player health for new level
            self.player.hp = min(self.player.max_hp, self.player.hp + 65)
        elif self.score >= 1000 and self.level == 4:
            self.level = 5
            self.max_level_reached = max(self.max_level_reached, 5)
            self.level_transition = True
            self.level_transition_timer = pygame.time.get_ticks()
            self.create_platforms()
            # Clear existing enemies when transitioning
            self.enemies.clear()
            self.flying_enemies.clear()
            self.boss_enemies.clear()
            self.jumping_bosses.clear()
            self.homing_missiles.clear()
            self.bombs.clear()
            self.powerups.clear()
            # Restore player health for new level
            self.player.hp = min(self.player.max_hp, self.player.hp + 60)
        elif self.score >= 500 and self.level == 3:
            self.level = 4
            self.max_level_reached = max(self.max_level_reached, 4)
            self.level_transition = True
            self.level_transition_timer = pygame.time.get_ticks()
            self.create_platforms()
            # Clear existing enemies when transitioning
            self.enemies.clear()
            self.flying_enemies.clear()
            self.boss_enemies.clear()
            self.jumping_bosses.clear()
            self.homing_missiles.clear()
            self.bombs.clear()
            self.powerups.clear()
            # Restore player health for new level
            self.player.hp = min(self.player.max_hp, self.player.hp + 50)
        elif self.score >= 175 and self.level == 2:
            self.level = 3
            self.max_level_reached = max(self.max_level_reached, 3)
            self.level_transition = True
            self.level_transition_timer = pygame.time.get_ticks()
            self.create_platforms()
            # Clear existing enemies when transitioning
            self.enemies.clear()
            self.flying_enemies.clear()
            self.boss_enemies.clear()
            self.jumping_bosses.clear()
            self.homing_missiles.clear()
            self.bombs.clear()
            self.powerups.clear()
            # Restore player health for new level
            self.player.hp = min(self.player.max_hp, self.player.hp + 40)
        elif self.score >= 75 and self.level == 1:
            self.level = 2
            self.max_level_reached = max(self.max_level_reached, 2)
            self.level_transition = True
            self.level_transition_timer = pygame.time.get_ticks()
            self.create_platforms()
            # Clear existing enemies when transitioning
            self.enemies.clear()
            self.flying_enemies.clear()
            self.boss_enemies.clear()
            self.jumping_bosses.clear()
            self.homing_missiles.clear()
            self.bombs.clear()
            self.powerups.clear()
            # Restore player health for new level
            self.player.hp = min(self.player.max_hp, self.player.hp + 30)
            
    def spawn_powerup(self):
        if self.level < 3:  # Only spawn power-ups in level 3+
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.powerup_spawn_timer > self.powerup_spawn_delay:
            self.powerup_spawn_timer = current_time
            
            # Choose a random platform to spawn the power-up on
            if self.platforms:
                platform = random.choice(self.platforms)
                powerup_x = platform.x + platform.width // 2 - 15  # Center on platform
                powerup_y = platform.y - 35  # Above the platform
                
                # Randomly choose between shotgun, machine gun, and penetrator
                power_type = random.choice(["shotgun", "machine_gun", "penetrator"])
                powerup = PowerUp(powerup_x, powerup_y, power_type)
                self.powerups.append(powerup)
            
    def spawn_enemy(self):
        if self.level == 6:  # No regular enemies in level 6
            return
        elif self.level >= 7:  # Spawn regular enemies in level 7+ (final boss level)
            current_time = pygame.time.get_ticks()
            if current_time - self.enemy_spawn_timer > self.enemy_spawn_delay:
                self.enemy_spawn_timer = current_time
                enemy_y = SCREEN_HEIGHT - 140
                enemy = Enemy(SCREEN_WIDTH, enemy_y)
                self.enemies.append(enemy)
        else:
            current_time = pygame.time.get_ticks()
            if current_time - self.enemy_spawn_timer > self.enemy_spawn_delay:
                self.enemy_spawn_timer = current_time
                enemy_y = SCREEN_HEIGHT - 140
                enemy = Enemy(SCREEN_WIDTH, enemy_y)
                self.enemies.append(enemy)
            
    def spawn_flying_enemy(self):
        if self.level < 2 or self.level == 4:  # Only spawn flying enemies in level 2-3, 5, 6, and 7+
            return
        elif self.level == 6:  # Level 6 - Only flying enemies, more frequent spawning
            current_time = pygame.time.get_ticks()
            if current_time - self.flying_enemy_spawn_timer > self.flying_enemy_spawn_delay // 2:  # Spawn twice as fast
                self.flying_enemy_spawn_timer = current_time
                enemy_y = random.randint(50, SCREEN_HEIGHT - 100)  # Can spawn anywhere in vertical space
                flying_enemy = FlyingEnemy(SCREEN_WIDTH, enemy_y)
                self.flying_enemies.append(flying_enemy)
        elif self.level >= 7:  # Spawn flying enemies in level 7+ (final boss level)
            current_time = pygame.time.get_ticks()
            if current_time - self.flying_enemy_spawn_timer > self.flying_enemy_spawn_delay:
                self.flying_enemy_spawn_timer = current_time
                enemy_y = random.randint(100, SCREEN_HEIGHT - 200)
                flying_enemy = FlyingEnemy(SCREEN_WIDTH, enemy_y)
                self.flying_enemies.append(flying_enemy)
        else:
            current_time = pygame.time.get_ticks()
            if current_time - self.flying_enemy_spawn_timer > self.flying_enemy_spawn_delay:
                self.flying_enemy_spawn_timer = current_time
                enemy_y = random.randint(100, SCREEN_HEIGHT - 200)
                flying_enemy = FlyingEnemy(SCREEN_WIDTH, enemy_y)
                self.flying_enemies.append(flying_enemy)
            
    def spawn_boss_enemy(self):
        if self.level < 3 or self.level == 4:  # Only spawn boss enemies in level 3, 5,6, and 7+
            return
        elif self.level >= 7:  # Spawn boss enemies in level 7+ (final boss level)
            current_time = pygame.time.get_ticks()
            if current_time - self.boss_enemy_spawn_timer > self.boss_enemy_spawn_delay:
                self.boss_enemy_spawn_timer = current_time
                enemy_y = random.randint(80, SCREEN_HEIGHT - 250)
                boss_enemy = BossEnemy(SCREEN_WIDTH, enemy_y)
                self.boss_enemies.append(boss_enemy)
        elif self.level == 5:  # Level 5 boss enemies
            current_time = pygame.time.get_ticks()
            if current_time - self.boss_enemy_spawn_timer > self.boss_enemy_spawn_delay:
                self.boss_enemy_spawn_timer = current_time
                enemy_y = random.randint(80, SCREEN_HEIGHT - 250)
                boss_enemy = BossEnemy(SCREEN_WIDTH, enemy_y)
                self.boss_enemies.append(boss_enemy)
        else:  # Level 3 boss enemies
            current_time = pygame.time.get_ticks()
            if current_time - self.boss_enemy_spawn_timer > self.boss_enemy_spawn_delay:
                self.boss_enemy_spawn_timer = current_time
                enemy_y = random.randint(80, SCREEN_HEIGHT - 250)
                boss_enemy = BossEnemy(SCREEN_WIDTH, enemy_y)
                self.boss_enemies.append(boss_enemy)
            
    def spawn_jumping_boss(self):
        if self.level < 4 or self.level == 6:  # Only spawn jumping bosses in level 4, 5, and 7+
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.jumping_boss_spawn_timer > self.jumping_boss_spawn_delay:
            self.jumping_boss_spawn_timer = current_time
            enemy_y = SCREEN_HEIGHT - 200  # Start on ground
            jumping_boss = JumpingBoss(SCREEN_WIDTH, enemy_y)
            self.jumping_bosses.append(jumping_boss)
            
    def update(self):
        if self.game_over:
            return
            
        # Handle level transition
        if self.level_transition:
            current_time = pygame.time.get_ticks()
            if current_time - self.level_transition_timer > 2000:  # 3 second transition
                self.level_transition = False
            return
            
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms, self.level)
        
        # Automatic machine gun firing
        if self.player.has_machine_gun:
            auto_bullets = self.player.auto_shoot_machine_gun()
            self.bullets.extend(auto_bullets)
        
        # Check level progression
        self.check_level_progression()
        
        # Check if player is still alive
        if not self.player.is_alive():
            self.game_over = True
            return
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
                self.bullets.remove(bullet)
        
        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update()
            
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.x + enemy.width < 0:
                self.enemies.remove(enemy)
                
        # Update flying enemies
        for flying_enemy in self.flying_enemies[:]:
            flying_enemy.update()
            if flying_enemy.x + flying_enemy.width < 0:
                self.flying_enemies.remove(flying_enemy)
                
        # Update boss enemies and their bombs
        for boss_enemy in self.boss_enemies[:]:
            boss_enemy.update()
            if boss_enemy.x + boss_enemy.width < 0:
                self.boss_enemies.remove(boss_enemy)
            elif boss_enemy.can_drop_bomb():
                bomb = boss_enemy.drop_bomb()
                self.bombs.append(bomb)
                
        # Update bombs
        for bomb in self.bombs[:]:
            bomb.update()
            if bomb.y > SCREEN_HEIGHT:
                self.bombs.remove(bomb)
                
        # Update jumping bosses and their missiles
        for jumping_boss in self.jumping_bosses[:]:
            jumping_boss.update()
            if jumping_boss.x + jumping_boss.width < 0:
                self.jumping_bosses.remove(jumping_boss)
            elif jumping_boss.can_fire_missile():
                player_center_x = self.player.x + self.player.width // 2
                player_center_y = self.player.y + self.player.height // 2
                missile = jumping_boss.fire_missile(player_center_x, player_center_y)
                self.homing_missiles.append(missile)
                
        # Update homing missiles
        player_center_x = self.player.x + self.player.width // 2
        player_center_y = self.player.y + self.player.height // 2
        for missile in self.homing_missiles[:]:
            missile.update(player_center_x, player_center_y)
            if (missile.x < -50 or missile.x > SCREEN_WIDTH + 50 or 
                missile.y < -50 or missile.y > SCREEN_HEIGHT + 50 or 
                missile.is_expired()):
                self.homing_missiles.remove(missile)
                
        # Check player-powerup collisions
        player_rect = self.player.get_rect()
        for powerup in self.powerups[:]:
            if player_rect.colliderect(powerup.get_rect()) and not powerup.collected:
                powerup.collected = True
                self.powerups.remove(powerup)
                # Restore 25 hit points when picking up any power-up
                self.player.hp = min(self.player.max_hp, self.player.hp + 25)
                if powerup.power_type == "shotgun":
                    self.player.pickup_shotgun()
                elif powerup.power_type == "machine_gun":
                    self.player.pickup_machine_gun()
                elif powerup.power_type == "penetrator":
                    self.player.pickup_penetrator()
                
        # Check bullet-enemy collisions (ground enemies)
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    # Handle penetrating bullets differently
                    if isinstance(bullet, PenetratingBullet):
                        # Check if this enemy was already hit by this bullet
                        if enemy not in bullet.enemies_hit:
                            bullet.enemies_hit.append(enemy)
                            self.enemies.remove(enemy)
                            self.score += 10
                    else:
                        # Regular bullet - remove both bullet and enemy
                        self.bullets.remove(bullet)
                        self.enemies.remove(enemy)
                        self.score += 10
                        break
                    
        # Check bullet-flying enemy collisions
        for bullet in self.bullets[:]:
            for flying_enemy in self.flying_enemies[:]:
                if bullet.get_rect().colliderect(flying_enemy.get_rect()):
                    # Handle penetrating bullets differently
                    if isinstance(bullet, PenetratingBullet):
                        # Check if this enemy was already hit by this bullet
                        if flying_enemy not in bullet.enemies_hit:
                            bullet.enemies_hit.append(flying_enemy)
                            self.flying_enemies.remove(flying_enemy)
                            self.score += 15  # Flying enemies worth more points
                    else:
                        # Regular bullet - remove both bullet and enemy
                        self.bullets.remove(bullet)
                        self.flying_enemies.remove(flying_enemy)
                        self.score += 15  # Flying enemies worth more points
                        break
                    
        # Check bullet-boss enemy collisions
        for bullet in self.bullets[:]:
            for boss_enemy in self.boss_enemies[:]:
                if bullet.get_rect().colliderect(boss_enemy.get_rect()):
                    # Handle penetrating bullets differently
                    if isinstance(bullet, PenetratingBullet):
                        # Check if this enemy was already hit by this bullet
                        if boss_enemy not in bullet.enemies_hit:
                            bullet.enemies_hit.append(boss_enemy)
                            if boss_enemy.take_damage():  # Returns True if boss is killed
                                self.boss_enemies.remove(boss_enemy)
                                self.score += 50  # Boss enemies worth much more points
                    else:
                        # Regular bullet - remove bullet
                        self.bullets.remove(bullet)
                        if boss_enemy.take_damage():  # Returns True if boss is killed
                            self.boss_enemies.remove(boss_enemy)
                            self.score += 50  # Boss enemies worth much more points
                        break
                    
        # Check bullet-jumping boss collisions
        for bullet in self.bullets[:]:
            for jumping_boss in self.jumping_bosses[:]:
                if bullet.get_rect().colliderect(jumping_boss.get_rect()):
                    # Handle penetrating bullets differently
                    if isinstance(bullet, PenetratingBullet):
                        # Check if this enemy was already hit by this bullet
                        if jumping_boss not in bullet.enemies_hit:
                            bullet.enemies_hit.append(jumping_boss)
                            if jumping_boss.take_damage():  # Returns True if boss is killed
                                self.jumping_bosses.remove(jumping_boss)
                                self.score += 100  # Jumping bosses worth even more points
                    else:
                        # Regular bullet - remove bullet
                        self.bullets.remove(bullet)
                        if jumping_boss.take_damage():  # Returns True if boss is killed
                            self.jumping_bosses.remove(jumping_boss)
                            self.score += 100  # Jumping bosses worth even more points
                        break
                    
        # Check player-enemy collisions (ground enemies)
        player_rect = self.player.get_rect()
        for enemy in self.enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                if self.player.take_damage(15):
                    self.enemies.remove(enemy)
                    
        # Check player-flying enemy collisions
        for flying_enemy in self.flying_enemies[:]:
            if player_rect.colliderect(flying_enemy.get_rect()):
                if self.player.take_damage(20):  # Flying enemies do more damage
                    self.flying_enemies.remove(flying_enemy)
                    
        # Check player-boss enemy collisions
        for boss_enemy in self.boss_enemies[:]:
            if player_rect.colliderect(boss_enemy.get_rect()):
                if self.player.take_damage(25):  # Boss enemies do most damage
                    pass  # Don't remove boss enemy on collision
                    
        # Check player-bomb collisions
        for bomb in self.bombs[:]:
            if player_rect.colliderect(bomb.get_rect()):
                if self.player.take_damage(25):
                    self.bombs.remove(bomb)
                    
        # Check player-jumping boss collisions
        for jumping_boss in self.jumping_bosses[:]:
            if player_rect.colliderect(jumping_boss.get_rect()):
                if self.player.take_damage(30):  # Jumping bosses do most damage
                    pass  # Don't remove jumping boss on collision
                    
        # Check player-homing missile collisions
        for missile in self.homing_missiles[:]:
            if player_rect.colliderect(missile.get_rect()):
                if self.player.take_damage(10):
                    self.homing_missiles.remove(missile)
                
        # Spawn enemies and power-ups
        self.spawn_enemy()
        self.spawn_flying_enemy()
        self.spawn_boss_enemy()
        self.spawn_jumping_boss()
        self.spawn_powerup()
        
        # Increase difficulty over time
        if self.score > 0 and self.score % 100 == 0:
            self.enemy_spawn_delay = max(500, self.enemy_spawn_delay - 50)
            if self.level >= 2:
                self.flying_enemy_spawn_delay = max(1000, self.flying_enemy_spawn_delay - 100)
            if self.level >= 3:
                self.boss_enemy_spawn_delay = max(4000, self.boss_enemy_spawn_delay - 200)
            if self.level >= 4:
                self.jumping_boss_spawn_delay = max(6000, self.jumping_boss_spawn_delay - 300)
            if self.level >= 5:  # Extra difficulty scaling for final level
                self.enemy_spawn_delay = max(300, self.enemy_spawn_delay - 25)
                self.flying_enemy_spawn_delay = max(800, self.flying_enemy_spawn_delay - 50)
                self.boss_enemy_spawn_delay = max(3000, self.boss_enemy_spawn_delay - 100)
                self.jumping_boss_spawn_delay = max(5000, self.jumping_boss_spawn_delay - 150)
            
    def draw_background(self):
        # Sky gradient (different colors for different levels)
        if self.level == 1:
            base_color = 135
        elif self.level == 2:
            base_color = 100
        elif self.level == 3:
            base_color = 80  # Even darker for level 3
        elif self.level == 4:
            base_color = 60  # Very dark and ominous for level 4
        elif self.level == 5:
            base_color = 40  # Dark apocalyptic sky for level 5
        elif self.level == 6:
            base_color = 200  # Bright sky level - high altitude
        else:  # Level 7+
            base_color = 20  # Extremely dark apocalyptic sky for final levels
            
        # Level 6 has no ground, so draw sky for entire screen
        sky_height = SCREEN_HEIGHT if self.level == 6 else SCREEN_HEIGHT - 100
        for y in range(sky_height):
            if self.level == 1:
                color_intensity = int(base_color + (120 * y / sky_height))
                color = (min(255, color_intensity), min(255, color_intensity + 20), 255)
            elif self.level == 2:
                color_intensity = int(base_color + (80 * y / sky_height))
                color = (min(200, color_intensity + 20), min(200, color_intensity), min(255, color_intensity + 40))
            elif self.level == 3:  # Level 3 - very dark, stormy sky
                color_intensity = int(base_color + (60 * y / sky_height))
                color = (min(150, color_intensity + 30), min(150, color_intensity), min(200, color_intensity + 20))
            elif self.level == 4:  # Level 4 - apocalyptic sky
                color_intensity = int(base_color + (40 * y / sky_height))
                color = (min(120, color_intensity + 40), min(100, color_intensity), min(150, color_intensity + 10))
            elif self.level == 5:  # Level 5 - dark sky
                color_intensity = int(base_color + (30 * y / sky_height))
                color = (min(100, color_intensity + 50), min(80, color_intensity), min(120, color_intensity + 5))
            elif self.level == 6:  # Level 6 - bright sky level
                color_intensity = int(base_color + (50 * y / sky_height))
                color = (min(255, color_intensity - 50), min(255, color_intensity), 255)
            else:  # Level 7+ - extremely dark
                color_intensity = int(base_color + (20 * y / sky_height))
                color = (min(80, color_intensity + 60), min(60, color_intensity), min(100, color_intensity + 5))
                
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
            
        # Ground (no ground for level 6)
        if self.level != 6:
            if self.level == 1:
                ground_color = GREEN
            elif self.level == 2:
                ground_color = (80, 120, 80)  # Darker green for level 2
            elif self.level == 3:
                ground_color = (60, 80, 60)  # Even darker for level 3
            elif self.level == 4:
                ground_color = (40, 50, 40)  # Very dark, corrupted ground for level 4
            elif self.level == 5:
                ground_color = (30, 30, 30)  # Almost black, desolate ground for level 5
            else:  # Level 7+
                ground_color = (20, 20, 20)  # Extremely dark ground for final levels
                
            pygame.draw.rect(self.screen, ground_color, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        
        # Simple clouds
        cloud_positions = [(150, 80), (400, 60), (650, 90), (850, 70)]
        if self.level == 1:
            cloud_color = WHITE
        elif self.level == 2:
            cloud_color = (200, 200, 200)  # Grayer clouds for level 2
        elif self.level == 3:
            cloud_color = (150, 150, 150)  # Very dark clouds for level 3
        elif self.level == 4:
            cloud_color = (100, 100, 120)  # Ominous purplish clouds for level 4
        elif self.level == 5:
            cloud_color = (80, 80, 100)  # Very dark, menacing clouds for level 5
        elif self.level == 6:
            cloud_color = (255, 255, 255)  # Bright white clouds for sky level
        else:  # Level 7+
            cloud_color = (60, 60, 80)  # Extremely dark clouds for final levels
            
        for cx, cy in cloud_positions:
            pygame.draw.circle(self.screen, cloud_color, (cx, cy), 30)
            pygame.draw.circle(self.screen, cloud_color, (cx - 20, cy), 25)
            pygame.draw.circle(self.screen, cloud_color, (cx + 20, cy), 25)
            
    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        level_text = self.font.render(f"Level: {self.level}", True, BLACK)
        self.screen.blit(level_text, (10, 80))
        
        # Draw health bar
        hp_bar_width = 200
        hp_bar_height = 20
        hp_bar_x = 10
        hp_bar_y = 50
        
        # Background (red)
        pygame.draw.rect(self.screen, RED, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        
        # Health (green)
        health_width = int((self.player.hp / self.player.max_hp) * hp_bar_width)
        pygame.draw.rect(self.screen, GREEN, (hp_bar_x, hp_bar_y, health_width, hp_bar_height))
        
        # Border
        pygame.draw.rect(self.screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
        
        # HP text
        hp_text = pygame.font.Font(None, 24).render(f"HP: {self.player.hp}/{self.player.max_hp}", True, BLACK)
        self.screen.blit(hp_text, (hp_bar_x + hp_bar_width + 10, hp_bar_y))
        
        # Shotgun power-up indicator
        if self.player.has_shotgun:
            remaining_time = self.player.shotgun_duration - (pygame.time.get_ticks() - self.player.shotgun_timer)
            remaining_seconds = max(0, remaining_time // 1000)
            
            shotgun_text = pygame.font.Font(None, 28).render(f"SHOTGUN: {remaining_seconds}s", True, CYAN)
            self.screen.blit(shotgun_text, (10, 110))
            
            # Shotgun timer bar
            timer_bar_width = 150
            timer_bar_height = 10
            timer_bar_x = 10
            timer_bar_y = 135
            
            # Background
            pygame.draw.rect(self.screen, DARK_GRAY, (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height))
            
            # Timer
            timer_width = int((remaining_time / self.player.shotgun_duration) * timer_bar_width)
            pygame.draw.rect(self.screen, CYAN, (timer_bar_x, timer_bar_y, timer_width, timer_bar_height))
            
            # Border
            pygame.draw.rect(self.screen, BLACK, (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height), 2)
        
        # Machine gun power-up indicator
        if self.player.has_machine_gun:
            remaining_time = self.player.machine_gun_duration - (pygame.time.get_ticks() - self.player.machine_gun_timer)
            remaining_seconds = max(0, remaining_time // 1000)
            
            # Adjust position if shotgun is also active
            ui_y_offset = 160 if self.player.has_shotgun else 110
            
            machine_gun_text = pygame.font.Font(None, 28).render(f"MACHINE GUN: {remaining_seconds}s", True, RED)
            self.screen.blit(machine_gun_text, (10, ui_y_offset))
            
            # Machine gun timer bar
            timer_bar_width = 150
            timer_bar_height = 10
            timer_bar_x = 10
            timer_bar_y = ui_y_offset + 25
            
            # Background
            pygame.draw.rect(self.screen, DARK_GRAY, (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height))
            
            # Timer
            timer_width = int((remaining_time / self.player.machine_gun_duration) * timer_bar_width)
            pygame.draw.rect(self.screen, RED, (timer_bar_x, timer_bar_y, timer_width, timer_bar_height))
            
            # Border
            pygame.draw.rect(self.screen, BLACK, (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height), 2)
        
        # Penetrator gun power-up indicator
        if self.player.has_penetrator:
            remaining_time = self.player.penetrator_duration - (pygame.time.get_ticks() - self.player.penetrator_timer)
            remaining_seconds = max(0, remaining_time // 1000)
            
            # Adjust position if shotgun is also active
            ui_y_offset = 160 if self.player.has_penetrator else 110
            
            penetrator_text = pygame.font.Font(None, 28).render(f"Penetrator: {remaining_seconds}s", True, PURPLE)
            self.screen.blit(penetrator_text, (10, ui_y_offset))
            
            # Machine gun timer bar
            timer_bar_width = 150
            timer_bar_height = 10
            timer_bar_x = 10
            timer_bar_y = ui_y_offset + 25
            
            # Background
            pygame.draw.rect(self.screen, DARK_GRAY, (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height))
            
            # Timer
            timer_width = int((remaining_time / self.player.penetrator_duration) * timer_bar_width)
            pygame.draw.rect(self.screen, PURPLE, (timer_bar_x, timer_bar_y, timer_width, timer_bar_height))
            
            # Border
            pygame.draw.rect(self.screen, BLACK, (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height), 2)
        

        # Level transition screen
        if self.level_transition:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if self.level == 2:
                level_up_text = pygame.font.Font(None, 72).render("LEVEL 2!", True, YELLOW)
                text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
                self.screen.blit(level_up_text, text_rect)
                
                warning_text = self.font.render("Flying enemies incoming!", True, RED)
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(warning_text, warning_rect)
            elif self.level == 3:
                level_up_text = pygame.font.Font(None, 72).render("LEVEL 3!", True, YELLOW)
                text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
                self.screen.blit(level_up_text, text_rect)
                
                warning_text = self.font.render("Boss birds with bombs!", True, RED)
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
                self.screen.blit(warning_text, warning_rect)
                
                warning_text2 = pygame.font.Font(None, 28).render("They take 2 hits to kill!", True, ORANGE)
                warning_rect2 = warning_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(warning_text2, warning_rect2)
                
                powerup_text = pygame.font.Font(None, 32).render("Shotgun power-ups available!", True, CYAN)
                powerup_rect = powerup_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
                self.screen.blit(powerup_text, powerup_rect)
            elif self.level == 4:
                level_up_text = pygame.font.Font(None, 72).render("LEVEL 4!", True, YELLOW)
                text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
                self.screen.blit(level_up_text, text_rect)
                
                warning_text = self.font.render("JUMPING MECH BOSSES!", True, RED)
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
                self.screen.blit(warning_text, warning_rect)
                
                warning_text2 = pygame.font.Font(None, 28).render("They shoot HOMING MISSILES!", True, ORANGE)
                warning_rect2 = warning_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
                self.screen.blit(warning_text2, warning_rect2)
                
                warning_text3 = pygame.font.Font(None, 28).render("Takes 5 hits to destroy!", True, ORANGE)
                warning_rect3 = warning_text3.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
                self.screen.blit(warning_text3, warning_rect3)
                
                powerup_text = pygame.font.Font(None, 32).render("Shotgun power-ups still available!", True, CYAN)
                powerup_rect = powerup_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
                self.screen.blit(powerup_text, powerup_rect)
            elif self.level == 5:
                level_up_text = pygame.font.Font(None, 72).render("LEVEL 5!", True, YELLOW)
                text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
                self.screen.blit(level_up_text, text_rect)
                
                warning_text = pygame.font.Font(None, 48).render("FINAL BOSS LEVEL!", True, RED)
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
                self.screen.blit(warning_text, warning_rect)
                
                warning_text2 = pygame.font.Font(None, 28).render("ALL ENEMY TYPES ATTACKING!", True, ORANGE)
                warning_rect2 = warning_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
                self.screen.blit(warning_text2, warning_rect2)
                
                warning_text3 = pygame.font.Font(None, 28).render("Ground Enemies, Flying Enemies,", True, WHITE)
                warning_rect3 = warning_text3.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
                self.screen.blit(warning_text3, warning_rect3)
                
                warning_text4 = pygame.font.Font(None, 28).render("Boss Birds & Jumping Mechs!", True, WHITE)
                warning_rect4 = warning_text4.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 15))
                self.screen.blit(warning_text4, warning_rect4)
                
                powerup_text = pygame.font.Font(None, 32).render("All power-ups available!", True, CYAN)
                powerup_rect = powerup_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 45))
                self.screen.blit(powerup_text, powerup_rect)
            elif self.level == 6:
                level_up_text = pygame.font.Font(None, 72).render("LEVEL 6!", True, YELLOW)
                text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
                self.screen.blit(level_up_text, text_rect)
                
                warning_text = pygame.font.Font(None, 48).render("SKY LEVEL!", True, CYAN)
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
                self.screen.blit(warning_text, warning_rect)
                
                warning_text2 = pygame.font.Font(None, 32).render("NO FLOOR - DON'T FALL!", True, RED)
                warning_rect2 = warning_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
                self.screen.blit(warning_text2, warning_rect2)
                
                warning_text3 = pygame.font.Font(None, 28).render("Only flying enemies attack!", True, ORANGE)
                warning_rect3 = warning_text3.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
                self.screen.blit(warning_text3, warning_rect3)
                
                warning_text4 = pygame.font.Font(None, 28).render("Use platforms to stay airborne!", True, WHITE)
                warning_rect4 = warning_text4.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 15))
                self.screen.blit(warning_text4, warning_rect4)
                
                powerup_text = pygame.font.Font(None, 32).render("All power-ups still available!", True, CYAN)
                powerup_rect = powerup_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 45))
                self.screen.blit(powerup_text, powerup_rect)
            elif self.level == 7:
                level_up_text = pygame.font.Font(None, 72).render("LEVEL 7!", True, YELLOW)
                text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
                self.screen.blit(level_up_text, text_rect)
                
                warning_text = pygame.font.Font(None, 48).render("ULTIMATE FINAL LEVEL!", True, RED)
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
                self.screen.blit(warning_text, warning_rect)
                
                warning_text2 = pygame.font.Font(None, 28).render("ALL ENEMY TYPES ATTACKING!", True, ORANGE)
                warning_rect2 = warning_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
                self.screen.blit(warning_text2, warning_rect2)
                
                warning_text3 = pygame.font.Font(None, 28).render("Ground Enemies, Flying Enemies,", True, WHITE)
                warning_rect3 = warning_text3.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
                self.screen.blit(warning_text3, warning_rect3)
                
                warning_text4 = pygame.font.Font(None, 28).render("Boss Birds & Jumping Mechs!", True, WHITE)
                warning_rect4 = warning_text4.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 15))
                self.screen.blit(warning_text4, warning_rect4)
                
                powerup_text = pygame.font.Font(None, 32).render("All power-ups available!", True, CYAN)
                powerup_rect = powerup_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 45))
                self.screen.blit(powerup_text, powerup_rect)
            
            health_text = pygame.font.Font(None, 36).render("Health restored!", True, GREEN)
            health_rect = health_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
            self.screen.blit(health_text, health_rect)
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = pygame.font.Font(None, 72).render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(final_score_text, score_rect)
            
            level_reached_text = self.font.render(f"Level Reached: {self.level}", True, WHITE)
            level_rect = level_reached_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
            self.screen.blit(level_reached_text, level_rect)
            
            restart_text = pygame.font.Font(None, 36).render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
            self.screen.blit(restart_text, restart_rect)
        
        # Instructions
        instructions = [
            "Arrow Keys: Move & Jump",
            "Down: Crouch",
            "Space: Shoot"
        ]
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, BLACK)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 25))
            
    def draw(self):
        self.draw_background()
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw game objects
        self.player.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
            
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        for flying_enemy in self.flying_enemies:
            flying_enemy.draw(self.screen)
            
        for boss_enemy in self.boss_enemies:
            boss_enemy.draw(self.screen)
            
        for jumping_boss in self.jumping_bosses:
            jumping_boss.draw(self.screen)
            
        for missile in self.homing_missiles:
            missile.draw(self.screen)
            
        for bomb in self.bombs:
            bomb.draw(self.screen)
            
        self.draw_ui()
        
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()