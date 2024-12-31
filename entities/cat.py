import pygame
import random

from entities.items.food import Food
from utils.pathfinding import find_path
from .base_entity import Entity
from utils.config import *

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
        
        # Personality traits (randomly assigned)
        self.traits = self._generate_traits()
        
        # Visual properties
        self.color = (random.randint(150, 200), 
                     random.randint(100, 150), 
                     random.randint(50, 100),
                     200)  # Brownish with alpha
        
        self.wire_task_queue = []  # Queue for wire tasks
    
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
            return  # Dead cats don't update
            
        # Update hunger
        self.hunger = max(0, self.hunger - self.hunger_rate * dt)
        
        # Check for death conditions
        if self.health <= 0:
            self.is_dead = True
            self.color = (100, 100, 100, 200)  # Gray out dead cats
            return
            
        # Health decreases when starving
        if self.hunger <= 0:
            self.health = max(0, self.health - 5 * dt)  # Lose 5 health per second when starving
            
        # Start seeking food when hungry
        if self.hunger <= self.max_hunger * (self.critical_hunger / 100) and not self.seeking_food:
            self.target_food = self.find_nearest_food()
            if self.target_food:
                self.seeking_food = True
                current_tile = (int(self.position.x // TILE_SIZE), 
                               int(self.position.y // TILE_SIZE))
                target_tile = (int(self.target_food.position.x // TILE_SIZE),
                              int(self.target_food.position.y // TILE_SIZE))
                self.path = find_path(current_tile, target_tile, 
                                    self.game_state.current_level.tilemap,
                                    self.game_state, self)
                if self.path:
                    self.current_waypoint = 1 if len(self.path) > 1 else 0
                    next_tile = self.path[self.current_waypoint]
                    self.target_position = pygame.math.Vector2(
                        (next_tile[0] + 0.5) * TILE_SIZE,
                        (next_tile[1] + 0.5) * TILE_SIZE
                    )
                    self.moving = True
        
        # Check if we reached food
        if self.seeking_food and self.target_food:
            distance = (self.target_food.position - self.position).length()
            if distance < TILE_SIZE:
                self.eat_food(self.target_food)
        
        # Update morale based on conditions (simplified)
        if self.health < self.max_health * 0.5:
            self.morale = max(0, self.morale - 10 * dt)
        
        # Movement logic
        if self.target_position and self.moving:
            direction = self.target_position - self.position
            distance = direction.length()
            
            if distance < 2:  # Reached waypoint
                self.position = self.target_position
                
                if self.path and self.current_waypoint < len(self.path) - 1:
                    self.current_waypoint += 1
                    next_tile = self.path[self.current_waypoint]
                    self.target_position = pygame.math.Vector2(
                        round((next_tile[0] + 0.5) * TILE_SIZE),
                        round((next_tile[1] + 0.5) * TILE_SIZE)
                    )
                else:
                    self.target_position = None
                    self.path = None
                    self.moving = False
                    # Check if we were placing a wire
                    if hasattr(self, 'wire_task') and self.wire_task:
                        wire_pos, wire_type = self.wire_task
                        print(f"Cat placing wire at {wire_pos}")
                        component = self.game_state.current_level.tilemap.electrical_components.get(wire_pos)
                        if component:
                            component.under_construction = False  # Construction complete
                        self.wire_task_queue.pop(0)  # Remove completed task
                        self.wire_task = None
                        
                        # Start next task if available
                        if self.wire_task_queue:
                            self._start_next_wire_task()
            else:
                # Apply personality traits to movement
                speed_modifier = 0.7 if 'lazy' in self.traits else 1.2 if 'aggressive' in self.traits else 1.0
                if self.seeking_food and self.hunger < self.max_hunger * 0.05:  # Very hungry cats move faster
                    speed_modifier *= 1.5
                
                normalized_dir = direction.normalize()
                movement = normalized_dir * self.speed * speed_modifier * dt
                
                if movement.length() > distance:
                    self.position = self.target_position
                else:
                    self.position += movement
        
        if hasattr(self, 'wire_task') and self.wire_task:
            wire_pos, wire_type = self.wire_task
            print(f"Cat placing wire at {wire_pos}")
            component = self.game_state.current_level.tilemap.electrical_components.get(wire_pos)
            if component:
                component.under_construction = False  # Construction complete
            self.wire_task_queue.pop(0)  # Remove completed task
            self.wire_task = None
            
            # Start next task if available
            if self.wire_task_queue:
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
        if not self.is_dead:
            self.wire_task_queue.append((wire_pos, wire_type))
            if not self.moving:  # Only start new path if not already moving
                self._start_next_wire_task()

    def _start_next_wire_task(self):
        if not self.wire_task_queue:
            return
        
        wire_pos, wire_type = self.wire_task_queue[0]
        current_tile = (int(self.position.x // TILE_SIZE), int(self.position.y // TILE_SIZE))
        
        self.path = find_path(current_tile, wire_pos, 
                             self.game_state.current_level.tilemap)
        if self.path:
            self.current_waypoint = 1 if len(self.path) > 1 else 0
            next_tile = self.path[self.current_waypoint]
            self.target_position = pygame.math.Vector2(
                (next_tile[0] + 0.5) * TILE_SIZE,
                (next_tile[1] + 0.5) * TILE_SIZE
            )
            self.moving = True
            self.wire_task = self.wire_task_queue[0]  # Current task 