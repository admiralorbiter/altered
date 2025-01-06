import pygame
import math

from systems.capture_system import CaptureState
from .base_renderer import BaseRenderer

class FOVRenderer(BaseRenderer):
    def render(self, entity, surface, camera_x, camera_y):
        if entity.capture_state != CaptureState.NONE:
            return
            
        screen_x, screen_y = self.get_screen_position(entity, camera_x, camera_y)
        zoom_level = entity.game_state.zoom_level
        
        # Create FOV surface
        fov_radius = entity.detection_range * zoom_level
        fov_surface = pygame.Surface((fov_radius * 2, fov_radius * 2), pygame.SRCALPHA)
        
        # Calculate FOV points
        center = (fov_radius, fov_radius)
        
        # Calculate the angle based on view direction vector
        direction_angle = math.degrees(math.atan2(entity.view_direction.y, entity.view_direction.x))
        start_angle = direction_angle - entity.fov_angle/2
        end_angle = direction_angle + entity.fov_angle/2
        
        # Draw FOV cone
        points = [center]
        num_points = int(entity.fov_angle)
        for i in range(num_points + 1):
            angle = math.radians(start_angle + (i * entity.fov_angle / num_points))
            x = center[0] + math.cos(angle) * fov_radius
            y = center[1] + math.sin(angle) * fov_radius
            points.append((x, y))
            
        if len(points) > 2:
            pygame.draw.polygon(fov_surface, (255, 255, 0, 30), points)
            
        # Draw direction indicator line
        pygame.draw.line(fov_surface, (255, 255, 0, 128),
                        center,
                        (center[0] + entity.view_direction.x * 30 * zoom_level,
                         center[1] + entity.view_direction.y * 30 * zoom_level),
                        max(1, int(2 * zoom_level)))
        
        surface.blit(fov_surface, 
                    (screen_x - fov_radius,
                     screen_y - fov_radius)) 