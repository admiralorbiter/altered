import random
from components.base_component import Component
from components.movement_component import MovementComponent
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

    def start(self) -> None:
        """Get references to required components"""
        self._movement = self.entity.get_component(MovementComponent)
        self._task = self.entity.get_component(TaskComponent)

    def update(self, dt: float) -> None:
        """Main AI update loop"""
        if not self.entity.health.is_alive:
            return

        # Execute state-specific behavior first
        if self.state == EntityState.WANDERING:
            self._update_wandering(dt)
        elif self.state == EntityState.IDLE:
            self._update_idle(dt)
        elif self.state == EntityState.WORKING:
            self._update_working(dt)
        elif self.state == EntityState.SEEKING_FOOD:
            self._update_seeking_food(dt)
            return  # Don't do state transitions while actively seeking food

        # Priority 1: Critical hunger - drop everything and find food
        if self.entity.hunger.hunger <= 20:  # Critical hunger threshold
            if self.state != EntityState.SEEKING_FOOD:
                print(f"[DEBUG] Cat switching to SEEKING_FOOD due to critical hunger")
                if self._task.has_task():
                    self._saved_task = self._task.current_task
                    self._task.stop()
                self._switch_state(EntityState.SEEKING_FOOD)
                return

        # Priority 2: Continue existing task
        if self._task.has_task():
            if self.state != EntityState.WORKING:
                print(f"[DEBUG] Cat resuming WORKING state for existing task")
                self._switch_state(EntityState.WORKING)
            return

        # Priority 3: Handle non-critical hunger
        if self.entity.hunger.hunger <= 50 and self.state != EntityState.SEEKING_FOOD:
            nearest_food = self._find_nearest_food()
            if nearest_food:
                print(f"[DEBUG] Cat switching to SEEKING_FOOD due to hunger")
                self._switch_state(EntityState.SEEKING_FOOD)
                return

        # Priority 4: Get new task if not too hungry
        if self.entity.hunger.hunger > 50:  # Only take new tasks if not too hungry
            task = self.entity.game_state.task_system.get_available_task(self.entity)
            if task:
                print(f"[DEBUG] Cat starting new task: {task.type}")
                if self._task.start_task(task):
                    self._switch_state(EntityState.WORKING)
                    return

    def _update_wandering(self, dt: float) -> None:
        """Controls random exploration behavior"""
        # Check for tasks first
        if not self._task.has_task():
            task = self.entity.game_state.task_system.get_available_task(self.entity)
            if task:
                if self._task.start_task(task):
                    self._switch_state(EntityState.WORKING)
                    return

        # Normal wandering behavior
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            self._switch_state(EntityState.IDLE)
            self.idle_timer = random.uniform(2.0, 5.0)
        elif self._movement.has_arrived:
            self._movement.allow_movement()
            self._movement.start_random_movement()

    def _update_idle(self, dt: float) -> None:
        """Manages idle state and transitions"""
        # Check for tasks first
        if not self._task.has_task():
            task = self.entity.game_state.task_system.get_available_task(self.entity)
            if task:
                if self._task.start_task(task):
                    self._switch_state(EntityState.WORKING)
                    return

        self.idle_timer -= dt
        if self.idle_timer <= 0:
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)

    def _update_working(self, dt: float) -> None:
        """Updates the working state"""
        if not self._task.current_task:
            print(f"[DEBUG] No current task, switching to WANDERING")
            self._switch_state(EntityState.WANDERING)
            return

        task_pos = self._task.get_task_position()
        if not task_pos:
            print(f"[DEBUG] No task position available")
            return

        # Get current tile position
        current_tile = (
            int(self.entity.position.x // TILE_SIZE),
            int(self.entity.position.y // TILE_SIZE)
        )

        # Calculate distance to task
        dx = abs(task_pos[0] - current_tile[0])
        dy = abs(task_pos[1] - current_tile[1])
        in_range = dx <= 1 and dy <= 1

        print(f"[DEBUG] Cat position check:")
        print(f"  - Cat pos: ({self.entity.position.x:.1f}, {self.entity.position.y:.1f})")
        print(f"  - Task pos: {task_pos}")
        print(f"  - Distance: dx={dx}, dy={dy}")
        print(f"  - In range: {in_range}")
        print(f"  - Task progress: {self._task.progress:.1f}/{self._task.required_progress}")
        print(f"  - Current task: {self._task.current_task.type}")
        print(f"  - Task assigned to: Cat-{id(self.entity)}")

        # Only complete task if we've reached required progress
        if self._task.progress >= self._task.required_progress:
            print(f"[DEBUG] Task complete (progress={self._task.progress:.1f}), cleaning up and switching to WANDERING")
            self.entity.game_state.task_system.return_task(self._task.current_task)
            self._task.stop()
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)
            return

        if in_range:
            # Update task progress
            task_complete = self._task.update(dt)
            if task_complete:
                self._switch_state(EntityState.WANDERING)
                self.wander_timer = random.uniform(3.0, 8.0)
        else:
            # Move towards task if not in range
            if not self._movement.moving:
                self._movement.allow_movement()
                success = self._movement.start_path_to_position(
                    pygame.math.Vector2(task_pos[0] * TILE_SIZE + TILE_SIZE/2,
                                      task_pos[1] * TILE_SIZE + TILE_SIZE/2)
                )
                if not success:
                    print(f"[DEBUG] Failed to find path to task")
                    self._switch_state(EntityState.WANDERING)

    def _find_best_adjacent_position(self, task_pos, current_tile):
        """Find the best adjacent position to the task"""
        best_pos = None
        min_distance = float('inf')
        
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            new_x = task_pos[0] + dx
            new_y = task_pos[1] + dy
            
            if not self.entity.game_state.current_level.tilemap.is_walkable(new_x, new_y):
                continue
                
            dist = abs(new_x - current_tile[0]) + abs(new_y - current_tile[1])
            print(f"[DEBUG] Checking position ({new_x}, {new_y}): dist={dist}")
            
            if dist < min_distance:
                min_distance = dist
                best_pos = (new_x, new_y)
        
        return best_pos

    def _update_seeking_food(self, dt: float) -> None:
        """Manages food-seeking behavior"""
        # Store the original task if we haven't already
        if not hasattr(self, '_saved_task'):
            self._saved_task = self._task.current_task
            if self._saved_task:
                self.entity.game_state.task_system.return_task(self._saved_task)
        
        nearest_food = self._find_nearest_food()
        
        if nearest_food:
            # If we're close enough to the food, consume it
            if (nearest_food.position - self.entity.position).length() < TILE_SIZE:
                if nearest_food.use(self.entity):
                    self.entity.game_state.current_level.entity_manager.remove_item(nearest_food)
                    # Restore original task if we had one
                    if hasattr(self, '_saved_task') and self._saved_task:
                        if self._task.start_task(self._saved_task):
                            self._switch_state(EntityState.WORKING)
                        delattr(self, '_saved_task')
                    else:
                        self._switch_state(EntityState.WANDERING)
                    return
            
            # If not close enough, move towards the food
            if not self._movement.moving:
                self._movement.allow_movement()
                success = self._movement.start_path_to_position(nearest_food.position)
                if not success:
                    self._switch_state(EntityState.WANDERING)
                    self.wander_timer = random.uniform(3.0, 8.0)
        else:
            # If no food is found, try to restore original task
            if hasattr(self, '_saved_task') and self._saved_task:
                if self._task.start_task(self._saved_task):
                    self._switch_state(EntityState.WORKING)
                delattr(self, '_saved_task')
            else:
                self._switch_state(EntityState.WANDERING)
                self.wander_timer = random.uniform(3.0, 8.0)

    def _switch_state(self, new_state: EntityState) -> None:
        """Switch AI state with logging"""
        old_state = self.state
        print(f"[DEBUG] Cat state transition: {old_state} -> {new_state}")
        print(f"  - Position: ({self.entity.position.x:.1f}, {self.entity.position.y:.1f})")
        print(f"  - Has task: {bool(self._task.current_task)}")
        print(f"  - Is moving: {self._movement.moving}")
        self.state = new_state
        
        # Reset relevant timers and states
        if new_state == EntityState.WANDERING:
            self.wander_timer = random.uniform(3.0, 8.0)
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