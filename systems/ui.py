import pygame
from entities.alien import Alien
from entities.cat import Cat
from entities.enemies.base_enemy import BaseEnemy
from systems.capture_system import CaptureState
from utils.config import *

class UIElement:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.active = True
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def handle_event(self, event):
        if not self.active:
            return False
        
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        return False

    def update(self, dt):
        if not self.active:
            return
        
        for child in self.children:
            child.update(dt)

    def draw(self, surface):
        if not self.visible:
            return
        
        for child in self.children:
            child.draw(surface)

class Label(UIElement):
    def __init__(self, x, y, text, font_size=32, color=WHITE):
        self.font = pygame.font.Font(None, font_size)
        self.text = text
        self.color = color
        text_surface = self.font.render(text, True, color)
        super().__init__(x, y, text_surface.get_width(), text_surface.get_height())

    def set_text(self, text):
        self.text = text
        text_surface = self.font.render(text, True, self.color)
        self.rect.width = text_surface.get_width()
        self.rect.height = text_surface.get_height()

    def draw(self, surface):
        if not self.visible:
            return
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, self.rect)
        super().draw(surface)

class Button(UIElement):
    def __init__(self, x, y, width, height, text, callback=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 24)
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.text_color = (255, 255, 255)
        self.is_hovered = False
        
    def handle_event(self, event):
        if not self.visible or not self.active:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered and self.callback:
                self.callback()
                return True
        return False
        
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class HUD(UIElement):
    def __init__(self, game_state):
        super().__init__(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.game_state = game_state
        
        # Create status labels
        self.health_label = Label(10, 10, "Health: 100%")
        self.add_child(self.health_label)
        
        self.morale_label = Label(10, 40, "Morale: 100%")
        self.add_child(self.morale_label)
        
        # Add capture button
        self.capture_button = Button(10, 70, 100, 30, "Capture", self.attempt_capture)
        self.capture_button.visible = False
        self.add_child(self.capture_button)
        
        # Add release button
        self.release_button = Button(10, 70, 100, 30, "Release", self.release_captured)
        self.release_button.visible = False
        self.add_child(self.release_button)
        
    def attempt_capture(self):
        """Handle capture button press"""
        selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                             if alien.selected), None)
        if not selected_alien:
            return
            
        # Find nearest valid target
        nearest_target = None
        min_distance = float('inf')
        
        for entity in self.game_state.current_level.entity_manager.entities:
            if (isinstance(entity, BaseEnemy) and 
                hasattr(entity, 'capture_state') and 
                entity.capture_state == CaptureState.NONE):
                
                distance = (entity.position - selected_alien.position).length()
                if distance < min_distance and distance <= selected_alien.capture_range:
                    min_distance = distance
                    nearest_target = entity
                    
        if nearest_target:
            success = selected_alien.attempt_capture(nearest_target)
            if success:
                self.capture_button.visible = False
                self.release_button.visible = True
        else:
            print("No valid target in range")  # Debug print
            
    def release_captured(self):
        """Handle release button press"""
        selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                             if alien.selected), None)
        if selected_alien and selected_alien.carrying_target:
            selected_alien.release_target()
            self.release_button.visible = False
            
    def update(self, dt):
        super().update(dt)
        
        # Update button visibility based on selected alien
        selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                             if alien.selected), None)
                             
        if selected_alien:
            if selected_alien.carrying_target:
                self.capture_button.visible = False
                self.release_button.visible = True
            else:
                # Check if any valid targets are in range
                has_target_in_range = any(
                    isinstance(entity, BaseEnemy) and
                    hasattr(entity, 'capture_state') and
                    entity.capture_state == CaptureState.NONE and
                    (entity.position - selected_alien.position).length() <= selected_alien.capture_range
                    for entity in self.game_state.current_level.entity_manager.entities
                )
                self.capture_button.visible = has_target_in_range
                self.release_button.visible = False
        else:
            self.capture_button.visible = False
            self.release_button.visible = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.capture_button.visible and self.capture_button.rect.collidepoint(mouse_pos):
                print("Capture button clicked")  # Debug print
                self.attempt_capture()
        super().handle_event(event)

class WireUI(UIElement):
    def __init__(self, x, y, width, height, game_state):
        super().__init__(x, y, width, height)
        self.game_state = game_state
        self.ghost_position = None
        self.ghost_valid = False
        self.selected_component = 'wire'
        self.pending_wires = []

    def handle_event(self, event):
        if not self.game_state.wire_mode:
            return False

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            # Convert screen coordinates to tile coordinates
            tile_x = int((mouse_pos[0] / self.game_state.zoom_level + self.game_state.camera_x) // TILE_SIZE)
            tile_y = int((mouse_pos[1] / self.game_state.zoom_level + self.game_state.camera_y) // TILE_SIZE)
            self.ghost_position = (tile_x, tile_y)
            self.ghost_valid = self.game_state.current_level.tilemap.is_walkable(tile_x, tile_y)
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.ghost_position and self.ghost_valid:
                tile_x, tile_y = self.ghost_position
                
                # Create and add the electrical component
                from core.tiles import ElectricalComponent
                component = ElectricalComponent(type='wire')
                self.game_state.current_level.tilemap.electrical_components[(tile_x, tile_y)] = component
                
                # Add to pending wires for entity placement
                self.pending_wires.append(self.ghost_position)
                self.assign_wire_placement()
                return True

        return super().handle_event(event)

    def draw(self, surface):
        # Always draw ghost wire when in wire mode
        if self.game_state.wire_mode and self.ghost_position:
            tile_x, tile_y = self.ghost_position
            
            # Calculate screen position
            screen_x = int((tile_x * TILE_SIZE - self.game_state.camera_x) * self.game_state.zoom_level)
            screen_y = int((tile_y * TILE_SIZE - self.game_state.camera_y) * self.game_state.zoom_level)
            tile_size = int(TILE_SIZE * self.game_state.zoom_level)
            
            # Draw ghost wire with transparency
            ghost_color = (255, 255, 0, 128) if self.ghost_valid else (255, 0, 0, 128)
            ghost_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            
            # Draw wire pattern with thicker lines
            wire_width = max(4 * self.game_state.zoom_level, 2)
            
            # Draw background for better visibility
            pygame.draw.rect(ghost_surface, (0, 0, 0, 100),
                           (0, 0, tile_size, tile_size))
            
            # Draw wire line
            pygame.draw.line(ghost_surface, ghost_color,
                           (tile_size * 0.2, tile_size * 0.5),
                           (tile_size * 0.8, tile_size * 0.5),
                           int(wire_width))
            
            # Draw larger connection nodes
            node_radius = max(4 * self.game_state.zoom_level, 3)
            pygame.draw.circle(ghost_surface, ghost_color,
                             (int(tile_size * 0.2), int(tile_size * 0.5)),
                             int(node_radius))
            pygame.draw.circle(ghost_surface, ghost_color,
                             (int(tile_size * 0.8), int(tile_size * 0.5)),
                             int(node_radius))
            
            # Draw border for better visibility
            pygame.draw.rect(ghost_surface, ghost_color,
                           (0, 0, tile_size, tile_size), 2)
            
            surface.blit(ghost_surface, (screen_x, screen_y))

    def assign_wire_placement(self):
        """Find nearest cat or selected alien to place the wire"""
        if not self.pending_wires:
            return

        wire_pos = self.pending_wires[0]
        
        # Try to find the nearest entity to place the wire
        nearest_entity = None
        min_distance = float('inf')
        
        # Check selected alien first
        selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                             if alien.selected), None)
        if selected_alien:
            distance = ((selected_alien.position.x // TILE_SIZE - wire_pos[0]) ** 2 + 
                       (selected_alien.position.y // TILE_SIZE - wire_pos[1]) ** 2) ** 0.5
            if distance < min_distance:
                nearest_entity = selected_alien
                min_distance = distance

        # Check cats
        for cat in self.game_state.current_level.cats:
            if not cat.is_dead and not cat.current_task:
                distance = ((cat.position.x // TILE_SIZE - wire_pos[0]) ** 2 + 
                          (cat.position.y // TILE_SIZE - wire_pos[1]) ** 2) ** 0.5
                if distance < min_distance:
                    nearest_entity = cat
                    min_distance = distance

        if nearest_entity:
            # Assign the wire placement task
            nearest_entity.set_wire_task(wire_pos, self.selected_component)
            self.pending_wires.pop(0)

class CaptureUI(UIElement):
    def __init__(self, game_state):
        # Position at bottom of screen
        super().__init__(10, WINDOW_HEIGHT - 75, 420, 30)  # Increased width for 3 buttons
        self.game_state = game_state
        
        # Create capture mode toggle button
        self.capture_mode_btn = Button(10, WINDOW_HEIGHT - 75, 130, 25,
                                    "Capture Mode: OFF",
                                    self.toggle_capture_mode)
        self.add_child(self.capture_mode_btn)
        
        # Create stealth mode toggle button
        self.stealth_mode_btn = Button(150, WINDOW_HEIGHT - 75, 130, 25,
                                    "Stealth: OFF",
                                    self.toggle_stealth_mode)
        self.add_child(self.stealth_mode_btn)
        
        # Add wire mode toggle button
        self.wire_mode_btn = Button(290, WINDOW_HEIGHT - 75, 130, 25,
                                 "Place Wire: OFF",
                                 self.toggle_wire_mode)
        self.add_child(self.wire_mode_btn)
    
    def toggle_wire_mode(self):
        """Toggle wire placement mode"""
        self.game_state.wire_mode = not self.game_state.wire_mode
        self.wire_mode_btn.text = f"Place Wire: {'ON' if self.game_state.wire_mode else 'OFF'}"
        
        # Turn off other modes when wire mode is enabled
        if self.game_state.wire_mode:
            self.game_state.capture_system.capture_mode = False
            self.capture_mode_btn.text = "Capture Mode: OFF"
            self.game_state.capture_system.stealth_mode = False
            self.stealth_mode_btn.text = "Stealth: OFF"
    
    def toggle_capture_mode(self):
        system = self.game_state.capture_system
        system.capture_mode = not system.capture_mode
        self.capture_mode_btn.text = f"Capture Mode: {'ON' if system.capture_mode else 'OFF'}"
        
        # Turn off wire mode when capture mode is enabled
        if system.capture_mode:
            self.game_state.wire_mode = False
            self.wire_mode_btn.text = "Place Wire: OFF"
    
    def toggle_stealth_mode(self):
        system = self.game_state.capture_system
        system.stealth_mode = not system.stealth_mode
        self.stealth_mode_btn.text = f"Stealth: {'ON' if system.stealth_mode else 'OFF'}" 