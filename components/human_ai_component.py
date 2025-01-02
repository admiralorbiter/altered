from components.base_component import Component
from components.movement_component import MovementComponent
from components.pathfinding_component import PathfindingComponent
from components.health_component import HealthComponent
from utils.config import TILE_SIZE
import pygame
import random

class HumanAIComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.state = 'patrol'
        self.target = None
        self.attack_range = entity.attack_range  # Use entity's attack range
        self.detection_range = TILE_SIZE * 8  # Detection range
        self.attack_cooldown = entity.attack_cooldown  # Use entity's cooldown
        self.attack_timer = 0.0
        self.path_update_timer = 0.3
        self._movement = None
        self._pathfinding = None
        self.last_known_position = None
        self.position_timeout = 1.0  # Time before considering last known position stale
        self.position_timer = 0.0
        
    def start(self) -> None:
        """Get references to required components"""
        self._movement = self.entity.get_component(MovementComponent)
        self._pathfinding = self.entity.get_component(PathfindingComponent)

    def update(self, dt: float) -> None:
        """Update AI behavior"""
        if not self._movement or not self._pathfinding:
            self._movement = self.entity.get_component(MovementComponent)
            self._pathfinding = self.entity.get_component(PathfindingComponent)
            return

        # Update attack cooldown
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Find nearest target and update state
        nearest_target, distance = self._find_nearest_target()
        
        # Update state based on distance
        if nearest_target:
            if distance <= self.attack_range:
                self._change_state('attack')
                self.target = nearest_target
            elif distance <= self.detection_range:
                if self.state != 'chase' or self.target != nearest_target:
                    self._change_state('chase')
                    self.target = nearest_target
                    self._update_chase_path()
            else:
                self._change_state('patrol')
                self.target = None
        else:
            self._change_state('patrol')
            self.target = None

        # Handle state behaviors
        if self.state == 'chase' and self.target:
            # Always try to move closer if in detection range but not in attack range
            distance = (self.target.position - self.entity.position).length()
            if distance > self.attack_range:
                self.path_update_timer -= dt
                if self.path_update_timer <= 0 or not self._movement.moving:
                    self._update_chase_path()
            else:
                # Stop moving if in attack range
                if self._movement.moving:
                    self._movement.stop()
        elif self.state == 'attack':
            self._handle_attack_state()
        elif self.state == 'patrol':
            self._handle_patrol_state()

    def _handle_attack_state(self) -> None:
        """Handle attack behavior"""
        if not self.target:
            return
            
        if self.attack_timer <= 0:
            if hasattr(self.entity, 'attack'):
                self.entity.attack(self.target)
                self.attack_timer = self.attack_cooldown

    def _handle_patrol_state(self) -> None:
        """Handle patrol behavior"""
        if not self._movement.moving and hasattr(self.entity, 'patrol_points'):
            if self.entity.patrol_points:
                current_point = self.entity.patrol_points[self.entity.current_patrol_index]
                target_x = (current_point[0] + 0.5) * TILE_SIZE
                target_y = (current_point[1] + 0.5) * TILE_SIZE
                
                if self._pathfinding.set_target(target_x, target_y):
                    self.entity.current_patrol_index = (
                        self.entity.current_patrol_index + 1
                    ) % len(self.entity.patrol_points)

    def _find_nearest_target(self):
        """Find nearest valid target and distance"""
        min_distance = float('inf')
        nearest_target = None
        
        level = self.entity.game_state.current_level
        
        # Check aliens first, then cats
        potential_targets = []
        if hasattr(level, 'aliens'):
            potential_targets.extend(alien for alien in level.aliens if alien.active)
        if hasattr(level, 'cats'):
            potential_targets.extend(cat for cat in level.cats if cat.active and not cat.is_dead)
        
        # Find nearest target that we can path to
        for target in potential_targets:
            distance = (target.position - self.entity.position).length()
            if distance < min_distance and distance <= self.detection_range:
                # Check if we can path to a tile near the target
                target_tile = (
                    int(target.position.x // TILE_SIZE),
                    int(target.position.y // TILE_SIZE)
                )
                # Try tiles around the target
                for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                    check_tile = (target_tile[0] + dx, target_tile[1] + dy)
                    if self._pathfinding.can_reach(
                        check_tile[0] * TILE_SIZE,
                        check_tile[1] * TILE_SIZE
                    ):
                        min_distance = distance
                        nearest_target = target
                        break
                    
        return nearest_target, min_distance

    def _change_state(self, new_state: str) -> None:
        """Change AI state and reset relevant flags"""
        self.state = new_state
        if new_state == 'chase':
            # Make sure movement is enabled when starting chase
            movement = self.entity.get_component(MovementComponent)
            if movement:
                movement.allow_movement()
    
    def _update_chase_path(self) -> None:
        """Update path to target with better position tracking"""
        if not self.target or not self._pathfinding:
            return

        target_tile = (
            int(self.target.position.x // TILE_SIZE),
            int(self.target.position.y // TILE_SIZE)
        )
        
        # Try to find a valid adjacent tile to move to
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            check_tile = (target_tile[0] + dx, target_tile[1] + dy)
            target_x = (check_tile[0] + 0.5) * TILE_SIZE
            target_y = (check_tile[1] + 0.5) * TILE_SIZE
            
            if self._pathfinding.set_target(target_x, target_y):
                self.path_update_timer = 0.5
                return
            
        # If no adjacent tiles work, try diagonal tiles
        for dx, dy in [(1,1), (-1,1), (1,-1), (-1,-1)]:
            check_tile = (target_tile[0] + dx, target_tile[1] + dy)
            target_x = (check_tile[0] + 0.5) * TILE_SIZE
            target_y = (check_tile[1] + 0.5) * TILE_SIZE
            
            if self._pathfinding.set_target(target_x, target_y):
                self.path_update_timer = 0.5
                return
        
        # If no path found, use shorter update timer
        self.path_update_timer = 0.3 