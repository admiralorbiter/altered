import pygame

from systems.capture_system import CaptureState
from .base_enemy import BaseEnemy
from utils.config import *
from utils.pathfinding import find_path
import random
import math
from .renderers.human_renderer import HumanRenderer
from .renderers.capture_effect_renderer import CaptureEffectRenderer
from .renderers.detection_range_renderer import DetectionRangeRenderer

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
        
        # Set size for collision detection
        self.size = pygame.math.Vector2(32, 32)
        
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
        
        # Initialize renderers
        self.detection_renderer = DetectionRangeRenderer()
        self.character_renderer = HumanRenderer(color=(200, 150, 150, 200))
        self.capture_renderer = CaptureEffectRenderer()
        
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
            
        # Render in order: detection range, capture effects, then character
        self.detection_renderer.render(self, surface, camera_x, camera_y)
        self.capture_renderer.render(self, surface, camera_x, camera_y)
        self.character_renderer.render(self, surface, camera_x, camera_y)

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
                                    game_state.current_level.tilemap)
                self.path_update_timer = 0.5
        
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

    def get_rect(self) -> pygame.Rect:
        """
        Get the collision rectangle for this entity.
        Returns a pygame Rect centered on the entity's position.
        """
        return pygame.Rect(
            self.position.x - self.size.x/2,
            self.position.y - self.size.y/2,
            self.size.x,
            self.size.y
        ) 