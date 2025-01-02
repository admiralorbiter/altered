import random
from components.base_component import Component
from components.hunger_component import HungerComponent
from components.movement_component import MovementComponent
from components.pathfinding_component import PathfindingComponent
from components.task_component import TaskComponent
from utils.types import EntityState, TaskType
from entities.items.food import Food
from utils.config import TILE_SIZE
import pygame
from typing import Optional
import math

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

        # First priority: Check hunger and look for food if critical
        hunger = self.entity.get_component(HungerComponent)
        if hunger and hunger.is_critical:
            if self.state != EntityState.SEEKING_FOOD:
                print(f"[DEBUG] Cat {self.entity.entity_id} is hungry! Hunger: {hunger.hunger}")
                nearest_food = self._find_nearest_food()
                if nearest_food:
                    print(f"[DEBUG] Cat {self.entity.entity_id} found food at {nearest_food.position}")
                    if self._pathfinding.set_target(nearest_food.position.x, nearest_food.position.y):
                        self._change_state(EntityState.SEEKING_FOOD)
                        return

        # Handle food seeking state
        if self.state == EntityState.SEEKING_FOOD:
            if not self._movement.moving:
                # Check if we're near food
                nearest_food = self._find_nearest_food()
                if nearest_food and self._is_near_food(nearest_food):
                    print(f"[DEBUG] Cat {self.entity.entity_id} eating food")
                    nearest_food.use(self.entity)
                    # Remove food from game
                    self.entity.game_state.current_level.entity_manager.remove_item(nearest_food)
                    self._change_state(EntityState.WANDERING)
                else:
                    # No food nearby, go back to wandering
                    self._change_state(EntityState.WANDERING)
            return

        # Normal wandering behavior
        if self.state == EntityState.WANDERING:
            self.wander_timer -= dt
            if not self._movement.moving or self.wander_timer <= 0:
                if self._try_find_task():
                    self._change_state(EntityState.WORKING)
                    return
                self._pick_random_wander_target()
                self.wander_timer = random.uniform(3.0, 8.0)

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

    def _is_near_food(self, food_item: Food) -> bool:
        """Check if we're close enough to eat the food"""
        distance = (food_item.position - self.entity.position).length()
        return distance < TILE_SIZE * 1.5  # Within 1.5 tiles

    def _find_nearest_food(self) -> Optional[Food]:
        """Find the nearest accessible food item"""
        nearest_food = None
        min_distance = float('inf')
        
        for item in self.entity.game_state.current_level.entity_manager.items:
            if isinstance(item, Food):
                distance = (item.position - self.entity.position).length()
                if distance < min_distance:
                    # Check if we can path to this food
                    if self._pathfinding.can_reach(item.position.x, item.position.y):
                        min_distance = distance
                        nearest_food = item
        
        return nearest_food 

    def _pick_random_wander_target(self) -> None:
        """Pick a random position to wander to"""
        if not self._movement or not self._pathfinding:
            return
        
        # Get current position in tiles
        current_x = int(self.entity.position.x / TILE_SIZE)
        current_y = int(self.entity.position.y / TILE_SIZE)
                
        # Try increasingly larger areas until valid path found
        for radius in [2, 3, 4]:
            
            # Try multiple angles at this radius
            angles = [i * (2 * math.pi / 8) + random.uniform(-0.2, 0.2) for i in range(8)]
            random.shuffle(angles)  # Randomize order
            
            for angle in angles:
                dx = int(round(math.cos(angle) * radius))
                dy = int(round(math.sin(angle) * radius))
                
                target_x = current_x + dx
                target_y = current_y + dy
                                
                # Skip if out of bounds
                if not (0 <= target_x < self.entity.game_state.current_level.tilemap.width and 
                       0 <= target_y < self.entity.game_state.current_level.tilemap.height):
                    continue
                
                # Convert to pixel coordinates and try path
                pixel_x = (target_x + 0.5) * TILE_SIZE
                pixel_y = (target_y + 0.5) * TILE_SIZE
                
                if self._pathfinding.set_target(pixel_x, pixel_y):
                    return    