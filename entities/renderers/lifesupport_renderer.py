import pygame
from utils.config import TILE_SIZE
from .base_renderer import BaseElectricalRenderer

class LifeSupportRenderer(BaseElectricalRenderer):
    def render(self, component, surface, screen_x, screen_y, zoom_level):
        # Calculate size for 2x2 tiles
        tile_size = TILE_SIZE * zoom_level
        size = tile_size * 2  # 2x2 tiles
        
        # Create surface with transparency
        life_support_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if component.under_construction:
            # Draw construction progress
            progress = component.construction_progress / component.construction_time
            height = size * progress
            
            # Base structure (gray)
            pygame.draw.rect(life_support_surface, (128, 128, 128, 180),
                           (0, size - height, size, height))
            
            # Construction scaffolding
            scaffold_color = (200, 200, 200, 100)
            for i in range(4):
                x = size * (i / 3)
                pygame.draw.line(life_support_surface, scaffold_color,
                               (x, size), (x, 0), max(1, int(2 * zoom_level)))
        else:
            # Main body
            margin = size * 0.1
            body_rect = (margin, margin, size - 2*margin, size - 2*margin)
            if component.is_powered and component.is_active:
                body_color = (100, 150, 255, 255)  # Blue when active
            else:
                body_color = (80, 100, 150, 255)  # Darker blue when inactive
            pygame.draw.rect(life_support_surface, body_color, body_rect)
            
            # Draw ventilation grills
            grill_color = (192, 192, 192, 255)
            grill_spacing = size * 0.2
            grill_height = size * 0.1
            for i in range(3):
                y_pos = size * 0.3 + (i * grill_spacing)
                pygame.draw.rect(life_support_surface, grill_color,
                               (margin * 2, y_pos, size - 4*margin, grill_height))
            
            # Draw oxygen particles when active
            if component.is_active:
                particle_color = (150, 220, 255, 150)  # Light blue particles
                current_time = pygame.time.get_ticks() / 1000.0
                for i in range(6):
                    # Create flowing particle effect
                    offset = (current_time * 2 + i/2) % 1.0
                    particle_x = size * (0.3 + 0.4 * (i/5))
                    particle_y = size * (0.2 + offset * 0.6)
                    particle_size = max(2, int(4 * zoom_level))
                    pygame.draw.circle(life_support_surface, particle_color,
                                    (particle_x, particle_y), particle_size)
            
            # Status indicator light
            status_color = (0, 255, 0, 200) if component.is_active else (255, 0, 0, 200)
            pygame.draw.circle(life_support_surface, status_color,
                             (size - margin*2, margin*2), max(3, int(5 * zoom_level)))
        
        # Blit to main surface
        surface.blit(life_support_surface, (screen_x, screen_y))
