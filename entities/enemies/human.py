import pygame

from systems.capture_system import CaptureState
from .base_enemy import BaseEnemy
from utils.config import *
from utils.pathfinding import find_path
from .renderers.human_renderer import HumanRenderer
from .renderers.capture_effect_renderer import CaptureEffectRenderer
from .renderers.detection_range_renderer import DetectionRangeRenderer
from components.movement_component import MovementComponent
from components.health_component import HealthComponent
from components.pathfinding_component import PathfindingComponent
from components.human_ai_component import HumanAIComponent

class Human(BaseEnemy):
    """
    Human enemy type that extends BaseEnemy with specific behaviors and attributes.
    Features unique capture mechanics, visual representation, and combat stats.
    """
    def __init__(self, x, y):
        # Convert tile coordinates to pixel coordinates
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        
        # Call super() first to initialize base class and components dict
        super().__init__(pixel_x, pixel_y)
        
        # Set size for collision detection
        self.size = pygame.math.Vector2(32, 32)
        
        # Add components
        self.movement = MovementComponent(self)
        self.add_component(self.movement)
        
        self.health = self.add_component(HealthComponent(self, max_health=80))
        
        self.pathfinding = PathfindingComponent(self)
        self.add_component(self.pathfinding)
        
        self.ai = HumanAIComponent(self)
        self.add_component(self.ai)
        
        # Start components in order
        self.movement.start()
        self.pathfinding.start()
        self.ai.start()
        
        # Patrol state
        self.patrol_points = []
        self.current_patrol_index = 0
        
        # Initialize renderers
        self.detection_renderer = DetectionRangeRenderer()
        self.character_renderer = HumanRenderer(color=(200, 150, 150, 200))
        self.capture_renderer = CaptureEffectRenderer()
        
        # Combat attributes
        self.attack_power = 15
        self.attack_range = TILE_SIZE * 1.2
        self.attack_cooldown = 1.0
        self.attack_timer = 0

    def update(self, dt):
        if self.capture_state != CaptureState.NONE:
            self._handle_captured_state(dt)
            return
        
        super().update(dt)
        
        # Update attack cooldown
        if self.attack_timer > 0:
            self.attack_timer -= dt

    def _handle_captured_state(self, dt):
        """Handle behavior when captured"""
        if self.capture_state == CaptureState.BEING_CARRIED and self.carrier:
            self.position = self.carrier.position.copy()
        elif self.capture_state == CaptureState.UNCONSCIOUS:
            if hasattr(self, 'unconscious_timer'):
                self.unconscious_timer -= dt
                if self.unconscious_timer <= 0:
                    self.capture_state = CaptureState.NONE

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

    def attack(self, target):
        """Attack a target entity if within range"""
        if not target or not hasattr(target, 'take_damage'):
            return False
            
        distance = (target.position - self.position).length()
        if distance > self.ai.attack_range:  # Use AI component's range
            return False
            
        target.take_damage(self.attack_power)
        return True 

    def move_to_target(self, target_pos):
        """Move towards a target position using pathfinding"""
        if not hasattr(self, 'movement'):
            return False
            
        # Convert target position to tile coordinates
        target_tile = (
            int(target_pos[0] // TILE_SIZE),
            int(target_pos[1] // TILE_SIZE)
        )
        
        # Get current tile position
        current_tile = (
            int(self.position.x // TILE_SIZE),
            int(self.position.y // TILE_SIZE)
        )
        
        # Find path to target
        path = find_path(current_tile, target_tile, 
                        self.game_state.current_level.tilemap)
                        
        if path:
            # Convert first waypoint to pixel coordinates
            next_x = (path[0][0] + 0.5) * TILE_SIZE
            next_y = (path[0][1] + 0.5) * TILE_SIZE
            self.movement.set_target_position(next_x, next_y)
            return True
            
        return False 