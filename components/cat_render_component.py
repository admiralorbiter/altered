import pygame
from components.base_component import Component
from utils.config import TILE_SIZE

class CatRenderComponent(Component):
    def __init__(self, entity, color):
        super().__init__(entity)
        # Store cat-specific rendering properties
        self.color = color
        self.base_size = 20
        self.ear_color = (
            min(color[0] + 30, 255),
            min(color[1] + 30, 255),
            min(color[2] + 30, 255)
        )

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Render the cat with camera offset and zoom"""
        # Get zoom level from game state
        zoom_level = self.entity.game_state.zoom_level
        
        # Calculate screen position
        screen_x = (self.entity.position.x - camera_x) * zoom_level
        screen_y = (self.entity.position.y - camera_y) * zoom_level
        
        # Base size scaled by zoom
        base_size = int(self.base_size * zoom_level)
        
        # Create a surface for the cat with transparency
        cat_surface = pygame.Surface((base_size * 3, base_size * 3), pygame.SRCALPHA)
        
        # Draw body (circle)
        pygame.draw.circle(cat_surface, self.color, 
                         (base_size * 1.5, base_size * 1.5), 
                         base_size)
        
        # Draw ears (triangles)
        ear_points_left = [
            (base_size, base_size),
            (base_size * 0.7, base_size * 0.5),
            (base_size * 1.3, base_size * 0.7)
        ]
        ear_points_right = [
            (base_size * 2, base_size),
            (base_size * 1.7, base_size * 0.7),
            (base_size * 2.3, base_size * 0.5)
        ]
        pygame.draw.polygon(cat_surface, self.ear_color, ear_points_left)
        pygame.draw.polygon(cat_surface, self.ear_color, ear_points_right)
        
        # Draw eyes (small circles)
        eye_color = (50, 50, 50)  # Dark grey
        eye_size = max(2, int(base_size * 0.2))
        pygame.draw.circle(cat_surface, eye_color,
                         (int(base_size * 1.2), int(base_size * 1.3)),
                         eye_size)
        pygame.draw.circle(cat_surface, eye_color,
                         (int(base_size * 1.8), int(base_size * 1.3)),
                         eye_size)
        
        # Draw nose (small triangle)
        nose_points = [
            (base_size * 1.5, base_size * 1.5),
            (base_size * 1.4, base_size * 1.6),
            (base_size * 1.6, base_size * 1.6)
        ]
        pygame.draw.polygon(cat_surface, (255, 192, 203), nose_points)  # Pink nose
        
        # Draw whiskers (lines)
        whisker_color = (200, 200, 200)  # Light grey
        whisker_length = base_size * 0.8
        whisker_start_left = (base_size * 1.2, base_size * 1.6)
        whisker_start_right = (base_size * 1.8, base_size * 1.6)
        
        for angle in [-20, 0, 20]:  # Three whiskers on each side
            # Left whiskers
            end_x = whisker_start_left[0] - whisker_length * pygame.math.Vector2(1, 0).rotate(angle).x
            end_y = whisker_start_left[1] + whisker_length * pygame.math.Vector2(1, 0).rotate(angle).y
            pygame.draw.line(cat_surface, whisker_color, 
                           whisker_start_left, (end_x, end_y), 
                           max(1, int(zoom_level)))
            
            # Right whiskers
            end_x = whisker_start_right[0] + whisker_length * pygame.math.Vector2(1, 0).rotate(-angle).x
            end_y = whisker_start_right[1] + whisker_length * pygame.math.Vector2(1, 0).rotate(-angle).y
            pygame.draw.line(cat_surface, whisker_color, 
                           whisker_start_right, (end_x, end_y), 
                           max(1, int(zoom_level)))
        
        # Draw the cat at its position (using screen coordinates)
        surface.blit(cat_surface, 
                    (screen_x - base_size * 1.5,
                     screen_y - base_size * 1.5))
        
        # Draw health and hunger bars if needed
        health = self.entity.health.health if hasattr(self.entity.health, 'health') else 100
        max_health = self.entity.health.max_health if hasattr(self.entity.health, 'max_health') else 100
        hunger = self.entity.hunger.hunger if hasattr(self.entity.hunger, 'hunger') else 100
        max_hunger = self.entity.hunger.max_hunger if hasattr(self.entity.hunger, 'max_hunger') else 100

        if health < max_health or hunger < max_hunger:
            # Health bar (red/green)
            health_width = (base_size * 2 * health) / max_health
            pygame.draw.rect(surface, (255, 0, 0),  # Red background
                           (screen_x - base_size,
                            screen_y - base_size * 2,
                            base_size * 2, max(2, int(zoom_level * 2))))
            pygame.draw.rect(surface, (0, 255, 0),  # Green health
                           (screen_x - base_size,
                            screen_y - base_size * 2,
                            health_width, max(2, int(zoom_level * 2))))

            # Hunger bar (brown/gold)
            hunger_width = (base_size * 2 * hunger) / max_hunger
            pygame.draw.rect(surface, (139, 69, 19),  # Brown background
                           (screen_x - base_size,
                            screen_y - base_size * 1.7,  # Position it below health bar
                            base_size * 2, max(2, int(zoom_level * 2))))
            pygame.draw.rect(surface, (255, 198, 0),  # Gold hunger
                           (screen_x - base_size,
                            screen_y - base_size * 1.7,
                            hunger_width, max(2, int(zoom_level * 2))))
