import pygame
import random
from entities.items.food import Food
from utils.types import EntityState, TaskType
from .base_entity import Entity
from utils.config import *
from utils.task_handler import TaskHandler
from utils.movement_handler import MovementHandler

class Cat(Entity):
    """
    Autonomous cat entity with complex AI behaviors, hunger system, and task handling.
    Features state-based decision making and dynamic movement patterns.
    """
    def __init__(self, x, y, game_state):
        # Convert tile coordinates to pixel coordinates
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        # Basic stats and attributes
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.speed = random.uniform(250, 350)  # Each cat has unique speed
        self.morale = 100
        
        # Hunger system configuration
        self.hunger = 25  # Start partially hungry
        self.max_hunger = 100
        self.hunger_rate = 2  # Hunger points lost per second
        self.critical_hunger = 10  # Percentage when cat starts seeking food
        self.is_dead = False
        
        # AI state management
        self.state = EntityState.WANDERING
        self.game_state = game_state
        self.task_handler = TaskHandler(self)  # Manages work assignments
        self.movement_handler = MovementHandler(self, game_state)  # Handles pathfinding
        
        # Behavior timers
        self.wander_timer = random.uniform(3.0, 8.0)  # Random wander duration
        self.idle_timer = 0  # Time to remain idle
        
        # Visual customization
        self.color = (random.randint(150, 200),  # Random fur color
                     random.randint(150, 200), 
                     random.randint(150, 200))
        self.base_size = 20  # Physical size for collision
        self.size = pygame.math.Vector2(self.base_size, self.base_size)

    def update(self, dt):
        """
        Main update loop handling state transitions and behaviors.
        Prioritizes survival (hunger) over other activities.
        
        Args:
            dt (float): Delta time since last update
        """
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
        """
        Controls random exploration behavior between tasks.
        Includes task checking and random movement patterns.
        """
        # Check for tasks first
        if not self.task_handler.has_task():
            task = self.game_state.task_system.get_available_task(self)
            if task:
                if self.task_handler.start_task(task):
                    self._switch_state(EntityState.WORKING)
                    return

        # Normal wandering behavior
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            self._switch_state(EntityState.IDLE)
            self.idle_timer = random.uniform(2.0, 5.0)
        elif self.movement_handler.has_arrived:  # Only start new movement if we've arrived
            self.movement_handler.allow_movement()  # Ensure movement is allowed
            self.movement_handler.start_random_movement()

    def _update_working(self, dt):
        """
        Handles work-related behaviors including task navigation and completion.
        Manages transitions between working and other states based on task status.
        """
        if not self.task_handler.has_task():
            self.movement_handler.stop()
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)
            return

        task_pos = self.task_handler.get_task_position()
        if not task_pos:
            self.movement_handler.stop()
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)
            return
        
        current_tile = (
            int(self.position.x // TILE_SIZE),
            int(self.position.y // TILE_SIZE)
        )
        
        # If we're close enough, work on the task
        dx = abs(task_pos[0] - current_tile[0])
        dy = abs(task_pos[1] - current_tile[1])
        
        if dx <= 1 and dy <= 1:
            self.movement_handler.stop()
            self.task_handler.update(dt)
            return
        
        # Move to task if not already moving
        if not self.movement_handler.moving:
            target_pos = pygame.math.Vector2(
                task_pos[0] * TILE_SIZE + TILE_SIZE/2,
                task_pos[1] * TILE_SIZE + TILE_SIZE/2
            )
            self.movement_handler.allow_movement()
            success = self.movement_handler.start_path_to_position(target_pos)
            if not success:
                self._switch_state(EntityState.WANDERING)
                self.wander_timer = random.uniform(3.0, 8.0)

    def _update_seeking_food(self, dt):
        """
        Manages food-seeking behavior when hunger is critical.
        Includes food detection, pathfinding, and consumption logic.
        """
        # Find nearest food item
        nearest_food = None
        min_distance = float('inf')
        
        # Look through all items in the level
        for item in self.game_state.current_level.entity_manager.items:
            if isinstance(item, Food):
                distance = (item.position - self.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_food = item
        
        if nearest_food:
            # If we're close enough to the food, consume it
            if min_distance < TILE_SIZE:
                if nearest_food.use(self):
                    # Remove the food item after consumption
                    self.game_state.current_level.entity_manager.remove_item(nearest_food)
                    self._switch_state(EntityState.WANDERING)
                    return
            
            # If not close enough, move towards the food
            if not self.movement_handler.moving:
                self.movement_handler.allow_movement()
                success = self.movement_handler.start_path_to_position(nearest_food.position)
                if not success:
                    # If we can't path to the food, go back to wandering
                    self._switch_state(EntityState.WANDERING)
                    self.wander_timer = random.uniform(3.0, 8.0)
        else:
            # If no food is found, go back to wandering
            self._switch_state(EntityState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)

    def _update_idle(self, dt):
        """
        Manages idle state behavior and transitions.
        Checks for new tasks and handles timing for state changes.
        """
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
        """
        Updates hunger system and triggers survival behaviors.
        Handles starvation damage and state transitions when hungry.
        """
        self.hunger = max(0, self.hunger - self.hunger_rate * dt)
        
        # If hunger is at 0, start taking damage
        if self.hunger <= 0:
            self.take_damage(5 * dt)  # Lose 5 health per second when starving
        
        # Switch to seeking food if hunger is critical and we're not already seeking
        if self.hunger <= self.critical_hunger and self.state != EntityState.SEEKING_FOOD:
            self._switch_state(EntityState.SEEKING_FOOD)

    def _switch_state(self, new_state: EntityState) -> None:
        """Switch to a new state"""
        
        # Clear any existing movement restrictions when entering wandering state
        if new_state == EntityState.WANDERING:
            self.movement_handler.allow_movement()  # Allow new movements
            self.wander_timer = random.uniform(3.0, 8.0)
        
        self.state = new_state

    def render_with_offset(self, surface, camera_x, camera_y):
        """Render the cat with camera offset and zoom"""
        # Get zoom level from game state
        zoom_level = self.game_state.zoom_level
        
        # Calculate screen position
        screen_x = (self.position.x - camera_x) * zoom_level
        screen_y = (self.position.y - camera_y) * zoom_level
        
        # Base size scaled by zoom
        base_size = int(self.base_size * zoom_level)
        
        # Create a surface for the cat with transparency
        cat_surface = pygame.Surface((base_size * 3, base_size * 3), pygame.SRCALPHA)
        
        # Colors
        body_color = self.color
        ear_color = (min(body_color[0] + 30, 255), 
                    min(body_color[1] + 30, 255), 
                    min(body_color[2] + 30, 255))
        
        # Draw body (circle)
        pygame.draw.circle(cat_surface, body_color, 
                          (base_size * 1.5, base_size * 1.5), 
                          base_size)
        
        # Draw ears (triangles)
        ear_points_left = [
            (base_size, base_size),
            (base_size * 0.7, base_size * 0.5),
            (base_size * 1.3, base_size * 0.7)
        ]
        ear_points_right = [
            (base_size * 2, base_size),
            (base_size * 1.7, base_size * 0.7),
            (base_size * 2.3, base_size * 0.5)
        ]
        pygame.draw.polygon(cat_surface, ear_color, ear_points_left)
        pygame.draw.polygon(cat_surface, ear_color, ear_points_right)
        
        # Draw eyes (small circles)
        eye_color = (50, 50, 50)  # Dark grey
        eye_size = max(2, int(base_size * 0.2))
        pygame.draw.circle(cat_surface, eye_color,
                          (int(base_size * 1.2), int(base_size * 1.3)),
                          eye_size)
        pygame.draw.circle(cat_surface, eye_color,
                          (int(base_size * 1.8), int(base_size * 1.3)),
                          eye_size)
        
        # Draw nose (small triangle)
        nose_points = [
            (base_size * 1.5, base_size * 1.5),
            (base_size * 1.4, base_size * 1.6),
            (base_size * 1.6, base_size * 1.6)
        ]
        pygame.draw.polygon(cat_surface, (255, 192, 203), nose_points)  # Pink nose
        
        # Draw whiskers (lines)
        whisker_color = (200, 200, 200)  # Light grey
        whisker_length = base_size * 0.8
        whisker_start_left = (base_size * 1.2, base_size * 1.6)
        whisker_start_right = (base_size * 1.8, base_size * 1.6)
        
        for angle in [-20, 0, 20]:  # Three whiskers on each side
            # Left whiskers
            end_x = whisker_start_left[0] - whisker_length * pygame.math.Vector2(1, 0).rotate(angle).x
            end_y = whisker_start_left[1] + whisker_length * pygame.math.Vector2(1, 0).rotate(angle).y
            pygame.draw.line(cat_surface, whisker_color, 
                            whisker_start_left, (end_x, end_y), 
                            max(1, int(zoom_level)))
            
            # Right whiskers
            end_x = whisker_start_right[0] + whisker_length * pygame.math.Vector2(1, 0).rotate(-angle).x
            end_y = whisker_start_right[1] + whisker_length * pygame.math.Vector2(1, 0).rotate(-angle).y
            pygame.draw.line(cat_surface, whisker_color, 
                            whisker_start_right, (end_x, end_y), 
                            max(1, int(zoom_level)))
        
        # Draw the cat at its position (using screen coordinates)
        surface.blit(cat_surface, 
                    (screen_x - base_size * 1.5,
                     screen_y - base_size * 1.5))
        
        # Draw health bar if damaged or hungry
        if self.health < self.max_health or self.hunger < self.max_hunger:
            # Calculate screen position for bars
            screen_x = (self.position.x - camera_x) * zoom_level
            screen_y = (self.position.y - camera_y) * zoom_level
            
            # Health bar (red/green)
            health_width = (base_size * 2 * self.health) / self.max_health
            pygame.draw.rect(surface, (255, 0, 0),  # Red background
                            (screen_x - base_size,
                             screen_y - base_size * 2,
                             base_size * 2, max(2, int(zoom_level * 2))))
            pygame.draw.rect(surface, (0, 255, 0),  # Green health
                            (screen_x - base_size,
                             screen_y - base_size * 2,
                             health_width, max(2, int(zoom_level * 2))))

            # Hunger bar (brown/gold)
            hunger_width = (base_size * 2 * self.hunger) / self.max_hunger
            pygame.draw.rect(surface, (139, 69, 19),  # Brown background
                            (screen_x - base_size,
                             screen_y - base_size * 1.7,  # Position it below health bar
                             base_size * 2, max(2, int(zoom_level * 2))))
            pygame.draw.rect(surface, (255, 198, 0),  # Gold hunger
                            (screen_x - base_size,
                             screen_y - base_size * 1.7,
                             hunger_width, max(2, int(zoom_level * 2)))) 

    def take_damage(self, amount):
        """Handle taking damage"""
        if self.is_dead:
            return
        self.health = max(0, self.health - amount)
        
        if self.health <= 0:
            self.die()
            
    def die(self):
        """Handle death"""
        if self.is_dead:
            return
        self.is_dead = True
        self.active = False
        
        # Stop all current actions
        self.movement_handler.stop()
        if self.task_handler:
            self.task_handler.stop() 