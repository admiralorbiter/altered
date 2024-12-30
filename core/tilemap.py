import pygame
from utils.config import *
from .tiles import TILES, TILE_FLOOR, Tile

class TileMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Store tile objects instead of just IDs
        self.tiles = [[TILE_FLOOR for _ in range(width)] for _ in range(height)]
        
    def set_tile(self, x, y, tile_name: str):
        """Set a tile using its name"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = TILES[tile_name]
            
    def get_tile(self, x, y) -> Tile:
        """Get the tile object at the given position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
        
    def is_walkable(self, x, y) -> bool:
        """Check if the tile at (x,y) is walkable"""
        tile = self.get_tile(x, y)
        return tile and tile.walkable
        
    def render(self, surface, camera_x, camera_y):
        """Render visible tiles"""
        start_x = max(0, camera_x // TILE_SIZE)
        start_y = max(0, camera_y // TILE_SIZE)
        end_x = min(self.width, (camera_x + WINDOW_WIDTH) // TILE_SIZE + 1)
        end_y = min(self.height, (camera_y + WINDOW_HEIGHT) // TILE_SIZE + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                screen_x = x * TILE_SIZE - camera_x
                screen_y = y * TILE_SIZE - camera_y
                
                # Draw tile
                pygame.draw.rect(surface, tile.color, 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                # Add grid lines
                pygame.draw.rect(surface, (50, 50, 50), 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)