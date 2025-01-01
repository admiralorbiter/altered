import pygame
from typing import Dict, Type
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
        
        # Component management
        self.components: Dict[Type[Component], Component] = {}
        
        # Basic properties
        self.color = WHITE
        self.active = True
        self.game_state = None

    def add_component(self, component: Component) -> Component:
        """
        Add a component to the entity.
        
        Args:
            component: Component instance to add
            
        Returns:
            The added component
        """
        component_type = type(component)
        if component_type in self.components:
            raise ValueError(f"Component of type {component_type.__name__} already exists")
        
        self.components[component_type] = component
        return component

    def get_component(self, component_type: Type[Component]) -> Component:
        """
        Get a component by type.
        
        Args:
            component_type: Type of component to retrieve
            
        Returns:
            Component instance if found
            
        Raises:
            KeyError if component type not found
        """
        return self.components[component_type]

    def has_component(self, component_type: Type[Component]) -> bool:
        """
        Check if entity has a specific component type.
        
        Args:
            component_type: Type of component to check for
            
        Returns:
            True if component exists, False otherwise
        """
        return component_type in self.components

    def update(self, dt: float) -> None:
        """
        Update entity and all its components.
        
        Args:
            dt: Delta time in seconds
        """
        for component in self.components.values():
            if component.active:
                component.update(dt)

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