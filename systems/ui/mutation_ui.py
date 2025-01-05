import random
import pygame
import math
from utils.config import *

class MutationMenu:
    def __init__(self, game_state):
        self.game_state = game_state
        self.is_open = False
        self.animation_progress = 0.0
        self.dna_particles = []
        self.hover_slot = None
        
        # Get mutations from the mutation system
        self.mutation_slots = []
        for mutation_id, mutation in self.game_state.mutation_system.mutations.items():
            slot = {
                "id": mutation_id,
                "name": mutation["name"],
                "cost": mutation["cost"],
                "unlocked": mutation["unlocked"],
                "icon": mutation["icon"],
                "description": mutation["description"],
                "stats": mutation["stats"],
                "pos": (0, 0)  # Will be updated during drawing
            }
            self.mutation_slots.append(slot)
        
        self.colors = {
            "background": (20, 22, 30, 200),
            "dna_strand": (64, 156, 255),
            "locked": (100, 100, 100),
            "unlocked": (0, 255, 150),
            "hover": (255, 215, 0)
        }

    def toggle(self):
        self.is_open = not self.is_open

    def update(self, dt):
        if self.is_open and self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + dt * 4)
        elif not self.is_open and self.animation_progress > 0.0:
            self.animation_progress = max(0.0, self.animation_progress - dt * 4)
            
        # Update DNA particles
        self._update_dna_particles(dt)
        
        # Add new particles occasionally
        if self.is_open and len(self.dna_particles) < 20:
            if random.random() < dt * 2:
                self._add_dna_particle()

    def draw(self, surface):
        """Draw the mutation menu"""
        if self.animation_progress <= 0:
            return
            
        # Calculate menu position and size
        width = 300
        height = 410
        x = WINDOW_WIDTH - width * self.animation_progress
        y = WINDOW_HEIGHT - height
        
        # Create menu surface with alpha
        menu_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw background
        self._draw_background(menu_surface, width, height)
        
        # Draw DNA helix
        self._draw_dna_helix(menu_surface, width, height)
        
        # Draw mutation slots
        self._draw_mutation_slots(menu_surface, width, height)
        
        # Draw particles
        self._draw_dna_particles(menu_surface)
        
        # Draw title
        self._draw_title(menu_surface, width)
        
        # Apply the menu to the main surface
        surface.blit(menu_surface, (x, y))

    def _draw_background(self, surface, width, height):
        """Draw stylized background with alien-tech feel"""
        pygame.draw.rect(surface, self.colors["background"], 
                        (0, 0, width, height), border_radius=15)
        
        # Draw hex grid pattern
        for i in range(0, width + 50, 50):
            for j in range(0, height + 50, 50):
                points = self._get_hex_points(i, j, 20)
                pygame.draw.lines(surface, (255, 255, 255, 20), True, points, 1)

    def _draw_dna_helix(self, surface, width, height):
        """Draw animated DNA double helix"""
        time = pygame.time.get_ticks() / 1000
        center_x = width // 2
        
        for i in range(height):
            y = i
            offset = math.sin(y * 0.05 + time) * 30
            
            # Draw connecting lines
            if i % 20 == 0:
                color = (*self.colors["dna_strand"], 150)
                pygame.draw.line(surface,
                               color,
                               (center_x + offset, y),
                               (center_x - offset, y),
                               2)

    def _draw_mutation_slots(self, surface, width, height):
        """Draw mutation slots with icons and hover tooltips"""
        center_x = width // 2
        
        for i, slot in enumerate(self.mutation_slots):
            y = 100 + i * 80
            x = center_x
            
            # Update slot position for click detection
            slot["pos"] = (x, y)
            
            # Get mutation state from mutation system
            mutation = self.game_state.mutation_system.mutations[slot["id"]]
            is_unlocked = mutation["unlocked"]
            
            # Draw hexagonal slot background with state-based colors
            if is_unlocked:
                # Bright green for unlocked mutations
                color = (0, 255, 150)
                # Add strong glow effect for unlocked mutations
                glow_radius = 30
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                for r in range(glow_radius, 0, -5):  # Layer the glow
                    alpha = 100 if r == glow_radius else 50
                    pygame.draw.circle(glow_surface, (*color, alpha), 
                                     (glow_radius, glow_radius), r)
                surface.blit(glow_surface, (x - glow_radius, y - glow_radius))
            else:
                color = self.colors["locked"]
            
            if self.hover_slot == i:
                color = self.colors["hover"]
            
            # Draw hexagonal slot
            points = self._get_hex_points(x, y, 25)
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255, 30), points, 2)
            
            # Draw paw icon (🐾)
            font = pygame.font.Font(None, 36)
            icon_color = (255, 255, 255) if is_unlocked else (150, 150, 150)
            icon = font.render("🐾", True, icon_color)
            surface.blit(icon, (x - icon.get_width()//2, y - icon.get_height()//2))
            
            # Draw name and cost
            self._draw_slot_content(surface, slot, x, y)

    def _draw_title(self, surface, width):
        """Draw the menu title with glow effect"""
        font = pygame.font.Font(None, 36)
        text = font.render("Mutations", True, (255, 255, 255))
        
        # Draw glow
        glow_surf = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        glow_surf.blit(text, (0, 0))
        for i in range(10):
            pygame.draw.rect(glow_surf, (0, 255, 150, 5), 
                           glow_surf.get_rect().inflate(i*2, i*2))
        
        # Blit both surfaces
        surface.blit(glow_surf, (width//2 - text.get_width()//2, 20))
        surface.blit(text, (width//2 - text.get_width()//2, 20))

    def _get_hex_points(self, x, y, size):
        """Calculate points for hexagon pattern"""
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            points.append((x + size * math.cos(angle),
                         y + size * math.sin(angle)))
        return points

    def _add_dna_particle(self):
        """Add a new floating DNA particle"""
        self.dna_particles.append({
            'x': random.randint(0, 300),
            'y': random.randint(0, 400),
            'size': random.randint(2, 5),
            'speed': random.uniform(10, 30),
            'angle': random.uniform(0, math.pi * 2)
        })

    def _update_dna_particles(self, dt):
        """Update DNA particle positions"""
        for particle in self.dna_particles[:]:
            particle['y'] -= particle['speed'] * dt
            particle['x'] += math.sin(particle['angle']) * dt * 10
            
            if particle['y'] < 0:
                self.dna_particles.remove(particle)

    def _draw_dna_particles(self, surface):
        """Draw floating DNA particles"""
        for particle in self.dna_particles:
            pygame.draw.circle(surface, 
                             (*self.colors["dna_strand"], 150),
                             (int(particle['x']), int(particle['y'])),
                             particle['size']) 

    def _draw_tooltip(self, surface, slot, x, y):
        """Draw detailed tooltip for mutation slot"""
        padding = 10
        line_height = 20
        
        # Create tooltip content
        lines = [
            slot["description"],
            "",  # Empty line
            *slot["stats"]
        ]
        
        # Calculate tooltip dimensions
        font = pygame.font.Font(None, 20)
        text_surfaces = [font.render(line, True, (255, 255, 255)) for line in lines]
        tooltip_width = max(surface.get_width() for surface in text_surfaces) + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2
        
        # Create tooltip surface
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surface, (0, 0, 0, 220), 
                        tooltip_surface.get_rect(), border_radius=5)
        
        # Draw text
        for i, text_surface in enumerate(text_surfaces):
            tooltip_surface.blit(text_surface, 
                               (padding, padding + i * line_height))
        
        # Position tooltip
        tooltip_x = x + 40
        tooltip_y = y - tooltip_height//2
        
        # Keep tooltip on screen
        if tooltip_x + tooltip_width > surface.get_width():
            tooltip_x = x - tooltip_width - 40
        
        # Draw tooltip
        surface.blit(tooltip_surface, (tooltip_x, tooltip_y))
        
        # Draw connecting line
        pygame.draw.line(surface, self.colors["hover"],
                        (x + 25, y),
                        (tooltip_x, tooltip_y + tooltip_height//2),
                        2)

    def handle_event(self, event):
        """Handle mouse events for tooltips and mutation activation"""
        if not self.is_open:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check for clicks on mutation slots
            mouse_pos = event.pos
            menu_x = WINDOW_WIDTH - 300 * self.animation_progress
            local_x = mouse_pos[0] - menu_x
            local_y = mouse_pos[1] - (WINDOW_HEIGHT - 410)
            
            for i, slot in enumerate(self.mutation_slots):
                x, y = slot["pos"]
                distance = math.sqrt((local_x - x)**2 + (local_y - y)**2)
                
                if distance < 25:
                    mutation_id = slot.get("id")
                    if mutation_id and self.game_state.mutation_system.can_unlock(mutation_id):
                        self.game_state.mutation_system.unlock_mutation(mutation_id)
                        return True
        
        # Handle hover effects
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            menu_x = WINDOW_WIDTH - 300 * self.animation_progress
            local_x = mouse_pos[0] - menu_x
            local_y = mouse_pos[1] - (WINDOW_HEIGHT - 410)
            
            # Check each slot
            self.hover_slot = None
            for i, slot in enumerate(self.mutation_slots):
                x, y = slot["pos"]
                distance = math.sqrt((local_x - x)**2 + (local_y - y)**2)
                if distance < 25:
                    self.hover_slot = i
                    return True
        
        return False 

    def _draw_slot_content(self, surface, slot, x, y):
        """Draw the icon and text for a mutation slot"""
        # Draw name
        font = pygame.font.Font(None, 24)
        text = font.render(slot["name"], True, (255, 255, 255))
        surface.blit(text, (x - text.get_width()//2, y + 30))
        
        # Draw cost
        cost_text = font.render(f"Cost: {slot['cost']}", True, (200, 200, 200))
        surface.blit(cost_text, (x - cost_text.get_width()//2, y + 50))
        
        # Draw tooltip if hovered
        if self.hover_slot is not None and self.mutation_slots[self.hover_slot] == slot:
            self._draw_tooltip(surface, slot, x, y) 