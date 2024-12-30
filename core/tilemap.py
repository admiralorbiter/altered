from utils.config import *
import pygame

class TileMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Basic layers (2D arrays)
        self.ground_layer = [[0 for _ in range(width)] for _ in range(height)]
        self.collision_layer = [[0 for _ in range(width)] for _ in range(height)]
        
        # Advanced layers (dictionaries for sparse data)
        self.utility_layer = {}  # For things like wires, pipes, etc.
        self.decor_layer = {}    # For decorative elements
        
        # Temporary tileset (replace with proper tileset loading later)
        self.tileset = {
            0: self._create_colored_tile((100, 100, 100)),  # Empty/default
            1: self._create_colored_tile((34, 139, 34)),    # Grass
            2: self._create_colored_tile((139, 69, 19)),    # Dirt
            3: self._create_colored_tile((128, 128, 128)),  # Wall
        }
        
    def _create_colored_tile(self, color):
        """Temporary function to create colored tiles until we have proper sprites"""
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(color)
        # Add a border to make tiles visible
        pygame.draw.rect(surface, (200, 200, 200), surface.get_rect(), 1)
        return surface
    
    def is_walkable(self, x, y):
        """Check if a position is walkable"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.collision_layer[y][x] == 0
    
    def set_tile(self, x, y, layer, tile_id):
        """Set a tile in the specified layer"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if layer == "ground":
                self.ground_layer[y][x] = tile_id
            elif layer == "collision":
                self.collision_layer[y][x] = tile_id
    
    def render(self, surface, camera_x, camera_y):
        """Render visible portion of tilemap"""
        # Convert camera position to tile coordinates
        start_x = max(0, camera_x // TILE_SIZE)
        start_y = max(0, camera_y // TILE_SIZE)
        
        # Calculate how many tiles fit on screen
        tiles_x = min(self.width - start_x, (WINDOW_WIDTH // TILE_SIZE) + 2)
        tiles_y = min(self.height - start_y, (WINDOW_HEIGHT // TILE_SIZE) + 2)
        
        # Render ground layer
        for y in range(tiles_y):
            for x in range(tiles_x):
                map_x = start_x + x
                map_y = start_y + y
                
                # Get tile ID and corresponding image
                tile_id = self.ground_layer[map_y][map_x]
                tile_img = self.tileset[tile_id]
                
                # Calculate screen position
                screen_x = x * TILE_SIZE - (camera_x % TILE_SIZE)
                screen_y = y * TILE_SIZE - (camera_y % TILE_SIZE)
                
                # Draw the tile
                surface.blit(tile_img, (screen_x, screen_y))
                
                # Draw collision tiles (for debugging)
                if self.collision_layer[map_y][map_x]:
                    pygame.draw.rect(surface, (255, 0, 0, 128), 
                                  (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)