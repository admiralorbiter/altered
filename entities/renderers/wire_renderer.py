import pygame
from utils.config import TILE_SIZE
from .base_renderer import BaseElectricalRenderer

class WireRenderer(BaseElectricalRenderer):
    def render(self, component, surface, screen_x, screen_y, zoom_level):
        tile_size = TILE_SIZE * zoom_level
        
        # Choose color based on construction state
        if component.is_built:
            wire_color = (0, 255, 255)  # Cyan for completed
        elif component.under_construction:
            wire_color = (255, 255, 0)  # Yellow for under construction
        else:
            wire_color = (128, 128, 128)  # Gray for not started
        
        # Draw main wire line
        pygame.draw.line(surface, wire_color,
                        (screen_x + tile_size * 0.2, screen_y + tile_size * 0.5),
                        (screen_x + tile_size * 0.8, screen_y + tile_size * 0.5),
                        int(max(2 * zoom_level, 1)))
        
        # Draw connection nodes
        node_radius = max(3 * zoom_level, 2)
        pygame.draw.circle(surface, wire_color,
                         (int(screen_x + tile_size * 0.2), int(screen_y + tile_size * 0.5)),
                         int(node_radius))
        pygame.draw.circle(surface, wire_color,
                         (int(screen_x + tile_size * 0.8), int(screen_y + tile_size * 0.5)),
                         int(node_radius)) 