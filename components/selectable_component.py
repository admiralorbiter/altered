from components.base_component import Component
from components.alien_render_component import AlienRenderComponent
from typing import Optional
import pygame

class SelectableComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        self.selected = False
        self._renderer: Optional[AlienRenderComponent] = None

    def start(self) -> None:
        """Get reference to renderer when component starts"""
        super().start()
        self._renderer = self.entity.get_component(AlienRenderComponent)

    def select(self) -> None:
        """Select this entity"""
        self.selected = True
        if self._renderer:
            self._renderer.select()

    def deselect(self) -> None:
        """Deselect this entity"""
        self.selected = False
        if self._renderer:
            self._renderer.deselect()

    @property
    def is_selected(self) -> bool:
        """Property to check if entity is selected"""
        return self.selected

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        """Draw selection indicator"""
        pass 