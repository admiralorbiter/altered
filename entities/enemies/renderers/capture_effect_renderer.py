import pygame
import math
from .base_renderer import BaseRenderer
from systems.capture_system import CaptureState

class CaptureEffectRenderer(BaseRenderer):
    def render(self, entity, surface, camera_x, camera_y):
        if entity.capture_state == CaptureState.NONE:
            return
            
        screen_x, screen_y = self.get_screen_position(entity, camera_x, camera_y)
        zoom_level = entity.game_state.zoom_level
        
        if entity.capture_state == CaptureState.BEING_CARRIED:
            self._render_ufo_effect(surface, screen_x, screen_y, zoom_level)
        elif entity.capture_state == CaptureState.UNCONSCIOUS:
            self._render_unconscious_effect(surface, screen_x, screen_y, zoom_level)

    def _render_ufo_effect(self, surface, screen_x, screen_y, zoom_level):
        # UFO beam effect
        beam_height = int(50 * zoom_level)
        beam_width = int(40 * zoom_level)
        beam_surface = pygame.Surface((beam_width, beam_height), pygame.SRCALPHA)
        
        # Pulsing effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
        alpha = int(50 + (30 * pulse))
        
        # Draw beam
        points = [
            (beam_width//2, 0),
            (0, beam_height),
            (beam_width, beam_height)
        ]
        pygame.draw.polygon(beam_surface, (0, 150, 255, alpha), points)
        
        # Draw UFO
        ufo_radius = int(25 * zoom_level)
        ufo_surface = pygame.Surface((ufo_radius * 2, ufo_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(ufo_surface, (0, 200, 255, alpha + 50), 
                         (ufo_radius, ufo_radius), ufo_radius)
        
        # Blit both effects
        surface.blit(beam_surface, 
                    (screen_x - beam_width//2, 
                     screen_y - beam_height))
        surface.blit(ufo_surface,
                    (screen_x - ufo_radius,
                     screen_y - beam_height - ufo_radius))

    def _render_unconscious_effect(self, surface, screen_x, screen_y, zoom_level):
        font = pygame.font.Font(None, int(20 * zoom_level))
        text = font.render("zZZ", True, (255, 255, 255))
        surface.blit(text, (screen_x - text.get_width()/2, 
                           screen_y - 30 * zoom_level)) 