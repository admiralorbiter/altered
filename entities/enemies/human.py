import pygame

from systems.capture_system import CaptureState
from .base_enemy import BaseEnemy
from utils.config import *
from utils.pathfinding import find_path
import random
import math

class Human(BaseEnemy):
    """
    Human enemy type that extends BaseEnemy with specific behaviors and attributes.
    Features unique capture mechanics, visual representation, and combat stats.
    """
    def __init__(self, x, y):
        # Convert tile coordinates to pixel coordinates
        pixel_x = (x + 0.5) * TILE_SIZE  # Center in tile
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        # Combat statistics
        self.max_health = 80  # Maximum health points
        self.health = self.max_health
        self.attack_power = 15  # Damage dealt per attack
        self.speed = 250  # Movement speed in pixels/second
        self.attack_cooldown = 1.0  # Time between attacks
        self.attack_timer = 0  # Current attack cooldown
        
        # Visual properties
        self.color = (200, 150, 150, 200)  # RGBA color for rendering
        
        # Human-specific capture mechanics
        self.struggle_chance = 0.15  # Higher chance to break free than base
        self.unconscious_duration = 8.0  # Longer unconscious duration
        
    def attack(self, target):
        if self.attack_timer <= 0:
            target.take_damage(self.attack_power)
            self.attack_timer = self.attack_cooldown
            
    def update(self, dt):
        # Check capture state first
        if self.capture_state != CaptureState.NONE:
            # When captured, only update position if being carried
            if self.capture_state == CaptureState.BEING_CARRIED and self.carrier:
                self.position = self.carrier.position.copy()
                self.target = None
                self.path = None
                self.moving = False
            elif self.capture_state == CaptureState.UNCONSCIOUS:
                self.target = None
                self.path = None
                self.moving = False
                if hasattr(self, 'unconscious_timer'):
                    self.unconscious_timer -= dt
                    if self.unconscious_timer <= 0:
                        self.capture_state = CaptureState.NONE
            return  # Don't do any other updates when captured
            
        # Only proceed with normal updates if not captured
        super().update(dt)

    def render_with_offset(self, surface, camera_x, camera_y):
        """
        Renders the human enemy with all visual effects including capture states,
        detection range, health bar, and character model.
        
        Args:
            surface (pygame.Surface): Target surface for rendering
            camera_x, camera_y (float): Camera offset coordinates
        """
        if not self.active:
            return
            
        zoom_level = self.game_state.zoom_level
        screen_x = (self.position.x - camera_x) * zoom_level
        screen_y = (self.position.y - camera_y) * zoom_level
        
        # Draw UFO capture effect if being carried
        if self.capture_state == CaptureState.BEING_CARRIED:
            # Create UFO beam effect
            beam_height = int(50 * zoom_level)
            beam_width = int(40 * zoom_level)
            beam_surface = pygame.Surface((beam_width, beam_height), pygame.SRCALPHA)
            
            # Pulsing effect
            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
            alpha = int(50 + (30 * pulse))
            
            # Draw beam cone
            points = [
                (beam_width//2, 0),  # Top point
                (0, beam_height),    # Bottom left
                (beam_width, beam_height)  # Bottom right
            ]
            pygame.draw.polygon(beam_surface, (0, 150, 255, alpha), points)
            
            # Draw UFO circle
            ufo_radius = int(25 * zoom_level)
            ufo_surface = pygame.Surface((ufo_radius * 2, ufo_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(ufo_surface, (0, 200, 255, alpha + 50), 
                             (ufo_radius, ufo_radius), ufo_radius)
            
            # Blit beam and UFO
            surface.blit(beam_surface, 
                        (screen_x - beam_width//2, 
                         screen_y - beam_height))
            surface.blit(ufo_surface,
                        (screen_x - ufo_radius,
                         screen_y - beam_height - ufo_radius))
        
        # Only draw detection range if not captured
        if self.capture_state == CaptureState.NONE:
            range_radius = self.detection_range * zoom_level
            range_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
            if self.state == 'chase':
                pygame.draw.circle(range_surface, (255, 0, 0, 30), 
                                 (range_radius, range_radius), range_radius)
            else:
                pygame.draw.circle(range_surface, (100, 100, 100, 30), 
                                 (range_radius, range_radius), range_radius)
            surface.blit(range_surface, 
                        (screen_x - range_radius, screen_y - range_radius))
        
        # Draw capture effect first (if captured)
        if self.capture_state == CaptureState.BEING_CARRIED:
            # Create hover effect
            hover_size = int(40 * zoom_level)
            hover_surface = pygame.Surface((hover_size, hover_size), pygame.SRCALPHA)
            
            # Pulsing effect based on time
            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5  # 0 to 1
            alpha = int(100 + (50 * pulse))  # Pulsing alpha between 100-150
            
            pygame.draw.circle(hover_surface, (255, 215, 0, alpha), 
                             (hover_size//2, hover_size//2), hover_size//2)
            surface.blit(hover_surface, 
                        (screen_x - hover_size//2, screen_y - hover_size//2))
        
        # Draw the human character (existing code)
        scaled_size = pygame.Vector2(self.size.x * zoom_level, self.size.y * zoom_level)
        human_surface = pygame.Surface((scaled_size.x, scaled_size.y), pygame.SRCALPHA)
        
        # Modify color if captured
        render_color = self.color
        if self.capture_state != CaptureState.NONE:
            # Make the human slightly transparent when captured
            render_color = (*self.color[:3], 150)
        
        # Draw body (rectangle)
        body_rect = (scaled_size.x * 0.3, scaled_size.y * 0.3, 
                    scaled_size.x * 0.4, scaled_size.y * 0.5)
        pygame.draw.rect(human_surface, render_color, body_rect)
        
        # Draw head (circle)
        head_size = scaled_size.x * 0.3
        pygame.draw.circle(human_surface, render_color,
                         (scaled_size.x/2, scaled_size.y * 0.25),
                         head_size/2)
        
        # Draw arms (lines)
        arm_color = tuple(max(0, min(255, c - 20)) for c in render_color[:3]) + (render_color[3],)
        line_width = max(1, int(3 * zoom_level))
        # Left arm
        pygame.draw.line(human_surface, arm_color,
                        (scaled_size.x * 0.3, scaled_size.y * 0.35),
                        (scaled_size.x * 0.2, scaled_size.y * 0.5), line_width)
        # Right arm
        pygame.draw.line(human_surface, arm_color,
                        (scaled_size.x * 0.7, scaled_size.y * 0.35),
                        (scaled_size.x * 0.8, scaled_size.y * 0.5), line_width)
        
        # Draw legs (lines)
        # Left leg
        pygame.draw.line(human_surface, arm_color,
                        (scaled_size.x * 0.4, scaled_size.y * 0.8),
                        (scaled_size.x * 0.3, scaled_size.y * 0.95), line_width)
        # Right leg
        pygame.draw.line(human_surface, arm_color,
                        (scaled_size.x * 0.6, scaled_size.y * 0.8),
                        (scaled_size.x * 0.7, scaled_size.y * 0.95), line_width)
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            health_width = (scaled_size.x * self.health) / self.max_health
            bar_height = max(2, 3 * zoom_level)
            pygame.draw.rect(surface, (255, 0, 0),
                           (screen_x - scaled_size.x/2,
                            screen_y - scaled_size.y/2 - 5 * zoom_level,
                            scaled_size.x, bar_height))
            pygame.draw.rect(surface, (0, 255, 0),
                           (screen_x - scaled_size.x/2,
                            screen_y - scaled_size.y/2 - 5 * zoom_level,
                            health_width, bar_height))
        
        # Blit the human to the screen
        surface.blit(human_surface,
                    (screen_x - scaled_size.x/2,
                     screen_y - scaled_size.y/2)) 
        
        # Add human-specific capture state visuals
        if self.capture_state == CaptureState.UNCONSCIOUS:
            font = pygame.font.Font(None, int(20 * zoom_level))
            text = font.render("zZZ", True, (255, 255, 255))
            surface.blit(text, (screen_x - text.get_width()/2, 
                               screen_y - 30 * zoom_level))

    def update_ai_state(self, dt, game_state):
        """
        Extends base AI state update with human-specific pathfinding behavior.
        Updates movement paths more frequently during chase state.
        
        Args:
            dt (float): Delta time
            game_state: Current game state
        """
        super().update_ai_state(dt, game_state)
        
        if self.state == 'chase' and self.target:
            current_tile = (int(self.position.x // TILE_SIZE),
                           int(self.position.y // TILE_SIZE))
            target_tile = (int(self.target.position.x // TILE_SIZE),
                          int(self.target.position.y // TILE_SIZE))
            
            # Update path periodically
            self.path_update_timer -= dt
            if self.path_update_timer <= 0:
                self.path = find_path(current_tile, target_tile,
                                    game_state.current_level.tilemap,
                                    game_state, self)
                self.path_update_timer = 0.5  # Update path every 0.5 seconds
        
    def set_target(self, tile_x, tile_y):
        """
        Sets a new movement target for the human and calculates a path.
        Only processes if the human is currently selected.
        
        Args:
            tile_x, tile_y (int): Target tile coordinates
        """
        if not self.selected:
            return
        
        current_tile = (int(self.position.x // TILE_SIZE), 
                       int(self.position.y // TILE_SIZE))
        target_tile = (tile_x, tile_y)
        
        # Find path using A* with entity collision checking
        self.path = find_path(current_tile, target_tile, 
                             self.game_state.current_level.tilemap,
                             self.game_state, self) 