import pygame
from .base_state import State
from utils.config import *
from entities.manager import EntityManager
from entities.player import Player
from core.tilemap import TileMap
from utils.save_load import save_game, load_game

class GameState(State):
    def __init__(self, game):
        super().__init__(game)
        self.entity_manager = EntityManager()
        
        # Create tilemap
        self.tilemap = TileMap(MAP_WIDTH, MAP_HEIGHT)
        
        # Create some example terrain (temporary)
        self._create_example_map()
        
        # Create player at center of map (in tile coordinates)
        center_tile_x = MAP_WIDTH // 2
        center_tile_y = MAP_HEIGHT // 2
        self.player = Player(center_tile_x, center_tile_y)
        self.entity_manager.add_entity(self.player)
        
        # Camera position (follows player)
        self.camera_x = 0
        self.camera_y = 0
        
    def _create_example_map(self):
        """Create a simple example map (temporary)"""
        # Create a border of walls
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                # Set ground tiles
                if x % 2 == y % 2:
                    self.tilemap.set_tile(x, y, "ground", 1)  # Grass
                else:
                    self.tilemap.set_tile(x, y, "ground", 2)  # Dirt
                
                # Set collision for borders
                if x == 0 or x == MAP_WIDTH-1 or y == 0 or y == MAP_HEIGHT-1:
                    self.tilemap.set_tile(x, y, "collision", 1)
                    self.tilemap.set_tile(x, y, "ground", 3)  # Wall tile
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state('pause')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Convert screen coordinates to world coordinates
                    world_x = mouse_x + self.camera_x
                    world_y = mouse_y + self.camera_y
                    # Convert to tile coordinates
                    tile_x = int(world_x // TILE_SIZE)
                    tile_y = int(world_y // TILE_SIZE)
                    
                    # Get player's current tile position
                    player_tile_x = int(self.player.current_tile[0])
                    player_tile_y = int(self.player.current_tile[1])
                    
                    if (tile_x, tile_y) == (player_tile_x, player_tile_y):
                        self.player.select()
                    elif self.player.selected:
                        # Check if tile is walkable
                        if self.tilemap.is_walkable(tile_x, tile_y):
                            self.player.set_target(tile_x, tile_y)
                            if not self.player.moving:  # Only deselect if not moving
                                self.player.deselect()

    def update(self, dt):
        self.entity_manager.update(dt)
        
        # Update camera to follow player
        self.camera_x = self.player.position.x - WINDOW_WIDTH // 2
        self.camera_y = self.player.position.y - WINDOW_HEIGHT // 2
        
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
            if entity_data["type"] == "Player":
                self.player = Player.from_dict(entity_data)
                self.entity_manager.add_entity(self.player)
            # Add more entity types as needed 