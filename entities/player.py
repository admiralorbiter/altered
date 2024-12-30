import pygame
from .base_entity import Entity
from utils.config import *

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0, 255, 0)  # Green
        self.speed = 300
        
    def update(self, dt):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        self.velocity.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        self.velocity.y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed
        
        super().update(dt)
        
        # Keep player in bounds
        self.position.x = max(self.size.x/2, min(WINDOW_WIDTH - self.size.x/2, self.position.x))
        self.position.y = max(self.size.y/2, min(WINDOW_HEIGHT - self.size.y/2, self.position.y)) 