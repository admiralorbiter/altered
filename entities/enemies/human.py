import pygame
from .base_enemy import BaseEnemy
from utils.config import *
from utils.pathfinding import find_path
import random

class Human(BaseEnemy):
    def __init__(self, x, y):
        # Convert tile coordinates to pixel coordinates
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        # Human-specific stats
        self.max_health = 80
        self.health = self.max_health
        self.attack_power = 15
        self.speed = 250
        self.attack_cooldown = 1.0  # 1 second between attacks
        self.attack_timer = 0
        
        # Visual properties
        self.color = (200, 150, 150, 200)  # Pinkish for human skin tone
        
    def attack(self, target):
        """Implement human attack behavior"""
        if self.attack_timer <= 0:
            target.take_damage(self.attack_power)
            self.attack_timer = self.attack_cooldown
            
    def update(self, dt):
        if not self.active:
            return
            
        # Update attack cooldown
        self.attack_timer = max(0, self.attack_timer - dt)
        
        # Update AI state
        self.update_ai_state(dt, self.game_state)
        
        # Handle different states
        if self.state == 'idle':
            # Randomly decide to start wandering
            if random.random() < 0.01:  # 1% chance per frame to start wandering
                self.start_wandering()
                
        elif self.state == 'patrol':
            if not self.moving or not self.target_position:
                self.start_wandering()
                
        elif self.state == 'chase':
            if self.target:
                # Update path to target every second
                if not hasattr(self, 'path_update_timer'):
                    self.path_update_timer = 0
                self.path_update_timer -= dt
                
                if self.path_update_timer <= 0:
                    self.path_update_timer = 1.0
                    self.update_chase_path()
        
        # Movement logic
        if self.target_position and self.moving:
            direction = self.target_position - self.position
            distance = direction.length()
            
            if distance < 2:  # Reached waypoint
                self.handle_waypoint_reached()
            else:
                self.move_towards_target(direction, distance, dt)

    def start_wandering(self):
        """Start wandering to a random nearby position"""
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        
        # Try to find a valid wandering target
        for _ in range(10):  # Try 10 times
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            target_tile = (current_tile[0] + dx, current_tile[1] + dy)
            
            if self.game_state.current_level.tilemap.is_walkable(*target_tile):
                self.path = find_path(current_tile, target_tile, 
                                    self.game_state.current_level.tilemap)
                if self.path:
                    self.current_waypoint = 1 if len(self.path) > 1 else 0
                    next_tile = self.path[self.current_waypoint]
                    self.target_position = pygame.math.Vector2(
                        (next_tile[0] + 0.5) * TILE_SIZE,
                        (next_tile[1] + 0.5) * TILE_SIZE
                    )
                    self.moving = True
                    break

    def update_chase_path(self):
        """Update path to chase target"""
        if not self.target:
            return
        
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        target_tile = (int(self.target.position.x // TILE_SIZE),
                      int(self.target.position.y // TILE_SIZE))
        
        self.path = find_path(current_tile, target_tile, 
                             self.game_state.current_level.tilemap)
        if self.path:
            self.current_waypoint = 1 if len(self.path) > 1 else 0
            next_tile = self.path[self.current_waypoint]
            self.target_position = pygame.math.Vector2(
                (next_tile[0] + 0.5) * TILE_SIZE,
                (next_tile[1] + 0.5) * TILE_SIZE
            )
            self.moving = True

    def handle_waypoint_reached(self):
        """Handle reaching a waypoint in the path"""
        self.position = self.target_position
        
        if self.path and self.current_waypoint < len(self.path) - 1:
            self.current_waypoint += 1
            next_tile = self.path[self.current_waypoint]
            self.target_position = pygame.math.Vector2(
                (next_tile[0] + 0.5) * TILE_SIZE,
                (next_tile[1] + 0.5) * TILE_SIZE
            )
        else:
            self.target_position = None
            self.path = None
            self.moving = False

    def move_towards_target(self, direction, distance, dt):
        """Move towards the current target"""
        normalized_dir = direction.normalize()
        movement = normalized_dir * self.speed * dt
        
        if movement.length() > distance:
            self.position = self.target_position
        else:
            self.position += movement

    def render_with_offset(self, surface, camera_x, camera_y):
        if not self.active:
            return
            
        # Get zoom level from game state
        zoom_level = self.game_state.zoom_level
        
        # Draw detection range circle
        screen_x = (self.position.x - camera_x) * zoom_level
        screen_y = (self.position.y - camera_y) * zoom_level
        range_radius = self.detection_range * zoom_level
        
        # Draw semi-transparent detection range
        range_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
        if self.state == 'chase':
            pygame.draw.circle(range_surface, (255, 0, 0, 30), 
                             (range_radius, range_radius), range_radius)
        else:
            pygame.draw.circle(range_surface, (100, 100, 100, 30), 
                             (range_radius, range_radius), range_radius)
        surface.blit(range_surface, 
                    (screen_x - range_radius, screen_y - range_radius))
        
        # Calculate screen position with zoom
        screen_x = (self.position.x - camera_x) * zoom_level
        screen_y = (self.position.y - camera_y) * zoom_level
        
        # Scale size based on zoom
        scaled_size = pygame.Vector2(self.size.x * zoom_level, self.size.y * zoom_level)
        
        # Create a surface with alpha for the human
        human_surface = pygame.Surface((scaled_size.x, scaled_size.y), pygame.SRCALPHA)
        
        # Draw body (rectangle)
        body_rect = (scaled_size.x * 0.3, scaled_size.y * 0.3, 
                    scaled_size.x * 0.4, scaled_size.y * 0.5)
        pygame.draw.rect(human_surface, self.color, body_rect)
        
        # Draw head (circle)
        head_size = scaled_size.x * 0.3
        pygame.draw.circle(human_surface, self.color,
                         (scaled_size.x/2, scaled_size.y * 0.25),
                         head_size/2)
        
        # Draw arms (lines)
        arm_color = tuple(max(0, min(255, c - 20)) for c in self.color[:3]) + (self.color[3],)
        line_width = max(1, int(3 * zoom_level))
        # Left arm
        pygame.draw.line(human_surface, arm_color,
                        (scaled_size.x * 0.3, scaled_size.y * 0.35),
                        (scaled_size.x * 0.2, scaled_size.y * 0.5), line_width)
        # Right arm
        pygame.draw.line(human_surface, arm_color,
                        (scaled_size.x * 0.7, scaled_size.y * 0.35),
                        (scaled_size.x * 0.8, scaled_size.y * 0.5), line_width)
        
        # Draw legs (lines)
        # Left leg
        pygame.draw.line(human_surface, arm_color,
                        (scaled_size.x * 0.4, scaled_size.y * 0.8),
                        (scaled_size.x * 0.3, scaled_size.y * 0.95), line_width)
        # Right leg
        pygame.draw.line(human_surface, arm_color,
                        (scaled_size.x * 0.6, scaled_size.y * 0.8),
                        (scaled_size.x * 0.7, scaled_size.y * 0.95), line_width)
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            health_width = (scaled_size.x * self.health) / self.max_health
            bar_height = max(2, 3 * zoom_level)
            pygame.draw.rect(surface, (255, 0, 0),
                           (screen_x - scaled_size.x/2,
                            screen_y - scaled_size.y/2 - 5 * zoom_level,
                            scaled_size.x, bar_height))
            pygame.draw.rect(surface, (0, 255, 0),
                           (screen_x - scaled_size.x/2,
                            screen_y - scaled_size.y/2 - 5 * zoom_level,
                            health_width, bar_height))
        
        # Blit the human to the screen
        surface.blit(human_surface,
                    (screen_x - scaled_size.x/2,
                     screen_y - scaled_size.y/2)) 