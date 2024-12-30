import pygame
from .base_item import Item

class Food(Item):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Apple"
        self.description = "A fresh, red apple"
        self.nutrition_value = 100
        
    def use(self, user):
        if hasattr(user, 'health'):
            if hasattr(user, 'hunger'):
                user.hunger = user.max_hunger
                user.health = user.max_health
            else:
                user.health = min(user.health + self.nutrition_value, user.max_health)
            return True  # Item was consumed
        return False
        
    def render_at_position(self, surface, x, y):
        # Draw apple body (red circle)
        apple_color = (255, 0, 0)  # Red
        pygame.draw.circle(surface, apple_color, 
                         (x + self.size.x/2, y + self.size.y/2), 
                         self.size.x/2)
        
        # Add highlight (small white oval)
        highlight_color = (255, 255, 255)
        highlight_rect = pygame.Rect(x + self.size.x/3, y + self.size.y/4, 
                                   self.size.x/4, self.size.y/6)
        pygame.draw.ellipse(surface, highlight_color, highlight_rect)
        
        # Add stem (brown rectangle)
        stem_color = (101, 67, 33)  # Brown
        stem_rect = pygame.Rect(x + self.size.x/2 - 2, y + 2, 4, 6)
        pygame.draw.rect(surface, stem_color, stem_rect)
        
        # Add leaf (green triangle)
        leaf_color = (34, 139, 34)  # Forest Green
        leaf_points = [
            (x + self.size.x/2 + 4, y + 4),  # Tip
            (x + self.size.x/2 - 2, y + 2),  # Base
            (x + self.size.x/2 + 2, y + 8)   # Back
        ]
        pygame.draw.polygon(surface, leaf_color, leaf_points) 