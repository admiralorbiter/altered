from abc import ABC, abstractmethod
import pygame

class BaseRenderer(ABC):
    @abstractmethod
    def render(self, entity, surface, camera_x, camera_y):
        """Base render method that all renderers must implement"""
        pass

    def get_screen_position(self, entity, camera_x, camera_y):
        """Helper method to calculate screen position"""
        zoom_level = entity.game_state.zoom_level
        screen_x = (entity.position.x - camera_x) * zoom_level
        screen_y = (entity.position.y - camera_y) * zoom_level
        return screen_x, screen_y 