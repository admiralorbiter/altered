import pygame
from entities.alien import Alien
from entities.cat import Cat
from entities.enemies.base_enemy import BaseEnemy
from systems.capture_system import CaptureState
from utils.config import *
from systems.ui.ui_elements import StylizedUIElements
from systems.ui.mutation_ui import MutationMenu
import math

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
        """Initialize the HUD with all UI components"""
        super().__init__(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.game_state = game_state
        self.stylized_ui = StylizedUIElements()
        
        # Add BuildUI as a separate component
        self.build_ui = BuildUI(game_state)
        self.add_child(self.build_ui)
        
        # Remove old labels since we'll use new stylized elements
        
        # Add capture button
        self.capture_button = Button(10, 70, 100, 30, "Capture", self.attempt_capture)
        self.capture_button.visible = False
        self.add_child(self.capture_button)
        
        # Add release button
        self.release_button = Button(10, 70, 100, 30, "Release", self.release_captured)
        self.release_button.visible = False
        self.add_child(self.release_button)
        
        # Add mutation menu
        self.mutation_menu = MutationMenu(game_state)
        self.dna_button = DNAButton(WINDOW_WIDTH - 50, WINDOW_HEIGHT // 2 - 25, 
                                  lambda: self.mutation_menu.toggle())
        self.add_child(self.dna_button)
        
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
        self.mutation_menu.update(dt)
        
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
        
        # Draw oxygen indicator if level requires it
        if (self.game_state.current_level and 
            self.game_state.current_level.requires_oxygen):
            # Get average oxygen level from entire level
            oxygen_level = self._get_local_oxygen_level()
            self.stylized_ui.draw_oxygen_indicator(
                surface, 
                WINDOW_WIDTH - 180,  # Position in top-right
                10, 
                oxygen_level
            )
        
        self.mutation_menu.draw(surface)
    
    def _get_local_oxygen_level(self) -> float:
        """Get average oxygen level from entire level"""
        if not hasattr(self.game_state, 'oxygen_system'):
            return 1.0
        
        total = 0
        count = 0
        
        # Sample oxygen levels from entire level
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if self.game_state.oxygen_system._is_inside_ship(x, y):
                    total += self.game_state.oxygen_system.oxygen_grid[x, y]
                    count += 1
        
        if count == 0:
            return 0.0
        return total / count

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # 'M' key toggles mutation menu
                self.mutation_menu.toggle()
                return True
                
        # Check for mutation slot hovering/clicking
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.mutation_menu.is_open:
                # Add hover detection logic here
                pass
                
        return super().handle_event(event)

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

class BuildUI(UIElement):
    def __init__(self, game_state):
        """Initialize build interface controls"""
        super().__init__(10, WINDOW_HEIGHT - 75, 130, 25)
        self.game_state = game_state
        self.is_menu_open = False
        self.current_submenu = None
        
        # Add build preview UI
        self.preview_ui = BuildPreviewUI(game_state)
        self.add_child(self.preview_ui)
        
        # Create build menu toggle button
        self.build_menu_btn = Button(10, WINDOW_HEIGHT - 75, 130, 25,
                                   "Build Menu",
                                   self.toggle_build_menu)
        self.add_child(self.build_menu_btn)
        
        # Create power submenu button (initially hidden)
        self.power_btn = Button(10, WINDOW_HEIGHT - 110, 130, 25,
                              "Power Systems",
                              self.toggle_power_menu)
        self.power_btn.visible = False
        self.add_child(self.power_btn)
        
        # Create reactor button (initially hidden)
        self.reactor_btn = Button(150, WINDOW_HEIGHT - 110, 130, 25,
                                "Build Reactor",
                                self.build_reactor)
        self.reactor_btn.visible = False
        self.add_child(self.reactor_btn)

        # Create life support button (initially hidden)
        self.life_support_btn = Button(290, WINDOW_HEIGHT - 110, 130, 25,
                                    "Life Support",
                                    self.build_life_support)
        self.life_support_btn.visible = False
        self.add_child(self.life_support_btn)

    def toggle_build_menu(self):
        """Toggle the build menu state"""
        self.is_menu_open = not self.is_menu_open
        self.power_btn.visible = self.is_menu_open
        
        # Hide submenu items if closing main menu
        if not self.is_menu_open:
            self.current_submenu = None
            self.reactor_btn.visible = False
            self.life_support_btn.visible = False
        
        print(f"Build menu {'opened' if self.is_menu_open else 'closed'}")

    def toggle_power_menu(self):
        """Toggle the power submenu"""
        if self.current_submenu == 'power':
            self.current_submenu = None
            self.reactor_btn.visible = False
            self.life_support_btn.visible = False
        else:
            self.current_submenu = 'power'
            self.reactor_btn.visible = True
            self.life_support_btn.visible = True

    def build_reactor(self):
        """Start reactor placement mode"""
        # Cancel any other placement modes
        self.game_state.wire_mode = False
        self.game_state.capture_system.capture_mode = False
        
        # Start reactor placement
        self.game_state.build_system.start_placement('reactor')

    def build_life_support(self):
        """Start life support placement mode"""
        # Cancel any other placement modes
        self.game_state.wire_mode = False
        self.game_state.capture_system.capture_mode = False
        
        # Start life support placement
        self.game_state.build_system.start_placement('life_support')

    def handle_event(self, event):
        """Handle keyboard shortcuts for build menu"""
        if event.type == pygame.KEYDOWN:
            if self.is_menu_open and event.key == pygame.K_p:
                self.toggle_power_menu()
                return True
        return super().handle_event(event) 

class BuildPreviewUI(UIElement):
    def __init__(self, game_state):
        super().__init__(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.game_state = game_state

    def handle_event(self, event):
        """Handle only mouse movement for building ghost preview"""
        if not self.game_state.build_system.is_placing:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.game_state.build_system._update_ghost_position(mouse_pos)
            return True
            
        return super().handle_event(event)

    def draw(self, surface):
        """Draw the ghost building preview"""
        if not self.game_state.build_system.is_placing:
            return
            
        self.game_state.build_system.draw(surface) 

# Add this new class to handle the DNA button
class DNAButton(Button):
    def __init__(self, x, y, callback):
        super().__init__(x, y, 40, 50, "", callback)
        self.glow_amount = 0
        self.pulse_direction = 1
        self.dna_color = (64, 156, 255)  # Match DNA strand color from mutation menu
        
    def update(self, dt):
        # Update glow pulse effect
        self.glow_amount += dt * self.pulse_direction
        if self.glow_amount > 1.0:
            self.glow_amount = 1.0
            self.pulse_direction = -1
        elif self.glow_amount < 0.0:
            self.glow_amount = 0.0
            self.pulse_direction = 1
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Create button surface with alpha
        button_surface = pygame.Surface((self.rect.width, self.rect.height), 
                                     pygame.SRCALPHA)
        
        # Draw DNA helix background
        time = pygame.time.get_ticks() / 1000
        center_x = self.rect.width // 2
        
        # Draw glow effect
        glow_radius = 25 + self.glow_amount * 5
        glow_surface = pygame.Surface((int(glow_radius * 2), 
                                     self.rect.height), pygame.SRCALPHA)
        
        glow_color = (*self.dna_color, int(50 * self.glow_amount))
        pygame.draw.circle(glow_surface, glow_color,
                         (int(glow_radius), self.rect.height // 2),
                         int(glow_radius))
        
        # Center the glow on the button
        button_surface.blit(glow_surface, 
                          (center_x - glow_radius, 0))
        
        # Draw DNA strands
        for i in range(0, self.rect.height, 8):
            y = i
            offset = math.sin(y * 0.2 + time * 2) * 8
            
            # Draw connecting lines
            if i % 16 == 0:
                color = (*self.dna_color, 
                        255 if self.is_hovered else 200)
                pygame.draw.line(button_surface,
                               color,
                               (center_x + offset, y),
                               (center_x - offset, y),
                               2)
                
                # Draw nodes at ends
                pygame.draw.circle(button_surface,
                                 color,
                                 (int(center_x + offset), y),
                                 3)
                pygame.draw.circle(button_surface,
                                 color,
                                 (int(center_x - offset), y),
                                 3)
        
        # Draw border when hovered
        if self.is_hovered:
            pygame.draw.rect(button_surface, 
                           self.dna_color,
                           button_surface.get_rect(),
                           2,
                           border_radius=10)
        
        # Apply the button to the main surface
        surface.blit(button_surface, self.rect) 