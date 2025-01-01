import pygame
from components.base_component import Component
from components.selectable_component import SelectableComponent

class MovementComponent(Component):
    def __init__(self, entity, speed: float = 300):
        super().__init__(entity)
        self.speed = speed
        self.target_position = None
        self.moving = False
        self.position = pygame.math.Vector2(entity.position)  # Track position separately

    def set_target_position(self, pixel_x: float, pixel_y: float) -> None:
        """Set movement target in pixel coordinates"""
        self.target_position = pygame.math.Vector2(pixel_x, pixel_y)
        self.moving = True

    def update(self, dt: float) -> None:
        """Update entity position"""
        if not self.moving or not self.target_position:
            return

        try:
            # Calculate movement direction and distance
            direction = self.target_position - self.position
            distance = direction.length()
            
            if distance < 1:  # Reached target (smaller threshold)
                self.position = pygame.math.Vector2(self.target_position)
                self.entity.position = pygame.math.Vector2(self.position)
                self.moving = False
                self.target_position = None
            else:
                # Normalize direction and apply movement
                normalized_dir = direction.normalize()
                movement = normalized_dir * self.speed * dt
                
                # Check if we would overshoot
                if movement.length() > distance:
                    self.position = pygame.math.Vector2(self.target_position)
                else:
                    self.position += movement
                
                # Update entity position
                self.entity.position.x = round(self.position.x)
                self.entity.position.y = round(self.position.y)
                
        except (TypeError, AttributeError) as e:
            self.moving = False
            self.target_position = None

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Draw movement debug info"""
        if self.moving and self.target_position:
            # Draw line to target
            start_pos = (
                int(self.entity.position.x - camera_x),
                int(self.entity.position.y - camera_y)
            )
            end_pos = (
                int(self.target_position.x - camera_x),
                int(self.target_position.y - camera_y)
            )
            # Draw movement line
            pygame.draw.line(surface, (255, 255, 0), start_pos, end_pos, 2)
            # Draw current position marker
            pygame.draw.circle(surface, (255, 0, 0), start_pos, 3)
            # Draw target marker
            pygame.draw.circle(surface, (0, 255, 0), end_pos, 3) 