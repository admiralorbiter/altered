from typing import Optional, List, Tuple
import pygame
from utils.pathfinding import find_path
from utils.config import TILE_SIZE

class MovementHandler:
    def __init__(self, entity):
        self.entity = entity
        self.path: Optional[List[Tuple[int, int]]] = None
        self.current_waypoint: int = 0
        self.moving: bool = False
        self.target_position: Optional[pygame.math.Vector2] = None
        self.arrival_threshold: float = 1.0  # How close we need to be to count as "arrived"

    def start_path_to_position(self, target_pos: pygame.math.Vector2) -> bool:
        """Start moving to a target position"""
        current_pos = (
            int(self.entity.position.x // TILE_SIZE), 
            int(self.entity.position.y // TILE_SIZE)
        )
        target_tile = (
            int(target_pos.x // TILE_SIZE), 
            int(target_pos.y // TILE_SIZE)
        )
        
        # Don't pathfind to current position
        if current_pos == target_tile:
            print(f"Already at target position {target_tile}")
            return False
        
        print(f"\nEntity {id(self.entity)} finding path:")
        print(f"From: {current_pos}")
        print(f"To: {target_tile}")
        
        self.path = find_path(
            current_pos, 
            target_tile, 
            self.entity.game_state.current_level.tilemap,
            self.entity.game_state,
            self.entity
        )
        
        if not self.path:
            print(f"No path found!")
            return False
        
        print(f"Found path: {self.path}")
        self.current_waypoint = 0
        next_tile = self.path[self.current_waypoint]
        self.target_position = pygame.math.Vector2(
            (next_tile[0] + 0.5) * TILE_SIZE,
            (next_tile[1] + 0.5) * TILE_SIZE
        )
        self.moving = True
        return True

    def start_random_movement(self, range_x: int = 5, range_y: int = 5) -> bool:
        """Start moving to a random position within range"""
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