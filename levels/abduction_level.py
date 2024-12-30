import pygame

from utils.pathfinding import find_path
from .base_level import BaseLevel
from entities.alien import Alien
from entities.cat import Cat
from utils.config import *
from core.tiles import TILE_GRASS, TILE_ROCK, TILE_WALL, TILE_BARRIER
import random
from entities.items.food import Food

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
                    cat = Cat(x, y)
                    cat.game_state = self.game_state
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
                    food = Food((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE)
                    self.entity_manager.add_item(food)
                    break
    
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
            if not cat.moving and random.random() < 0.02:  # 2% chance to start moving each frame
                # Find random walkable position
                while True:
                    dx = random.randint(-8, 8)  # Larger range for outdoor environment
                    dy = random.randint(-8, 8)
                    target_x = int(cat.position.x // TILE_SIZE) + dx
                    target_y = int(cat.position.y // TILE_SIZE) + dy
                    
                    if self.tilemap.is_walkable(target_x, target_y):
                        current_tile = (int(cat.position.x // TILE_SIZE), 
                                      int(cat.position.y // TILE_SIZE))
                        cat.path = find_path(current_tile, (target_x, target_y), self.tilemap)
                        if cat.path:
                            cat.current_waypoint = 1 if len(cat.path) > 1 else 0
                            next_tile = cat.path[cat.current_waypoint]
                            cat.target_position = pygame.math.Vector2(
                                (next_tile[0] + 0.5) * TILE_SIZE,
                                (next_tile[1] + 0.5) * TILE_SIZE
                            )
                            cat.moving = True
                        break 