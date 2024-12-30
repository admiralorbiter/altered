import pygame
from .base_entity import Entity
from utils.config import *
from utils.pathfinding import find_path

class Alien(Entity):
    def __init__(self, x, y, color=(255, 192, 203, 128)):
        # Convert tile coordinates to pixel coordinates
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        self.color = color
        self.speed = 300
        self.selected = False
        self.target_position = None
        self.current_tile = (x, y)
        self.moving = False
        self.path = None
        self.current_waypoint = 0
        
    def select(self):
        self.selected = True
        
    def deselect(self):
        self.selected = False
        
    def set_target(self, tile_x, tile_y):
        if not self.selected:
            return
        
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        target_tile = (tile_x, tile_y)
        
        # Find path using A*
        self.path = find_path(current_tile, target_tile, self.game_state.current_level.tilemap)
        
        if self.path:
            # Set next waypoint
            self.current_waypoint = 1 if len(self.path) > 1 else 0
            next_tile = self.path[self.current_waypoint]
            self.target_position = pygame.math.Vector2(
                (next_tile[0] + 0.5) * TILE_SIZE,
                (next_tile[1] + 0.5) * TILE_SIZE
            )
            self.moving = True
    
    def update(self, dt):
        if self.target_position and self.moving:
            direction = self.target_position - self.position
            distance = direction.length()
            
            # Increased threshold slightly to prevent jittering
            if distance < 2:  # Reached waypoint
                # Snap to exact position
                self.position = self.target_position
                
                # Check if there are more waypoints
                if self.path and self.current_waypoint < len(self.path) - 1:
                    self.current_waypoint += 1
                    next_tile = self.path[self.current_waypoint]
                    # Ensure exact pixel positioning
                    self.target_position = pygame.math.Vector2(
                        round((next_tile[0] + 0.5) * TILE_SIZE),
                        round((next_tile[1] + 0.5) * TILE_SIZE)
                    )
                else:
                    self.target_position = None
                    self.path = None
                    self.moving = False
                    self.deselect()
            else:
                # Normalize direction and apply speed
                normalized_dir = direction.normalize()
                movement = normalized_dir * self.speed * dt
                
                # If we would overshoot the target, just snap to it
                if movement.length() > distance:
                    self.position = self.target_position
                else:
                    self.position += movement
    
    def render_with_offset(self, surface, camera_x, camera_y):
        # Calculate screen position
        screen_x = self.position.x - camera_x
        screen_y = self.position.y - camera_y
        
        # Create a surface with alpha for the alien
        alien_surface = pygame.Surface((self.size.x, self.size.y), pygame.SRCALPHA)
        
        # Draw alien body (oval)
        ellipse_rect = (0, self.size.y * 0.2, self.size.x, self.size.y * 0.6)
        pygame.draw.ellipse(alien_surface, self.color, ellipse_rect)
        
        # Draw alien head (circle)
        head_size = self.size.x * 0.6
        head_x = (self.size.x - head_size) / 2
        pygame.draw.circle(alien_surface, self.color, 
                          (self.size.x/2, self.size.y * 0.3),
                          head_size/2)
        
        # Draw alien eyes (black circles)
        eye_size = head_size * 0.3
        eye_y = self.size.y * 0.25
        pygame.draw.circle(alien_surface, (0, 0, 0), 
                          (self.size.x/2 - eye_size, eye_y), eye_size/2)
        pygame.draw.circle(alien_surface, (0, 0, 0), 
                          (self.size.x/2 + eye_size, eye_y), eye_size/2)
        
        # Draw alien tentacles
        tentacle_color = tuple(max(0, min(255, c + 30)) for c in self.color[:3]) + (self.color[3],)
        for i in range(3):
            start_x = self.size.x * (0.3 + 0.2 * i)
            pygame.draw.line(alien_surface, tentacle_color,
                            (start_x, self.size.y * 0.8),
                            (start_x, self.size.y),
                            3)
        
        # Blit the alien to the screen
        surface.blit(alien_surface, 
                    (screen_x - self.size.x/2, 
                     screen_y - self.size.y/2))
        
        # Draw selection circle when selected
        if self.selected:
            pygame.draw.circle(surface, (255, 255, 0), 
                             (int(screen_x), int(screen_y)), 
                             int(self.size.x * 0.75), 2)
            
        # Draw movement indicator if moving
        if self.moving and self.target_position:
            target_screen_x = self.target_position.x - camera_x
            target_screen_y = self.target_position.y - camera_y
            pygame.draw.line(surface, (255, 255, 0),
                           (screen_x, screen_y),
                           (target_screen_x, target_screen_y), 1) 