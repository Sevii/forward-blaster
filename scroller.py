import pygame
import random
import math

from monsters import Enemy, BossEnemy, FlyingEnemy, JumpingBoss
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
from level import Level, Platform

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
        self.has_rain = False
        self.rain_timer = 0
        self.rain_duration = 10000  # 10 seconds

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

        # Handle rain power-up timer
        if self.has_rain:
            current_time = pygame.time.get_ticks()
            if current_time - self.rain_timer > self.rain_duration:
                self.has_rain = False

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

        # Ground collision (check if level has floor)
        if level != 6:  # Keep original logic for now, will be improved later
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

    def pickup_rain(self):
        self.has_rain = True
        self.rain_timer = pygame.time.get_ticks()

    def shoot(self):
        current_time = pygame.time.get_ticks()

        # Determine shoot delay based on active power-ups
        effective_delay = self.shoot_delay
        if self.has_machine_gun:
            effective_delay = 20

        if current_time - self.last_shot > effective_delay:
            self.last_shot = current_time
            bullets = []

            if self.has_rain and not self.has_machine_gun:
                # Rain - shoot 10 bullets falling from above, spread out more
                player_front_x = self.x + self.width + 10
                for i in range(15):
                    # Double the spacing (8 pixels apart instead of 4)
                    bullet_x = player_front_x + (i * 8)
                    bullet_y = -20  # Start above screen
                    bullets.append(RainBullet(bullet_x, bullet_y))
            elif self.has_penetrator and not self.has_machine_gun:
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
            pygame.draw.rect(
                screen, gun_color, (gun_x, gun_y - 8, gun_width, barrel_height)
            )
            pygame.draw.rect(
                screen, gun_color, (gun_x, gun_y + 4, gun_width, barrel_height)
            )
        else:
            pygame.draw.rect(
                screen,
                gun_color,
                (gun_x, gun_y - gun_height // 2, gun_width, gun_height),
            )


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
        pygame.draw.ellipse(
            screen,
            (150, 50, 255),
            (self.x - 2, self.y - 2, self.width + 4, self.height + 4),
        )
        # Main bullet
        pygame.draw.ellipse(screen, (200, 100, 255), self.get_rect())
        # Inner core
        pygame.draw.ellipse(
            screen, WHITE, (self.x + 4, self.y + 2, self.width - 8, self.height - 4)
        )


class RainBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 6
        self.height = 12
        self.speed = 8

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        # Draw as a blue/cyan falling bullet
        pygame.draw.ellipse(screen, CYAN, self.get_rect())
        # Add a white core
        core_rect = pygame.Rect(self.x + 1, self.y + 2, self.width - 2, self.height - 4)
        pygame.draw.ellipse(screen, WHITE, core_rect)


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
                    pygame.draw.circle(
                        screen, glow_color, (center_x, center_y), 18 - i * 3
                    )

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
                    pygame.draw.circle(
                        screen, glow_color, (center_x, center_y), 18 - i * 3
                    )

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
                    pygame.draw.circle(
                        screen, glow_color, (center_x, center_y), 18 - i * 3
                    )

                # Main icon (dual barrel shape)
                pygame.draw.rect(
                    screen, (200, 100, 255), (center_x - 8, center_y - 4, 16, 3)
                )
                pygame.draw.rect(
                    screen, (200, 100, 255), (center_x - 8, center_y + 1, 16, 3)
                )
                pygame.draw.rect(
                    screen, (150, 50, 255), (center_x - 12, center_y - 3, 4, 6)
                )

                # "P" for penetrator
                font = pygame.font.Font(None, 20)
                text = font.render("P", True, WHITE)
                text_rect = text.get_rect(center=(center_x, center_y))
                screen.blit(text, text_rect)

            elif self.power_type == "rain":
                # Draw rain power-up
                # Outer glow (blue/cyan theme)
                for i in range(3):
                    glow_color = (50 + i * 30, 150 + i * 30, 255)
                    pygame.draw.circle(
                        screen, glow_color, (center_x, center_y), 18 - i * 3
                    )

                # Main icon (rain drops falling)
                for j in range(4):
                    drop_x = center_x - 6 + j * 4
                    drop_y = center_y - 6 + j * 2
                    pygame.draw.ellipse(screen, CYAN, (drop_x, drop_y, 3, 8))

                # "R" for rain
                font = pygame.font.Font(None, 20)
                text = font.render("R", True, WHITE)
                text_rect = text.get_rect(center=(center_x, center_y + 4))
                screen.blit(text, text_rect)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Side-Scrolling Shooter")
        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player(50, SCREEN_HEIGHT - 160)
        self.bullets = []
        self.rain_bullets = []
        self.enemies = []
        self.flying_enemies = []
        self.boss_enemies = []
        self.jumping_bosses = []
        self.homing_missiles = []
        self.bombs = []
        self.powerups = []
        self.score = 0
        self.level_number = 1
        self.max_level_reached = 1
        self.enemy_spawn_timer = 0
        self.flying_enemy_spawn_timer = 0
        self.boss_enemy_spawn_timer = 0
        self.jumping_boss_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.game_over = False
        self.level_transition = False
        self.level_transition_timer = 0

        # Create level object
        self.current_level = Level(self.level_number)

        # Font for UI
        self.font = pygame.font.Font(None, 36)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over and not self.level_transition:
                        bullets = self.player.shoot()
                        # Separate rain bullets from regular bullets
                        for bullet in bullets:
                            if isinstance(bullet, RainBullet):
                                self.rain_bullets.append(bullet)
                            else:
                                self.bullets.append(bullet)
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()

    def restart_game(self):
        self.player = Player(50, SCREEN_HEIGHT - 160)
        self.bullets = []
        self.rain_bullets = []
        self.enemies = []
        self.flying_enemies = []
        self.boss_enemies = []
        self.jumping_bosses = []
        self.homing_missiles = []
        self.bombs = []
        self.powerups = []
        self.score = self.max_level_reached * 100
        self.level_number = self.max_level_reached
        self.enemy_spawn_timer = 0
        self.flying_enemy_spawn_timer = 0
        self.boss_enemy_spawn_timer = 0
        self.jumping_boss_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.game_over = False
        self.level_transition = False
        self.level_transition_timer = 0
        self.current_level = Level(self.level_number)

    def check_level_progression(self):
        level_thresholds = {1: 75, 2: 175, 3: 500, 4: 1000, 5: 1500, 6: 2000}
        health_bonuses = {2: 30, 3: 40, 4: 50, 5: 60, 6: 65, 7: 70}

        for level, threshold in level_thresholds.items():
            if self.score >= threshold and self.level_number == level:
                self.level_number = level + 1
                self.max_level_reached = max(self.max_level_reached, self.level_number)
                self.level_transition = True
                self.level_transition_timer = pygame.time.get_ticks()
                self.current_level = Level(self.level_number)
                # Clear existing enemies when transitioning
                self.enemies.clear()
                self.flying_enemies.clear()
                self.boss_enemies.clear()
                self.jumping_bosses.clear()
                self.homing_missiles.clear()
                self.bombs.clear()
                self.powerups.clear()
                self.rain_bullets.clear()
                # Restore player health for new level
                health_bonus = health_bonuses.get(self.level_number, 70)
                self.player.hp = min(self.player.max_hp, self.player.hp + health_bonus)
                # Reset player position to starting location
                self.player.x = 50
                self.player.y = SCREEN_HEIGHT - 160
                self.player.vel_x = 0
                self.player.vel_y = 0
                break

    def spawn_powerup(self):
        if not self.current_level.powerups_enabled:
            return

        current_time = pygame.time.get_ticks()
        spawn_delay = self.current_level.get_spawn_delay("powerup_spawn_delay")
        if current_time - self.powerup_spawn_timer > spawn_delay:
            self.powerup_spawn_timer = current_time

            # Choose a random platform to spawn the power-up on
            if self.current_level.platforms:
                platform = random.choice(self.current_level.platforms)
                powerup_x = platform.x + platform.width // 2 - 15  # Center on platform
                powerup_y = platform.y - 35  # Above the platform

                # Randomly choose between shotgun, machine gun, penetrator, and rain
                power_type = random.choice(
                    ["shotgun", "machine_gun", "penetrator", "rain"]
                )
                powerup = PowerUp(powerup_x, powerup_y, power_type)
                self.powerups.append(powerup)

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        enemy, self.enemy_spawn_timer = self.current_level.spawn_enemy(
            current_time, self.enemy_spawn_timer
        )
        if enemy:
            self.enemies.append(enemy)

    def spawn_flying_enemy(self):
        current_time = pygame.time.get_ticks()
        flying_enemy, self.flying_enemy_spawn_timer = (
            self.current_level.spawn_flying_enemy(
                current_time, self.flying_enemy_spawn_timer
            )
        )
        if flying_enemy:
            self.flying_enemies.append(flying_enemy)

    def spawn_boss_enemy(self):
        current_time = pygame.time.get_ticks()
        boss_enemy, self.boss_enemy_spawn_timer = self.current_level.spawn_boss_enemy(
            current_time, self.boss_enemy_spawn_timer
        )
        if boss_enemy:
            self.boss_enemies.append(boss_enemy)

    def spawn_jumping_boss(self):
        current_time = pygame.time.get_ticks()
        jumping_boss, self.jumping_boss_spawn_timer = (
            self.current_level.spawn_jumping_boss(
                current_time, self.jumping_boss_spawn_timer
            )
        )
        if jumping_boss:
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
        self.player.update(keys, self.current_level.platforms, self.level_number)

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

        # Update rain bullets
        for rain_bullet in self.rain_bullets[:]:
            rain_bullet.update()
            if rain_bullet.y > SCREEN_HEIGHT:
                self.rain_bullets.remove(rain_bullet)

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
            if (
                missile.x < -50
                or missile.x > SCREEN_WIDTH + 50
                or missile.y < -50
                or missile.y > SCREEN_HEIGHT + 50
                or missile.is_expired()
            ):
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
                elif powerup.power_type == "rain":
                    self.player.pickup_rain()

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
                            if (
                                boss_enemy.take_damage()
                            ):  # Returns True if boss is killed
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
                            if (
                                jumping_boss.take_damage()
                            ):  # Returns True if boss is killed
                                self.jumping_bosses.remove(jumping_boss)
                                self.score += (
                                    100  # Jumping bosses worth even more points
                                )
                    else:
                        # Regular bullet - remove bullet
                        self.bullets.remove(bullet)
                        if jumping_boss.take_damage():  # Returns True if boss is killed
                            self.jumping_bosses.remove(jumping_boss)
                            self.score += 100  # Jumping bosses worth even more points
                        break

        # Check rain bullet-enemy collisions (ground enemies)
        for rain_bullet in self.rain_bullets[:]:
            for enemy in self.enemies[:]:
                if rain_bullet.get_rect().colliderect(enemy.get_rect()):
                    self.rain_bullets.remove(rain_bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break

        # Check rain bullet-flying enemy collisions
        for rain_bullet in self.rain_bullets[:]:
            for flying_enemy in self.flying_enemies[:]:
                if rain_bullet.get_rect().colliderect(flying_enemy.get_rect()):
                    self.rain_bullets.remove(rain_bullet)
                    self.flying_enemies.remove(flying_enemy)
                    self.score += 15
                    break

        # Check rain bullet-boss enemy collisions
        for rain_bullet in self.rain_bullets[:]:
            for boss_enemy in self.boss_enemies[:]:
                if rain_bullet.get_rect().colliderect(boss_enemy.get_rect()):
                    self.rain_bullets.remove(rain_bullet)
                    if boss_enemy.take_damage():
                        self.boss_enemies.remove(boss_enemy)
                        self.score += 50
                    break

        # Check rain bullet-jumping boss collisions
        for rain_bullet in self.rain_bullets[:]:
            for jumping_boss in self.jumping_bosses[:]:
                if rain_bullet.get_rect().colliderect(jumping_boss.get_rect()):
                    self.rain_bullets.remove(rain_bullet)
                    if jumping_boss.take_damage():
                        self.jumping_bosses.remove(jumping_boss)
                        self.score += 100
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

    def draw_background(self):
        self.current_level.draw_background(self.screen)

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        level_text = self.font.render(f"Level: {self.level_number}", True, BLACK)
        self.screen.blit(level_text, (10, 80))

        # Draw health bar
        hp_bar_width = 200
        hp_bar_height = 20
        hp_bar_x = 10
        hp_bar_y = 50

        # Background (red)
        pygame.draw.rect(
            self.screen, RED, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height)
        )

        # Health (green)
        health_width = int((self.player.hp / self.player.max_hp) * hp_bar_width)
        pygame.draw.rect(
            self.screen, GREEN, (hp_bar_x, hp_bar_y, health_width, hp_bar_height)
        )

        # Border
        pygame.draw.rect(
            self.screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2
        )

        # HP text
        hp_text = pygame.font.Font(None, 24).render(
            f"HP: {self.player.hp}/{self.player.max_hp}", True, BLACK
        )
        self.screen.blit(hp_text, (hp_bar_x + hp_bar_width + 10, hp_bar_y))

        # Shotgun power-up indicator
        if self.player.has_shotgun:
            remaining_time = self.player.shotgun_duration - (
                pygame.time.get_ticks() - self.player.shotgun_timer
            )
            remaining_seconds = max(0, remaining_time // 1000)

            shotgun_text = pygame.font.Font(None, 28).render(
                f"SHOTGUN: {remaining_seconds}s", True, CYAN
            )
            self.screen.blit(shotgun_text, (10, 110))

            # Shotgun timer bar
            timer_bar_width = 150
            timer_bar_height = 10
            timer_bar_x = 10
            timer_bar_y = 135

            # Background
            pygame.draw.rect(
                self.screen,
                DARK_GRAY,
                (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height),
            )

            # Timer
            timer_width = int(
                (remaining_time / self.player.shotgun_duration) * timer_bar_width
            )
            pygame.draw.rect(
                self.screen,
                CYAN,
                (timer_bar_x, timer_bar_y, timer_width, timer_bar_height),
            )

            # Border
            pygame.draw.rect(
                self.screen,
                BLACK,
                (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height),
                2,
            )

        # Machine gun power-up indicator
        if self.player.has_machine_gun:
            remaining_time = self.player.machine_gun_duration - (
                pygame.time.get_ticks() - self.player.machine_gun_timer
            )
            remaining_seconds = max(0, remaining_time // 1000)

            # Adjust position if shotgun is also active
            ui_y_offset = 160 if self.player.has_shotgun else 110

            machine_gun_text = pygame.font.Font(None, 28).render(
                f"MACHINE GUN: {remaining_seconds}s", True, RED
            )
            self.screen.blit(machine_gun_text, (10, ui_y_offset))

            # Machine gun timer bar
            timer_bar_width = 150
            timer_bar_height = 10
            timer_bar_x = 10
            timer_bar_y = ui_y_offset + 25

            # Background
            pygame.draw.rect(
                self.screen,
                DARK_GRAY,
                (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height),
            )

            # Timer
            timer_width = int(
                (remaining_time / self.player.machine_gun_duration) * timer_bar_width
            )
            pygame.draw.rect(
                self.screen,
                RED,
                (timer_bar_x, timer_bar_y, timer_width, timer_bar_height),
            )

            # Border
            pygame.draw.rect(
                self.screen,
                BLACK,
                (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height),
                2,
            )

        # Penetrator gun power-up indicator
        if self.player.has_penetrator:
            remaining_time = self.player.penetrator_duration - (
                pygame.time.get_ticks() - self.player.penetrator_timer
            )
            remaining_seconds = max(0, remaining_time // 1000)

            # Adjust position if shotgun is also active
            ui_y_offset = 160 if self.player.has_penetrator else 110

            penetrator_text = pygame.font.Font(None, 28).render(
                f"Penetrator: {remaining_seconds}s", True, PURPLE
            )
            self.screen.blit(penetrator_text, (10, ui_y_offset))

            # Machine gun timer bar
            timer_bar_width = 150
            timer_bar_height = 10
            timer_bar_x = 10
            timer_bar_y = ui_y_offset + 25

            # Background
            pygame.draw.rect(
                self.screen,
                DARK_GRAY,
                (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height),
            )

            # Timer
            timer_width = int(
                (remaining_time / self.player.penetrator_duration) * timer_bar_width
            )
            pygame.draw.rect(
                self.screen,
                PURPLE,
                (timer_bar_x, timer_bar_y, timer_width, timer_bar_height),
            )

            # Border
            pygame.draw.rect(
                self.screen,
                BLACK,
                (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height),
                2,
            )

        # Rain power-up indicator
        if self.player.has_rain:
            remaining_time = self.player.rain_duration - (
                pygame.time.get_ticks() - self.player.rain_timer
            )
            remaining_seconds = max(0, remaining_time // 1000)

            # Calculate position based on active power-ups
            ui_y_offset = 110
            if self.player.has_shotgun:
                ui_y_offset += 50
            if self.player.has_machine_gun:
                ui_y_offset += 50
            if self.player.has_penetrator:
                ui_y_offset += 50

            rain_text = pygame.font.Font(None, 28).render(
                f"RAIN: {remaining_seconds}s", True, CYAN
            )
            self.screen.blit(rain_text, (10, ui_y_offset))

            # Rain timer bar
            timer_bar_width = 150
            timer_bar_height = 10
            timer_bar_x = 10
            timer_bar_y = ui_y_offset + 25

            # Background
            pygame.draw.rect(
                self.screen,
                DARK_GRAY,
                (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height),
            )

            # Timer
            timer_width = int(
                (remaining_time / self.player.rain_duration) * timer_bar_width
            )
            pygame.draw.rect(
                self.screen,
                CYAN,
                (timer_bar_x, timer_bar_y, timer_width, timer_bar_height),
            )

            # Border
            pygame.draw.rect(
                self.screen,
                BLACK,
                (timer_bar_x, timer_bar_y, timer_bar_width, timer_bar_height),
                2,
            )

        # Level transition screen
        if self.level_transition:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            transition_data = self.current_level.get_level_transition_text()

            level_up_text = pygame.font.Font(None, 72).render(
                transition_data["title"], True, YELLOW
            )
            text_rect = level_up_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)
            )
            self.screen.blit(level_up_text, text_rect)

            y_offset = -70
            for warning in transition_data["warnings"]:
                if "LEVEL!" in warning or "FINAL" in warning or "ULTIMATE" in warning:
                    font_size = 48
                    color = RED
                elif "SKY LEVEL!" in warning:
                    font_size = 48
                    color = CYAN
                elif "NO FLOOR" in warning:
                    font_size = 32
                    color = RED
                else:
                    font_size = 28
                    color = (
                        ORANGE if "hits" in warning or "MISSILES" in warning else WHITE
                    )

                warning_text = pygame.font.Font(None, font_size).render(
                    warning, True, color
                )
                warning_rect = warning_text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset)
                )
                self.screen.blit(warning_text, warning_rect)
                y_offset += 30

            for info in transition_data["info"]:
                info_text = pygame.font.Font(None, 32).render(info, True, CYAN)
                info_rect = info_text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset)
                )
                self.screen.blit(info_text, info_rect)
                y_offset += 30

            if False:  # Old hardcoded transition text (keeping as reference)
                pass

            health_text = pygame.font.Font(None, 36).render(
                "Health restored!", True, GREEN
            )
            health_rect = health_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
            )
            self.screen.blit(health_text, health_rect)

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = pygame.font.Font(None, 72).render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            )
            self.screen.blit(game_over_text, text_rect)

            final_score_text = self.font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            score_rect = final_score_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(final_score_text, score_rect)

            level_reached_text = self.font.render(
                f"Level Reached: {self.level_number}", True, WHITE
            )
            level_rect = level_reached_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
            )
            self.screen.blit(level_reached_text, level_rect)

            restart_text = pygame.font.Font(None, 36).render(
                "Press R to Restart", True, WHITE
            )
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
            )
            self.screen.blit(restart_text, restart_rect)

        # Instructions
        instructions = ["Arrow Keys: Move & Jump", "Down: Crouch", "Space: Shoot"]
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, BLACK)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 25))

    def draw(self):
        self.draw_background()

        # Draw platforms
        for platform in self.current_level.platforms:
            platform.draw(self.screen)

        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw game objects
        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for rain_bullet in self.rain_bullets:
            rain_bullet.draw(self.screen)

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
