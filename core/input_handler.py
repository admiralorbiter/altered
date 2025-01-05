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
        elif event.key == pygame.K_c:
            # Get selected aliens
            selected_aliens = [alien for alien in self.game_state.current_level.aliens if alien.selected]
            
            # Get nearest enemy to each selected alien
            for alien in selected_aliens:
                nearest_enemy = None
                min_distance = float('inf')
                
                # Find nearest enemy within capture range
                for entity in self.game_state.current_level.entity_manager.entities:
                    if isinstance(entity, BaseEnemy):
                        distance = (entity.position - alien.position).length()
                        if distance <= alien.capture_range and distance < min_distance:
                            min_distance = distance
                            nearest_enemy = entity
                
                # Attempt capture if enemy found
                if nearest_enemy and alien.capture:
                    alien.capture.attempt_capture(nearest_enemy)
            
            return True
        elif event.key == pygame.K_r:  # Add release key handler
            # Get selected aliens
            selected_aliens = [alien for alien in self.game_state.current_level.aliens if alien.selected]
            
            # Release any carried targets
            for alien in selected_aliens:
                if alien.capture and alien.capture.carrying_target:
                    alien.capture.release_target()
            
            return True
        elif event.key == pygame.K_b:
            # Toggle build menu
            if hasattr(self.game_state.ui.hud, 'build_ui'):
                self.game_state.ui.hud.build_ui.toggle_build_menu()
            return True
        return False

    def _handle_mouse_click(self, event):
        # First check if we're in building placement mode
        if self.game_state.build_system.is_placing:
            if event.button == 1:  # Left click
                if self.game_state.build_system.ghost_valid:
                    success = self.game_state.build_system.place_building()
                    if success:
                        self.game_state.build_system.cancel_placement()
                    return True
            elif event.button == 3:  # Right click
                self.game_state.build_system.cancel_placement()
                return True
            return False  # Consume other clicks while in build mode

        # Handle existing click logic for other game modes
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
        # Get mouse position before zoom
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Let camera system handle the zoom
        self.game_state.camera_system.handle_zoom(event.y, (mouse_x, mouse_y))
        return True