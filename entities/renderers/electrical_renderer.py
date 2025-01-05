from abc import ABC, abstractmethod
import pygame
from utils.config import TILE_SIZE

class BaseElectricalRenderer(ABC):
    @abstractmethod
    def render(self, component, surface, screen_x, screen_y, zoom_level):
        """Base render method that all electrical renderers must implement"""
        pass

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

class ReactorRenderer(BaseElectricalRenderer):
    def render(self, component, surface, screen_x, screen_y, zoom_level):
        # Calculate size for 2x2 tiles
        tile_size = TILE_SIZE * zoom_level
        size = tile_size * 2  # 2x2 tiles
        
        # Create surface with transparency
        reactor_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if component.under_construction:
            # Draw construction progress
            progress = component.construction_progress / component.construction_time
            height = size * progress
            
            # Base structure (gray)
            pygame.draw.rect(reactor_surface, (128, 128, 128, 180),
                           (0, size - height, size, height))
            
            # Construction scaffolding
            scaffold_color = (200, 200, 200, 100)
            for i in range(4):
                x = size * (i / 3)
                pygame.draw.line(reactor_surface, scaffold_color,
                               (x, size), (x, 0), max(1, int(2 * zoom_level)))
        else:
            # Fully built reactor
            # Main body (slightly smaller than full size)
            margin = size * 0.1
            body_rect = (margin, margin, size - 2*margin, size - 2*margin)
            pygame.draw.rect(reactor_surface, (64, 64, 64, 255), body_rect)
            
            # Cooling towers (positioned within body)
            tower_size = size * 0.35  # Slightly smaller towers
            tower_margin = size * 0.15
            pygame.draw.rect(reactor_surface, (192, 192, 192, 255),
                           (tower_margin, tower_margin, tower_size, tower_size))
            pygame.draw.rect(reactor_surface, (192, 192, 192, 255),
                           (size - tower_size - tower_margin, tower_margin, 
                            tower_size, tower_size))
            
            # Core glow (centered)
            core_color = (0, 255, 128, 150)  # Green nuclear glow
            core_center = (size // 2, size // 2)
            core_radius = int(size * 0.25)  # Slightly smaller glow
            pygame.draw.circle(reactor_surface, core_color,
                             core_center, core_radius)
            
        # Blit to main surface - centered on the tile position
        surface.blit(reactor_surface, (screen_x, screen_y))

class ElectricalRendererSystem:
    def __init__(self):
        self.renderers = {
            'wire': WireRenderer(),
            'reactor': ReactorRenderer(),
            # Easy to add new electrical component renderers:
            # 'solar_panel': SolarPanelRenderer(),
        }
    
    def render(self, component, surface, screen_x, screen_y, zoom_level):
        """Render an electrical component using its appropriate renderer"""
        if component.type in self.renderers:
            self.renderers[component.type].render(
                component, surface, screen_x, screen_y, zoom_level
            ) 