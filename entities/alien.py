import pygame
from components.base_entity import Entity
from utils.config import TILE_SIZE
from components.movement_component import MovementComponent
from components.alien_render_component import AlienRenderComponent
from components.health_component import HealthComponent
from components.selectable_component import SelectableComponent
from components.capture_component import CaptureComponent
from components.pathfinding_component import PathfindingComponent
from components.wire_component import WireComponent
import math

class Alien(Entity):
    """
    Player-controlled alien entity with advanced movement, capture mechanics,
    and visual effects. Features detailed rendering with body parts and animations.
    """
    def __init__(self, x: int, y: int, color=(255, 192, 203, 128)):
        # Convert tile coordinates to pixel coordinates for centered positioning
        pixel_x = (x + 0.5) * TILE_SIZE
        pixel_y = (y + 0.5) * TILE_SIZE
        super().__init__(pixel_x, pixel_y)
        
        # Set basic properties
        self.size = pygame.math.Vector2(32, 32)
        
        # Add components
        self.movement = self.add_component(MovementComponent(self, speed=300))
        self.renderer = self.add_component(AlienRenderComponent(self, color))
        self.health = self.add_component(HealthComponent(self))
        self.selectable = self.add_component(SelectableComponent(self))
        self.capture = self.add_component(CaptureComponent(self))
        self.pathfinding = self.add_component(PathfindingComponent(self))
        self.wire = self.add_component(WireComponent(self))
        
        # Initialize components
        for component in self.components.values():
            if hasattr(component, 'start'):
                component.start()
        
        # Add stealth properties
        self.stealth_alpha = 128  # Base alpha for stealth effect

    @property
    def capture_range(self) -> float:
        """Shorthand property to get capture range"""
        return self.capture.capture_range if self.capture else TILE_SIZE * 2

    @property
    def carrying_target(self):
        """Shorthand property to check if alien is carrying a target"""
        return self.capture.carrying_target if self.capture else None

    @property
    def selected(self) -> bool:
        """Shorthand property to check if alien is selected"""
        return self.selectable.is_selected if self.selectable else False

    @selected.setter
    def selected(self, value: bool) -> None:
        """Shorthand property to set alien selection state"""
        if self.selectable:
            if value:
                self.selectable.select()
            else:
                self.selectable.deselect()

    # Add these methods for backwards compatibility
    def select(self) -> None:
        """Shorthand method to select the alien"""
        if self.selectable:
            self.selectable.select()

    def deselect(self) -> None:
        """Shorthand method to deselect the alien"""
        if self.selectable:
            self.selectable.deselect()

    @classmethod
    def from_dict(cls, data: dict) -> 'Alien':
        """Create an alien instance from serialized data"""
        alien = cls(data['position'][0], data['position'][1])
        
        # Restore component states
        if 'health' in data:
            alien.health.health = data['health']
            alien.health.morale = data.get('morale', 100)
            
        if 'selected' in data:
            alien.selected = data['selected']  # Use the new property
                
        return alien

    def to_dict(self) -> dict:
        """Serialize alien state to dictionary"""
        return {
            'type': 'Alien',
            'position': [self.position.x, self.position.y],
            'health': self.health.health,
            'morale': self.health.morale,
            'selected': self.selected  # Use the new property
        } 

    def render_with_offset(self, surface, camera_x: float, camera_y: float) -> None:
        """
        Render alien and all its components with camera offset.
        Delegates to component-based rendering.
        """
        if not self.active:
            return
            
        # Apply stealth visual effect
        if self.is_stealthed:
            # Create stealth effect surface
            screen_x = (self.position.x - camera_x) * self.game_state.zoom_level
            screen_y = (self.position.y - camera_y) * self.game_state.zoom_level
            
            # Add stealth glow effect
            glow_radius = int(40 * self.game_state.zoom_level)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            # Pulsing stealth effect
            alpha = int(self.stealth_alpha + math.sin(pygame.time.get_ticks() * 0.005) * 30)
            pygame.draw.circle(glow_surface, (0, 255, 255, alpha), 
                             (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, 
                        (screen_x - glow_radius, screen_y - glow_radius))
            
        # Continue with normal rendering
        super().render_with_offset(surface, camera_x, camera_y) 

    def set_target(self, tile_x: int, tile_y: int) -> None:
        """Set movement target for the alien"""
        if self.health and self.health.is_corpse:
            return  # Dead aliens can't move
        
        if self.pathfinding:
            pixel_x = (tile_x + 0.5) * TILE_SIZE
            pixel_y = (tile_y + 0.5) * TILE_SIZE
            self.pathfinding.set_target(pixel_x, pixel_y)

    def take_damage(self, amount: float) -> None:
        """Delegate damage handling to health component"""
        if self.health:
            self.health.take_damage(amount)

    def heal(self, amount: float) -> None:
        """Delegate healing to health component"""
        if self.health:
            self.health.heal(amount)

    def change_morale(self, amount: float) -> None:
        """Delegate morale changes to health component"""
        if self.health:
            self.health.change_morale(amount)

    @property
    def is_alive(self) -> bool:
        """Check if entity is alive via health component"""
        return self.health.is_alive if self.health else False 

    def update(self, dt: float) -> None:
        """Update alien and components"""
        if self.health and self.health.is_corpse:
            # Only allow minimal updates when dead
            if self.capture and self.capture.carrier:
                self.position = self.capture.carrier.position.copy()
            return
        
        super().update(dt) 

    def attempt_capture(self, target) -> bool:
        """Delegate capture attempt to the capture component"""
        if self.capture:
            return self.capture.attempt_capture(target)
        return False 