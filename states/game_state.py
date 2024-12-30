import pygame

from entities.alien import Alien
from .base_state import State
from utils.config import *
from entities.manager import EntityManager
from entities.alien import Alien
from core.tilemap import TileMap
from utils.save_load import save_game, load_game
import random
from levels.ufo_level import UfoLevel
from levels.abduction_level import AbductionLevel

class GameState(State):
    def __init__(self, game):
        super().__init__(game)
        
        # Level management
        self.levels = {
            'ufo': UfoLevel(self),
            'abduction': AbductionLevel(self)
        }
        self.current_level = None
        # Initialize the entity manager
        self.entity_manager = EntityManager()
        
    def change_level(self, level_name):
        if self.current_level:
            self.current_level.cleanup()
            
        self.current_level = self.levels[level_name]
        self.current_level.initialize()
        
    def enter_state(self):
        # Start with UFO level by default
        self.change_level('ufo')

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state('pause')
                elif event.key == pygame.K_TAB:
                    # Toggle between UFO and Abduction levels
                    new_level = 'abduction' if self.current_level == self.levels['ufo'] else 'ufo'
                    self.change_level(new_level)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x = mouse_x + int(self.camera_x)
                    world_y = mouse_y + int(self.camera_y)
                    tile_x = world_x // TILE_SIZE
                    tile_y = world_y // TILE_SIZE
                    
                    # Delegate click handling to current level
                    self.current_level.handle_click(tile_x, tile_y)

    def update(self, dt):
        if self.current_level:
            self.current_level.update(dt)
            
            # Camera follows selected alien
            followed_alien = next((alien for alien in self.current_level.aliens if alien.selected), 
                                self.current_level.aliens[0])
            
            self.camera_x = followed_alien.position.x - WINDOW_WIDTH // 2
            self.camera_y = followed_alien.position.y - WINDOW_HEIGHT // 2
            
            # Keep camera in bounds
            self.camera_x = max(0, min(self.camera_x, MAP_WIDTH * TILE_SIZE - WINDOW_WIDTH))
            self.camera_y = max(0, min(self.camera_y, MAP_HEIGHT * TILE_SIZE - WINDOW_HEIGHT))

    def render(self, screen):
        screen.fill(BLACK)
        if self.current_level:
            self.current_level.render(screen, self.camera_x, self.camera_y)

    def save_game_state(self, slot=None):
        filepath = save_game(self, slot)
        print(f"Game saved to: {filepath}")
    
    def load_game_state(self, filepath):
        save_data = load_game(filepath)
        
        # Clear current entities
        self.entity_manager.clear()
        
        # Recreate entities from save data
        for entity_data in save_data["entities"]:
            if entity_data["type"] == "Alien":
                new_alien = Alien.from_dict(entity_data)
                new_alien.game_state = self
                self.aliens.append(new_alien)
                self.entity_manager.add_entity(new_alien)
            # Add more entity types as needed 