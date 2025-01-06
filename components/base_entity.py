import pygame
from typing import Dict, Type, Union
from components.base_component import Component
from utils.config import TILE_SIZE, WHITE

class Entity:
    """
    Base class for all game entities. Provides core functionality for
    positioning, movement, rendering, and component management.
    """
    def __init__(self, x: float, y: float):
        # Core positioning and physics properties
        self.position = pygame.math.Vector2(x, y)
        self.size = pygame.math.Vector2(TILE_SIZE * 0.8, TILE_SIZE * 0.8)
        
        # Component management - store by both type and name
        self.components: Dict[str, Component] = {}
        
        # Basic properties
        self.color = WHITE
        self.active = True
        self.game_state = None
        
        # Add stealth properties
        self.is_stealthed = False
        self.stealth_cooldown = 0
        self.stealth_duration = 5.0  # 5 seconds of stealth
        self.stealth_recharge_time = 8.0  # 8 seconds to recharge

    def add_component(self, component: Component) -> Component:
        """
        Add a component to the entity.
        
        Args:
            component: Component instance to add
            
        Returns:
            The added component
        """
        component_name = component.__class__.__name__
        if component_name in self.components:
            raise ValueError(f"Component of type {component_name} already exists")
        
        self.components[component_name] = component
        return component

    def get_component(self, component_type: Union[Type[Component], str]) -> Component:
        """
        Get a component by type or name.
        
        Args:
            component_type: Type of component or string name to retrieve
            
        Returns:
            Component instance if found
            
        Raises:
            KeyError if component type not found
        """
        if isinstance(component_type, str):
            return self.components[component_type]
        return self.components[component_type.__name__]

    def has_component(self, component_type: Union[Type[Component], str]) -> bool:
        """
        Check if entity has a specific component type.
        
        Args:
            component_type: Type of component or string name to check for
            
        Returns:
            True if component exists, False otherwise
        """
        if isinstance(component_type, str):
            return component_type in self.components
        return component_type.__name__ in self.components

    def update(self, dt: float) -> None:
        """
        Update entity and all its components.
        
        Args:
            dt: Delta time in seconds
        """
        for component in self.components.values():
            if component.active:
                component.update(dt)

        # Update stealth cooldown
        if self.stealth_cooldown > 0:
            self.stealth_cooldown -= dt
            if self.stealth_cooldown <= 0:
                self.is_stealthed = False
                self.stealth_cooldown = -self.stealth_recharge_time  # Start recharge
        elif self.stealth_cooldown < 0:  # Recharging
            self.stealth_cooldown += dt

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """
        Render entity and all its components.
        
        Args:
            surface: Pygame surface to render on
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        # Let components render first
        for component in self.components.values():
            if component.active:
                component.render(surface, camera_x, camera_y)
        
        # Fallback rendering if no components handle it
        if not self.components:
            screen_x = (self.position.x - camera_x) * self.game_state.zoom_level
            screen_y = (self.position.y - camera_y) * self.game_state.zoom_level
            scaled_size = self.size * self.game_state.zoom_level
            
            pygame.draw.rect(surface, self.color,
                           (screen_x - scaled_size.x/2,
                            screen_y - scaled_size.y/2,
                            scaled_size.x, scaled_size.y))

    def render_with_offset(self, surface, camera_x: float, camera_y: float) -> None:
        """
        Render entity and all its components with camera offset.
        This is the main render method called by the game engine.
        
        Args:
            surface: Pygame surface to render on
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        # Let components render first
        for component in self.components.values():
            if component.active:
                component.render(surface, camera_x, camera_y)
        
        # Fallback rendering if no components handle it
        if not self.components:
            zoom_level = getattr(self.game_state, 'zoom_level', 1.0)
            screen_x = (self.position.x - camera_x) * zoom_level
            screen_y = (self.position.y - camera_y) * zoom_level
            scaled_size = self.size * zoom_level
            
            pygame.draw.rect(surface, self.color,
                           (screen_x - scaled_size.x/2,
                            screen_y - scaled_size.y/2,
                            scaled_size.x, scaled_size.y))

    def toggle_stealth(self) -> bool:
        """Toggle stealth mode if available"""
        if self.stealth_cooldown <= 0:
            self.is_stealthed = not self.is_stealthed
            if self.is_stealthed:
                self.stealth_cooldown = self.stealth_duration
            return True
        return False