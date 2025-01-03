import pygame
from components.render_component import RenderComponent

class AlienRenderComponent(RenderComponent):
    def __init__(self, entity, color=(255, 192, 203, 128)):  # Pink with alpha
        super().__init__(entity, color)
        self.selected = False

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """
        Render the alien with detailed body parts and effects.
        """
        # Get zoom level from game state (default to 1 if not available)
        zoom_level = getattr(self.entity.game_state, 'zoom_level', 1)
        
        # Calculate screen position with zoom
        screen_x = (self.entity.position.x - camera_x) * zoom_level
        screen_y = (self.entity.position.y - camera_y) * zoom_level
        
        # Create a surface with alpha for the alien scaled by zoom
        scaled_size = pygame.Vector2(self.entity.size.x * zoom_level, 
                                   self.entity.size.y * zoom_level)
        alien_surface = pygame.Surface((scaled_size.x, scaled_size.y), pygame.SRCALPHA)
        
        # Modify color if dead
        if self.entity.health and self.entity.health.is_corpse:
            # Desaturate and darken the color for dead state
            dead_color = (
                min(255, self.color[0] * 0.5),
                min(255, self.color[1] * 0.5),
                min(255, self.color[2] * 0.5),
                self.color[3] * 0.8  # More transparent when dead
            )
            render_color = dead_color
        else:
            render_color = self.color
        
        # Draw alien body (oval)
        ellipse_rect = (0, scaled_size.y * 0.2, scaled_size.x, scaled_size.y * 0.6)
        pygame.draw.ellipse(alien_surface, render_color, ellipse_rect)
        
        # Draw alien head (circle)
        head_size = scaled_size.x * 0.6
        pygame.draw.circle(alien_surface, render_color,
                         (scaled_size.x/2, scaled_size.y * 0.3),
                         head_size/2)
        
        if self.entity.health and self.entity.health.is_corpse:
            # Draw X eyes for dead state
            eye_size = head_size * 0.3
            eye_y = scaled_size.y * 0.25
            eye_offset = eye_size * 0.5
            
            # Left X eye
            pygame.draw.line(alien_surface, (0, 0, 0),
                            (scaled_size.x/2 - eye_size - eye_offset, eye_y - eye_offset),
                            (scaled_size.x/2 - eye_size + eye_offset, eye_y + eye_offset),
                            max(1, int(2 * zoom_level)))
            pygame.draw.line(alien_surface, (0, 0, 0),
                            (scaled_size.x/2 - eye_size - eye_offset, eye_y + eye_offset),
                            (scaled_size.x/2 - eye_size + eye_offset, eye_y - eye_offset),
                            max(1, int(2 * zoom_level)))
            
            # Right X eye
            pygame.draw.line(alien_surface, (0, 0, 0),
                            (scaled_size.x/2 + eye_size - eye_offset, eye_y - eye_offset),
                            (scaled_size.x/2 + eye_size + eye_offset, eye_y + eye_offset),
                            max(1, int(2 * zoom_level)))
            pygame.draw.line(alien_surface, (0, 0, 0),
                            (scaled_size.x/2 + eye_size - eye_offset, eye_y + eye_offset),
                            (scaled_size.x/2 + eye_size + eye_offset, eye_y - eye_offset),
                            max(1, int(2 * zoom_level)))
            
            # Draw squiggly mouth
            mouth_y = scaled_size.y * 0.35
            points = []
            for i in range(8):
                x = scaled_size.x * (0.3 + 0.05 * i)
                y = mouth_y + (scaled_size.y * 0.02 * (-1 if i % 2 == 0 else 1))
                points.append((x, y))
            pygame.draw.lines(alien_surface, (0, 0, 0), False, points, 
                             max(1, int(2 * zoom_level)))
            
            # Add some floating "spirit particles" rising up
            for i in range(3):
                particle_x = scaled_size.x * (0.3 + 0.2 * i)
                particle_y = scaled_size.y * (0.2 + 0.1 * i)
                pygame.draw.circle(alien_surface, (255, 255, 255, 100),
                                 (particle_x, particle_y),
                                 max(1, int(3 * zoom_level)))
        else:
            # Normal alive eyes
            eye_size = head_size * 0.3
            eye_y = scaled_size.y * 0.25
            pygame.draw.circle(alien_surface, (0, 0, 0),
                             (scaled_size.x/2 - eye_size, eye_y), eye_size/2)
            pygame.draw.circle(alien_surface, (0, 0, 0),
                             (scaled_size.x/2 + eye_size, eye_y), eye_size/2)
        
        # Draw alien tentacles (droopy if dead)
        tentacle_color = tuple(max(0, min(255, c + 30)) for c in render_color[:3]) + (render_color[3],)
        for i in range(3):
            start_x = scaled_size.x * (0.3 + 0.2 * i)
            if self.entity.health and self.entity.health.is_corpse:
                # Droopy curved tentacles for dead state
                control_x = start_x + scaled_size.x * 0.1
                end_x = start_x + scaled_size.x * 0.15
                pygame.draw.arc(alien_surface, tentacle_color,
                              (start_x - scaled_size.x * 0.1,
                               scaled_size.y * 0.7,
                               scaled_size.x * 0.3,
                               scaled_size.y * 0.3),
                              0, 3.14, max(1, int(3 * zoom_level)))
            else:
                # Normal straight tentacles
                pygame.draw.line(alien_surface, tentacle_color,
                               (start_x, scaled_size.y * 0.8),
                               (start_x, scaled_size.y),
                               max(1, int(3 * zoom_level)))
        
        # Blit the alien to the screen
        surface.blit(alien_surface,
                    (screen_x - scaled_size.x/2,
                     screen_y - scaled_size.y/2))
        
        # Draw selection circle when selected
        if self.selected:
            pygame.draw.circle(surface, (255, 255, 0),
                             (int(screen_x), int(screen_y)),
                             int(scaled_size.x * 0.75), 
                             max(1, int(2 * zoom_level))) 