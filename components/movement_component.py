import pygame
from components.base_component import Component
from components.selectable_component import SelectableComponent

class MovementComponent(Component):
    def __init__(self, entity, speed: float = 300):
        super().__init__(entity)
        self.speed = speed
        self.target_position = None
        self.moving = False
        print(f"MovementComponent initialized with speed: {speed}")  # Debug

    def set_target_position(self, pixel_x: float, pixel_y: float) -> None:
        """Set movement target in pixel coordinates"""
        print(f"Movement target set: ({pixel_x}, {pixel_y})")  # Debug
        self.target_position = pygame.math.Vector2(pixel_x, pixel_y)
        self.moving = True
        print(f"Current position: {self.entity.position}, Target: {self.target_position}")  # Debug

    def update(self, dt: float) -> None:
        """Update entity position"""
        if not self.moving or not self.target_position:
            return

        # Calculate movement direction and distance
        try:
            direction = pygame.math.Vector2(
                self.target_position.x - self.entity.position.x,
                self.target_position.y - self.entity.position.y
            )
            distance = direction.length()
            
            print(f"\nMOVEMENT UPDATE:")
            print(f"Current position: {self.entity.position}")
            print(f"Target position: {self.target_position}")
            print(f"Distance to target: {distance}")
            print(f"Direction: {direction}")
            print(f"Delta time: {dt}")
            
            if distance < 2:  # Reached target
                self.entity.position.x = self.target_position.x
                self.entity.position.y = self.target_position.y
                self.moving = False
                self.target_position = None
                print("Target reached!")
            else:
                # Normalize direction and apply movement
                direction.scale_to_length(self.speed * dt)
                old_pos = pygame.math.Vector2(self.entity.position)
                self.entity.position += direction
                print(f"Movement vector: {direction}")
                print(f"New position: {self.entity.position}")
                
        except (TypeError, AttributeError) as e:
            print(f"ERROR in movement update: {e}")
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