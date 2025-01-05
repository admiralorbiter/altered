import random
import pygame
import math
from utils.config import *

class MutationMenu:
    def __init__(self, game_state):
        self.game_state = game_state
        self.is_open = False
        self.animation_progress = 0.0  # 0.0 to 1.0
        self.dna_particles = []
        self.hover_slot = None
        
        # Define mutation slots with more detailed information
        self.mutation_slots = [
            {
                "name": "Enhanced Reflexes",
                "cost": 100,
                "unlocked": False,
                "pos": (0, 0),
                "icon": "⚡",  # Using Unicode for now, can be replaced with images
                "description": "Increases movement and attack speed by 20%",
                "stats": ["+20% Movement Speed", "+20% Attack Speed"]
            },
            {
                "name": "Night Vision",
                "cost": 150,
                "unlocked": False,
                "pos": (1, 1),
                "icon": "👁️",
                "description": "See clearly in dark areas",
                "stats": ["+100% Vision in darkness", "+30% Detection range"]
            },
            {
                "name": "Telepathic Bond",
                "cost": 200,
                "unlocked": False,
                "pos": (0, 2),
                "icon": "🧠",
                "description": "Share vision and status with nearby allies",
                "stats": ["+50% Team coordination", "Shared vision radius: 10"]
            },
            {
                "name": "Adaptive Camouflage",
                "cost": 250,
                "unlocked": False,
                "pos": (1, 3),
                "icon": "🦎",
                "description": "Blend with surroundings when stationary",
                "stats": ["-80% Detection while still", "+2s Stealth duration"]
            }
        ]
        
        # Colors for the DNA theme
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
        if self.animation_progress <= 0:
            return
            
        # Calculate menu dimensions and position
        width = 300
        height = 400
        x = WINDOW_WIDTH - width * self.animation_progress
        y = WINDOW_HEIGHT - height - 10
        
        # Create menu surface with alpha
        menu_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw background with blur effect
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
        time = pygame.time.get_ticks() / 1000
        center_x = width // 2
        
        for i, slot in enumerate(self.mutation_slots):
            y = 100 + i * 80
            offset = math.sin(y * 0.05 + time) * 30
            x = center_x + (offset if i % 2 == 0 else -offset)
            
            # Update slot position
            slot["pos"] = (x, y)
            
            # Draw hexagonal slot background
            color = (self.colors["unlocked"] if slot["unlocked"] 
                    else self.colors["locked"])
            if self.hover_slot == i:
                color = self.colors["hover"]
            
            # Draw hexagonal slot
            points = self._get_hex_points(x, y, 25)
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255, 30), points, 2)
            
            # Draw icon
            icon_font = pygame.font.Font(None, 30)
            icon_text = icon_font.render(slot["icon"], True, (255, 255, 255))
            icon_rect = icon_text.get_rect(center=(x, y))
            surface.blit(icon_text, icon_rect)
            
            # Draw name and cost
            name_font = pygame.font.Font(None, 20)
            name_text = name_font.render(slot["name"], True, (255, 255, 255))
            cost_text = name_font.render(f"Cost: {slot['cost']}", True, (200, 200, 200))
            
            surface.blit(name_text, (x - name_text.get_width()//2, y + 30))
            surface.blit(cost_text, (x - cost_text.get_width()//2, y + 45))
            
            # Draw tooltip if hovered
            if self.hover_slot == i:
                self._draw_tooltip(surface, slot, x, y)

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
        """Handle mouse events for tooltips"""
        if not self.is_open:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            # Adjust mouse position for menu position
            menu_x = WINDOW_WIDTH - 300 * self.animation_progress
            local_x = mouse_pos[0] - menu_x
            local_y = mouse_pos[1] - (WINDOW_HEIGHT - 410)
            
            # Check each slot
            self.hover_slot = None
            for i, slot in enumerate(self.mutation_slots):
                x, y = slot["pos"]
                # Simple circular hit detection
                distance = math.sqrt((local_x - x)**2 + (local_y - y)**2)
                if distance < 25:
                    self.hover_slot = i
                    return True
        
        return False 