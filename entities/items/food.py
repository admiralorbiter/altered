import pygame

from utils.config import TILE_SIZE
from .base_item import Item

class Food(Item):
    """
    Food item that can be consumed to restore health and hunger.
    Features a detailed apple visual representation with dynamic scaling.
    """
    def __init__(self, x, y):
        super().__init__(x, y)
        # Item properties
        self.name = "Apple"
        self.description = "A fresh, red apple"
        self.nutrition_value = 100  # Amount of health/hunger restored
        self.position = pygame.Vector2(x, y)  # Store raw position
        
    def use(self, user):
        """
        Consume the food item to restore health and/or hunger.
        
        Args:
            user: Entity consuming the food
            
        Returns:
            bool: True if successfully consumed, False otherwise
        """
        if hasattr(user, 'health'):
            if hasattr(user, 'hunger'):
                # Restore both hunger and health if entity has both
                user.hunger = user.max_hunger
                user.health = user.max_health
            else:
                # Otherwise just restore health
                user.health = min(user.health + self.nutrition_value, user.max_health)
            return True  # Item was consumed
        return False
        
    def render_with_offset(self, surface, camera_x, camera_y):
        """
        Render the food item in the game world with camera offset and zoom.
        Draws a detailed apple with highlight, stem, and leaf.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
            camera_x, camera_y (float): Camera offset coordinates
        """
        # Get zoom level from game state
        zoom_level = self.game_state.zoom_level
        
        # Calculate screen position with zoom
        screen_x = (self.position.x - camera_x) * zoom_level
        screen_y = (self.position.y - camera_y) * zoom_level
        
        # Scale size based on zoom (make it slightly smaller than tile)
        scaled_size = TILE_SIZE * 0.6 * zoom_level
        
        # Create a surface with alpha for the apple
        apple_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
        
        # Draw apple body (red circle)
        apple_color = (255, 0, 0)  # Red
        pygame.draw.circle(apple_surface, apple_color, 
                         (scaled_size/2, scaled_size/2), 
                         scaled_size/2)
        
        # Add highlight (small white oval)
        highlight_color = (255, 255, 255, 128)  # Semi-transparent white
        highlight_rect = pygame.Rect(scaled_size/3, 
                                   scaled_size/4, 
                                   scaled_size/4, scaled_size/6)
        pygame.draw.ellipse(apple_surface, highlight_color, highlight_rect)
        
        # Add stem (brown rectangle)
        stem_color = (101, 67, 33)  # Brown
        stem_rect = pygame.Rect(scaled_size/2 - 2 * zoom_level, 
                              2 * zoom_level, 
                              4 * zoom_level, 6 * zoom_level)
        pygame.draw.rect(apple_surface, stem_color, stem_rect)
        
        # Add leaf (green triangle)
        leaf_color = (34, 139, 34)  # Forest Green
        leaf_points = [
            (scaled_size/2 + 4 * zoom_level, 4 * zoom_level),
            (scaled_size/2 - 2 * zoom_level, 2 * zoom_level),
            (scaled_size/2 + 2 * zoom_level, 8 * zoom_level)
        ]
        pygame.draw.polygon(apple_surface, leaf_color, leaf_points)
        
        # Blit the apple surface to the screen
        surface.blit(apple_surface,
                    (screen_x - scaled_size/2,
                     screen_y - scaled_size/2))
        
    def render_at_position(self, surface, x, y):
        """
        Render the food item at a specific position for inventory display.
        Creates a simplified version of the apple icon.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
            x, y (float): Screen coordinates for rendering
        """
        # Create a small surface for the food icon
        icon_size = 32
        food_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Draw apple body (red circle)
        apple_color = (255, 0, 0)  # Red
        pygame.draw.circle(food_surface, apple_color, 
                         (icon_size/2, icon_size/2), 
                         icon_size/2)
        
        # Add highlight (small white oval)
        highlight_color = (255, 255, 255)
        highlight_rect = pygame.Rect(icon_size/3, 
                                   icon_size/4, 
                                   icon_size/4, icon_size/6)
        pygame.draw.ellipse(food_surface, highlight_color, highlight_rect)
        
        # Add stem (brown rectangle)
        stem_color = (101, 67, 33)  # Brown
        stem_rect = pygame.Rect(icon_size/2 - 2, 
                              2, 
                              4, 6)
        pygame.draw.rect(food_surface, stem_color, stem_rect)
        
        # Add leaf (green triangle)
        leaf_color = (34, 139, 34)  # Forest Green
        leaf_points = [
            (icon_size/2 + 4, 4),
            (icon_size/2 - 2, 2),
            (icon_size/2 + 2, 8)
        ]
        pygame.draw.polygon(food_surface, leaf_color, leaf_points)
        
        # Blit the food surface to the main surface
        surface.blit(food_surface, (x, y)) 