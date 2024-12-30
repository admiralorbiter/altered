import pygame
import random
from .base_entity import Entity
from utils.config import *

class Cat(Entity):
    def __init__(self, x, y):
        # Convert tile coordinates to pixel coordinates like in Alien class
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        # Basic stats
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.speed = random.uniform(250, 350)  # Varying speed between cats
        self.morale = 100
        
        # State tracking
        self.current_task = None
        self.target_position = None
        self.current_tile = (x, y)
        self.moving = False
        self.path = None
        self.current_waypoint = 0
        
        # Personality traits (randomly assigned)
        self.traits = self._generate_traits()
        
        # Visual properties
        self.color = (random.randint(150, 200), 
                     random.randint(100, 150), 
                     random.randint(50, 100),
                     200)  # Brownish with alpha
    
    def _generate_traits(self):
        possible_traits = ['lazy', 'aggressive', 'curious', 'cautious', 'loyal']
        num_traits = random.randint(1, 2)  # Each cat gets 1-2 traits
        return random.sample(possible_traits, num_traits)
    
    def update(self, dt):
        # Update morale based on conditions (simplified)
        if self.health < self.max_health * 0.5:
            self.morale = max(0, self.morale - 10 * dt)
        
        # Movement logic (similar to Alien class)
        if self.target_position and self.moving:
            direction = self.target_position - self.position
            distance = direction.length()
            
            if distance < 2:  # Reached waypoint
                self.position = self.target_position
                
                if self.path and self.current_waypoint < len(self.path) - 1:
                    self.current_waypoint += 1
                    next_tile = self.path[self.current_waypoint]
                    self.target_position = pygame.math.Vector2(
                        round((next_tile[0] + 0.5) * TILE_SIZE),
                        round((next_tile[1] + 0.5) * TILE_SIZE)
                    )
                else:
                    self.target_position = None
                    self.path = None
                    self.moving = False
            else:
                # Apply personality traits to movement
                speed_modifier = 0.7 if 'lazy' in self.traits else 1.2 if 'aggressive' in self.traits else 1.0
                
                normalized_dir = direction.normalize()
                movement = normalized_dir * self.speed * speed_modifier * dt
                
                if movement.length() > distance:
                    self.position = self.target_position
                else:
                    self.position += movement
    
    def render_with_offset(self, surface, camera_x, camera_y):
        # Calculate screen position
        screen_x = self.position.x - camera_x
        screen_y = self.position.y - camera_y
        
        # Create a surface with alpha for the cat
        cat_surface = pygame.Surface((self.size.x, self.size.y), pygame.SRCALPHA)
        
        # Draw cat body (oval)
        body_rect = (self.size.x * 0.2, self.size.y * 0.3, 
                    self.size.x * 0.6, self.size.y * 0.5)
        pygame.draw.ellipse(cat_surface, self.color, body_rect)
        
        # Draw cat head (circle)
        head_size = self.size.x * 0.4
        pygame.draw.circle(cat_surface, self.color,
                          (self.size.x * 0.35, self.size.y * 0.4),
                          head_size/2)
        
        # Draw cat ears (triangles)
        ear_color = tuple(max(0, min(255, c - 30)) for c in self.color[:3]) + (self.color[3],)
        left_ear = [(self.size.x * 0.25, self.size.y * 0.3),
                    (self.size.x * 0.35, self.size.y * 0.15),
                    (self.size.x * 0.45, self.size.y * 0.3)]
        right_ear = [(self.size.x * 0.35, self.size.y * 0.3),
                     (self.size.x * 0.45, self.size.y * 0.15),
                     (self.size.x * 0.55, self.size.y * 0.3)]
        pygame.draw.polygon(cat_surface, ear_color, left_ear)
        pygame.draw.polygon(cat_surface, ear_color, right_ear)
        
        # Draw cat eyes
        eye_color = (0, 255, 0) if 'aggressive' in self.traits else (0, 200, 255)
        pygame.draw.circle(cat_surface, eye_color,
                          (self.size.x * 0.3, self.size.y * 0.35), 3)
        pygame.draw.circle(cat_surface, eye_color,
                          (self.size.x * 0.4, self.size.y * 0.35), 3)
        
        # Draw cat tail (curved line)
        tail_points = [
            (self.size.x * 0.8, self.size.y * 0.5),
            (self.size.x * 0.9, self.size.y * 0.4),
            (self.size.x * 0.95, self.size.y * 0.3)
        ]
        pygame.draw.lines(cat_surface, self.color, False, tail_points, 3)
        
        # Blit the cat to the screen
        surface.blit(cat_surface, 
                    (screen_x - self.size.x/2, 
                     screen_y - self.size.y/2))
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            health_width = (self.size.x * self.health) / self.max_health
            pygame.draw.rect(surface, (255, 0, 0), 
                           (screen_x - self.size.x/2, 
                            screen_y - self.size.y/2 - 5,
                            self.size.x, 3))
            pygame.draw.rect(surface, (0, 255, 0),
                           (screen_x - self.size.x/2, 
                            screen_y - self.size.y/2 - 5,
                            health_width, 3)) 