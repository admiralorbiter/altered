import pygame
import random
from enum import Enum

from core.tiles import ElectricalComponent
from entities.items.food import Food
from utils.pathfinding import find_path
from .base_entity import Entity
from utils.config import *
from systems.task_system import TaskType

class CatState(Enum):
    WANDERING = "wandering"
    SEEKING_FOOD = "seeking_food"
    WORKING = "working"
    IDLE = "idle"

class Cat(Entity):
    def __init__(self, x, y, game_state):
        # Convert tile coordinates to pixel coordinates like in Alien class
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
        
        # State tracking
        self.current_task = None
        self.target_position = None
        self.current_tile = (x, y)
        self.moving = False
        self.path = None
        self.current_waypoint = 0
        self.seeking_food = False
        self.target_food = None
        
        # Wire task tracking
        self.wire_task = None
        self.wire_task_queue = []
        
        # Personality traits (randomly assigned)
        self.traits = self._generate_traits()
        
        # Visual properties
        self.color = (random.randint(150, 200), 
                     random.randint(100, 150), 
                     random.randint(50, 100),
                     200)  # Brownish with alpha
        
        # Add state tracking
        self.state = CatState.WANDERING
        self.wander_timer = random.uniform(3.0, 8.0)  # Random wander duration
        self.idle_timer = 0
    
    def _generate_traits(self):
        possible_traits = ['lazy', 'aggressive', 'curious', 'cautious', 'loyal']
        num_traits = random.randint(1, 2)  # Each cat gets 1-2 traits
        return random.sample(possible_traits, num_traits)
    
    def take_damage(self, amount):
        """Handle taking damage"""
        self.health = max(0, self.health - amount)
        # Cats lose morale when damaged
        self.morale = max(0, self.morale - amount * 0.5)
        
        # Check if damage killed the cat
        if self.health <= 0:
            self.is_dead = True
            self.color = (100, 100, 100, 200)  # Gray out dead cats
    
    def find_nearest_food(self):
        """Find the nearest food item"""
        nearest_food = None
        min_distance = float('inf')
        
        for item in self.game_state.current_level.entity_manager.items:
            if isinstance(item, Food) and item.active:
                dx = item.position.x - self.position.x
                dy = item.position.y - self.position.y
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_food = item
        
        return nearest_food
    
    def eat_food(self, food):
        """Consume the food item"""
        if food and food.active:
            self.hunger = min(self.max_hunger, self.hunger + food.nutrition_value)
            self.health = min(self.max_health, self.health + food.nutrition_value * 0.5)
            food.active = False  # Food disappears
            self.seeking_food = False
            self.target_food = None
            return True
        return False
    
    def update(self, dt):
        if self.is_dead:
            return

        # Update hunger
        self.hunger = max(0, self.hunger - self.hunger_rate * dt)
        
        # First priority: Check for tasks regardless of current state
        if not self.current_task and not self.wire_task:
            task = self.game_state.task_system.get_available_task(self)
            if task and task.type == TaskType.WIRE_CONSTRUCTION:
                print(f"Cat {id(self)} got new task: {task.type.value} @ {task.position}")
                self.set_wire_task(task.position, 'wire')
                self.current_task = task
                self._switch_state(CatState.WORKING)
                return

        # State machine update
        if self.hunger < self.critical_hunger:
            self._switch_state(CatState.SEEKING_FOOD)
        
        # Update based on current state
        if self.state == CatState.SEEKING_FOOD:
            self._update_seeking_food(dt)
        elif self.state == CatState.WORKING:
            self._update_working(dt)
        elif self.state == CatState.WANDERING:
            self._update_wandering(dt)
        elif self.state == CatState.IDLE:
            self._update_idle(dt)

        # Handle movement
        if self.moving and self.target_position and self.path:
            self._update_movement(dt)

    def _update_seeking_food(self, dt):
        if not self.target_food:
            self.target_food = self.find_nearest_food()
            if self.target_food:
                self._start_path_to_position(self.target_food.position)
            else:
                self._switch_state(CatState.WANDERING)

    def _update_working(self, dt):
        if not self.current_task and not self.wire_task:
            print(f"Cat {id(self)} has no tasks, switching to wandering")
            self._switch_state(CatState.WANDERING)
            return
        
        if not self.moving and self.wire_task:
            print(f"Cat {id(self)} starting wire task at {self.wire_task[0]}")
            self._start_next_wire_task()

    def _update_wandering(self, dt):
        # Check for tasks first
        if self.wire_task_queue or self.current_task:
            print(f"Cat {id(self)} found pending task, switching to WORKING")
            self._switch_state(CatState.WORKING)
            return
        
        # Normal wandering behavior
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            self._switch_state(CatState.IDLE)
            self.idle_timer = random.uniform(2.0, 5.0)
        elif not self.moving:
            # Pick a random nearby tile to wander to
            self._start_random_movement()

    def _update_idle(self, dt):
        # Check for tasks first
        if self.wire_task_queue or self.current_task:
            print(f"Cat {id(self)} found pending task, switching to WORKING")
            self._switch_state(CatState.WORKING)
            return
        
        # Normal idle behavior
        self.idle_timer -= dt
        if self.idle_timer <= 0:
            self._switch_state(CatState.WANDERING)
            self.wander_timer = random.uniform(3.0, 8.0)

    def _switch_state(self, new_state):
        if new_state == self.state:
            return
            
        print(f"\nCat {id(self)} switching state: {self.state.value} -> {new_state.value}")
        print(f"Current task: {self.current_task}")
        print(f"Wire task queue: {self.wire_task_queue}")
        
        self.state = new_state
        if new_state == CatState.WORKING:
            print(f"Cat {id(self)} starting work")
            if not self.moving and (self.wire_task_queue or self.wire_task):
                self._start_next_wire_task()

    def render_with_offset(self, surface, camera_x, camera_y):
        # Get zoom level from game state
        zoom_level = self.game_state.zoom_level
        
        # Calculate screen position with zoom
        screen_x = (self.position.x - camera_x) * zoom_level
        screen_y = (self.position.y - camera_y) * zoom_level
        
        # Scale size based on zoom
        scaled_size = pygame.Vector2(self.size.x * zoom_level, self.size.y * zoom_level)
        
        # Create a surface with alpha for the cat
        cat_surface = pygame.Surface((scaled_size.x, scaled_size.y), pygame.SRCALPHA)
        
        # Draw cat body (oval)
        body_rect = (scaled_size.x * 0.2, scaled_size.y * 0.3, 
                    scaled_size.x * 0.6, scaled_size.y * 0.5)
        pygame.draw.ellipse(cat_surface, self.color, body_rect)
        
        # Draw cat head (circle)
        head_size = scaled_size.x * 0.4
        pygame.draw.circle(cat_surface, self.color,
                          (scaled_size.x * 0.35, scaled_size.y * 0.4),
                          head_size/2)
        
        # Draw cat ears (triangles)
        ear_color = tuple(max(0, min(255, c - 30)) for c in self.color[:3]) + (self.color[3],)
        left_ear = [(scaled_size.x * 0.25, scaled_size.y * 0.3),
                    (scaled_size.x * 0.35, scaled_size.y * 0.15),
                    (scaled_size.x * 0.45, scaled_size.y * 0.3)]
        right_ear = [(scaled_size.x * 0.35, scaled_size.y * 0.3),
                     (scaled_size.x * 0.45, scaled_size.y * 0.15),
                     (scaled_size.x * 0.55, scaled_size.y * 0.3)]
        pygame.draw.polygon(cat_surface, ear_color, left_ear)
        pygame.draw.polygon(cat_surface, ear_color, right_ear)
        
        # Draw cat eyes
        eye_color = (0, 255, 0) if 'aggressive' in self.traits else (0, 200, 255)
        eye_size = max(3 * zoom_level, 1)
        pygame.draw.circle(cat_surface, eye_color,
                          (scaled_size.x * 0.3, scaled_size.y * 0.35), eye_size)
        pygame.draw.circle(cat_surface, eye_color,
                          (scaled_size.x * 0.4, scaled_size.y * 0.35), eye_size)
        
        # Draw cat tail (curved line)
        tail_points = [
            (scaled_size.x * 0.8, scaled_size.y * 0.5),
            (scaled_size.x * 0.9, scaled_size.y * 0.4),
            (scaled_size.x * 0.95, scaled_size.y * 0.3)
        ]
        pygame.draw.lines(cat_surface, self.color, False, tail_points, 3)
        
        # Blit the cat to the screen
        surface.blit(cat_surface, 
                    (screen_x - scaled_size.x/2, 
                     screen_y - scaled_size.y/2))
        
        # Draw health and hunger bars
        if self.health < self.max_health:
            bar_height = max(3 * zoom_level, 1)
            health_width = (scaled_size.x * self.health) / self.max_health
            pygame.draw.rect(surface, (255, 0, 0), 
                           (screen_x - scaled_size.x/2, 
                            screen_y - scaled_size.y/2 - 5 * zoom_level,
                            scaled_size.x, bar_height))
            pygame.draw.rect(surface, (0, 255, 0),
                           (screen_x - scaled_size.x/2, 
                            screen_y - scaled_size.y/2 - 5 * zoom_level,
                            health_width, bar_height))
        
        # Add hunger bar below health bar
        if not self.is_dead:
            hunger_width = (scaled_size.x * self.hunger) / self.max_hunger
            bar_y_offset = -8 if self.health < self.max_health else -5
            pygame.draw.rect(surface, (150, 150, 0), 
                           (screen_x - scaled_size.x/2, 
                            screen_y - scaled_size.y/2 + bar_y_offset,
                            scaled_size.x, 3))
            pygame.draw.rect(surface, (255, 255, 0),
                           (screen_x - scaled_size.x/2, 
                            screen_y - scaled_size.y/2 + bar_y_offset,
                            hunger_width, 3)) 
    
    def set_wire_task(self, wire_pos, wire_type):
        if self.is_dead:
            return
        
        print(f"\n=== DEBUG: Cat {id(self)} receiving wire task at: {wire_pos} ===")
        # Store the wire task
        self.wire_task = (wire_pos, wire_type)
        
        # Find the corresponding task in the task system
        task = next((t for t in self.game_state.task_system.available_tasks 
                    if t.position == wire_pos and not t.assigned_to), None)
        
        if task:
            print(f"Found matching task: {task}")
            self.current_task = task
            task.assigned_to = self
        
        # Switch to working state and start movement
        self._switch_state(CatState.WORKING)
        if not self.moving:
            self._start_path_to_position(pygame.math.Vector2(
                (wire_pos[0] + 0.5) * TILE_SIZE,
                (wire_pos[1] + 0.5) * TILE_SIZE
            ))

    def _start_next_wire_task(self):
        if not self.wire_task_queue:
            print("Wire task queue empty")
            return
        
        wire_pos, wire_type = self.wire_task_queue[0]
        print(f"Starting wire task at position: {wire_pos}")
        current_tile = (int(self.position.x // TILE_SIZE), int(self.position.y // TILE_SIZE))
        
        self.path = find_path(current_tile, wire_pos, self.game_state.current_level.tilemap)
        if self.path:
            print(f"Found path of length: {len(self.path)}")
            self.current_waypoint = 1 if len(self.path) > 1 else 0
            next_tile = self.path[self.current_waypoint]
            self.target_position = pygame.math.Vector2(
                (next_tile[0] + 0.5) * TILE_SIZE,
                (next_tile[1] + 0.5) * TILE_SIZE
            )
            self.moving = True
            self.wire_task = self.wire_task_queue[0]
        else:
            print(f"No path found to wire position: {wire_pos}")

    def _start_path_to_position(self, target_pos):
        """Start a path to the given position"""
        # Convert positions to tile coordinates
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        target_tile = (int(target_pos.x // TILE_SIZE),
                      int(target_pos.y // TILE_SIZE))
        
        # Find path using pathfinding
        self.path = find_path(current_tile, target_tile, 
                             self.game_state.current_level.tilemap)
        
        if self.path:
            # Set initial waypoint
            self.current_waypoint = 1 if len(self.path) > 1 else 0
            next_tile = self.path[self.current_waypoint]
            
            # Set target position to center of next tile
            self.target_position = pygame.math.Vector2(
                (next_tile[0] + 0.5) * TILE_SIZE,
                (next_tile[1] + 0.5) * TILE_SIZE
            )
            self.moving = True
        else:
            # If no path found, clear movement state
            self.moving = False
            self.target_position = None
            self.path = None 

    def _update_movement(self, dt):
        if not self.target_position:
            return
        
        # Calculate direction and distance to target
        direction = self.target_position - self.position
        distance = direction.length()
        
        if distance > 1:  # If not at target yet
            # Normalize direction and apply movement
            direction.normalize_ip()
            movement = direction * self.speed * dt
            self.position += movement
        else:  # If reached target
            print(f"\n=== DEBUG: Cat reached waypoint ===")
            print(f"Position: {self.position}")
            print(f"Target: {self.target_position}")
            print(f"Current task: {self.current_task}")
            print(f"Current waypoint: {self.current_waypoint}")
            print(f"Path length: {len(self.path) if self.path else 0}")
            
            # Update position to exactly match target
            self.position = self.target_position.copy()
            
            # Check if we've reached the final waypoint
            if not self.path or self.current_waypoint >= len(self.path) - 1:
                print("=== Reached final waypoint ===")
                # If we have a current task
                if self.current_task and self.current_task.type == TaskType.WIRE_CONSTRUCTION:
                    # Convert current position to tile coordinates
                    current_tile = (int(self.position.x // TILE_SIZE), 
                                  int(self.position.y // TILE_SIZE))
                    task_tile = self.current_task.position
                    print(f"Current tile: {current_tile}, Task position: {task_tile}")
                    
                    # Check if we're at the task position
                    if current_tile == task_tile:
                        print(f"=== DEBUG: Completing wire task at {task_tile} ===")
                        # Complete the wire construction
                        self.game_state.wire_system.complete_wire_construction(task_tile)
                        # Mark task as completed
                        self.current_task.completed = True
                        # Clear task and wire task
                        self.current_task = None
                        self.wire_task = None
                        self.moving = False
                        self._switch_state(CatState.WANDERING)
                        return
                
                # If no task or not at task position, just stop moving
                self.moving = False
                self.target_position = None
                self.path = None
                return
            
            # Move to next waypoint
            self.current_waypoint += 1
            if self.current_waypoint < len(self.path):
                next_tile = self.path[self.current_waypoint]
                self.target_position = pygame.math.Vector2(
                    (next_tile[0] + 0.5) * TILE_SIZE,
                    (next_tile[1] + 0.5) * TILE_SIZE
                )

    def _start_random_movement(self):
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        rand_offset = (random.randint(-5, 5), random.randint(-5, 5))
        target_tile = (current_tile[0] + rand_offset[0],
                      current_tile[1] + rand_offset[1])
        self._start_path_to_position(pygame.math.Vector2(
            (target_tile[0] + 0.5) * TILE_SIZE,
            (target_tile[1] + 0.5) * TILE_SIZE
        )) 

    def complete_current_task(self):
        if self.current_task and self.current_task.type == TaskType.WIRE_CONSTRUCTION:
            # Complete the wire construction
            self.game_state.wire_system.complete_wire_construction(self.current_task.position)
            
        # Remove from queue and clear current task
        if self.wire_task_queue:
            self.wire_task_queue.pop(0)
        self.current_task = None
        
        if not self.wire_task_queue:
            self._switch_state(CatState.WANDERING)
        else:
            self._start_next_wire_task() 