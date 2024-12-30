from abc import ABC, abstractmethod
import pygame
from utils.config import TILE_SIZE

class Item(ABC):
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.size = pygame.math.Vector2(TILE_SIZE * 0.7, TILE_SIZE * 0.7)  # Made items larger
        self.holder = None  # Entity currently holding the item
        self.active = True
        self.name = "Unknown Item"
        self.description = "An mysterious item"
        
    def pick_up(self, entity):
        """Called when an entity picks up the item"""
        self.holder = entity
        
    def drop(self, x, y):
        """Called when the item is dropped at a position"""
        self.holder = None
        self.position.x = x
        self.position.y = y
        
    def use(self, user):
        """Called when the item is used by an entity"""
        pass
        
    def render_with_offset(self, surface, camera_x, camera_y):
        """Render the item with camera offset"""
        if not self.holder:  # Only render if not being held
            screen_x = self.position.x - camera_x - self.size.x/2
            screen_y = self.position.y - camera_y - self.size.y/2
            self.render_at_position(surface, screen_x, screen_y)
            
    @abstractmethod
    def render_at_position(self, surface, x, y):
        """Render the item at the given screen position"""
        pass
        
    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "position": [self.position.x, self.position.y],
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(data["position"][0], data["position"][1])
        item.active = data["active"]
        return item 