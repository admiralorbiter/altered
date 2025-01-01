from abc import ABC, abstractmethod
import pygame
from utils.config import TILE_SIZE

class Item(ABC):
    """
    Abstract base class for all collectible and usable items in the game.
    Provides core functionality for item pickup, dropping, and rendering.
    """
    def __init__(self, x, y):
        # Position and size properties
        self.position = pygame.math.Vector2(x, y)
        self.size = pygame.math.Vector2(TILE_SIZE * 0.7, TILE_SIZE * 0.7)  # Items are slightly smaller than tiles
        
        # Item state tracking
        self.holder = None  # Entity currently holding the item
        self.active = True  # Whether the item is available for interaction
        
        # Item identification
        self.name = "Unknown Item"  # Display name
        self.description = "An mysterious item"  # Description for tooltips/UI
        
        # Game state reference (set when added to level)
        self.game_state = None
        
    def pick_up(self, entity):
        """
        Called when an entity picks up the item.
        Updates holder reference and item state.
        
        Args:
            entity: The entity that picked up the item
        """
        self.holder = entity
        
    def drop(self, x, y):
        """
        Called when the item is dropped at a position.
        Resets holder reference and updates position.
        
        Args:
            x, y (float): World coordinates for drop location
        """
        self.holder = None
        self.position.x = x
        self.position.y = y
        
    def use(self, user):
        """
        Called when the item is used by an entity.
        To be implemented by specific item types.
        
        Args:
            user: The entity using the item
        """
        pass
        
    def render_with_offset(self, surface, camera_x, camera_y):
        """
        Render the item with camera offset when in the world.
        Only renders if not being held by an entity.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
            camera_x, camera_y (float): Camera offset coordinates
        """
        if not self.holder:  # Only render if not being held
            screen_x = self.position.x - camera_x - self.size.x/2
            screen_y = self.position.y - camera_y - self.size.y/2
            self.render_at_position(surface, screen_x, screen_y)
            
    @abstractmethod
    def render_at_position(self, surface, x, y):
        """
        Abstract method for rendering the item at a specific screen position.
        Must be implemented by specific item types.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
            x, y (float): Screen coordinates for rendering
        """
        pass
        
    def to_dict(self):
        """
        Serialize item state to dictionary for saving.
        
        Returns:
            dict: Serialized item data
        """
        return {
            "type": self.__class__.__name__,
            "position": [self.position.x, self.position.y],
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create item instance from serialized data.
        
        Args:
            data (dict): Serialized item data
            
        Returns:
            Item: New item instance with restored state
        """
        item = cls(data["position"][0], data["position"][1])
        item.active = data["active"]
        return item 