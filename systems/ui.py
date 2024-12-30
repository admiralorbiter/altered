import pygame
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
    def __init__(self, x, y, width, height, text, callback):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 32)
        self.normal_color = (100, 100, 100)  # Gray background
        self.hover_color = (150, 150, 150)   # Lighter gray when hovering
        self.text_color = (255, 255, 255)    # White text
        self.current_color = self.normal_color
        
    def handle_event(self, event):
        if not self.visible or not self.active:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                print(f"Button {self.text} clicked")  # Debug print
                if self.callback:
                    self.callback()
                return True
        elif event.type == pygame.MOUSEMOTION:
            # Update hover state
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.normal_color
        return False
        
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw button background
        pygame.draw.rect(surface, self.current_color, self.rect)
        
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
        print("Capture button pressed")  # Debug print
        selected_alien = next((alien for alien in self.game_state.current_level.aliens 
                             if alien.selected), None)
        if not selected_alien:
            print("No alien selected")  # Debug print
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
            print(f"Found target at distance {min_distance}")  # Debug print
            success = selected_alien.attempt_capture(nearest_target)
            if success:
                print("Capture successful")  # Debug print
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
            print("Mouse clicked on HUD")  # Debug print
            mouse_pos = pygame.mouse.get_pos()
            if self.capture_button.visible and self.capture_button.rect.collidepoint(mouse_pos):
                print("Capture button clicked")  # Debug print
                self.attempt_capture()
        super().handle_event(event)

class CaptureUI(UIElement):
    def __init__(self, game_state):
        super().__init__(10, WINDOW_HEIGHT - 60, 200, 50)
        self.game_state = game_state
        
        # Create capture mode toggle button
        self.capture_mode_btn = Button(10, WINDOW_HEIGHT - 50, 100, 20, 
                                     "Capture Mode: OFF",
                                     self.toggle_capture_mode)
        self.add_child(self.capture_mode_btn)
        
        # Create stealth mode toggle button
        self.stealth_mode_btn = Button(120, WINDOW_HEIGHT - 50, 100, 20,
                                     "Stealth: OFF",
                                     self.toggle_stealth_mode)
        self.add_child(self.stealth_mode_btn)
        
    def toggle_capture_mode(self):
        system = self.game_state.capture_system
        system.capture_mode = not system.capture_mode
        self.capture_mode_btn.text = f"Capture Mode: {'ON' if system.capture_mode else 'OFF'}"
        
    def toggle_stealth_mode(self):
        system = self.game_state.capture_system
        system.stealth_mode = not system.stealth_mode
        self.stealth_mode_btn.text = f"Stealth: {'ON' if system.stealth_mode else 'OFF'}" 