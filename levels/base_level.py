from abc import ABC, abstractmethod

import pygame
from core.tilemap import TileMap
from entities.manager import EntityManager
from utils.config import BLACK, MAP_HEIGHT, MAP_WIDTH, TILE_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH

class BaseLevel(ABC):
    def __init__(self, game_state):
        self.game_state = game_state
        self.tilemap = TileMap(MAP_WIDTH, MAP_HEIGHT, game_state)
        self.entity_manager = EntityManager(game_state)
        self.aliens = []
        self.enemies = []
        
    @abstractmethod
    def initialize(self):
        """Set up the level's initial state"""
        pass
        
    @abstractmethod
    def update(self, dt):
        """Update level-specific logic"""
        pass
        
    def render(self, screen, camera_x, camera_y):
        """Render the level and all its entities"""
        # Fill background
        screen.fill(BLACK)
        
        # Render tilemap
        self.tilemap.render(screen, camera_x, camera_y)
        
        # Render entities and items
        for item in self.entity_manager.items:
            if item.active:
                item.render_with_offset(screen, camera_x, camera_y)
        
        for entity in self.entity_manager.entities:
            if entity.active:
                entity.render_with_offset(screen, camera_x, camera_y)
        
    def handle_click(self, tile_x, tile_y):
        """Handle mouse click events"""
        # Check if clicking on any alien
        clicked_alien = None
        for alien in self.aliens:
            alien_tile_x = int(alien.position.x // TILE_SIZE)
            alien_tile_y = int(alien.position.y // TILE_SIZE)
            if (tile_x, tile_y) == (alien_tile_x, alien_tile_y):
                clicked_alien = alien
                break
        
        if clicked_alien:
            # Deselect all other aliens
            for alien in self.aliens:
                if alien != clicked_alien:
                    alien.deselect()
            clicked_alien.select()
        else:
            # If no alien clicked, try to move selected alien
            for alien in self.aliens:
                if alien.selected and self.tilemap.is_walkable(tile_x, tile_y):
                    alien.set_target(tile_x, tile_y)
                    break
        
    def cleanup(self):
        """Clean up resources when leaving level"""
        self.entity_manager.clear()
        self.aliens.clear()
        self.cats.clear() 