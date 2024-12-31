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
        
        # Add build timer properties
        self.build_timer = 0
        self.build_time_required = 2.0  # 2 seconds to build
        self.is_building = False
    
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

        # Update building progress
        if self.is_building:
            self.build_timer += dt
            print(f"Building progress: {self.build_timer}/{self.build_time_required}")
            if self.build_timer >= self.build_time_required:
                print(f"Wire construction complete at {self.current_task.position}")
                self.is_building = False
                self.complete_current_task()

    def _update_seeking_food(self, dt):
        if not self.target_food:
            self.target_food = self.find_nearest_food()
            if self.target_food:
                self._start_path_to_position(self.target_food.position)
            else:
                self._switch_state(CatState.WANDERING)

    def _update_working(self, dt):
        if not self.current_task and not self.wire_task:
            print("Cat has no tasks, switching to wandering")
            self._switch_state(CatState.WANDERING)
            return

        # Only log when wire construction is happening
        if self.wire_task or self.is_building:
            print(f"\n=== WIRE CONSTRUCTION STATUS ===")
            print(f"Cat {id(self)}:")
            print(f"Wire task: {self.wire_task}")
            print(f"Is building: {self.is_building}")
            print(f"Build timer: {self.build_timer}/{self.build_time_required}")

        # Update building progress
        if self.is_building:
            self.build_timer += dt
            if self.build_timer >= self.build_time_required:
                print(f"Wire construction complete at {self.current_task.position}")
                self.is_building = False
                self.complete_current_task()
                return

        if not self.moving and self.wire_task:
            wire_pos = self.wire_task[0]
            current_pos = (int(self.position.x // TILE_SIZE), 
                          int(self.position.y // TILE_SIZE))
            
            print(f"\n=== WIRE TASK CHECK ===")
            print(f"Cat position: {current_pos}")
            print(f"Wire position: {wire_pos}")
            
            if (abs(current_pos[0] - wire_pos[0]) <= 1 and 
                abs(current_pos[1] - wire_pos[1]) <= 1):
                print(f"Cat in position to complete wire")
                self.is_building = True
                self.build_timer = 0

        # If we're not moving and have a task, try to path to it
        if not self.moving and self.current_task:
            target_pos = pygame.math.Vector2(
                (self.current_task.position[0] + 0.5) * TILE_SIZE,
                (self.current_task.position[1] + 0.5) * TILE_SIZE
            )
            if not self._start_path_to_position(target_pos):
                print(f"Failed to find path to task at {self.current_task.position}")
                self.current_task = None
                self._switch_state(CatState.WANDERING)

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
        elif not self.moving and not self.target_position:  # Only start new movement if we're not moving
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
        
        # Find adjacent position to wire
        adjacent_positions = [
            (wire_pos[0] + 1, wire_pos[1]),
            (wire_pos[0] - 1, wire_pos[1]),
            (wire_pos[0], wire_pos[1] + 1),
            (wire_pos[0], wire_pos[1] - 1)
        ]
        
        # Find closest valid adjacent position that we can path to
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        best_pos = None
        best_distance = float('inf')
        
        print(f"Current position: {current_tile}")
        print(f"Checking adjacent positions to wire at {wire_pos}")
        
        for pos in adjacent_positions:
            # Check if position is walkable and we can path to it
            if self.game_state.current_level.tilemap.is_walkable(pos[0], pos[1]):
                test_path = find_path(
                    current_tile,
                    pos,
                    self.game_state.current_level.tilemap,
                    self.game_state,
                    self
                )
                if test_path:  # Only consider positions we can actually reach
                    dist = ((pos[0] - current_tile[0]) ** 2 + 
                           (pos[1] - current_tile[1]) ** 2) ** 0.5
                    print(f"Found valid path to {pos} with distance {dist}")
                    if dist < best_distance:
                        best_pos = pos
                        best_distance = dist
        
        if best_pos:
            print(f"Selected best adjacent position: {best_pos}")
            # Start movement to adjacent position
            self._switch_state(CatState.WORKING)
            if not self.moving:
                target_pos = pygame.math.Vector2(
                    (best_pos[0] + 0.5) * TILE_SIZE,
                    (best_pos[1] + 0.5) * TILE_SIZE
                )
                if self._start_path_to_position(target_pos):
                    print(f"Started moving to adjacent position {best_pos}")
                else:
                    print(f"Failed to start path to adjacent position {best_pos}")
        else:
            print(f"No valid adjacent positions found for wire at {wire_pos}")

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
        """Start moving to a target position"""
        current_pos = (int(self.position.x // TILE_SIZE), 
                      int(self.position.y // TILE_SIZE))
        target_tile = (int(target_pos.x // TILE_SIZE), int(target_pos.y // TILE_SIZE))
        
        # Don't pathfind to current position
        if current_pos == target_tile:
            print(f"Already at target position {target_tile}")
            return False
        
        print(f"\nCat {id(self)} finding path:")
        print(f"From: {current_pos}")
        print(f"To: {target_tile}")
        
        self.path = find_path(
            current_pos, 
            target_tile, 
            self.game_state.current_level.tilemap,
            self.game_state,
            self
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

    def _update_movement(self, dt):
        """Update entity movement"""
        if not self.moving or not self.target_position:
            return
        
        # Calculate direction and distance to target
        direction = self.target_position - self.position
        distance = direction.length()
        
        # Define a threshold for "close enough"
        ARRIVAL_THRESHOLD = 1.0
        
        if distance < ARRIVAL_THRESHOLD:
            # Snap to target position when very close
            self.position = pygame.math.Vector2(self.target_position)
            print(f"Cat {id(self)} reached target exactly")
            
            # If we have more waypoints, move to next one
            if self.path and self.current_waypoint < len(self.path) - 1:
                self.current_waypoint += 1
                next_tile = self.path[self.current_waypoint]
                self.target_position = pygame.math.Vector2(
                    (next_tile[0] + 0.5) * TILE_SIZE,
                    (next_tile[1] + 0.5) * TILE_SIZE
                )
                print(f"Moving to next waypoint: {next_tile}")
            else:
                print(f"Reached final destination!")
                self.moving = False
                self.path = None
                self.target_position = None
            return

        # Normalize direction and apply speed
        if distance > 0:  # Prevent division by zero
            direction = direction / distance
            move_distance = min(self.speed * dt, distance)  # Don't overshoot
            movement = direction * move_distance
            
            # Update position
            self.position += movement
            
            print(f"\nCat {id(self)} movement update:")
            print(f"Current pos: {self.position}")
            print(f"Target pos: {self.target_position}")
            print(f"Distance: {distance}")
            print(f"Moving by: {movement}")

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
        """Complete the current task"""
        if self.current_task and self.current_task.type == TaskType.WIRE_CONSTRUCTION:
            print(f"\n=== Cat {id(self)} completing task ===")
            print(f"Task position: {self.current_task.position}")
            
            # Complete the task in the task system
            self.game_state.task_system.complete_task(self.current_task)
            
            # Reset all task-related states
            self.is_building = False
            self.build_timer = 0
            self.wire_task = None  # Clear wire task too
            self.current_task = None
            self._switch_state(CatState.WANDERING) 

    def update_wire_task(self):
        """Check if we can complete the wire task"""
        if not self.wire_task_position:
            return
        
        # Get current tile position
        current_tile_x = int(self.position.x // TILE_SIZE)
        current_tile_y = int(self.position.y // TILE_SIZE)
        wire_x, wire_y = self.wire_task_position
        
        print("\n=== WIRE TASK CHECK ===")
        print(f"Cat position: ({current_tile_x}, {current_tile_y})")
        print(f"Wire position: ({wire_x}, {wire_y})")
        print(f"Distance: ({abs(wire_x - current_tile_x)}, {abs(wire_y - current_tile_y)})")
        
        # Check if we're close enough to complete the wire
        if (abs(wire_x - current_tile_x) <= 1 and 
            abs(wire_y - current_tile_y) <= 1):
            print("Cat in position to complete wire")
            if self.current_task:
                self.complete_current_task() 