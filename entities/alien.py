import pygame

from systems.capture_system import CaptureState
from .base_entity import Entity
from utils.config import *
from utils.pathfinding import find_path

class Alien(Entity):
    """
    Player-controlled alien entity with advanced movement, capture mechanics,
    and visual effects. Features detailed rendering with body parts and animations.
    """
    def __init__(self, x, y, color=(255, 192, 203, 128)):
        # Convert tile coordinates to pixel coordinates for centered positioning
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        # Visual properties
        self.color = color  # Base color with alpha for transparency
        
        # Movement and control properties
        self.speed = 300  # Movement speed in pixels/second
        self.selected = False  # Selection state for player control
        self.target_position = None  # Target position for movement
        self.current_tile = (x, y)  # Current tile coordinates
        self.moving = False  # Movement state
        self.path = None  # Current pathfinding path
        self.current_waypoint = 0  # Index in current path
        
        # Status attributes
        self.max_health = 100
        self.health = self.max_health
        self.max_morale = 100
        self.morale = self.max_morale
        
        # Capture mechanics
        self.capture_range = TILE_SIZE * 2  # Range for capturing targets
        self.capture_strength = 50  # Base capture effectiveness
        self.carrying_target = None  # Currently carried entity
        
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
        
        # Find path using A* with entity collision checking
        self.path = find_path(current_tile, target_tile, 
                             self.game_state.current_level.tilemap,
                             self.game_state, self)
        
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
        """
        Update alien state including movement and path following.
        Handles waypoint navigation and task completion.
        
        Args:
            dt (float): Delta time since last update
        """
        if self.target_position and self.moving:
            # Calculate movement direction and distance
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
                    # Check if we were placing a wire
                    if hasattr(self, 'wire_task') and self.wire_task:
                        wire_pos, wire_type = self.wire_task
                        self.game_state.current_level.tilemap.set_electrical(wire_pos[0], wire_pos[1], wire_type)
                        self.wire_task = None
                    self.deselect()
            else:
                # Apply movement with speed and time
                normalized_dir = direction.normalize()
                movement = normalized_dir * self.speed * dt
                
                # Prevent overshooting target
                if movement.length() > distance:
                    self.position = self.target_position
                else:
                    self.position += movement
    
    def render_with_offset(self, surface, camera_x, camera_y):
        """
        Render the alien with detailed body parts and effects.
        Includes selection indicator and movement path visualization.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
            camera_x, camera_y (float): Camera offset coordinates
        """
        # Get zoom level from game state
        zoom_level = self.game_state.zoom_level
        
        # Calculate screen position with zoom
        screen_x = (self.position.x - camera_x) * zoom_level
        screen_y = (self.position.y - camera_y) * zoom_level
        
        # Create a surface with alpha for the alien scaled by zoom
        scaled_size = pygame.Vector2(self.size.x * zoom_level, self.size.y * zoom_level)
        alien_surface = pygame.Surface((scaled_size.x, scaled_size.y), pygame.SRCALPHA)
        
        # Draw alien body (oval) scaled
        ellipse_rect = (0, scaled_size.y * 0.2, scaled_size.x, scaled_size.y * 0.6)
        pygame.draw.ellipse(alien_surface, self.color, ellipse_rect)
        
        # Draw alien head (circle) scaled
        head_size = scaled_size.x * 0.6
        pygame.draw.circle(alien_surface, self.color,
                          (scaled_size.x/2, scaled_size.y * 0.3),
                          head_size/2)
        
        # Draw alien eyes (black circles) scaled
        eye_size = head_size * 0.3
        eye_y = scaled_size.y * 0.25
        pygame.draw.circle(alien_surface, (0, 0, 0),
                          (scaled_size.x/2 - eye_size, eye_y), eye_size/2)
        pygame.draw.circle(alien_surface, (0, 0, 0),
                          (scaled_size.x/2 + eye_size, eye_y), eye_size/2)
        
        # Draw alien tentacles scaled
        tentacle_color = tuple(max(0, min(255, c + 30)) for c in self.color[:3]) + (self.color[3],)
        for i in range(3):
            start_x = scaled_size.x * (0.3 + 0.2 * i)
            pygame.draw.line(alien_surface, tentacle_color,
                            (start_x, scaled_size.y * 0.8),
                            (start_x, scaled_size.y),
                            max(1, int(3 * zoom_level)))
        
        # Blit the alien to the screen
        surface.blit(alien_surface,
                    (screen_x - scaled_size.x/2,
                     screen_y - scaled_size.y/2))
        
        # Draw selection circle when selected
        if self.selected:
            pygame.draw.circle(surface, (255, 255, 0),
                             (int(screen_x), int(screen_y)),
                             int(scaled_size.x * 0.75), max(1, int(2 * zoom_level)))
            
        # Draw movement indicator if moving
        if self.moving and self.target_position:
            target_screen_x = (self.target_position.x - camera_x) * zoom_level
            target_screen_y = (self.target_position.y - camera_y) * zoom_level
            pygame.draw.line(surface, (255, 255, 0),
                           (screen_x, screen_y),
                           (target_screen_x, target_screen_y), max(1, int(zoom_level))) 
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def change_morale(self, amount):
        self.morale = max(0, min(self.max_morale, self.morale + amount)) 
    
    def can_capture(self, target):
        """Check if target is within capture range"""
        if not hasattr(target, 'capture_state'):
            return False
            
        distance = (target.position - self.position).length()
        return distance <= self.capture_range
        
    def attempt_capture(self, target):
        """
        Attempt to capture a target entity.
        Handles both knockout and carrying mechanics.
        
        Args:
            target: Entity to attempt capturing
            
        Returns:
            bool: True if capture attempt was successful
        """
        if not self.can_capture(target):
            return False
            
        # Handle different capture states
        if target.capture_state == CaptureState.NONE:
            return self.game_state.capture_system.attempt_knockout(self, target)
        elif target.capture_state == CaptureState.UNCONSCIOUS:
            return self.game_state.capture_system.start_carrying(self, target)
        return False
        
    def release_target(self):
        """Release currently carried target"""
        if self.carrying_target:
            self.carrying_target.capture_state = CaptureState.NONE
            self.carrying_target.carrier = None
            self.carrying_target = None
            self.speed /= 0.6  # Restore normal speed 
    
    def set_wire_task(self, wire_pos, wire_type):
        target_tile = wire_pos
        current_tile = (int(self.position.x // TILE_SIZE), int(self.position.y // TILE_SIZE))
        
        self.path = find_path(current_tile, target_tile, 
                             self.game_state.current_level.tilemap,
                             self.game_state, self)
        
        if self.path:
            self.current_waypoint = 1 if len(self.path) > 1 else 0
            next_tile = self.path[self.current_waypoint]
            self.target_position = pygame.math.Vector2(
                (next_tile[0] + 0.5) * TILE_SIZE,
                (next_tile[1] + 0.5) * TILE_SIZE
            )
            self.moving = True
            self.wire_task = (wire_pos, wire_type) 