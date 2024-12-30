from utils.pathfinding import find_path
from .base_level import BaseLevel
from entities.alien import Alien
from entities.cat import Cat
from utils.config import *
from core.tiles import TILE_FLOOR, TILE_WALL, TILE_BARRIER
import random
import pygame

class UfoLevel(BaseLevel):
    def __init__(self, game_state):
        super().__init__(game_state)
        self.cats = []  # Add cats list
        
    def initialize(self):
        # Create UFO layout
        self._create_ufo_map()
        
        # Create crew positions
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        
        # Create aliens in UFO bridge positions
        crew_positions = [
            (center_x, center_y),      # Captain (pink)
            (center_x - 2, center_y),  # Navigation (blue)
            (center_x + 2, center_y),  # Weapons (green)
            (center_x, center_y - 2),  # Science (purple)
            (center_x, center_y + 2),  # Engineering (orange)
        ]
        
        crew_colors = [
            (255, 192, 203, 128),  # Pink
            (100, 149, 237, 128),  # Blue
            (144, 238, 144, 128),  # Green
            (147, 112, 219, 128),  # Purple
            (255, 165, 0, 128),    # Orange
        ]
        
        for pos, color in zip(crew_positions, crew_colors):
            alien = Alien(pos[0], pos[1], color)
            alien.game_state = self.game_state
            self.aliens.append(alien)
            self.entity_manager.add_entity(alien)
            
        # Add cats around the UFO
        cat_positions = [
            (center_x - 4, center_y - 4),
            (center_x + 4, center_y - 4),
            (center_x - 4, center_y + 4),
            (center_x + 4, center_y + 4),
        ]
        
        for x, y in cat_positions:
            cat = Cat(x, y)
            cat.game_state = self.game_state
            self.cats.append(cat)
            self.entity_manager.add_entity(cat)
    
    def _create_ufo_map(self):
        # Fill with floor tiles
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                self.tilemap.set_tile(x, y, TILE_FLOOR.name)
        
        # Create circular UFO shape
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        radius = min(MAP_WIDTH, MAP_HEIGHT) // 3
        
        # Add walls for UFO outline
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                dx = x - center_x
                dy = y - center_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                # Create circular wall boundary
                if abs(distance - radius) < 1.5:
                    self.tilemap.set_tile(x, y, TILE_WALL.name)
                # Make outside of UFO unwalkable
                elif distance > radius:
                    self.tilemap.set_tile(x, y, TILE_BARRIER.name)
    
    def update(self, dt):
        self.entity_manager.update(dt)
        
        # Update cat wandering behavior
        for cat in self.cats:
            if not cat.moving and random.random() < 0.02:  # 2% chance to start moving each frame
                # Find random walkable position
                while True:
                    dx = random.randint(-5, 5)
                    dy = random.randint(-5, 5)
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