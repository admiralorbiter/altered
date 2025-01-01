import pygame

from entities.alien import Alien
from levels.test_level import TestLevel
from systems.debug_ui import DebugUI
from .base_state import State
from utils.config import *
from entities.entity_manager import EntityManager
from entities.alien import Alien
from utils.save_load import save_game, load_game
from levels.ufo_level import UfoLevel
from levels.abduction_level import AbductionLevel
from systems.ui import HUD, CaptureUI, WireUI
from systems.ai_system import AISystem
from utils.pathfinding import PathReservationSystem
from systems.capture_system import CaptureSystem
from entities.enemies.base_enemy import BaseEnemy
from systems.wire_system import WireSystem
from systems.task_system import TaskSystem
from systems.camera.camera_system import CameraSystem
from core.input_handler import InputHandler

class GameState(State):
    """
    Main gameplay state handling level management, systems coordination,
    and player interaction. Manages the active game world and its entities.
    """
    def __init__(self, game):
        super().__init__(game)
        
        # Initialize core systems
        self.camera_system = CameraSystem(self)
        self.input_handler = InputHandler(self)
        
        # Initialize UI elements list before adding elements
        self.ui_elements = []
        
        # Create UI elements
        self.hud = HUD(self)
        self.capture_ui = CaptureUI(self)
        self.wire_ui = WireUI(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, self)
        self.debug_ui = DebugUI(self)
        
        # Add UI elements to list
        self.ui_elements.extend([self.hud, self.capture_ui, self.wire_ui])
        
        # Initialize gameplay systems
        self.capture_system = CaptureSystem(self)
        self.ai_system = AISystem()
        self.path_reservation_system = PathReservationSystem()
        self.wire_system = WireSystem(self)
        self.task_system = TaskSystem(self)
        
        # Level management
        self.levels = {
            'ufo': UfoLevel(self),
            'abduction': AbductionLevel(self),
            'test': TestLevel(self)
        }
        self.current_level = None
        
        # Initialize the entity manager
        self.entity_manager = EntityManager(self)
        self.current_time = 0
        self.wire_mode = False

    @property
    def zoom_level(self):
        """Compatibility property that forwards zoom requests to camera system"""
        return self.camera_system.zoom_level

    @property
    def camera_x(self):
        """Compatibility property that forwards camera x position to camera system"""
        return self.camera_system.position.x

    @property
    def camera_y(self):
        """Compatibility property that forwards camera y position to camera system"""
        return self.camera_system.position.y

    def handle_events(self, events):
        """Process input events for gameplay."""
        for event in events:
            # Check if any UI element handled the event
            ui_handled = False
            for ui_element in self.ui_elements:
                if ui_element.handle_event(event):
                    ui_handled = True
                    break
                    
            # If UI didn't handle it, try other systems
            if not ui_handled:
                if self.wire_mode and self.wire_system.handle_event(event):
                    continue
                elif self.input_handler.handle_game_input(event):
                    continue
                elif event.type == pygame.MOUSEWHEEL:
                    mouse_pos = pygame.mouse.get_pos()
                    self.camera_system.handle_zoom(event.y, mouse_pos)

    def update(self, dt):
        """Update game state including level, camera, and systems."""
        if self.current_level:
            # Update core systems
            self.capture_system.update(dt)
            self.current_level.update(dt)
            
            # Update camera position to follow selected alien
            followed_alien = next((alien for alien in self.current_level.aliens if alien.selected), 
                                self.current_level.aliens[0])
            self.camera_system.update(followed_alien)

        self.hud.update(dt)
        self.ai_system.update(dt, self)
    
    def render(self, screen):
        """Render the game world, entities, and UI."""
        screen.fill(BLACK)
        
        if self.current_level:
            # Create world view
            world_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            world_surface.fill(BLACK)
            
            # Render the level with camera position from camera system
            self.current_level.render(world_surface, 
                                    self.camera_system.position.x, 
                                    self.camera_system.position.y)
            
            # Draw wire system preview
            self.wire_system.draw(world_surface)
            
            # Apply zoom from camera system
            if self.camera_system.zoom_level != 1.0:
                scaled_size = (int(WINDOW_WIDTH * self.camera_system.zoom_level),
                             int(WINDOW_HEIGHT * self.camera_system.zoom_level))
                world_surface = pygame.transform.scale(world_surface, scaled_size)
            
            # Blit the world surface to the screen
            screen.blit(world_surface, (0, 0))
            
            # Draw UI elements
            for ui_element in self.ui_elements:
                ui_element.draw(screen)
            
            # Draw debug UI last
            self.debug_ui.draw(screen)
        
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

    def change_level(self, level_name):
        """
        Change to a different level.
        
        Args:
            level_name (str): Name of the level to change to ('ufo', 'abduction', or 'test')
        """
        if level_name in self.levels:
            # Clear current level if it exists
            if self.current_level:
                self.entity_manager.clear()
            
            # Set and initialize the new level
            self.current_level = self.levels[level_name]
            self.current_level.initialize()
            
            # Reset camera position
            self.camera_system.position = pygame.math.Vector2(0, 0)
            self.camera_system.zoom_level = 1.0
        else:
            print(f"Warning: Level '{level_name}' not found") 