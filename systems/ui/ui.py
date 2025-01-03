import pygame
from entities.alien import Alien
from entities.cat import Cat
from entities.enemies.base_enemy import BaseEnemy
from systems.capture_system import CaptureState
from utils.config import *
from systems.ui.ui_elements import StylizedUIElements

# Base class for all UI elements providing core functionality for visibility, 
# event handling, and parent-child relationships
class UIElement:
    def __init__(self, x, y, width, height):
        """Initialize a UI element with position and dimensions"""
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.active = True
        self.parent = None
        self.children = []

    def add_child(self, child):
        """Add a child UI element and set its parent reference"""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        """Remove a child UI element and clear its parent reference"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def handle_event(self, event):
        """Process pygame events, propagating them to children in reverse order
        Returns True if the event was handled"""
        if not self.active:
            return False
        
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        return False

    def update(self, dt):
        """Update the element and its children with the given delta time"""
        if not self.active:
            return
        
        for child in self.children:
            child.update(dt)

    def draw(self, surface):
        """Draw the element and its children to the given surface"""
        if not self.visible:
            return
        
        for child in self.children:
            child.draw(surface)

# Text display component that renders a string with specified font and color
class Label(UIElement):
    def __init__(self, x, y, text, font_size=32, color=WHITE):
        """Initialize a text label with given position, content, and style"""
        self.font = pygame.font.Font(None, font_size)
        self.text = text
        self.color = color
        text_surface = self.font.render(text, True, color)
        super().__init__(x, y, text_surface.get_width(), text_surface.get_height())

    def set_text(self, text):
        """Update the label's text and recalculate its dimensions"""
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

# Interactive button component with hover effects and click callback
class Button(UIElement):
    def __init__(self, x, y, width, height, text, callback=None):
        """Initialize a button with given dimensions, text, and click handler"""
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

# Heads-up display showing game status and control buttons
class HUD(UIElement):
    def __init__(self, game_state):
        """Initialize the HUD with health, morale, and capture controls"""
        super().__init__(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.game_state = game_state
        self.stylized_ui = StylizedUIElements()
        
        # Remove old labels since we'll use new stylized elements
        
        # Add capture button
        self.capture_button = Button(10, 70, 100, 30, "Capture", self.attempt_capture)
        self.capture_button.visible = False
        self.add_child(self.capture_button)
        
        # Add release button
        self.release_button = Button(10, 70, 100, 30, "Release", self.release_captured)
        self.release_button.visible = False
        self.add_child(self.release_button)
        
    def attempt_capture(self):
        """Try to capture the nearest valid target within range of selected alien"""
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
                
                # Stop any current tasks when captured
                if hasattr(nearest_target, 'task_handler'):
                    nearest_target.task_handler.clear_tasks()
                if hasattr(nearest_target, 'movement_handler'):
                    nearest_target.movement_handler.stop_movement()
            
    def release_captured(self):
        """Release the currently captured target from the selected alien"""
        selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                             if alien.selected), None)
        if selected_alien and selected_alien.capture and selected_alien.capture.carrying_target:
            selected_alien.capture.release_target()
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
        
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw stylized UI for selected entity
        selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                             if alien.selected), None)
        
        if selected_alien:
            # Draw health orb
            self.stylized_ui.draw_health_orb(surface, 40, 40, 
                                           selected_alien.health.health,
                                           selected_alien.health.max_health)
            
            # Draw morale bar
            self.stylized_ui.draw_morale_bar(surface, 80, 35,
                                           selected_alien.health.morale, 100)
            
            # Draw status icons
            self.stylized_ui.draw_status_icons(surface, 200, 40, selected_alien)
            
            # Draw selection highlight
            self.stylized_ui.draw_selection_highlight(surface, selected_alien,
                                                    self.game_state.camera_x,
                                                    self.game_state.camera_y,
                                                    self.game_state.zoom_level)
            
            # Draw name tag
            self.stylized_ui.draw_name_tag(surface, 80, 60, "Alien", id(selected_alien))
        
        # Draw capture/release buttons and other existing UI elements
        super().draw(surface)

# UI component for handling wire placement mode and preview
class WireUI(UIElement):
    def __init__(self, x, y, width, height, game_state):
        """Initialize wire placement interface"""
        super().__init__(x, y, width, height)
        self.game_state = game_state
        self.selected_component = 'wire'

    def handle_event(self, event):
        """Handle mouse movement for wire ghost preview"""
        if not self.game_state.wire_mode:
            return False
            
        # Only handle mouse motion for ghost wire preview
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            # Let wire system handle the ghost position
            self.game_state.wire_system._update_ghost_position(mouse_pos)
            return True
            
        return super().handle_event(event)

    def draw(self, surface):
        """Draw the ghost wire preview when in wire placement mode"""
        # Only draw ghost wire when in wire mode
        if not self.game_state.wire_mode:
            return
        
        # Use wire system's ghost position and validity
        ghost_position = self.game_state.wire_system.ghost_position
        ghost_valid = self.game_state.wire_system.ghost_valid
        
        if ghost_position:
            tile_x, tile_y = ghost_position
            
            # Calculate screen position
            screen_x = int((tile_x * TILE_SIZE - self.game_state.camera_x) * self.game_state.zoom_level)
            screen_y = int((tile_y * TILE_SIZE - self.game_state.camera_y) * self.game_state.zoom_level)
            tile_size = int(TILE_SIZE * self.game_state.zoom_level)
            
            # Draw ghost wire with transparency
            ghost_color = (255, 255, 0, 128) if ghost_valid else (255, 0, 0, 128)
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

# Control panel for game mode toggles (capture, stealth, wire placement)
class CaptureUI(UIElement):
    def __init__(self, game_state):
        """Initialize mode toggle buttons at the bottom of the screen"""
        # Position at bottom of screen
        super().__init__(10, WINDOW_HEIGHT - 75, 420, 30)  # Increased width for 3 buttons
        self.game_state = game_state
        
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
        """Toggle wire placement mode and disable other modes"""
        self.game_state.wire_mode = not self.game_state.wire_mode
        self.wire_mode_btn.text = f"Place Wire: {'ON' if self.game_state.wire_mode else 'OFF'}"
        
        # Turn off other modes when wire mode is enabled
        if self.game_state.wire_mode:
            self.game_state.capture_system.capture_mode = False
            self.game_state.capture_system.stealth_mode = False
            self.stealth_mode_btn.text = "Stealth: OFF"

    def toggle_stealth_mode(self):
        """Toggle stealth mode for capture operations"""
        system = self.game_state.capture_system
        system.stealth_mode = not system.stealth_mode
        self.stealth_mode_btn.text = f"Stealth: {'ON' if system.stealth_mode else 'OFF'}" 