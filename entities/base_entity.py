import pygame
from utils.config import *

class Entity:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(TILE_SIZE * 0.8, TILE_SIZE * 0.8)
        self.color = WHITE  # Default color
        self.active = True
        
    def update(self, dt):
        # Update position based on velocity
        self.position += self.velocity * dt
        
    def render(self, surface):
        # Default rendering (a rectangle)
        pygame.draw.rect(surface, self.color, 
                        (self.position.x - self.size.x/2,
                         self.position.y - self.size.y/2,
                         self.size.x, self.size.y))
    
    @property
    def rect(self):
        return pygame.Rect(self.position.x - self.size.x/2,
                         self.position.y - self.size.y/2,
                         self.size.x, self.size.y) 
    
    def to_dict(self):
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
        entity = cls(data["position"][0], data["position"][1])
        entity.velocity = pygame.math.Vector2(data["velocity"])
        entity.size = pygame.math.Vector2(data["size"])
        entity.color = data["color"]
        entity.active = data["active"]
        return entity 
    
    def render_with_offset(self, surface, camera_x, camera_y):
        """Render the entity with camera offset"""
        # Get zoom level from game state
        zoom_level = self.game_state.zoom_level
        
        # Calculate screen position
        screen_x = (self.position.x - camera_x)
        screen_y = (self.position.y - camera_y)
        
        # Draw the entity
        pygame.draw.rect(surface, self.color, 
                        (screen_x - self.size.x/2,
                         screen_y - self.size.y/2,
                         self.size.x, self.size.y)) 