import pygame
from .base_state import State
from utils.config import *
from entities.manager import EntityManager
from entities.player import Player
from utils.save_load import save_game, load_game

class GameState(State):
    def __init__(self, game):
        super().__init__(game)
        self.entity_manager = EntityManager()
        # Create player at center of screen
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.entity_manager.add_entity(self.player)
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state('pause')

    def update(self, dt):
        self.entity_manager.update(dt)

    def render(self, screen):
        screen.fill(BLACK)
        self.entity_manager.render(screen) 

    def save_game_state(self, slot=None):
        filepath = save_game(self, slot)
        print(f"Game saved to: {filepath}")
    
    def load_game_state(self, filepath):
        save_data = load_game(filepath)
        
        # Clear current entities
        self.entity_manager.clear()
        
        # Recreate entities from save data
        for entity_data in save_data["entities"]:
            if entity_data["type"] == "Player":
                self.player = Player.from_dict(entity_data)
                self.entity_manager.add_entity(self.player)
            # Add more entity types as needed 