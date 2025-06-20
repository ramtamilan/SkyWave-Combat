import pygame
import math
import random
import sys
from pygame import gfxdraw

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
MOUNTAIN_BROWN = (139, 69, 19)
CLOUD_WHITE = (255, 255, 255)
PLANE_COLOR = (200, 0, 0)
ENEMY_COLOR = (50, 50, 200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wave-Based Flight Combat Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load sound effects
try:
    pygame.mixer.init()
    engine_sound = pygame.mixer.Sound("engine.wav")
    engine_sound.set_volume(0.3)
    engine_sound.play(-1)  # Loop indefinitely
    collect_sound = pygame.mixer.Sound("collect.wav")
    hit_sound = pygame.mixer.Sound("hit.wav")
    shoot_sound = pygame.mixer.Sound("shoot.wav")
except:
    print("Sound files not found. Game will run without sound.")

class Particle:
    def __init__(self, x, y, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.size = random.randint(1, 3)
        self.color = color
        self.lifetime = random.randint(10, 30)
        self.velocity_x = random.uniform(-1, 1)
        self.velocity_y = random.uniform(-1, 1)
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1
        
    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class Bullet:
    def __init__(self, x, y, angle, speed=10, friendly=True):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = 3
        self.friendly = friendly  # True if player bullet, False if enemy bullet
        
    def update(self):
        angle_rad = math.radians(self.angle)
        self.x += self.speed * math.cos(angle_rad)
        self.y -= self.speed * math.sin(angle_rad)
        
    def draw(self, surface):
        if self.friendly:
            color = YELLOW
        else:
            color = RED
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
        
    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)

class Airplane:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.angle = 0  # Angle in degrees
        self.speed = 3
        self.max_speed = 10
        self.size = 25
        self.trail = []
        self.particles = []
        self.bullets = []
        self.health = 100
        self.fuel = 100
        self.invincible = False
        self.invincible_timer = 0
        self.last_shot_time = 0
        self.shoot_delay = 300  # milliseconds between shots
        self.score = 0  # This is just for tracking internally, the Game class manages the actual score
        
    def draw(self, surface):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            color = (min(255, PLANE_COLOR[0] + 50), min(255, PLANE_COLOR[1] + 50), min(255, PLANE_COLOR[2] + 50), alpha)
            s = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (2, 2), 2)
            surface.blit(s, (pos[0] - 2, pos[1] - 2))
        
        # Draw particles
        for particle in self.particles:
            particle.update()
            particle.draw(surface)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.lifetime > 0]
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)
        
        # Calculate points for a triangle representing the plane
        angle_rad = math.radians(self.angle)
        
        # Nose of the plane
        nose_x = self.x + self.size * math.cos(angle_rad)
        nose_y = self.y - self.size * math.sin(angle_rad)
        
        # Right wing
        right_angle = angle_rad + 2.5  # Angle for right wing
        right_x = self.x + (self.size * 0.8) * math.cos(right_angle)
        right_y = self.y - (self.size * 0.8) * math.sin(right_angle)
        
        # Left wing
        left_angle = angle_rad - 2.5  # Angle for left wing
        left_x = self.x + (self.size * 0.8) * math.cos(left_angle)
        left_y = self.y - (self.size * 0.8) * math.sin(left_angle)
        
        # Tail points
        tail_x = self.x - (self.size * 0.5) * math.cos(angle_rad)
        tail_y = self.y + (self.size * 0.5) * math.sin(angle_rad)
        
        # Right tail
        right_tail_angle = angle_rad + 1.5
        right_tail_x = tail_x + (self.size * 0.4) * math.cos(right_tail_angle)
        right_tail_y = tail_y - (self.size * 0.4) * math.sin(right_tail_angle)
        
        # Left tail
        left_tail_angle = angle_rad - 1.5
        left_tail_x = tail_x + (self.size * 0.4) * math.cos(left_tail_angle)
        left_tail_y = tail_y - (self.size * 0.4) * math.sin(left_tail_angle)
        
        # Draw the plane body
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            # Flash if invincible
            plane_color = (255, 255, 255)
        else:
            plane_color = PLANE_COLOR
            
        # Main body
        pygame.draw.polygon(surface, plane_color, [
            (nose_x, nose_y), 
            (right_x, right_y), 
            (tail_x, tail_y),
            (left_x, left_y)
        ])
        
        # Tail
        pygame.draw.polygon(surface, plane_color, [
            (tail_x, tail_y),
            (right_tail_x, right_tail_y),
            (left_tail_x, left_tail_y)
        ])
        
        # Draw a small cockpit
        cockpit_x = self.x + (self.size * 0.3) * math.cos(angle_rad)
        cockpit_y = self.y - (self.size * 0.3) * math.sin(angle_rad)
        pygame.draw.circle(surface, BLACK, (int(cockpit_x), int(cockpit_y)), 4)
        
        # Add engine particles when moving fast
        if self.speed > 5 and random.random() < 0.3:
            for _ in range(2):
                particle_x = tail_x + random.uniform(-2, 2)
                particle_y = tail_y + random.uniform(-2, 2)
                particle_color = (200 + random.randint(0, 55), 
                                 100 + random.randint(0, 155), 
                                 0)
                self.particles.append(Particle(particle_x, particle_y, particle_color))
    
    def update(self, keys, obstacles, collectibles, mountains, enemies):
        # Handle rotation
        if keys[pygame.K_LEFT]:
            self.angle += 3
        if keys[pygame.K_RIGHT]:
            self.angle -= 3
            
        # Handle speed
        if keys[pygame.K_UP]:
            self.speed = min(self.max_speed, self.speed + 0.1)
            self.fuel = max(0, self.fuel - 0.05)  # Consume fuel
        if keys[pygame.K_DOWN]:
            self.speed = max(1, self.speed - 0.1)
            
        # Handle shooting
        if keys[pygame.K_SPACE]:
            self.shoot()
            
        # Move the plane based on its angle and speed
        angle_rad = math.radians(self.angle)
        self.x += self.speed * math.cos(angle_rad)
        self.y -= self.speed * math.sin(angle_rad)
        
        # Add position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:  # Limit trail length
            self.trail.pop(0)
        
        # Wrap around the screen
        if self.x > SCREEN_WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = SCREEN_WIDTH
            
        if self.y > SCREEN_HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = SCREEN_HEIGHT
            
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                
        # Check for bullet collisions with obstacles (stars)
        hit_obstacles = []
        for bullet in self.bullets[:]:
            for obstacle in obstacles[:]:
                # Calculate distance between bullet and obstacle
                distance = math.sqrt((bullet.x - obstacle.x) ** 2 + (bullet.y - obstacle.y) ** 2)
                if distance < (bullet.size + obstacle.size):
                    # Remove bullet and mark obstacle for removal
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if obstacle not in hit_obstacles:
                        hit_obstacles.append(obstacle)
                    break
                
        # Check for collisions with obstacles
        if not self.invincible:
            for obstacle in obstacles:
                if self.check_collision(obstacle):
                    self.health -= 10
                    self.invincible = True
                    self.invincible_timer = pygame.time.get_ticks()
                    try:
                        hit_sound.play()
                    except:
                        pass
                    break
                    
            # Check for collisions with mountains
            for mountain in mountains:
                if self.check_mountain_collision(mountain):
                    self.health -= 15
                    self.invincible = True
                    self.invincible_timer = pygame.time.get_ticks()
                    try:
                        hit_sound.play()
                    except:
                        pass
                    break
                    
            # Check for collisions with enemy bullets
            for enemy in enemies:
                for bullet in enemy.bullets[:]:
                    if self.check_bullet_collision(bullet):
                        self.health -= 5
                        enemy.bullets.remove(bullet)
                        self.invincible = True
                        self.invincible_timer = pygame.time.get_ticks()
                        try:
                            hit_sound.play()
                        except:
                            pass
        else:
            # Check if invincibility should end
            if pygame.time.get_ticks() - self.invincible_timer > 2000:  # 2 seconds
                self.invincible = False
                
        # Check for collectibles and return the ones collected
        collected_items = []
        for collectible in collectibles:
            if self.check_collision(collectible):
                collected_items.append(collectible)
                
        # Slowly decrease fuel
        self.fuel = max(0, self.fuel - 0.01)
        
        # If out of fuel, slow down
        if self.fuel <= 0:
            self.speed = max(1, self.speed - 0.05)
            
        # Check for hits on enemies
        for enemy in enemies[:]:
            for bullet in self.bullets[:]:
                if enemy.check_bullet_collision(bullet):
                    enemy.health -= 20
                    self.bullets.remove(bullet)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        break
    
        # Return list of hit obstacles and collected items
        return hit_obstacles, collected_items
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            angle_rad = math.radians(self.angle)
            bullet_x = self.x + (self.size + 5) * math.cos(angle_rad)
            bullet_y = self.y - (self.size + 5) * math.sin(angle_rad)
            self.bullets.append(Bullet(bullet_x, bullet_y, self.angle))
            self.last_shot_time = current_time
            try:
                shoot_sound.play()
            except:
                pass
    
    def check_collision(self, obj):
        # Simple distance-based collision detection
        distance = math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2)
        return distance < (self.size + obj.size)
        
    def check_bullet_collision(self, bullet):
        # Check if a bullet hits the plane
        distance = math.sqrt((self.x - bullet.x) ** 2 + (self.y - bullet.y) ** 2)
        return distance < (self.size + bullet.size)
        
    def check_mountain_collision(self, mountain):
        # Check if plane is over mountain and below its peak
        mountain_left = mountain.x - mountain.base_width // 2
        mountain_right = mountain.x + mountain.base_width // 2
        
        if mountain_left <= self.x <= mountain_right:
            # Calculate mountain height at this x position
            # Mountain is a triangle, so height decreases linearly from center
            distance_from_center = abs(self.x - mountain.x)
            ratio = distance_from_center / (mountain.base_width / 2)
            height_at_x = mountain.height * (1 - ratio)
            
            # Check if plane is below the mountain height at this position
            mountain_y_at_x = SCREEN_HEIGHT - height_at_x
            return self.y > mountain_y_at_x
        return False

class EnemyPlane:
    def __init__(self):
        # Start from a random edge of the screen
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = 0
            self.angle = random.randint(225, 315)
        elif side == 1:  # Right
            self.x = SCREEN_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.angle = random.randint(135, 225)
        elif side == 2:  # Bottom
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT
            self.angle = random.randint(45, 135)
        else:  # Left
            self.x = 0
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.angle = random.randint(-45, 45)
            
        self.speed = random.uniform(2, 4)
        self.size = 20
        self.health = 40
        self.bullets = []
        self.last_shot_time = 0
        self.shoot_delay = random.randint(1000, 3000)  # Random delay between shots
        self.change_direction_timer = 0
        self.direction_change_delay = random.randint(2000, 5000)
        
    def draw(self, surface):
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)
            
        # Calculate points for the enemy plane
        angle_rad = math.radians(self.angle)
        
        # Nose of the plane
        nose_x = self.x + self.size * math.cos(angle_rad)
        nose_y = self.y - self.size * math.sin(angle_rad)
        
        # Right wing
        right_angle = angle_rad + 2.5
        right_x = self.x + (self.size * 0.8) * math.cos(right_angle)
        right_y = self.y - (self.size * 0.8) * math.sin(right_angle)
        
        # Left wing
        left_angle = angle_rad - 2.5
        left_x = self.x + (self.size * 0.8) * math.cos(left_angle)
        left_y = self.y - (self.size * 0.8) * math.sin(left_angle)
        
        # Tail points
        tail_x = self.x - (self.size * 0.5) * math.cos(angle_rad)
        tail_y = self.y + (self.size * 0.5) * math.sin(angle_rad)
        
        # Draw the enemy plane
        pygame.draw.polygon(surface, ENEMY_COLOR, [
            (nose_x, nose_y), 
            (right_x, right_y), 
            (tail_x, tail_y),
            (left_x, left_y)
        ])
        
        # Draw a small cockpit
        cockpit_x = self.x + (self.size * 0.3) * math.cos(angle_rad)
        cockpit_y = self.y - (self.size * 0.3) * math.sin(angle_rad)
        pygame.draw.circle(surface, BLACK, (int(cockpit_x), int(cockpit_y)), 3)
        
        # Draw health bar above enemy
        health_width = int((self.health / 40) * self.size * 2)
        pygame.draw.rect(surface, RED, (self.x - self.size, self.y - self.size - 10, self.size * 2, 5))
        pygame.draw.rect(surface, GREEN, (self.x - self.size, self.y - self.size - 10, health_width, 5))
        
    def update(self, player):
        current_time = pygame.time.get_ticks()
        
        # Periodically change direction
        if current_time - self.change_direction_timer > self.direction_change_delay:
            self.change_direction_timer = current_time
            self.direction_change_delay = random.randint(2000, 5000)
            
            # Sometimes chase the player, sometimes move randomly
            if random.random() < 0.7:
                # Chase the player
                dx = player.x - self.x
                dy = player.y - self.y
                self.angle = (math.degrees(math.atan2(-dy, dx)) + 360) % 360
            else:
                # Move randomly
                self.angle = random.randint(0, 359)
        
        # Move the plane
        angle_rad = math.radians(self.angle)
        self.x += self.speed * math.cos(angle_rad)
        self.y -= self.speed * math.sin(angle_rad)
        
        # Wrap around the screen
        if self.x > SCREEN_WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = SCREEN_WIDTH
            
        if self.y > SCREEN_HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = SCREEN_HEIGHT
            
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                
        # Shoot at player
        if current_time - self.last_shot_time > self.shoot_delay:
            self.shoot(player)
            self.last_shot_time = current_time
            self.shoot_delay = random.randint(1000, 3000)
            
    def shoot(self, player):
        # Calculate angle to player
        dx = player.x - self.x
        dy = player.y - self.y
        angle_to_player = (math.degrees(math.atan2(-dy, dx)) + 360) % 360
        
        # Add some randomness to make it less accurate
        angle_to_player += random.uniform(-10, 10)
        
        bullet_x = self.x + (self.size + 5) * math.cos(math.radians(angle_to_player))
        bullet_y = self.y - (self.size + 5) * math.sin(math.radians(angle_to_player))
        self.bullets.append(Bullet(bullet_x, bullet_y, angle_to_player, speed=7, friendly=False))
        
    def check_bullet_collision(self, bullet):
        # Check if a bullet hits this enemy
        distance = math.sqrt((self.x - bullet.x) ** 2 + (self.y - bullet.y) ** 2)
        return distance < (self.size + bullet.size)

class Cloud:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT // 2)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(30, 60)
        self.circles = []
        
        # Generate random cloud shape
        num_circles = random.randint(3, 6)
        for _ in range(num_circles):
            offset_x = random.uniform(-self.size * 0.5, self.size * 0.5)
            offset_y = random.uniform(-self.size * 0.3, self.size * 0.3)
            size = random.uniform(self.size * 0.5, self.size)
            self.circles.append((offset_x, offset_y, size))
        
    def draw(self, surface):
        # Draw a cloud with multiple circles
        for offset_x, offset_y, size in self.circles:
            pygame.draw.circle(surface, CLOUD_WHITE, 
                              (int(self.x + offset_x), int(self.y + offset_y)), 
                              int(size))
        
    def update(self):
        self.x -= self.speed
        if self.x < -self.size * 2:
            self.x = SCREEN_WIDTH + self.size
            self.y = random.randint(0, SCREEN_HEIGHT // 2)

class Mountain:
    def __init__(self, x=None, height_factor=1.0):
        if x is None:
            self.x = random.randint(0, SCREEN_WIDTH)
        else:
            self.x = x
        self.base_width = random.randint(150, 300)
        self.height = random.randint(100, 200) * height_factor
        self.color = (
            random.randint(100, 139),  # R
            random.randint(50, 69),    # G
            random.randint(10, 19)     # B
        )
        
    def draw(self, surface):
        # Draw a triangle for the mountain
        points = [
            (self.x - self.base_width // 2, SCREEN_HEIGHT),
            (self.x, SCREEN_HEIGHT - self.height),
            (self.x + self.base_width // 2, SCREEN_HEIGHT)
        ]
        pygame.draw.polygon(surface, self.color, points)
        
        # Add a snow cap if the mountain is tall enough
        if self.height > 150:
            snow_points = [
                (self.x, SCREEN_HEIGHT - self.height),
                (self.x - self.base_width // 6, SCREEN_HEIGHT - self.height + 30),
                (self.x + self.base_width // 6, SCREEN_HEIGHT - self.height + 30)
            ]
            pygame.draw.polygon(surface, CLOUD_WHITE, snow_points)

class Obstacle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(15, 25)
        self.speed = random.uniform(1, 3)
        self.angle = 0
        self.rotation_speed = random.uniform(-2, 2)
        
    def draw(self, surface):
        # Draw a spinning obstacle (asteroid/bird)
        self.angle += self.rotation_speed
        angle_rad = math.radians(self.angle)
        
        points = []
        for i in range(5):  # 5-pointed star
            # Outer point
            outer_angle = angle_rad + i * 2 * math.pi / 5
            outer_x = self.x + self.size * math.cos(outer_angle)
            outer_y = self.y + self.size * math.sin(outer_angle)
            points.append((outer_x, outer_y))
            
            # Inner point
            inner_angle = angle_rad + (i + 0.5) * 2 * math.pi / 5
            inner_x = self.x + (self.size * 0.4) * math.cos(inner_angle)
            inner_y = self.y + (self.size * 0.4) * math.sin(inner_angle)
            points.append((inner_x, inner_y))
        
        pygame.draw.polygon(surface, (200, 100, 50), points)
        
    def update(self):
        self.x -= self.speed
        if self.x < -self.size:
            self.x = SCREEN_WIDTH + self.size
            self.y = random.randint(0, SCREEN_HEIGHT)

class Collectible:
    def __init__(self, type="fuel"):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = 15
        self.type = type  # "fuel", "health", or "speed"
        self.angle = 0
        
    def draw(self, surface):
        self.angle += 2
        if self.angle >= 360:
            self.angle = 0
            
        if self.type == "fuel":
            color = (255, 215, 0)  # Gold
        elif self.type == "health":
            color = (0, 255, 0)    # Green
        elif self.type == "speed":
            color = (0, 191, 255)  # Deep Sky Blue
            
        # Draw a spinning collectible
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
        
        # Draw an icon inside based on type
        if self.type == "fuel":
            # Draw an F
            font = pygame.font.SysFont(None, 20)
            text = font.render("F", True, BLACK)
            surface.blit(text, (self.x - 5, self.y - 8))
        elif self.type == "health":
            # Draw a +
            pygame.draw.rect(surface, BLACK, (self.x - 2, self.y - 7, 4, 14))
            pygame.draw.rect(surface, BLACK, (self.x - 7, self.y - 2, 14, 4))
        elif self.type == "speed":
            # Draw an S
            font = pygame.font.SysFont(None, 20)
            text = font.render("S", True, BLACK)
            surface.blit(text, (self.x - 5, self.y - 8))
        
    def update(self):
        # Collectibles don't move in this version
        pass
class Game:
    def __init__(self):
        self.airplane = Airplane()
        self.clouds = [Cloud() for _ in range(15)]
        self.mountains = []
        self.obstacles = []
        self.collectibles = []
        self.enemies = []
        self.score = 0
        self.high_score = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.game_over = False
        self.victory = False
        self.start_time = pygame.time.get_ticks()
        self.last_collectible_time = 0
        
        # Wave system
        self.current_wave = 1
        self.max_waves = 5
        self.wave_start_time = pygame.time.get_ticks()
        self.wave_duration = 30000  # 30 seconds per wave
        self.wave_transition = False
        self.transition_start_time = 0
        self.transition_duration = 3000  # 3 seconds between waves
        
        # Initialize first wave
        self.initialize_wave(self.current_wave)
        
        # Load high score if available
        try:
            with open("highscore.txt", "r") as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0
    
    def initialize_wave(self, wave_num):
        # Clear existing objects
        self.obstacles = []
        self.collectibles = []
        self.enemies = []
        
        # Reset wave timer
        self.wave_start_time = pygame.time.get_ticks()
        
        # Create mountains with increasing height based on wave
        self.mountains = []
        height_factor = 1.0 + (wave_num - 1) * 0.25  # Increase height by 25% each wave
        for x in range(0, SCREEN_WIDTH + 300, 200):
            self.mountains.append(Mountain(x, height_factor))
        
        # Add obstacles based on wave
        num_obstacles = 3 + wave_num
        for _ in range(num_obstacles):
            self.obstacles.append(Obstacle())
            
        # Add collectibles
        for _ in range(3):
            self.add_random_collectible()
            
        # Add enemies only in wave 5
        if wave_num == 5:
            for _ in range(3):
                self.enemies.append(EnemyPlane())
                
        print(f"Wave {wave_num} started!")
        
    def add_random_collectible(self):
        # Determine type based on probabilities
        rand = random.random()
        if rand < 0.5:
            collectible_type = "fuel"
        elif rand < 0.8:
            collectible_type = "health"
        else:
            collectible_type = "speed"
            
        self.collectibles.append(Collectible(collectible_type))
        
    def draw(self, surface):
        # Draw sky with gradient
        for y in range(0, SCREEN_HEIGHT):
            # Calculate color gradient from top to bottom
            t = y / SCREEN_HEIGHT
            r = int((1-t) * 135 + t * 65)
            g = int((1-t) * 206 + t * 105)
            b = int((1-t) * 235 + t * 225)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(surface)
        
        # Draw ground
        pygame.draw.rect(surface, GROUND_GREEN, (0, SCREEN_HEIGHT * 3//4, SCREEN_WIDTH, SCREEN_HEIGHT//4))
        
        # Draw mountains
        for mountain in self.mountains:
            mountain.draw(surface)
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(surface)
            
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(surface)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface)
        
        # Draw airplane
        self.airplane.draw(surface)
        
        # Draw HUD
        self.draw_hud(surface)
        
        # Draw wave transition
        if self.wave_transition:
            self.draw_wave_transition(surface)
        
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over(surface)
            
        # Draw victory screen if needed
        if self.victory:
            self.draw_victory(surface)
        
    def draw_hud(self, surface):
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        surface.blit(score_text, (10, 10))
        
        # Draw high score
        high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, BLACK)
        surface.blit(high_score_text, (10, 50))
        
        # Draw speed
        speed_text = self.font.render(f"Speed: {self.airplane.speed:.1f}", True, BLACK)
        surface.blit(speed_text, (10, 80))
        
        # Draw wave info
        wave_text = self.font.render(f"Wave: {self.current_wave}/{self.max_waves}", True, BLACK)
        surface.blit(wave_text, (SCREEN_WIDTH // 2 - 60, 10))
        
        # Draw wave timer
        if not self.wave_transition and not self.game_over and not self.victory:
            elapsed = pygame.time.get_ticks() - self.wave_start_time
            remaining = max(0, self.wave_duration - elapsed)
            seconds = remaining // 1000
            timer_text = self.font.render(f"Time: {seconds}s", True, BLACK)
            surface.blit(timer_text, (SCREEN_WIDTH // 2 - 40, 50))
        
        # Draw health bar
        pygame.draw.rect(surface, BLACK, (SCREEN_WIDTH - 210, 10, 200, 20), 1)
        health_width = int((self.airplane.health / 100) * 198)
        pygame.draw.rect(surface, (255, 0, 0), (SCREEN_WIDTH - 209, 11, health_width, 18))
        health_text = self.small_font.render("Health", True, BLACK)
        surface.blit(health_text, (SCREEN_WIDTH - 270, 10))
        
        # Draw fuel bar
        pygame.draw.rect(surface, BLACK, (SCREEN_WIDTH - 210, 40, 200, 20), 1)
        fuel_width = int((self.airplane.fuel / 100) * 198)
        pygame.draw.rect(surface, (255, 215, 0), (SCREEN_WIDTH - 209, 41, fuel_width, 18))
        fuel_text = self.small_font.render("Fuel", True, BLACK)
        surface.blit(fuel_text, (SCREEN_WIDTH - 270, 40))
        
        # Draw enemy count in wave 5
        if self.current_wave == 5:
            enemy_text = self.small_font.render(f"Enemies: {len(self.enemies)}", True, BLACK)
            surface.blit(enemy_text, (SCREEN_WIDTH // 2 - 40, 90))
    
    def draw_wave_transition(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        
        # Wave transition text
        if self.current_wave <= self.max_waves:
            wave_font = pygame.font.SysFont(None, 72)
            wave_text = wave_font.render(f"WAVE {self.current_wave}", True, WHITE)
            surface.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            # Instructions for final wave
            if self.current_wave == 5:
                instruction_font = pygame.font.SysFont(None, 36)
                instruction_text = instruction_font.render("Enemy aircraft incoming! Survive for 30 seconds!", True, WHITE)
                surface.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def draw_game_over(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        
        # Game over text
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, WHITE)
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        # Score
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        surface.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # High score
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
        surface.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Wave reached
        wave_text = self.font.render(f"Reached Wave: {self.current_wave}/{self.max_waves}", True, WHITE)
        surface.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        
        # Restart instructions
        restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, WHITE)
        surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))
        
    def draw_victory(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        
        # Victory text
        victory_font = pygame.font.SysFont(None, 72)
        victory_text = victory_font.render("VICTORY!", True, (255, 215, 0))  # Gold color
        surface.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        # Score
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        surface.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # High score
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
        surface.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Congratulations
        congrats_text = self.font.render("You survived all waves!", True, WHITE)
        surface.blit(congrats_text, (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        
        # Restart instructions
        restart_text = self.font.render("Press SPACE to play again or ESC to quit", True, WHITE)
        surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))
        
    def update(self):
        if self.game_over or self.victory:
            return
            
        # Handle wave transitions
        if self.wave_transition:
            if pygame.time.get_ticks() - self.transition_start_time > self.transition_duration:
                self.wave_transition = False
                self.initialize_wave(self.current_wave)
            else:
                return
                
        # Check if wave time is up
        current_time = pygame.time.get_ticks()
        if current_time - self.wave_start_time > self.wave_duration:
            # Wave completed
            if self.current_wave < self.max_waves:
                # Move to next wave
                self.current_wave += 1
                self.wave_transition = True
                self.transition_start_time = current_time
                self.score += 1000  # Bonus for completing a wave
            else:
                # Game completed - victory!
                self.victory = True
                self.score += 5000  # Big bonus for winning
                
                # Update high score if needed
                if self.score > self.high_score:
                    self.high_score = self.score
                    try:
                        with open("highscore.txt", "w") as f:
                            f.write(str(self.high_score))
                    except:
                        pass
            return
            
        keys = pygame.key.get_pressed()
        result = self.airplane.update(keys, self.obstacles, self.collectibles, self.mountains, self.enemies)
        
        # Unpack the result
        hit_obstacles, collected_items = result
        
        # Handle hit obstacles and update score
        for obstacle in hit_obstacles:
            if obstacle in self.obstacles:
                self.obstacles.remove(obstacle)
                self.score += 50  # Add score for shooting a star
        
        # Handle collected items
        for collectible in collected_items:
            if collectible in self.collectibles:
                if collectible.type == "fuel":
                    self.airplane.fuel = min(100, self.airplane.fuel + 20)
                elif collectible.type == "health":
                    self.airplane.health = min(100, self.airplane.health + 20)
                elif collectible.type == "speed":
                    self.airplane.max_speed = min(15, self.airplane.max_speed + 1)
                self.collectibles.remove(collectible)
                try:
                    collect_sound.play()
                except:
                    pass
        
        for cloud in self.clouds:
            cloud.update()
            
        for obstacle in self.obstacles:
            obstacle.update()
            
        for collectible in self.collectibles:
            collectible.update()
            
        for enemy in self.enemies:
            enemy.update(self.airplane)
            
        # Spawn new collectibles periodically
        if current_time - self.last_collectible_time > 5000:  # Every 5 seconds
            self.last_collectible_time = current_time
            self.add_random_collectible()
            
            # Limit number of collectibles
            if len(self.collectibles) > 10:
                self.collectibles.pop(0)
        
        # Increase score over time
        self.score += int(self.airplane.speed * 0.1)
        
        # Check game over conditions
        if self.airplane.health <= 0 or (self.airplane.fuel <= 0 and self.airplane.speed <= 1.1):
            self.game_over = True
            
            # Update high score if needed
            if self.score > self.high_score:
                self.high_score = self.score
                try:
                    with open("highscore.txt", "w") as f:
                        f.write(str(self.high_score))
                except:
                    pass
        
    def reset(self):
        self.__init__()
        
    def display_instructions(self):
        print("""
Wave-Based Flight Combat Game Controls:
- Arrow Left/Right: Turn the airplane
- Arrow Up/Down: Increase/Decrease speed
- SPACE: Shoot (in all waves)
- F12: Take screenshot
- Shoot orange star obstacles to destroy them and earn points
- Collect gold items for fuel
- Collect green items for health
- Collect blue items for max speed boost
- Avoid the orange obstacles and mountains
- In Wave 5, enemy aircraft will appear - survive for 30 seconds to win!
- ESC: Quit
- SPACE: Restart (when game over)
""")

def main():
    game = Game()
    game.display_instructions()
    
    # Add screenshot notification text
    screenshot_text = None
    screenshot_time = 0
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and (game.game_over or game.victory):
                    game.reset()
                elif event.key == pygame.K_F12:  # F12 key for screenshot
                    timestamp = pygame.time.get_ticks()
                    filename = f"flight_game_screenshot_{timestamp}.png"
                    pygame.image.save(screen, filename)
                    screenshot_text = f"Screenshot saved as {filename}"
                    screenshot_time = pygame.time.get_ticks()
                    print(screenshot_text)
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw(screen)
        
        # Display screenshot notification if needed
        if screenshot_text and pygame.time.get_ticks() - screenshot_time < 3000:  # Show for 3 seconds
            font = pygame.font.SysFont(None, 24)
            text = font.render(screenshot_text, True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 50))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
