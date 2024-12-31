import pygame

from entities.alien import Alien
from levels.test_level import TestLevel
from systems.debug_ui import DebugUI
from .base_state import State
from utils.config import *
from entities.manager import EntityManager
from entities.alien import Alien
from core.tilemap import TileMap
from utils.save_load import save_game, load_game
import random
from levels.ufo_level import UfoLevel
from levels.abduction_level import AbductionLevel
from systems.ui import HUD, CaptureUI, WireUI
from systems.ai_system import AISystem
from utils.pathfinding import PathReservationSystem
from systems.capture_system import CaptureSystem
from entities.enemies.base_enemy import BaseEnemy
from systems.wire_system import WireSystem
from systems.task_system import TaskSystem

class GameState(State):
    def __init__(self, game):
        super().__init__(game)
        
        # Initialize game state
        self.zoom_level = 1.0
        self.camera_x = 0
        self.camera_y = 0
        self.wire_mode = False
        
        # Initialize UI elements list before adding elements
        self.ui_elements = []
        
        # Create UI elements
        self.hud = HUD(self)
        self.capture_ui = CaptureUI(self)
        self.wire_ui = WireUI(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, self)
        self.debug_ui = DebugUI(self)
        
        # Add UI elements to list
        self.ui_elements.extend([self.hud, self.capture_ui, self.wire_ui])
        
        # Initialize systems
        self.capture_system = CaptureSystem(self)
        self.ai_system = AISystem()
        self.path_reservation_system = PathReservationSystem()
        self.wire_system = WireSystem(self)
        self.task_system = TaskSystem(self)
        
        # Initialize level
        self.current_level = self.load_level('test')  # Changed to test level for now
        
        # Camera and zoom properties
        self.min_zoom = 0.5  # Maximum zoom out (half size)
        self.max_zoom = 2.0  # Maximum zoom in (double size)
        self.zoom_speed = 0.1  # How much to zoom per scroll
        
        # Level management
        self.levels = {
            'ufo': UfoLevel(self),
            'abduction': AbductionLevel(self),
            'test': TestLevel(self)
        }
        # Initialize the entity manager
        self.entity_manager = EntityManager(self)
        self.current_time = 0  # Add time tracking
        
    def load_level(self, level_name):
        """Load a level by name"""
        if level_name == 'test':
            self.current_level = TestLevel(self)
        elif level_name == 'ufo':
            self.current_level = UfoLevel(self)
        elif level_name == 'abduction':
            self.current_level = AbductionLevel(self)
        else:
            raise ValueError(f"Unknown level: {level_name}")
            
        self.current_level.initialize()
        return self.current_level
        
    def change_level(self, level_name):
        if self.current_level:
            self.current_level.cleanup()
            
        self.current_level = self.levels[level_name]
        self.current_level.initialize()
        
    def enter_state(self):
        # Start with UFO level by default
        self.change_level('ufo')

    def handle_events(self, events):
        # Handle UI elements first
        for event in events:
            # Check if any UI element handled the event
            ui_handled = False
            for ui_element in self.ui_elements:
                if ui_element.handle_event(event):
                    ui_handled = True
                    break
                
            # If UI didn't handle it and we're in wire mode, let wire system try
            if not ui_handled and self.wire_mode:
                if self.wire_system.handle_event(event):
                    continue
                
            # Handle other game events if neither UI nor wire system handled it
            if not ui_handled:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game.change_state('pause')
                    elif event.key == pygame.K_TAB:
                        # Toggle between UFO and Abduction levels
                        new_level = 'abduction' if self.current_level == self.levels['ufo'] else 'ufo'
                        self.change_level(new_level)
                    elif event.key == pygame.K_F3:  # F3 to toggle debug UI
                        self.debug_ui.toggle()
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
                        
                        # If in capture mode, try to mark targets
                        if self.capture_system.capture_mode:
                            for entity in self.current_level.entity_manager.entities:
                                if isinstance(entity, BaseEnemy):
                                    entity_rect = entity.get_rect()
                                    if entity_rect.collidepoint(world_x, world_y):
                                        self.capture_system.mark_target(entity)
                                        break
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
            # Remove or comment out electrical components debug print
            # print("\n=== GameState Update ===")
            # print(f"Total electrical components: {len(self.current_level.tilemap.electrical_components)}")
            # for pos, comp in self.current_level.tilemap.electrical_components.items():
            #     print(f"Component at {pos}: {comp}")
            
            self.capture_system.update(dt)
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
            
            # Render the level
            self.current_level.render(world_surface, self.camera_x, self.camera_y)
            
            # Draw wire system preview
            self.wire_system.draw(world_surface)
            
            # Blit the world surface to the screen
            screen.blit(world_surface, (0, 0))
            
            # Draw all UI elements
            for ui_element in self.ui_elements:
                ui_element.draw(screen)
            
            # Draw debug UI last so it's on top
            self.debug_ui.draw(screen)
        
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