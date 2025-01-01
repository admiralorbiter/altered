import pygame
from components.base_component import Component

class RenderComponent(Component):
    def __init__(self, entity, color=(255, 0, 0)):
        super().__init__(entity)
        self.color = color

    def render(self, surface, camera_x: float, camera_y: float) -> None:
        pygame.draw.circle(surface, self.color,
                         (int(self.entity.position.x),
                          int(self.entity.position.y)),
                         16)  # radius 