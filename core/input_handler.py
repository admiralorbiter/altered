import pygame
from entities.enemies.base_enemy import BaseEnemy
from utils.config import *


class InputHandler:
    def __init__(self, game_state):
        self.game_state = game_state
        
    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            return self._handle_keyboard(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click(event)
        elif event.type == pygame.MOUSEWHEEL:
            return self._handle_mouse_wheel(event)
        return False
        
    def _handle_keyboard(self, event):
        if event.key == pygame.K_ESCAPE:
            self.game_state.game.change_state('pause')
            return True
        elif event.key == pygame.K_TAB:
            new_level = 'abduction' if self.game_state.current_level == self.game_state.levels['ufo'] else 'ufo'
            self.game_state.change_level(new_level)
            return True
        elif event.key == pygame.K_F3:
            self.game_state.debug_ui.toggle()
            return True
        return False

    def _handle_mouse_click(self, event):
        if event.button == 1:  # Left click
            # Convert screen coordinates to world coordinates considering zoom
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x = (mouse_x / self.game_state.zoom_level) + int(self.game_state.camera_x)
            world_y = (mouse_y / self.game_state.zoom_level) + int(self.game_state.camera_y)
            tile_x = int(world_x // TILE_SIZE)
            tile_y = int(world_y // TILE_SIZE)
            
            # Delegate click handling to current level
            self.game_state.current_level.handle_click(tile_x, tile_y)
            
            # If in capture mode, try to mark targets
            if self.game_state.capture_system.capture_mode:
                for entity in self.game_state.current_level.entity_manager.entities:
                    if isinstance(entity, BaseEnemy):
                        entity_rect = entity.get_rect()
                        if entity_rect.collidepoint(world_x, world_y):
                            self.game_state.capture_system.mark_target(entity)
                            return True
        return False

    def _handle_mouse_wheel(self, event):
        # Store old zoom for comparison
        old_zoom = self.game_state.zoom_level
        
        # Calculate new zoom level
        new_zoom = max(self.game_state.min_zoom,
                      min(self.game_state.max_zoom,
                          self.game_state.zoom_level + event.y * self.game_state.zoom_speed))
        
        # If zoom changed, adjust camera
        if old_zoom != new_zoom:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            zoom_factor = new_zoom / old_zoom
            
            # Update game state
            self.game_state.zoom_level = new_zoom
            self.game_state.camera_x += (mouse_x / old_zoom) * (1 - zoom_factor)
            self.game_state.camera_y += (mouse_y / old_zoom) * (1 - zoom_factor)
            return True
            
        return False