import pygame
import random
from utils.types import EntityState, TaskType
from .base_entity import Entity
from utils.config import *
from utils.task_handler import TaskHandler
from utils.movement_handler import MovementHandler

class Cat(Entity):
    def __init__(self, x, y, game_state):
        # Convert tile coordinates to pixel coordinates
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        # Basic stats
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.speed = random.uniform(250, 350)  # Varying speed between cats
        self.morale = 100
        
        # Hunger system
        self.hunger = 100  # Start full
        self.max_hunger = 100
        self.hunger_rate = 2  # Lose 2 hunger per second
        self.critical_hunger = 10  # Percentage when cat starts seeking food
        self.is_dead = False
        
        # State and handlers
        self.state = EntityState.WANDERING
        self.game_state = game_state
        self.task_handler = TaskHandler(self)
        self.movement_handler = MovementHandler(self, game_state)
        
        # Timers
        self.wander_timer = random.uniform(3.0, 8.0)
        self.idle_timer = 0
        
        # Visual properties
        self.color = (random.randint(150, 200), 
                     random.randint(150, 200), 
                     random.randint(150, 200))
        self.size = pygame.math.Vector2(20, 20)

    def update(self, dt):
        """Main update loop"""
        if self.is_dead:
            return

        # Update hunger first (survival priority)
        self._update_hunger(dt)

        # Only check for tasks if we're not already working
        if self.state != EntityState.WORKING:
            if not self.task_handler.has_task():
                task = self.game_state.task_system.get_available_task(self)
                if task:
                    if self.task_handler.start_task(task):
                        self._switch_state(EntityState.WORKING)
                        return

        # Regular state updates
        if self.state == EntityState.WORKING:
            self._update_working(dt)
        elif self.state == EntityState.WANDERING:
            self._update_wandering(dt)
        elif self.state == EntityState.SEEKING_FOOD:
            self._update_seeking_food(dt)
        elif self.state == EntityState.IDLE:
            self._update_idle(dt)

        # Update handlers
        self.movement_handler.update(dt)
        self.task_handler.update(dt)

    def _update_wandering(self, dt):
        """Handle wandering state"""
        # Check for tasks first
        if not self.task_handler.has_task():
            task = self.game_state.task_system.get_available_task(self)
            if task:
                print(f"\n=== TASK ASSIGNMENT ===")
                print(f"Cat {id(self)} received task at {task.position}")
                print(f"Task type: {task.type}")
                if self.task_handler.start_task(task):
                    print(f"Task started successfully, switching to WORKING")
                    self._switch_state(EntityState.WORKING)
                    return
                else:
                    print(f"Failed to start task, returning task to pool")
                    self.game_state.task_system.return_task(task)

        # Normal wandering behavior
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            self._switch_state(EntityState.IDLE)
            self.idle_timer = random.uniform(2.0, 5.0)
        elif self.movement_handler.has_arrived:
            self.movement_handler.start_random_movement()

    def _update_working(self, dt):
        """Handle working state"""
        if not self.task_handler.has_task():
            print(f"Cat {id(self)} has no task, switching to wandering")
            self._switch_state(EntityState.WANDERING)
            return

        task_pos = self.task_handler.get_task_position()
        if not task_pos:
            print(f"Cat {id(self)} has task but no position")
            return
        
        current_tile = (
            int(self.position.x // TILE_SIZE),
            int(self.position.y // TILE_SIZE)
        )
        
        print(f"\n=== CAT WORKING UPDATE ===")
        print(f"Cat {id(self)} at {current_tile}")
        print(f"Task at {task_pos}")
        
        # If we're close enough, work on the task
        dx = abs(task_pos[0] - current_tile[0])
        dy = abs(task_pos[1] - current_tile[1])
        
        if dx <= 1 and dy <= 1:
            print(f"Cat {id(self)} within range, working on wire")
            self.movement_handler.stop()  # Only stop when we're ready to work
            self.task_handler.update(dt)
            return
        
        # Move to task if not already moving
        if not self.movement_handler.moving:
            target_pos = pygame.math.Vector2(
                task_pos[0] * TILE_SIZE + TILE_SIZE/2,
                task_pos[1] * TILE_SIZE + TILE_SIZE/2
            )
            print(f"Cat {id(self)} starting movement to wire at {task_pos}")
            self.movement_handler.allow_movement()  # Allow movement before pathfinding
            success = self.movement_handler.start_path_to_position(target_pos)
            print(f"Movement start success: {success}")

    def _update_seeking_food(self, dt):
        """Handle food seeking state"""
        # TODO: Implement food seeking behavior
        self._switch_state(EntityState.WANDERING)

    def _update_idle(self, dt):
        """Handle idle state"""
        # Check for tasks first
        if not self.task_handler.has_task():
            task = self.game_state.task_system.get_available_task(self)
            if task:
                self.task_handler.start_task(task)
                self._switch_state(EntityState.WORKING)
                return

        # Normal idle behavior
        self.idle_timer -= dt
        if self.idle_timer <= 0:
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)

    def _update_hunger(self, dt):
        """Update hunger system"""
        self.hunger = max(0, self.hunger - self.hunger_rate * dt)
        if self.hunger <= self.critical_hunger:
            self._switch_state(EntityState.SEEKING_FOOD)

    def _switch_state(self, new_state: EntityState):
        """Handle state transitions"""
        if new_state == self.state:
            return
            
        print(f"\n=== STATE CHANGE ===")
        print(f"Cat {id(self)} switching from {self.state} to {new_state}")
        
        self.state = new_state

    def render(self, surface):
        """Render the cat"""
        pygame.draw.circle(surface, self.color, 
                         (int(self.position.x), int(self.position.y)), 
                         self.size) 