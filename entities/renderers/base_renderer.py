from abc import ABC, abstractmethod
import pygame
from utils.config import TILE_SIZE

class BaseRenderer(ABC):
    """Base class for all renderers in the game"""
    @abstractmethod
    def render(self, component, surface, screen_x, screen_y, zoom_level):
        """
        Base render method that all renderers must implement
        
        Args:
            component: The component to render
            surface: Pygame surface to render on
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate
            zoom_level: Current zoom level
        """
        pass

class BaseElectricalRenderer(BaseRenderer):
    """Base class specifically for electrical component renderers"""
    
    def draw_construction_progress(self, surface, size, progress, zoom_level):
        """Shared method for drawing construction progress"""
        height = size * progress
        
        # Base structure (gray)
        pygame.draw.rect(surface, (128, 128, 128, 180),
                        (0, size - height, size, height))
        
        # Construction scaffolding
        scaffold_color = (200, 200, 200, 100)
        for i in range(4):
            x = size * (i / 3)
            pygame.draw.line(surface, scaffold_color,
                           (x, size), (x, 0), max(1, int(2 * zoom_level))) 