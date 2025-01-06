from entities.items.food import Food
from utils.pathfinding import find_path
from .base_level import BaseLevel
from entities.alien import Alien
from entities.cat import Cat
from entities.enemies.human import Human
from utils.config import *
from core.tiles import TILE_FLOOR, TILE_WALL, TILE_BARRIER
import random
import pygame

class TestLevel(BaseLevel):
    """
    Test level with three distinct rooms:
    1. Starting room with cats
    2. Maze room for pathfinding testing
    3. Enemy room for combat testing
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.cats = []  # List of autonomous cat entities
        
    def initialize(self):
        """Set up the three-room test environment"""
        # Create the room layout
        self._create_test_map()
        
        # Create alien in starting room (left room)
        start_x = MAP_WIDTH // 6  # Left third of map
        start_y = MAP_HEIGHT // 2
        
        # Create one alien (pink) for testing
        alien = Alien(start_x, start_y, (255, 192, 203, 128))
        alien.game_state = self.game_state
        
        # Make alien invincible for testing
        if alien.health:
            alien.health.is_invincible = True
            alien.health.max_health = 100
            alien.health.health = 100
            alien.health.max_morale = 100
            alien.health.morale = 100
        
        self.aliens.append(alien)
        self.entity_manager.add_entity(alien)
        
        # Add two cats in starting room
        cat_positions = [
            (start_x - 2, start_y - 2),
            (start_x + 2, start_y - 2),
        ]
        
        for x, y in cat_positions:
            cat = Cat(x, y, self.game_state)
            self.cats.append(cat)
            self.entity_manager.add_entity(cat)
        
        # Add food items in starting room
        food_positions = [
            (start_x - 3, start_y),
            (start_x + 3, start_y),
            (start_x, start_y - 3)
        ]
        
        for x, y in food_positions:
            food = Food(x * TILE_SIZE + TILE_SIZE/2, y * TILE_SIZE + TILE_SIZE/2)
            food.game_state = self.game_state
            self.entity_manager.add_item(food)
        
        # Add single enemy in right room
        enemy_x = 5 * MAP_WIDTH // 6  # Right third of map
        enemy_y = MAP_HEIGHT // 2
        
        human = Human(enemy_x, enemy_y)
        human.game_state = self.game_state
        
        # Create a 10x10 square patrol route
        patrol_route = [
            (enemy_x - 5, enemy_y - 5),      # Top-left
            (enemy_x + 5, enemy_y - 5),      # Top-right
            (enemy_x + 5, enemy_y + 5),      # Bottom-right
            (enemy_x - 5, enemy_y + 5),      # Bottom-left
            (enemy_x - 5, enemy_y - 5)       # Back to start to complete the square
        ]
        human.set_patrol_points(patrol_route)
        self.enemies.append(human)
        self.entity_manager.add_entity(human)
    
    def _create_test_map(self):
        """Generate three-room layout with maze in middle"""
        # Fill with floor tiles
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                self.tilemap.set_tile(x, y, TILE_FLOOR.name)
        
        # Create outer walls
        for x in range(MAP_WIDTH):
            self.tilemap.set_tile(x, 0, TILE_WALL.name)
            self.tilemap.set_tile(x, MAP_HEIGHT-1, TILE_WALL.name)
        for y in range(MAP_HEIGHT):
            self.tilemap.set_tile(0, y, TILE_WALL.name)
            self.tilemap.set_tile(MAP_WIDTH-1, y, TILE_WALL.name)
        
        # Create room dividers with openings
        third_width = MAP_WIDTH // 3
        for y in range(MAP_HEIGHT):
            # Skip 3 tiles in the middle to create doorways
            if abs(y - MAP_HEIGHT // 2) >= 2:
                self.tilemap.set_tile(third_width, y, TILE_WALL.name)
                self.tilemap.set_tile(2 * third_width, y, TILE_WALL.name)
        
        # Create maze in middle room
        self._create_maze(third_width + 1, 1, 2 * third_width - 1, MAP_HEIGHT - 2)
    
    def _create_maze(self, start_x, start_y, end_x, end_y):
        """Create a simple maze pattern in the middle room"""
        center_y = (start_y + end_y) // 2
        
        # Create horizontal barriers
        for x in range(start_x, end_x):
            if (x - start_x) % 4 == 0:
                for y in range(start_y, end_y):
                    # Leave center path open AND ensure entrance/exit paths are clear
                    if (y != center_y and  # Don't block center path
                        abs(x - start_x) > 3 and  # Don't block left entrance
                        abs(x - end_x) > 3):      # Don't block right entrance
                        self.tilemap.set_tile(x, y, TILE_WALL.name)
        
        # Create vertical barriers
        for y in range(start_y, end_y):
            if (y - start_y) % 4 == 0:
                for x in range(start_x, end_x):
                    # Leave center path open AND ensure entrance/exit paths are clear
                    if (x != (start_x + end_x) // 2 and  # Don't block center path
                        abs(y - center_y) > 2):          # Don't block entrance corridors
                        self.tilemap.set_tile(x, y, TILE_WALL.name)
    
    def update(self, dt):
        self.entity_manager.update(dt)
        
        # Update cat wandering behavior
        for cat in self.cats:
            if (not cat.movement_handler.moving and 
                random.random() < 0.02):  # 2% chance to start moving each frame
                cat.movement_handler.start_random_movement() 