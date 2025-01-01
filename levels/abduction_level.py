import pygame

from utils.pathfinding import find_path
from .base_level import BaseLevel
from entities.alien import Alien
from entities.cat import Cat
from utils.config import *
from core.tiles import TILE_GRASS, TILE_ROCK, TILE_WALL, TILE_BARRIER
import random
from entities.items.food import Food
from entities.enemies.human import Human

class AbductionLevel(BaseLevel):
    def __init__(self, game_state):
        super().__init__(game_state)
        self.cats = []  # Add cats list
        
    def initialize(self):
        # Create the map layout
        self._create_abduction_map()
        
        # Create aliens in their starting positions
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        
        # Create aliens with their colors
        alien_configs = [
            (center_x, center_y, (255, 192, 203, 128)),      # Pink (center)
            (center_x - 2, center_y - 2, (100, 149, 237, 128)),  # Blue
            (center_x + 2, center_y - 2, (144, 238, 144, 128)),  # Green
            (center_x - 2, center_y + 2, (147, 112, 219, 128)),  # Purple
            (center_x + 2, center_y + 2, (255, 165, 0, 128))     # Orange
        ]
        
        for x, y, color in alien_configs:
            alien = Alien(x, y, color)
            alien.game_state = self.game_state
            self.aliens.append(alien)
            self.entity_manager.add_entity(alien)
            
        # Add cats scattered around the map
        for _ in range(6):  # Add 6 cats
            while True:
                x = random.randint(0, MAP_WIDTH - 1)
                y = random.randint(0, MAP_HEIGHT - 1)
                if self.tilemap.is_walkable(x, y):
                    cat = Cat(x, y, self.game_state)
                    self.cats.append(cat)
                    self.entity_manager.add_entity(cat)
                    break
        
        # Add food items near the aliens
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        radius = 8  # Slightly larger radius for outdoor environment
        
        for _ in range(8):  # 8 food items
            while True:
                # Randomly choose between spawning near center or near barriers
                if random.random() < 0.7:  # 70% chance to spawn near center
                    dx = random.randint(-radius, radius)
                    dy = random.randint(-radius, radius)
                    x = center_x + dx
                    y = center_y + dy
                else:  # 30% chance to spawn near one of the barriers
                    barrier = random.choice([
                        (5, 5),
                        (5, MAP_HEIGHT - 6),
                        (MAP_WIDTH - 6, 5),
                        (MAP_WIDTH - 6, MAP_HEIGHT - 6)
                    ])
                    x = barrier[0] + random.randint(-3, 3)
                    y = barrier[1] + random.randint(-3, 3)
                
                # Check if position is valid
                if self.tilemap.is_walkable(x, y):
                    food = Food(x * TILE_SIZE + TILE_SIZE/2, y * TILE_SIZE + TILE_SIZE/2)
                    food.game_state = self.game_state  # Make sure game_state is set
                    self.entity_manager.add_item(food)
                    break
        
        # Add some human enemies with patrol points
        patrol_routes = [
            [(10, 10), (20, 10), (20, 20), (10, 20)],  # Square patrol
            [(5, 5), (15, 5), (10, 15)],  # Triangle patrol
            [(30, 30), (40, 30)]  # Linear patrol
        ]
        
        for route in patrol_routes:
            human = Human(route[0][0], route[0][1])
            human.game_state = self.game_state
            human.set_patrol_points(route)
            self.enemies.append(human)
            self.entity_manager.add_entity(human)
    
    def _create_abduction_map(self):
        # Fill with grass (green)
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                self.tilemap.set_tile(x, y, TILE_GRASS.name)
        
        # Add random rocks (brown)
        for _ in range(MAP_WIDTH * MAP_HEIGHT // 10):  # 10% of tiles
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if (x, y) != (MAP_WIDTH // 2, MAP_HEIGHT // 2):  # Don't place on spawn
                self.tilemap.set_tile(x, y, TILE_ROCK.name)
        
        # Add barriers (red zones)
        barrier_positions = [
            (5, 5), (5, MAP_HEIGHT - 6),
            (MAP_WIDTH - 6, 5), (MAP_WIDTH - 6, MAP_HEIGHT - 6)
        ]
        
        for bx, by in barrier_positions:
            for dx in range(3):
                for dy in range(3):
                    self.tilemap.set_tile(bx + dx, by + dy, TILE_BARRIER.name)
        
        # Add vertical barriers (gray)
        for y in range(MAP_HEIGHT):
            self.tilemap.set_tile(MAP_WIDTH // 3, y, TILE_WALL.name)
            self.tilemap.set_tile(2 * MAP_WIDTH // 3, y, TILE_WALL.name)
    
    def update(self, dt):
        self.entity_manager.update(dt)
        
        # Update cat wandering behavior
        for cat in self.cats:
            if (not cat.movement_handler.moving and 
                random.random() < 0.02):  # 2% chance to start moving each frame
                cat.movement_handler.start_random_movement() 