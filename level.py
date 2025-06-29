import pygame
import random
from monsters import Enemy, BossEnemy, FlyingEnemy, JumpingBoss
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, GRAY, PURPLE, ORANGE, DARK_GRAY, BROWN, CYAN

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        rect = self.get_rect()
        pygame.draw.rect(screen, (101, 67, 33), rect)
        pygame.draw.rect(screen, (139, 69, 19), (self.x, self.y, self.width, 4))
        pygame.draw.rect(screen, (62, 39, 35), (self.x, self.y + self.height - 4, self.width, 4))

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.platforms = self._create_platforms()
        self.has_floor = self._has_floor()
        self.ground_y = SCREEN_HEIGHT - 100
        self.enemy_types = self._get_enemy_types()
        self.spawn_rates = self._get_spawn_rates()
        self.background_colors = self._get_background_colors()
        self.ground_color = self._get_ground_color()
        self.cloud_color = self._get_cloud_color()
        self.powerups_enabled = self._powerups_enabled()
        
    def _create_platforms(self):
        if self.level_number == 1:
            return [
                Platform(200, 400, 120, 20),
                Platform(400, 350, 100, 20),
            ]
        elif self.level_number == 2:
            return [
                Platform(300, 350, 150, 20),
                Platform(600, 250, 150, 20),
                Platform(150, 150, 150, 20),
            ]
        elif self.level_number == 3:
            return [
                Platform(200, 400, 120, 20),
                Platform(500, 300, 120, 20),
                Platform(100, 200, 120, 20),
                Platform(700, 150, 120, 20),
            ]
        elif self.level_number == 4:
            return [
                Platform(100, 450, 100, 20),
                Platform(300, 380, 120, 20),
                Platform(550, 300, 100, 20),
                Platform(750, 220, 120, 20),
                Platform(200, 150, 100, 20),
            ]
        elif self.level_number == 5:
            return [
                Platform(150, 400, 140, 20),
                Platform(400, 300, 140, 20),
                Platform(650, 200, 140, 20),
                Platform(250, 150, 140, 20),
            ]
        elif self.level_number == 6:
            return [
                Platform(50, 480, 120, 20),
                Platform(250, 380, 130, 20),
                Platform(450, 280, 140, 20),
                Platform(680, 380, 130, 20),
                Platform(830, 480, 120, 20),
            ]
        else:  # Level 7+
            return [
                Platform(150, 400, 140, 20),
                Platform(400, 300, 140, 20),
                Platform(650, 200, 140, 20),
                Platform(250, 150, 140, 20),
            ]
    
    def _has_floor(self):
        return self.level_number != 6
    
    def _get_enemy_types(self):
        """Returns dictionary of enemy types that can spawn in this level"""
        enemy_config = {
            'ground_enemies': False,
            'flying_enemies': False,
            'boss_enemies': False,
            'jumping_bosses': False
        }
        
        if self.level_number == 1:
            enemy_config['ground_enemies'] = True
        elif self.level_number == 2:
            enemy_config['ground_enemies'] = True
            enemy_config['flying_enemies'] = True
        elif self.level_number == 3:
            enemy_config['ground_enemies'] = True
            enemy_config['flying_enemies'] = True
            enemy_config['boss_enemies'] = True
        elif self.level_number == 4:
            enemy_config['ground_enemies'] = True
            enemy_config['jumping_bosses'] = True
        elif self.level_number == 5:
            enemy_config['boss_enemies'] = True
            enemy_config['jumping_bosses'] = True
        elif self.level_number == 6:
            enemy_config['flying_enemies'] = True
        else:  # Level 7+
            enemy_config['ground_enemies'] = True
            enemy_config['flying_enemies'] = True
            enemy_config['boss_enemies'] = True
            enemy_config['jumping_bosses'] = True
        
        return enemy_config
    
    def _get_spawn_rates(self):
        """Returns spawn delay times for different enemy types"""
        base_rates = {
            'enemy_spawn_delay': 2000,
            'flying_enemy_spawn_delay': 3000,
            'boss_enemy_spawn_delay': 8000,
            'jumping_boss_spawn_delay': 12000,
            'powerup_spawn_delay': 10000
        }
        
        if self.level_number == 6:
            base_rates['flying_enemy_spawn_delay'] = 1500
        if self.level_number == 5:
            base_rates['jumping_boss_spawn_delay'] = 3000
            base_rates['boss_enemy_spawn_delay'] = 3000
        
        return base_rates
    
    def _get_background_colors(self):
        """Returns background color configuration for this level"""
        if self.level_number == 1:
            return {'base_color': 135, 'color_type': 'bright_blue'}
        elif self.level_number == 2:
            return {'base_color': 100, 'color_type': 'blue_purple'}
        elif self.level_number == 3:
            return {'base_color': 80, 'color_type': 'dark_storm'}
        elif self.level_number == 4:
            return {'base_color': 60, 'color_type': 'apocalyptic'}
        elif self.level_number == 5:
            return {'base_color': 40, 'color_type': 'dark_apocalyptic'}
        elif self.level_number == 6:
            return {'base_color': 200, 'color_type': 'bright_sky'}
        else:  # Level 7+
            return {'base_color': 20, 'color_type': 'final_dark'}
    
    def _get_ground_color(self):
        """Returns ground color for this level"""
        if self.level_number == 1:
            return GREEN
        elif self.level_number == 2:
            return (80, 120, 80)
        elif self.level_number == 3:
            return (60, 80, 60)
        elif self.level_number == 4:
            return (40, 50, 40)
        elif self.level_number == 5:
            return (30, 30, 30)
        else:  # Level 7+
            return (20, 20, 20)
    
    def _get_cloud_color(self):
        """Returns cloud color for this level"""
        if self.level_number == 1:
            return WHITE
        elif self.level_number == 2:
            return (200, 200, 200)
        elif self.level_number == 3:
            return (150, 150, 150)
        elif self.level_number == 4:
            return (100, 100, 120)
        elif self.level_number == 5:
            return (80, 80, 100)
        elif self.level_number == 6:
            return (255, 255, 255)
        else:  # Level 7+
            return (60, 60, 80)
    
    def _powerups_enabled(self):
        """Returns whether power-ups spawn in this level"""
        return self.level_number >= 3
    
    def should_spawn_enemy_type(self, enemy_type):
        """Check if a specific enemy type should spawn in this level"""
        return self.enemy_types.get(enemy_type, False)
    
    def get_spawn_delay(self, spawn_type):
        """Get spawn delay for a specific spawn type"""
        return self.spawn_rates.get(spawn_type, 2000)
    
    def spawn_enemy(self, current_time, last_spawn_time):
        """Spawn a ground enemy if conditions are met"""
        if not self.should_spawn_enemy_type('ground_enemies'):
            return None, last_spawn_time
            
        spawn_delay = self.get_spawn_delay('enemy_spawn_delay')
        if current_time - last_spawn_time > spawn_delay:
            enemy_y = SCREEN_HEIGHT - 140
            enemy = Enemy(SCREEN_WIDTH, enemy_y)
            return enemy, current_time
        return None, last_spawn_time
    
    def spawn_flying_enemy(self, current_time, last_spawn_time):
        """Spawn a flying enemy if conditions are met"""
        if not self.should_spawn_enemy_type('flying_enemies'):
            return None, last_spawn_time
            
        spawn_delay = self.get_spawn_delay('flying_enemy_spawn_delay')
        if current_time - last_spawn_time > spawn_delay:
            if self.level_number == 6:
                enemy_y = random.randint(50, SCREEN_HEIGHT - 100)
            else:
                enemy_y = random.randint(100, SCREEN_HEIGHT - 200)
            flying_enemy = FlyingEnemy(SCREEN_WIDTH, enemy_y)
            return flying_enemy, current_time
        return None, last_spawn_time
    
    def spawn_boss_enemy(self, current_time, last_spawn_time):
        """Spawn a boss enemy if conditions are met"""
        if not self.should_spawn_enemy_type('boss_enemies'):
            return None, last_spawn_time
            
        spawn_delay = self.get_spawn_delay('boss_enemy_spawn_delay')
        if current_time - last_spawn_time > spawn_delay:
            enemy_y = random.randint(80, SCREEN_HEIGHT - 250)
            boss_enemy = BossEnemy(SCREEN_WIDTH, enemy_y)
            return boss_enemy, current_time
        return None, last_spawn_time
    
    def spawn_jumping_boss(self, current_time, last_spawn_time):
        """Spawn a jumping boss if conditions are met"""
        if not self.should_spawn_enemy_type('jumping_bosses'):
            return None, last_spawn_time
            
        spawn_delay = self.get_spawn_delay('jumping_boss_spawn_delay')
        if current_time - last_spawn_time > spawn_delay:
            enemy_y = SCREEN_HEIGHT - 200
            jumping_boss = JumpingBoss(SCREEN_WIDTH, enemy_y)
            return jumping_boss, current_time
        return None, last_spawn_time
    
    def draw_background(self, screen):
        """Draw the background for this level"""
        bg_config = self.background_colors
        base_color = bg_config['base_color']
        color_type = bg_config['color_type']
        
        sky_height = SCREEN_HEIGHT if not self.has_floor else SCREEN_HEIGHT - 100
        
        for y in range(sky_height):
            if color_type == 'bright_blue':
                color_intensity = int(base_color + (120 * y / sky_height))
                color = (min(255, color_intensity), min(255, color_intensity + 20), 255)
            elif color_type == 'blue_purple':
                color_intensity = int(base_color + (80 * y / sky_height))
                color = (min(200, color_intensity + 20), min(200, color_intensity), min(255, color_intensity + 40))
            elif color_type == 'dark_storm':
                color_intensity = int(base_color + (60 * y / sky_height))
                color = (min(150, color_intensity + 30), min(150, color_intensity), min(200, color_intensity + 20))
            elif color_type == 'apocalyptic':
                color_intensity = int(base_color + (40 * y / sky_height))
                color = (min(120, color_intensity + 40), min(100, color_intensity), min(150, color_intensity + 10))
            elif color_type == 'dark_apocalyptic':
                color_intensity = int(base_color + (30 * y / sky_height))
                color = (min(100, color_intensity + 50), min(80, color_intensity), min(120, color_intensity + 5))
            elif color_type == 'bright_sky':
                color_intensity = int(base_color + (50 * y / sky_height))
                color = (min(255, color_intensity - 50), min(255, color_intensity), 255)
            else:  # final_dark
                color_intensity = int(base_color + (20 * y / sky_height))
                color = (min(80, color_intensity + 60), min(60, color_intensity), min(100, color_intensity + 5))
                
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw ground if this level has a floor
        if self.has_floor:
            pygame.draw.rect(screen, self.ground_color, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        
        # Draw clouds
        cloud_positions = [(150, 80), (400, 60), (650, 90), (850, 70)]
        for cx, cy in cloud_positions:
            pygame.draw.circle(screen, self.cloud_color, (cx, cy), 30)
            pygame.draw.circle(screen, self.cloud_color, (cx - 20, cy), 25)
            pygame.draw.circle(screen, self.cloud_color, (cx + 20, cy), 25)
    
    def get_level_transition_text(self):
        """Returns text to display during level transition"""
        if self.level_number == 2:
            return {
                'title': 'LEVEL 2!',
                'warnings': ['Flying enemies incoming!'],
                'info': []
            }
        elif self.level_number == 3:
            return {
                'title': 'LEVEL 3!',
                'warnings': ['Boss birds with bombs!', 'They take 2 hits to kill!'],
                'info': ['Shotgun power-ups available!']
            }
        elif self.level_number == 4:
            return {
                'title': 'LEVEL 4!',
                'warnings': ['JUMPING MECH BOSSES!', 'They shoot HOMING MISSILES!', 'Takes 5 hits to destroy!'],
                'info': ['Shotgun power-ups still available!']
            }
        elif self.level_number == 5:
            return {
                'title': 'LEVEL 5!',
                'warnings': ['FINAL BOSS LEVEL!', 'ALL ENEMY TYPES ATTACKING!', 'Ground Enemies, Flying Enemies,', 'Boss Birds & Jumping Mechs!'],
                'info': ['All power-ups available!']
            }
        elif self.level_number == 6:
            return {
                'title': 'LEVEL 6!',
                'warnings': ['SKY LEVEL!', "NO FLOOR - DON'T FALL!", 'Only flying enemies attack!', 'Use platforms to stay airborne!'],
                'info': ['All power-ups still available!']
            }
        elif self.level_number == 7:
            return {
                'title': 'LEVEL 7!',
                'warnings': ['ULTIMATE FINAL LEVEL!', 'ALL ENEMY TYPES ATTACKING!', 'Ground Enemies, Flying Enemies,', 'Boss Birds & Jumping Mechs!'],
                'info': ['All power-ups available!']
            }
        else:
            return {
                'title': f'LEVEL {self.level_number}!',
                'warnings': ['ULTIMATE FINAL LEVEL!', 'ALL ENEMY TYPES ATTACKING!'],
                'info': ['All power-ups available!']
            }