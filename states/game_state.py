import pygame

from entities.alien import Alien
from levels.test_level import TestLevel
from .base_state import State
from utils.config import *
from entities.manager import EntityManager
from entities.alien import Alien
from core.tilemap import TileMap
from utils.save_load import save_game, load_game
import random
from levels.ufo_level import UfoLevel
from levels.abduction_level import AbductionLevel
from systems.ui import HUD
from systems.ai_system import AISystem
from utils.pathfinding import PathReservationSystem

class GameState(State):
    def __init__(self, game):
        super().__init__(game)
        
        # Camera and zoom properties
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_level = 1.0
        self.min_zoom = 0.5  # Maximum zoom out (half size)
        self.max_zoom = 2.0  # Maximum zoom in (double size)
        self.zoom_speed = 0.1  # How much to zoom per scroll
        
        # Level management
        self.levels = {
            'ufo': UfoLevel(self),
            'abduction': AbductionLevel(self),
            'test': TestLevel(self)
        }
        self.current_level = None
        # Initialize the entity manager
        self.entity_manager = EntityManager(self)
        self.hud = HUD(self)
        self.ai_system = AISystem()
        self.path_reservation_system = PathReservationSystem()
        self.current_time = 0  # Add time tracking
        
    def change_level(self, level_name):
        if self.current_level:
            self.current_level.cleanup()
            
        self.current_level = self.levels[level_name]
        self.current_level.initialize()
        
    def enter_state(self):
        # Start with UFO level by default
        self.change_level('ufo')

    def handle_events(self, events):
        # Let HUD handle events first
        for event in events:
            if self.hud.handle_event(event):
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state('pause')
                elif event.key == pygame.K_TAB:
                    # Toggle between UFO and Abduction levels
                    new_level = 'abduction' if self.current_level == self.levels['ufo'] else 'ufo'
                    self.change_level(new_level)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Convert screen coordinates to world coordinates considering zoom
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x = (mouse_x / self.zoom_level) + int(self.camera_x)
                    world_y = (mouse_y / self.zoom_level) + int(self.camera_y)
                    tile_x = int(world_x // TILE_SIZE)
                    tile_y = int(world_y // TILE_SIZE)
                    
                    # Delegate click handling to current level
                    self.current_level.handle_click(tile_x, tile_y)
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom in/out with mouse wheel
                old_zoom = self.zoom_level
                self.zoom_level = max(self.min_zoom, 
                                    min(self.max_zoom, 
                                        self.zoom_level + event.y * self.zoom_speed))
                
                # Adjust camera to zoom towards mouse position
                if old_zoom != self.zoom_level:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Calculate zoom adjustment to center on mouse position
                    zoom_factor = self.zoom_level / old_zoom
                    self.camera_x += (mouse_x / old_zoom) * (1 - zoom_factor)
                    self.camera_y += (mouse_y / old_zoom) * (1 - zoom_factor)

    def update(self, dt):
        if self.current_level:
            self.current_level.update(dt)
            
            # Camera follows selected alien
            followed_alien = next((alien for alien in self.current_level.aliens if alien.selected), 
                                self.current_level.aliens[0])
            
            # Adjust camera position based on zoom level
            visible_width = WINDOW_WIDTH / self.zoom_level
            visible_height = WINDOW_HEIGHT / self.zoom_level
            
            target_x = followed_alien.position.x - visible_width/2
            target_y = followed_alien.position.y - visible_height/2
            
            # Keep camera in bounds
            max_x = MAP_WIDTH * TILE_SIZE - visible_width
            max_y = MAP_HEIGHT * TILE_SIZE - visible_height
            self.camera_x = max(0, min(target_x, max_x))
            self.camera_y = max(0, min(target_y, max_y))

        self.hud.update(dt)
        self.ai_system.update(dt, self)

    def render(self, screen):
        # Fill background
        screen.fill(BLACK)
        
        if self.current_level:
            # Create a surface for the game world
            world_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            world_surface.fill(BLACK)
            
            # Calculate visible area
            visible_width = WINDOW_WIDTH / self.zoom_level
            visible_height = WINDOW_HEIGHT / self.zoom_level
            
            # Render the level
            self.current_level.render(world_surface, self.camera_x, self.camera_y)
            
            # Blit the world surface to the screen
            screen.blit(world_surface, (0, 0))
            
            # Draw HUD on top
            self.hud.draw(screen)
        
        # Flip display
        pygame.display.flip()

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