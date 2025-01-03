import pygame
from systems.capture_system import CaptureState

class HumanRenderer:
    def __init__(self, color=(200, 150, 150, 200)):
        self.color = color
        self.base_size = 32

    def render(self, entity, surface, camera_x, camera_y):
        # Get zoom level from game state (default to 1 if not available)
        zoom_level = getattr(entity.game_state, 'zoom_level', 1)
        
        # Calculate screen position with zoom
        screen_x = (entity.position.x - camera_x) * zoom_level
        screen_y = (entity.position.y - camera_y) * zoom_level
        
        # Calculate scaled size
        scaled_size = pygame.Vector2(
            entity.size.x * zoom_level, 
            entity.size.y * zoom_level
        )
        human_surface = pygame.Surface((scaled_size.x, scaled_size.y), pygame.SRCALPHA)
        
        # Modify color based on capture state
        render_color = self.color if entity.capture_state == CaptureState.NONE else (*self.color[:3], 150)
        
        # Draw character components
        self._draw_body(human_surface, scaled_size, render_color)
        self._draw_limbs(human_surface, scaled_size, render_color)
        
        # Draw health bar if needed
        health_component = entity.health
        if health_component and health_component.health < health_component.max_health:
            self._draw_health_bar(surface, health_component, screen_x, screen_y, scaled_size)
        
        # Blit the human to the screen
        surface.blit(human_surface, 
                    (screen_x - scaled_size.x/2,
                     screen_y - scaled_size.y/2))

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

    def _draw_limbs(self, surface, scaled_size, color):
        arm_color = tuple(max(0, min(255, c - 20)) for c in color[:3]) + (color[3],)
        line_width = max(1, int(3))
        
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

    def _draw_health_bar(self, surface, health_component, screen_x, screen_y, scaled_size):
        health_width = (scaled_size.x * health_component.health) / health_component.max_health
        bar_height = 3
        
        # Background (red)
        pygame.draw.rect(surface, (255, 0, 0),
                        (screen_x - scaled_size.x/2,
                         screen_y - scaled_size.y/2 - 5,
                         scaled_size.x, bar_height))
        # Foreground (green)
        pygame.draw.rect(surface, (0, 255, 0),
                        (screen_x - scaled_size.x/2,
                         screen_y - scaled_size.y/2 - 5,
                         health_width, bar_height)) 