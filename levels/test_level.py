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
    Test level for debugging and feature testing.
    Provides a controlled environment with basic entity interactions.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.cats = []  # List of autonomous cat entities
        
    def initialize(self):
        """
        Set up a simple test environment with one alien, two cats,
        food items, and patrolling enemies in a confined space.
        """
        # Create simple test layout
        self._create_test_map()
        
        # Create a single alien in the center
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        
        # Create one alien (pink) for testing controls
        alien = Alien(center_x, center_y, (255, 192, 203, 128))
        alien.game_state = self.game_state
        self.aliens.append(alien)
        self.entity_manager.add_entity(alien)
        
        # Add two cats nearby for testing AI behavior
        cat_positions = [
            (center_x - 2, center_y - 2),  # Top-left of alien
            (center_x + 2, center_y - 2),  # Top-right of alien
        ]
        
        # Create cats with basic wandering behavior
        for x, y in cat_positions:
            cat = Cat(x, y, self.game_state)
            self.cats.append(cat)
            self.entity_manager.add_entity(cat)
        
        # Add food items in triangular pattern for testing pickup mechanics
        food_positions = [
            (center_x - 3, center_y),    # Left
            (center_x + 3, center_y),    # Right
            (center_x, center_y - 3)     # Top
        ]
        
        # Create food items with proper positioning
        for x, y in food_positions:
            food = Food(x * TILE_SIZE + TILE_SIZE/2, y * TILE_SIZE + TILE_SIZE/2)
            food.game_state = self.game_state
            self.entity_manager.add_item(food)
        
        # Add enemies with simple patrol routes for testing AI
        patrol_routes = [
            [(center_x - 4, center_y - 4), (center_x - 4, center_y + 4)],  # Left vertical
            [(center_x + 4, center_y - 4), (center_x + 4, center_y + 4)],  # Right vertical
            [(center_x - 2, center_y + 3), (center_x + 2, center_y + 3)]   # Bottom horizontal
        ]
        
        # Create patrolling enemies
        for route in patrol_routes:
            human = Human(route[0][0], route[0][1])
            human.game_state = self.game_state
            human.set_patrol_points(route)
            self.enemies.append(human)
            self.entity_manager.add_entity(human)
    
    def _create_test_map(self):
        """
        Generate a simple enclosed testing area with walls.
        Creates a controlled environment for testing mechanics.
        """
        # Fill with floor tiles for basic movement
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                self.tilemap.set_tile(x, y, TILE_FLOOR.name)
        
        # Create a simple enclosed area with walls
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        radius = 8  # Small enclosed area for focused testing
        
        # Create wall boundary and outer barriers
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                dx = x - center_x
                dy = y - center_y
                distance = max(abs(dx), abs(dy))
                
                if distance == radius:
                    self.tilemap.set_tile(x, y, TILE_WALL.name)  # Boundary walls
                elif distance > radius:
                    self.tilemap.set_tile(x, y, TILE_BARRIER.name)  # Outer barriers
    
    def update(self, dt):
        self.entity_manager.update(dt)
        
        # Update cat wandering behavior
        for cat in self.cats:
            if (not cat.movement_handler.moving and 
                random.random() < 0.02):  # 2% chance to start moving each frame
                cat.movement_handler.start_random_movement() 