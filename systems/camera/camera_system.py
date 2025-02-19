import pygame

from utils.config import *


class CameraSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.position = pygame.math.Vector2(0, 0)
        self.zoom_level = 1.0
        self.min_zoom = MIN_ZOOM
        self.max_zoom = MAX_ZOOM
        self.zoom_speed = ZOOM_SPEED

    def update(self, target_entity):
        # Calculate visible area in world coordinates
        visible_width = WINDOW_WIDTH / self.zoom_level
        visible_height = WINDOW_HEIGHT / self.zoom_level
        
        # Calculate target position (centered on target entity)
        target_x = target_entity.position.x - visible_width/2
        target_y = target_entity.position.y - visible_height/2
        
        # Calculate world bounds
        world_width = MAP_WIDTH * TILE_SIZE
        world_height = MAP_HEIGHT * TILE_SIZE
        
        # Calculate maximum camera position based on zoom
        max_x = world_width - visible_width
        max_y = world_height - visible_height
        
        # Keep camera in bounds while accounting for zoom
        self.position.x = max(0, min(target_x, max_x))
        self.position.y = max(0, min(target_y, max_y))

    def handle_zoom(self, zoom_delta, mouse_pos):
        old_zoom = self.zoom_level
        self.zoom_level = max(self.min_zoom, 
                            min(self.max_zoom, 
                                self.zoom_level + zoom_delta * self.zoom_speed))
        
        if old_zoom != self.zoom_level:
            zoom_factor = self.zoom_level / old_zoom
            self.position.x += (mouse_pos[0] / old_zoom) * (1 - zoom_factor)
            self.position.y += (mouse_pos[1] / old_zoom) * (1 - zoom_factor)