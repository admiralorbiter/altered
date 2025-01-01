import random
from components.base_component import Component
from components.movement_component import MovementComponent
from components.task_component import TaskComponent
from utils.types import EntityState, TaskType
from entities.items.food import Food
from utils.config import TILE_SIZE

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

        # Check hunger state first (survival priority)
        if self.entity.hunger.is_critical and self.state != EntityState.SEEKING_FOOD:
            self._switch_state(EntityState.SEEKING_FOOD)

        # State-based behavior updates
        if self.state == EntityState.WORKING:
            self._update_working(dt)
        elif self.state == EntityState.WANDERING:
            self._update_wandering(dt)
        elif self.state == EntityState.SEEKING_FOOD:
            self._update_seeking_food(dt)
        elif self.state == EntityState.IDLE:
            self._update_idle(dt)

    def _update_wandering(self, dt: float) -> None:
        """Controls random exploration behavior"""
        # Check for tasks first
        if not self._task.has_task():
            task = self.entity.game_state.task_system.get_available_task(self.entity)
            if task and self._task.start_task(task):
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
        self.idle_timer -= dt
        if self.idle_timer <= 0:
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)

    def _update_working(self, dt: float) -> None:
        """Handles task execution state"""
        if not self._task.has_task():
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)

    def _update_seeking_food(self, dt: float) -> None:
        """Manages food-seeking behavior"""
        # Find nearest food item
        nearest_food = None
        min_distance = float('inf')
        
        # Look through all items in the level
        for item in self.entity.game_state.current_level.entity_manager.items:
            if isinstance(item, Food):
                distance = (item.position - self.entity.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_food = item
        
        if nearest_food:
            # If we're close enough to the food, consume it
            if min_distance < TILE_SIZE:
                if nearest_food.use(self.entity):
                    self.entity.game_state.current_level.entity_manager.remove_item(nearest_food)
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
            # If no food is found, go back to wandering
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)

    def _switch_state(self, new_state: EntityState) -> None:
        """Handle state transitions"""
        old_state = self.state
        self.state = new_state
        
        # Reset relevant timers and states
        if new_state == EntityState.WANDERING:
            self.wander_timer = random.uniform(3.0, 8.0)
        elif new_state == EntityState.IDLE:
            self.idle_timer = random.uniform(2.0, 5.0) 