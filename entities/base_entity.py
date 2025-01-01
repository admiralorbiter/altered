import pygame
from utils.config import *

class Entity:
    """
    Base class for all game entities. Provides core functionality for
    positioning, movement, rendering, and serialization.
    """
    def __init__(self, x, y):
        # Core positioning and physics properties
        self.position = pygame.math.Vector2(x, y)  # Center position in world space
        self.velocity = pygame.math.Vector2(0, 0)  # Current movement velocity
        self.size = pygame.math.Vector2(TILE_SIZE * 0.8, TILE_SIZE * 0.8)  # Collision bounds
        
        # Visual and state properties
        self.color = WHITE  # Default rendering color
        self.active = True  # Whether entity is currently active in game
        
    def update(self, dt):
        """
        Update entity state based on time elapsed.
        Handles basic physics movement.
        
        Args:
            dt (float): Delta time since last update
        """
        # Update position based on velocity and time
        self.position += self.velocity * dt
        
    def render(self, surface):
        """
        Default rendering method - only used if child class doesn't override.
        Draws a simple rectangular shape for debugging purposes.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
        """
        if self.__class__ == Entity:
            # Basic rectangle rendering as fallback for base Entity
            pygame.draw.rect(surface, self.color,
                           (self.position.x - self.size.x/2,
                            self.position.y - self.size.y/2,
                            self.size.x, self.size.y))
    
    @property
    def rect(self):
        """
        Get the entity's collision rectangle.
        Centered on entity's position.
        
        Returns:
            pygame.Rect: Collision bounds rectangle
        """
        return pygame.Rect(self.position.x - self.size.x/2,
                         self.position.y - self.size.y/2,
                         self.size.x, self.size.y)
    
    def to_dict(self):
        """
        Serialize entity state for saving.
        
        Returns:
            dict: Entity data including type, position, and properties
        """
        return {
            "type": self.__class__.__name__,
            "position": [self.position.x, self.position.y],
            "velocity": [self.velocity.x, self.velocity.y],
            "size": [self.size.x, self.size.y],
            "color": self.color,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create entity instance from serialized data.
        
        Args:
            data (dict): Serialized entity data
            
        Returns:
            Entity: New entity instance with restored state
        """
        entity = cls(data["position"][0], data["position"][1])
        entity.velocity = pygame.math.Vector2(data["velocity"])
        entity.size = pygame.math.Vector2(data["size"])
        entity.color = data["color"]
        entity.active = data["active"]
        return entity
    
    def render_with_offset(self, surface, camera_x, camera_y):
        """
        Render the entity with camera offset and zoom.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
            camera_x, camera_y (float): Camera offset coordinates
        """
        # Get zoom level from game state
        zoom_level = self.game_state.zoom_level
        
        # Calculate screen position with camera offset
        screen_x = (self.position.x - camera_x)
        screen_y = (self.position.y - camera_y)
        
        # Draw the entity as a basic rectangle
        pygame.draw.rect(surface, self.color, 
                        (screen_x - self.size.x/2,
                         screen_y - self.size.y/2,
                         self.size.x, self.size.y)) 