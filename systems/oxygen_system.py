from typing import Dict, Set
import numpy as np
from utils.config import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT
import pygame

class OxygenSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        # Initialize oxygen grid (0.0 = no oxygen, 1.0 = full oxygen)
        self.oxygen_grid = np.ones((MAP_WIDTH, MAP_HEIGHT))
        
        # Constants
        self.consumption_per_entity = 0.05  # Oxygen consumed per entity per second
        self.generation_per_lifesupport = 0.2  # Oxygen generated per life support per second
        self.diffusion_rate = 0.1  # How quickly oxygen spreads between tiles
        self.critical_oxygen = 0.3  # Level at which entities start taking damage
        self.damage_rate = 5.0  # Damage per second when oxygen is depleted
        
    def update(self, dt: float):
        if not self.game_state.current_level.requires_oxygen:
            return
            
        # Track entities in each tile
        entity_positions = {}
        for entity in self.game_state.current_level.entity_manager.entities:
            if hasattr(entity, 'position'):
                tile_x = int(entity.position.x // TILE_SIZE)
                tile_y = int(entity.position.y // TILE_SIZE)
                if (tile_x, tile_y) not in entity_positions:
                    entity_positions[(tile_x, tile_y)] = []
                entity_positions[(tile_x, tile_y)].append(entity)
        
        # Update oxygen levels
        new_grid = self.oxygen_grid.copy()
        
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                # Skip tiles outside the ship
                if not self._is_inside_ship(x, y):
                    new_grid[x, y] = 0.0
                    continue
                
                # Consume oxygen from entities
                if (x, y) in entity_positions:
                    consumption = len(entity_positions[(x, y)]) * self.consumption_per_entity * dt
                    new_grid[x, y] = max(0.0, self.oxygen_grid[x, y] - consumption)
                
                # Diffuse oxygen with neighbors
                self._diffuse_oxygen(x, y, new_grid, dt)
        
        self.oxygen_grid = new_grid
        
        # Apply effects to entities
        self._apply_oxygen_effects(entity_positions, dt)
    
    def _is_inside_ship(self, x: int, y: int) -> bool:
        """Check if tile is inside the ship's hull"""
        tile = self.game_state.current_level.tilemap.get_tile(x, y)
        return tile and tile.name != 'barrier'
    
    def _diffuse_oxygen(self, x: int, y: int, new_grid: np.ndarray, dt: float):
        """Handle oxygen diffusion between neighboring tiles"""
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT and self._is_inside_ship(nx, ny):
                diff = (self.oxygen_grid[nx, ny] - self.oxygen_grid[x, y]) * self.diffusion_rate * dt
                new_grid[x, y] += diff
                new_grid[nx, ny] -= diff
    
    def _apply_oxygen_effects(self, entity_positions: Dict, dt: float):
        """Apply oxygen effects to entities"""
        for pos, entities in entity_positions.items():
            oxygen_level = self.oxygen_grid[pos[0], pos[1]]
            if oxygen_level < self.critical_oxygen:
                damage = (self.critical_oxygen - oxygen_level) * self.damage_rate * dt
                for entity in entities:
                    if hasattr(entity, 'take_damage'):
                        entity.take_damage(damage)
    
    def add_oxygen(self, x: int, y: int, amount: float):
        """Add oxygen at specified location from life support"""
        if self._is_inside_ship(x, y):
            self.oxygen_grid[x, y] = min(1.0, self.oxygen_grid[x, y] + amount) 