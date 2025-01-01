from entities.items.food import Food
from utils.pathfinding import find_path
from .base_level import BaseLevel
from entities.alien import Alien
from entities.cat import Cat
from utils.config import *
from core.tiles import TILE_FLOOR, TILE_WALL, TILE_BARRIER
import random
import pygame

class UfoLevel(BaseLevel):
    """
    UFO-themed level featuring alien crew, cats, and food resources.
    Implements circular UFO layout with specific crew positions.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.cats = []  # List of autonomous cat entities
        
    def initialize(self):
        """
        Set up initial UFO level state including map layout,
        crew positions, cats, and food resources.
        """
        # Create UFO layout with circular walls
        self._create_ufo_map()
        
        # Set up crew positions in bridge formation
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        
        # Define crew positions and colors
        crew_positions = [
            (center_x, center_y),      # Captain (pink)
            (center_x - 2, center_y),  # Navigation (blue)
            (center_x + 2, center_y),  # Weapons (green)
            (center_x, center_y - 2),  # Science (purple)
            (center_x, center_y + 2),  # Engineering (orange)
        ]
        
        crew_colors = [
            (255, 192, 203, 128),  # Pink (semi-transparent)
            (100, 149, 237, 128),  # Blue (semi-transparent)
            (144, 238, 144, 128),  # Green (semi-transparent)
            (147, 112, 219, 128),  # Purple (semi-transparent)
            (255, 165, 0, 128),    # Orange (semi-transparent)
        ]
        
        # Create alien crew members
        for pos, color in zip(crew_positions, crew_colors):
            alien = Alien(pos[0], pos[1], color)
            alien.game_state = self.game_state
            self.aliens.append(alien)
            self.entity_manager.add_entity(alien)
            
        # Add cats in corner positions around UFO
        cat_positions = [
            (center_x - 4, center_y - 4),  # Top-left
            (center_x + 4, center_y - 4),  # Top-right
            (center_x - 4, center_y + 4),  # Bottom-left
            (center_x + 4, center_y + 4),  # Bottom-right
        ]
        
        # Create cat entities
        for x, y in cat_positions:
            cat = Cat(x, y, self.game_state)
            self.cats.append(cat)
            self.entity_manager.add_entity(cat)
        
        # Add food items near the crew
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        radius = 5  # Spawn food within 5 tiles of center
        
        for _ in range(6):  # Add 6 food items
            while True:
                dx = random.randint(-radius, radius)
                dy = random.randint(-radius, radius)
                x = center_x + dx
                y = center_y + dy
                
                # Check if position is valid
                if self.tilemap.is_walkable(x, y):
                    food = Food(x * TILE_SIZE + TILE_SIZE/2, y * TILE_SIZE + TILE_SIZE/2)
                    food.game_state = self.game_state  # Make sure game_state is set
                    self.entity_manager.add_item(food)
                    break
    
    def _create_ufo_map(self):
        """
        Generate circular UFO layout with walls and barriers.
        Creates walkable interior and unwalkable exterior.
        """
        # Fill entire map with floor tiles initially
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                self.tilemap.set_tile(x, y, TILE_FLOOR.name)
        
        # Create circular UFO boundary
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        radius = min(MAP_WIDTH, MAP_HEIGHT) // 3
        
        # Add walls and barriers based on distance from center
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                dx = x - center_x
                dy = y - center_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                if abs(distance - radius) < 1.5:
                    self.tilemap.set_tile(x, y, TILE_WALL.name)  # UFO hull
                elif distance > radius:
                    self.tilemap.set_tile(x, y, TILE_BARRIER.name)  # Space
    
    def update(self, dt):
        """
        Update level state including random cat movement.
        
        Args:
            dt (float): Delta time since last update
        """
        super().update(dt)
        
        # Random cat movement
        for cat in self.cats:
            if (not cat.movement_handler.moving and 
                random.random() < 0.02):  # 2% chance per frame
                cat.movement_handler.start_random_movement()
        
        # Update all entities
        self.entity_manager.update(dt) 