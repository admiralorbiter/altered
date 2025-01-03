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
        self.position = pygame.math.Vector2(entity.position)
        self._pathfinding = None
        self._force_stop = False  # New flag to prevent movement

    def start(self) -> None:
        """Get reference to pathfinding component"""
        from components.pathfinding_component import PathfindingComponent
        self._pathfinding = self.entity.get_component(PathfindingComponent)
        self._force_stop = False
        self.moving = False

    @property
    def path(self) -> list:
        """Compatibility property for path access"""
        return self._pathfinding.path if self._pathfinding else []

    @property
    def has_arrived(self) -> bool:
        """Check if entity has arrived at target position"""
        return not self.moving

    def allow_movement(self) -> None:
        """Allow movement again"""
        self._force_stop = False

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
        self._force_stop = False

    def update(self, dt: float) -> None:
        """Smooth movement between tiles"""
        if self._force_stop or not self.moving:
            return

        # Calculate movement with interpolation
        direction = self.target_position - self.position
        distance = direction.length()
        
        if distance < 1.0:
            self._handle_arrival()
        else:
            # Apply easing for smoother movement
            t = min(1.0, (self.speed * dt) / distance)
            t = self._ease_out_quad(t)  # Smooth deceleration
            
            # Interpolate position
            self.position = self.position.lerp(self.target_position, t)
            self.entity.position = pygame.math.Vector2(self.position)

    def _ease_out_quad(self, t: float) -> float:
        """Quadratic easing for smoother movement"""
        return -t * (t - 2)

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Draw movement debug info"""
        # Remove or comment out movement debug visualization
        pass

    def stop(self) -> None:
        """Stop current movement and prevent new movement"""
        self.moving = False
        self.target_position = None
        self._force_stop = True
        # Clear pathfinding state
        if self._pathfinding:
            self._pathfinding.clear_path() 

    def _handle_arrival(self) -> None:
        """Handle entity arrival at target position"""
        self.position = pygame.math.Vector2(self.target_position)
        self.entity.position = pygame.math.Vector2(self.position)
        self.moving = False
        self.target_position = None
        
        # Notify pathfinding component if it exists
        if self._pathfinding:
            self._pathfinding.waypoint_reached() 