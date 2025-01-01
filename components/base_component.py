from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.base_entity import Entity

class Component(ABC):
    """
    Base class for all entity components.
    Components encapsulate specific behaviors or attributes that can be attached to entities.
    """
    def __init__(self, entity: 'Entity'):
        self.entity = entity
        self.active = True

    def start(self) -> None:
        """Called when component is first added to entity"""
        pass

    def update(self, dt: float) -> None:
        """
        Update component logic.
        
        Args:
            dt: Delta time in seconds
        """
        pass

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """
        Render component visuals if needed.
        
        Args:
            surface: Pygame surface to render on
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        pass 