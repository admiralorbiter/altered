import pygame

from entities.alien import Alien
from .base_state import State
from utils.config import *
from entities.manager import EntityManager
from entities.alien import Alien
from core.tilemap import TileMap
from utils.save_load import save_game, load_game
import random

class GameState(State):
    def __init__(self, game):
        super().__init__(game)
        self.entity_manager = EntityManager()
        
        # Create tilemap
        self.tilemap = TileMap(MAP_WIDTH, MAP_HEIGHT)
        self._create_example_map()
        
        # Create aliens at different positions with different colors
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        
        # Main alien (pink)
        self.aliens = []
        main_alien = Alien(center_x, center_y, (255, 192, 203, 128))
        main_alien.game_state = self
        self.aliens.append(main_alien)
        
        # Blue alien
        blue_alien = Alien(center_x - 2, center_y - 2, (100, 149, 237, 128))
        blue_alien.game_state = self
        self.aliens.append(blue_alien)
        
        # Green alien
        green_alien = Alien(center_x + 2, center_y - 2, (144, 238, 144, 128))
        green_alien.game_state = self
        self.aliens.append(green_alien)
        
        # Purple alien
        purple_alien = Alien(center_x - 2, center_y + 2, (147, 112, 219, 128))
        purple_alien.game_state = self
        self.aliens.append(purple_alien)
        
        # Orange alien
        orange_alien = Alien(center_x + 2, center_y + 2, (255, 165, 0, 128))
        orange_alien.game_state = self
        self.aliens.append(orange_alien)
        
        # Add all aliens to entity manager
        for alien in self.aliens:
            self.entity_manager.add_entity(alien)
        
        # Camera position (follows selected alien or first alien)
        self.camera_x = 0
        self.camera_y = 0
        
    def _create_example_map(self):
        """Create a test level with clear wall patterns"""
        # Set base ground as grass
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                self.tilemap.set_tile(x, y, "ground", 1)  # Grass
        
        # Add random dirt patches (about 20% of tiles)
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if random.random() < 0.2:  # 20% chance for dirt
                    self.tilemap.set_tile(x, y, "ground", 2)  # Dirt
        
        # Create a clear test area near the player spawn
        center_x = MAP_WIDTH // 2
        center_y = MAP_HEIGHT // 2
        
        # Box around spawn (10 tiles away)
        for x in range(center_x - 10, center_x + 11):
            for y in range(center_y - 10, center_y + 11):
                if (x == center_x - 10 or x == center_x + 10 or 
                    y == center_y - 10 or y == center_y + 10):
                    self.tilemap.set_tile(x, y, "collision", 1)
                    self.tilemap.set_tile(x, y, "ground", 3)  # Dark wall
        
        # Cross pattern inside box
        for i in range(-5, 6):
            # Horizontal line
            self.tilemap.set_tile(center_x + i, center_y - 3, "collision", 1)
            self.tilemap.set_tile(center_x + i, center_y - 3, "ground", 4)  # Stone wall
            
            # Vertical line
            self.tilemap.set_tile(center_x - 3, center_y + i, "collision", 1)
            self.tilemap.set_tile(center_x - 3, center_y + i, "ground", 4)  # Stone wall
        
        # Red wall obstacles in corners
        corners = [
            (center_x - 7, center_y - 7),
            (center_x + 7, center_y - 7),
            (center_x - 7, center_y + 7),
            (center_x + 7, center_y + 7)
        ]
        
        for cx, cy in corners:
            for dx in range(3):
                for dy in range(3):
                    self.tilemap.set_tile(cx + dx, cy + dy, "collision", 1)
                    self.tilemap.set_tile(cx + dx, cy + dy, "ground", 5)  # Red wall

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state('pause')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x = mouse_x + int(self.camera_x)
                    world_y = mouse_y + int(self.camera_y)
                    tile_x = world_x // TILE_SIZE
                    tile_y = world_y // TILE_SIZE
                    
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

    def update(self, dt):
        self.entity_manager.update(dt)
        
        # Find selected alien or use first one
        followed_alien = next((alien for alien in self.aliens if alien.selected), self.aliens[0])
        
        # Update camera to follow the selected/first alien
        self.camera_x = followed_alien.position.x - WINDOW_WIDTH // 2
        self.camera_y = followed_alien.position.y - WINDOW_HEIGHT // 2
        
        # Keep camera in bounds
        self.camera_x = max(0, min(self.camera_x, MAP_WIDTH * TILE_SIZE - WINDOW_WIDTH))
        self.camera_y = max(0, min(self.camera_y, MAP_HEIGHT * TILE_SIZE - WINDOW_HEIGHT))

    def render(self, screen):
        screen.fill(BLACK)
        
        # Render tilemap
        self.tilemap.render(screen, int(self.camera_x), int(self.camera_y))
        
        # Render entities with camera offset
        for entity in self.entity_manager.entities:
            entity.render_with_offset(screen, self.camera_x, self.camera_y)

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