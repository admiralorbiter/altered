import pygame
from .base_entity import Entity
from utils.config import *

class Player(Entity):
    def __init__(self, x, y):
        # Convert tile coordinates to pixel coordinates
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        self.color = (255, 192, 203, 128)  # Pink with transparency
        self.speed = 300
        self.selected = False
        self.target_position = None
        self.current_tile = (x, y)
        self.moving = False
        
    def select(self):
        self.selected = True
        
    def deselect(self):
        self.selected = False
        
    def set_target(self, tile_x, tile_y):
        if self.selected:
            self.target_position = pygame.math.Vector2(
                (tile_x + 0.5) * TILE_SIZE,
                (tile_y + 0.5) * TILE_SIZE
            )
            self.current_tile = (tile_x, tile_y)
            self.moving = True
    
    def update(self, dt):
        if self.target_position and self.moving:
            # Move towards target
            direction = self.target_position - self.position
            distance = direction.length()
            
            if distance < 1:  # Arrived at target
                self.position = self.target_position
                self.target_position = None
                self.velocity = pygame.math.Vector2(0, 0)
                self.moving = False
            else:
                # Move towards target at constant speed
                self.velocity = direction.normalize() * self.speed
                super().update(dt)
    
    def render_with_offset(self, surface, camera_x, camera_y):
        # Create a surface with alpha for the player
        player_surface = pygame.Surface((self.size.x, self.size.y), pygame.SRCALPHA)
        pygame.draw.rect(player_surface, self.color, 
                        (0, 0, self.size.x, self.size.y))
        
        # Calculate screen position
        screen_x = self.position.x - camera_x - self.size.x/2
        screen_y = self.position.y - camera_y - self.size.y/2
        
        # Blit the semi-transparent player
        surface.blit(player_surface, (screen_x, screen_y))
        
        # Draw selection circle when selected
        if self.selected:
            screen_x = self.position.x - camera_x
            screen_y = self.position.y - camera_y
            pygame.draw.circle(surface, (255, 255, 0), 
                             (int(screen_x), int(screen_y)), 
                             int(self.size.x * 0.75), 2)
            
        # Draw movement indicator if moving
        if self.moving and self.target_position:
            target_screen_x = self.target_position.x - camera_x
            target_screen_y = self.target_position.y - camera_y
            pygame.draw.line(surface, (255, 255, 0),
                           (self.position.x - camera_x, self.position.y - camera_y),
                           (target_screen_x, target_screen_y), 1) 