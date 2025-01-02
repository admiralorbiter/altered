from typing import Optional, List, Tuple
import pygame
from utils.pathfinding import find_path
from utils.config import TILE_SIZE

# Handles entity movement, pathfinding, and position updates in the game world
class MovementHandler:
    """Manages movement behavior for game entities, including pathfinding and position updates"""
    def __init__(self, entity, game_state):
        """
        Initialize the movement handler for an entity
        Args:
            entity: The game entity to handle movement for
            game_state: Current game state containing level and environment info
        """
        self.entity = entity
        self.game_state = game_state
        self.path: Optional[List[Tuple[int, int]]] = None
        self.current_waypoint: int = 0
        self.moving: bool = False
        self.target_position: Optional[pygame.math.Vector2] = None
        self.arrival_threshold: float = 1.0
        self.force_stop: bool = False  # New flag to prevent random movement

    def start_path_to_position(self, target_pos):
        """
        Initiates pathfinding to a specified target position
        Args:
            target_pos: Vector2 representing the target position in world coordinates
        Returns:
            bool: True if a valid path was found, False otherwise
        """
        if self.force_stop:
            return False
            
        # Convert current position to tile coordinates
        current_tile = (
            int(self.entity.position.x // TILE_SIZE),
            int(self.entity.position.y // TILE_SIZE)
        )
        # Convert target position to tile coordinates
        target_tile = (
            int(target_pos.x // TILE_SIZE),
            int(target_pos.y // TILE_SIZE)
        )
        
        # Attempt to find a valid path using A* pathfinding
        path = find_path(
            current_tile,
            target_tile,
            self.game_state.current_level.tilemap,
            self.game_state,
            self.entity
        )
        
        # If path found, initialize movement parameters
        if path:
            self.path = path
            self.current_waypoint = 1 if len(path) > 1 else 0
            self.target_position = target_pos
            self.moving = True
            self.force_stop = False  # Make sure we're not blocked
            return True
        else:
            return False

    def start_random_movement(self, range_x: int = 5, range_y: int = 5) -> bool:
        """
        Initiates movement to a random position within specified range
        Args:
            range_x: Maximum horizontal distance in tiles to move
            range_y: Maximum vertical distance in tiles to move
        Returns:
            bool: True if a valid path was found to random position, False otherwise
        """
        if self.force_stop:
            return False
            
        import random
        current_tile = (
            int(self.entity.position.x // TILE_SIZE), 
            int(self.entity.position.y // TILE_SIZE)
        )
        rand_offset = (
            random.randint(-range_x, range_x), 
            random.randint(-range_y, range_y)
        )
        target_tile = (
            current_tile[0] + rand_offset[0],
            current_tile[1] + rand_offset[1]
        )
        return self.start_path_to_position(pygame.math.Vector2(
            (target_tile[0] + 0.5) * TILE_SIZE,
            (target_tile[1] + 0.5) * TILE_SIZE
        ))

    def update(self, dt: float) -> None:
        """
        Updates entity position based on current movement state
        Args:
            dt: Delta time since last update (in seconds)
        """
        # Skip if not currently moving
        if not self.moving or not self.target_position:
            return
        
        # Calculate vector to target and distance
        direction = self.target_position - self.entity.position
        distance = direction.length()
 
        if distance < self.arrival_threshold:
            # Entity has reached current waypoint
            self.entity.position = pygame.math.Vector2(self.target_position)
            
            # Check for next waypoint in path
            if self.path and self.current_waypoint < len(self.path) - 1:
                # Move to next waypoint
                self.current_waypoint += 1
                next_tile = self.path[self.current_waypoint]
                # Convert tile coordinates to world position (center of tile)
                self.target_position = pygame.math.Vector2(
                    (next_tile[0] + 0.5) * TILE_SIZE,
                    (next_tile[1] + 0.5) * TILE_SIZE
                )
            else:
                # Path completed
                self.moving = False
                self.path = None
                self.target_position = None
            return

        # Calculate movement for this frame
        if distance > 0:  # Prevent division by zero
            direction = direction / distance
            move_distance = min(self.entity.speed * dt, distance)  # Don't overshoot
            movement = direction * move_distance
            
            # Update position
            self.entity.position += movement

    @property
    def has_arrived(self) -> bool:
        """
        Checks if entity has completed its current path
        Returns:
            bool: True if no active movement or path exists
        """
        return not self.moving and not self.path

    def stop(self) -> None:
        """
        Immediately stops all movement and prevents new movement until explicitly allowed
        """
        self.moving = False
        self.path = None
        self.target_position = None
        self.current_waypoint = 0
        self.force_stop = True  # Prevent new movements until explicitly allowed

    def allow_movement(self) -> None:
        """
        Enables movement after a force stop
        """
        self.force_stop = False 