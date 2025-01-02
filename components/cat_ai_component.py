import random
from components.base_component import Component
from components.movement_component import MovementComponent
from components.pathfinding_component import PathfindingComponent
from components.task_component import TaskComponent
from utils.types import EntityState, TaskType
from entities.items.food import Food
from utils.config import TILE_SIZE
import pygame
from typing import Optional

class CatAIComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.state = EntityState.WANDERING
        self.wander_timer = random.uniform(3.0, 8.0)
        self.idle_timer = 0
        self._movement = None
        self._task = None
        self._pathfinding = None

    def start(self) -> None:
        """Get references to required components"""
        self._movement = self.entity.get_component(MovementComponent)
        self._task = self.entity.get_component(TaskComponent)
        self._pathfinding = self.entity.get_component(PathfindingComponent)

    def update(self, dt: float) -> None:
        """Update AI behavior"""
        if not self._movement or not self._pathfinding:
            self._movement = self.entity.get_component(MovementComponent)
            self._pathfinding = self.entity.get_component(PathfindingComponent)
            return
        
        # Always check for tasks if we're wandering and not moving
        if self.state == EntityState.WANDERING and not self._movement.moving:
            if self._try_find_task():
                self._change_state(EntityState.WORKING)
                return
        
        if self.state == EntityState.WORKING:
            # If we don't have a task anymore, go back to wandering
            if not self._task.has_task():
                self._change_state(EntityState.WANDERING)
                return
            
            # If we're at task position and stopped, work on task
            if self._task._is_at_task_position():
                if self._movement.moving:
                    self._movement.stop()  # Force stop when in position
                    return
                
                # Update task progress
                if self._task.update(dt):  # Task completed
                    self._movement.allow_movement()  # Allow movement again
                    self._change_state(EntityState.WANDERING)
                return

            # If not at task position and not moving, try to move there
            if not self._movement.moving:
                task_pos = self._task.get_task_position()
                if not task_pos:
                    self._change_state(EntityState.WANDERING)
                    return

                target_x = task_pos[0] * TILE_SIZE + (TILE_SIZE / 2)
                target_y = task_pos[1] * TILE_SIZE + (TILE_SIZE / 2)
                
                if not self._pathfinding.set_target(target_x, target_y):
                    self._task.stop()
                    self._change_state(EntityState.WANDERING)

        elif self.state == EntityState.WANDERING:
            # Update wander timer
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                # Pick new random position and reset timer
                self._pick_random_wander_target()
                self.wander_timer = random.uniform(3.0, 8.0)

    def _try_find_task(self) -> bool:
        """Attempt to find and claim a task"""
        task = self.entity.game_state.task_system.get_available_task(self.entity)
        if task:
            # Convert current position to tile coordinates
            current_pos = (
                int(self.entity.position.x / TILE_SIZE),
                int(self.entity.position.y / TILE_SIZE)
            )
            
            # Try to find path to task
            path = self._pathfinding.set_target(
                task.position[0] * TILE_SIZE + TILE_SIZE/2,
                task.position[1] * TILE_SIZE + TILE_SIZE/2
            )
            
            if path:
                return self._task.start_task(task)
        return False

    def _change_state(self, new_state: EntityState) -> None:
        """Switch AI state with proper cleanup"""
        self.state = new_state
        
        # Reset relevant timers and states
        if new_state == EntityState.WANDERING:
            self.wander_timer = random.uniform(3.0, 8.0)
            if self._movement:
                self._movement.allow_movement()  # Ensure movement is allowed
        elif new_state == EntityState.IDLE:
            self.idle_timer = random.uniform(2.0, 5.0)

    def _find_nearest_food(self) -> Optional[Food]:
        """Find the nearest food item"""
        nearest_food = None
        min_distance = float('inf')
        
        for item in self.entity.game_state.current_level.entity_manager.items:
            if isinstance(item, Food):
                distance = (item.position - self.entity.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_food = item
        
        return nearest_food 

    def _pick_random_wander_target(self) -> None:
        """Pick a random position to wander to"""
        if not self._movement:
            return
        
        # Get level dimensions
        level = self.entity.game_state.current_level
        if hasattr(level.tilemap, 'width') and hasattr(level.tilemap, 'height'):
            width, height = level.tilemap.width, level.tilemap.height
        else:
            width, height = 20, 20
        
        # Get current position in tiles
        current_x = int(self.entity.position.x / TILE_SIZE)
        current_y = int(self.entity.position.y / TILE_SIZE)
        
        # Try to find a valid position near current position first
        for radius in range(5, 21, 5):  # Try increasingly larger areas
            for _ in range(4):  # Try a few times at each radius
                # Pick random offset within radius
                dx = random.randint(-radius, radius)
                dy = random.randint(-radius, radius)
                
                target_x = (current_x + dx) * TILE_SIZE + (TILE_SIZE / 2)
                target_y = (current_y + dy) * TILE_SIZE + (TILE_SIZE / 2)
                
                # Ensure within bounds
                if 0 <= target_x < width * TILE_SIZE and 0 <= target_y < height * TILE_SIZE:
                    if self._pathfinding.set_target(target_x, target_y):
                        return
        