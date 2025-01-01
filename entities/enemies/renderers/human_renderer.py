import pygame

from systems.capture_system import CaptureState
from .base_renderer import BaseRenderer

class HumanRenderer(BaseRenderer):
    def __init__(self, color):
        self.color = color

    def render(self, entity, surface, camera_x, camera_y):
        screen_x, screen_y = self.get_screen_position(entity, camera_x, camera_y)
        zoom_level = entity.game_state.zoom_level
        
        # Calculate scaled size
        scaled_size = pygame.Vector2(entity.size.x * zoom_level, entity.size.y * zoom_level)
        human_surface = pygame.Surface((scaled_size.x, scaled_size.y), pygame.SRCALPHA)
        
        # Modify color based on capture state
        render_color = self.color if entity.capture_state == CaptureState.NONE else (*self.color[:3], 150)
        
        # Draw character components
        self._draw_body(human_surface, scaled_size, render_color)
        self._draw_limbs(human_surface, scaled_size, render_color, zoom_level)
        
        # Draw health bar if needed
        if entity.health < entity.max_health:
            self._draw_health_bar(surface, entity, screen_x, screen_y, scaled_size, zoom_level)
        
        # Blit the human to the screen
        surface.blit(human_surface, (screen_x - scaled_size.x/2, screen_y - scaled_size.y/2))

    def _draw_body(self, surface, scaled_size, color):
        # Draw body rectangle
        body_rect = (scaled_size.x * 0.3, scaled_size.y * 0.3, 
                    scaled_size.x * 0.4, scaled_size.y * 0.5)
        pygame.draw.rect(surface, color, body_rect)
        
        # Draw head circle
        head_size = scaled_size.x * 0.3
        pygame.draw.circle(surface, color,
                         (scaled_size.x/2, scaled_size.y * 0.25),
                         head_size/2)

    def _draw_limbs(self, surface, scaled_size, color, zoom_level):
        arm_color = tuple(max(0, min(255, c - 20)) for c in color[:3]) + (color[3],)
        line_width = max(1, int(3 * zoom_level))
        
        # Arms
        pygame.draw.line(surface, arm_color,
                        (scaled_size.x * 0.3, scaled_size.y * 0.35),
                        (scaled_size.x * 0.2, scaled_size.y * 0.5), line_width)
        pygame.draw.line(surface, arm_color,
                        (scaled_size.x * 0.7, scaled_size.y * 0.35),
                        (scaled_size.x * 0.8, scaled_size.y * 0.5), line_width)
        
        # Legs
        pygame.draw.line(surface, arm_color,
                        (scaled_size.x * 0.4, scaled_size.y * 0.8),
                        (scaled_size.x * 0.3, scaled_size.y * 0.95), line_width)
        pygame.draw.line(surface, arm_color,
                        (scaled_size.x * 0.6, scaled_size.y * 0.8),
                        (scaled_size.x * 0.7, scaled_size.y * 0.95), line_width)

    def _draw_health_bar(self, surface, entity, screen_x, screen_y, scaled_size, zoom_level):
        health_width = (scaled_size.x * entity.health) / entity.max_health
        bar_height = max(2, 3 * zoom_level)
        
        # Background (red)
        pygame.draw.rect(surface, (255, 0, 0),
                        (screen_x - scaled_size.x/2,
                         screen_y - scaled_size.y/2 - 5 * zoom_level,
                         scaled_size.x, bar_height))
        # Foreground (green)
        pygame.draw.rect(surface, (0, 255, 0),
                        (screen_x - scaled_size.x/2,
                         screen_y - scaled_size.y/2 - 5 * zoom_level,
                         health_width, bar_height)) 