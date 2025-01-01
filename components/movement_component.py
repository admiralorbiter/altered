import pygame
from components.base_component import Component
import random
from utils.config import TILE_SIZE

class MovementComponent(Component):
    def __init__(self, entity, speed: float = 300):
        super().__init__(entity)
        self.speed = speed
        self.target_position = None
        self.moving = False
        self.position = pygame.math.Vector2(entity.position)  # Track position separately
        self._pathfinding = None

    def start(self) -> None:
        """Get reference to pathfinding component"""
        # Import here to avoid circular import
        from components.pathfinding_component import PathfindingComponent
        self._pathfinding = self.entity.get_component(PathfindingComponent)

    @property
    def path(self) -> list:
        """Compatibility property for path access"""
        return self._pathfinding.path if self._pathfinding else []

    @property
    def has_arrived(self) -> bool:
        """Check if entity has arrived at target position"""
        return not self.moving

    def allow_movement(self) -> None:
        """Allow movement to start"""
        self.moving = False
        self.target_position = None

    def start_random_movement(self) -> None:
        """Start movement to a random position"""
        # Get random position within level bounds
        level = self.entity.game_state.current_level
        
        # Get level dimensions safely
        if hasattr(level, 'get_dimensions'):
            width, height = level.get_dimensions()
        elif hasattr(level.tilemap, 'width') and hasattr(level.tilemap, 'height'):
            width, height = level.tilemap.width, level.tilemap.height
        else:
            # Fallback dimensions
            width, height = 20, 20  # Default size if no dimensions available
        
        # Calculate random position in pixels
        x = random.randint(0, width - 1) * TILE_SIZE + TILE_SIZE // 2
        y = random.randint(0, height - 1) * TILE_SIZE + TILE_SIZE // 2
        
        self.set_target_position(x, y)

    def start_path_to_position(self, target_position) -> bool:
        """Start pathfinding to a target position"""
        if not self._pathfinding:
            return False
            
        return self._pathfinding.set_target(
            target_position.x,
            target_position.y
        )

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
            
            if distance < 2:  # Slightly larger threshold
                # Snap to target position
                self.position = pygame.math.Vector2(self.target_position)
                self.entity.position = pygame.math.Vector2(self.position)
                self.moving = False
                self.target_position = None
                # Signal pathfinding that we've reached the waypoint
                if self._pathfinding:
                    self._pathfinding.waypoint_reached()
            else:
                # Normalize direction and apply movement
                normalized_dir = direction.normalize()
                movement = normalized_dir * self.speed * dt
                
                # Update position
                self.position += movement
                self.entity.position = pygame.math.Vector2(self.position)
                
        except (TypeError, AttributeError) as e:
            print(f"[DEBUG] Movement error: {e}")
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

    def stop(self) -> None:
        """Stop current movement and clean up"""
        self.moving = False
        self.target_position = None
        # Clear pathfinding state
        if self._pathfinding:
            self._pathfinding.clear_path() 