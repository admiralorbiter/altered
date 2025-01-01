from typing import Optional, List, Tuple
import pygame
from utils.pathfinding import find_path
from utils.config import TILE_SIZE

class MovementHandler:
    def __init__(self, entity, game_state):
        self.entity = entity
        self.game_state = game_state
        self.path: Optional[List[Tuple[int, int]]] = None
        self.current_waypoint: int = 0
        self.moving: bool = False
        self.target_position: Optional[pygame.math.Vector2] = None
        self.arrival_threshold: float = 1.0
        self.force_stop: bool = False  # New flag to prevent random movement

    def start_path_to_position(self, target_pos):
        """Start pathfinding to a target position"""
        if self.force_stop:
            return False
            
        current_tile = (
            int(self.entity.position.x // TILE_SIZE),
            int(self.entity.position.y // TILE_SIZE)
        )
        target_tile = (
            int(target_pos.x // TILE_SIZE),
            int(target_pos.y // TILE_SIZE)
        )
        
        path = find_path(
            current_tile,
            target_tile,
            self.game_state.current_level.tilemap,
            self.game_state,
            self.entity
        )
        
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
        """Start moving to a random position within range"""
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
        """Update entity movement"""
        if not self.moving or not self.target_position:
            return
        
        # Calculate direction and distance to target
        direction = self.target_position - self.entity.position
        distance = direction.length()
 
        if distance < self.arrival_threshold:
            # Snap to target position when very close
            self.entity.position = pygame.math.Vector2(self.target_position)
            
            # If we have more waypoints, move to next one
            if self.path and self.current_waypoint < len(self.path) - 1:
                self.current_waypoint += 1
                next_tile = self.path[self.current_waypoint]
                self.target_position = pygame.math.Vector2(
                    (next_tile[0] + 0.5) * TILE_SIZE,
                    (next_tile[1] + 0.5) * TILE_SIZE
                )
            else:
                self.moving = False
                self.path = None
                self.target_position = None
            return

        # Normalize direction and apply speed
        if distance > 0:  # Prevent division by zero
            direction = direction / distance
            move_distance = min(self.entity.speed * dt, distance)  # Don't overshoot
            movement = direction * move_distance
            
            # Update position
            self.entity.position += movement

    @property
    def has_arrived(self) -> bool:
        """Check if we've reached the final destination"""
        return not self.moving and not self.path

    def stop(self) -> None:
        """Stop all movement"""
        self.moving = False
        self.path = None
        self.target_position = None
        self.current_waypoint = 0
        self.force_stop = True  # Prevent new movements until explicitly allowed

    def allow_movement(self) -> None:
        """Allow movement again after force stop"""
        self.force_stop = False 