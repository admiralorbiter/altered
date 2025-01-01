import pygame

from systems.capture_system import CaptureState
from .base_renderer import BaseRenderer

class DetectionRangeRenderer(BaseRenderer):
    def render(self, entity, surface, camera_x, camera_y):
        if entity.capture_state != CaptureState.NONE:
            return
            
        screen_x, screen_y = self.get_screen_position(entity, camera_x, camera_y)
        zoom_level = entity.game_state.zoom_level
        
        # Calculate detection range
        range_radius = entity.detection_range * zoom_level
        range_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
        
        # Different colors for chase vs normal state
        if entity.state == 'chase':
            color = (255, 0, 0, 30)  # Red for chase
        else:
            color = (100, 100, 100, 30)  # Gray for normal
            
        pygame.draw.circle(range_surface, color, 
                          (range_radius, range_radius), range_radius)
                          
        surface.blit(range_surface, 
                    (screen_x - range_radius, screen_y - range_radius)) 