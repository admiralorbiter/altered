import pygame
from utils.config import *
from .tiles import TILES, TILE_FLOOR, Tile

class TileMap:
    """
    Manages a 2D grid-based map containing both terrain tiles and electrical components.
    Handles rendering, tile manipulation, and electrical component placement.
    """
    def __init__(self, width, height, game_state):
        """
        Initialize a new tile map with specified dimensions.
        
        Args:
            width (int): Map width in tiles
            height (int): Map height in tiles
            game_state: Reference to the main game state object
        """
        self.width = width
        self.height = height
        self.game_state = game_state
        
        # Main ground layer
        self.tiles = [[TILE_FLOOR for _ in range(width)] for _ in range(height)]
        
        # Electrical layer
        self.electrical_layer = [[None for _ in range(width)] for _ in range(height)]
        self.electrical_components = {}  # (x,y) -> ElectricalComponent
    
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
        
    def set_electrical(self, x, y, component):
        """
        Store an electrical component at the given position.
        Uses dual storage for efficient access: a dictionary for quick lookups
        and a 2D array for spatial relationships.
        
        Args:
            x, y (int): Grid coordinates
            component (ElectricalComponent): Component to place
            
        Returns:
            bool: True if placement was successful
        """
        
        # Bounds check
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Store in both data structures
        key = (x, y)
        self.electrical_components[key] = component
        self.electrical_layer[y][x] = component
        
        # Verify storage
        stored = self.electrical_components.get(key)
        return True

    def get_electrical(self, x, y):
        """Get electrical component at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            key = (x, y)
            comp = self.electrical_components.get(key)
            return comp
        return None

    def render(self, surface, camera_x, camera_y):
        """
        Render the visible portion of the map using a camera-based viewport system.
        Handles both terrain tiles and electrical components with proper zoom scaling.
        
        Args:
            surface (pygame.Surface): Target surface to render on
            camera_x, camera_y (float): Camera position in world coordinates
        """
        zoom_level = self.game_state.zoom_level
        
        # Calculate visible area
        start_x = max(0, int(camera_x // TILE_SIZE))
        start_y = max(0, int(camera_y // TILE_SIZE))
        end_x = min(self.width, int((camera_x + WINDOW_WIDTH / zoom_level) // TILE_SIZE) + 3)
        end_y = min(self.height, int((camera_y + WINDOW_HEIGHT / zoom_level) // TILE_SIZE) + 3)
        
        # First render terrain tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                
                # Calculate screen position with zoom
                screen_x = (x * TILE_SIZE - camera_x) * zoom_level
                screen_y = (y * TILE_SIZE - camera_y) * zoom_level
                
                # Draw tile scaled by zoom
                pygame.draw.rect(surface, tile.color, 
                               (screen_x, screen_y, 
                                TILE_SIZE * zoom_level, TILE_SIZE * zoom_level))
                # Add grid lines
                pygame.draw.rect(surface, (50, 50, 50), 
                               (screen_x, screen_y, 
                                TILE_SIZE * zoom_level, TILE_SIZE * zoom_level), 
                               max(1, int(zoom_level)))

        # Then render electrical components
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if (x, y) in self.electrical_components:
                    self.render_electrical(surface, x, y, camera_x, camera_y, zoom_level)

    def _render_electrical_layer(self, surface, camera_x, camera_y):
        zoom_level = self.game_state.zoom_level
        
        # Calculate visible area
        start_x = max(0, int(camera_x // TILE_SIZE))
        start_y = max(0, int(camera_y // TILE_SIZE))
        end_x = min(self.width, int((camera_x + WINDOW_WIDTH / zoom_level) // TILE_SIZE) + 1)
        end_y = min(self.height, int((camera_y + WINDOW_HEIGHT / zoom_level) // TILE_SIZE) + 1)
        
        # Render visible electrical components
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if (x, y) in self.electrical_components:
                    screen_x = (x * TILE_SIZE - camera_x) * zoom_level
                    screen_y = (y * TILE_SIZE - camera_y) * zoom_level
                    tile_size = TILE_SIZE * zoom_level
                    
                    # Draw wire pattern
                    wire_color = (255, 255, 0)
                    wire_width = max(2 * zoom_level, 1)
                    
                    # Draw main wire line
                    pygame.draw.line(surface, wire_color,
                                   (screen_x + tile_size * 0.2, screen_y + tile_size * 0.5),
                                   (screen_x + tile_size * 0.8, screen_y + tile_size * 0.5),
                                   int(wire_width))
                    
                    # Draw connection nodes
                    node_radius = max(3 * zoom_level, 2)
                    pygame.draw.circle(surface, wire_color,
                                     (int(screen_x + tile_size * 0.2), int(screen_y + tile_size * 0.5)),
                                     int(node_radius))
                    pygame.draw.circle(surface, wire_color,
                                     (int(screen_x + tile_size * 0.8), int(screen_y + tile_size * 0.5)),
                                     int(node_radius))

    def render_electrical(self, surface, tile_x, tile_y, camera_x, camera_y, zoom_level):
        """Render a single electrical component"""
        component = self.electrical_components.get((tile_x, tile_y))
        if not component or component.type != 'wire':
            return
        
        # Calculate screen position
        screen_x = (tile_x * TILE_SIZE - camera_x) * zoom_level
        screen_y = (tile_y * TILE_SIZE - camera_y) * zoom_level
        tile_size = TILE_SIZE * zoom_level
        
        # Choose color based on construction state
        if component.is_built:
            wire_color = (0, 255, 255)  # Cyan for completed
        elif component.under_construction:
            wire_color = (255, 255, 0)  # Yellow for under construction
        else:
            wire_color = (128, 128, 128)  # Gray for not started
        
        # Draw main wire line
        pygame.draw.line(surface, wire_color,
                        (screen_x + tile_size * 0.2, screen_y + tile_size * 0.5),
                        (screen_x + tile_size * 0.8, screen_y + tile_size * 0.5),
                        int(max(2 * zoom_level, 1)))
        
        # Draw connection nodes
        node_radius = max(3 * zoom_level, 2)
        pygame.draw.circle(surface, wire_color,
                          (int(screen_x + tile_size * 0.2), int(screen_y + tile_size * 0.5)),
                          int(node_radius))
        pygame.draw.circle(surface, wire_color,
                          (int(screen_x + tile_size * 0.8), int(screen_y + tile_size * 0.5)),
                          int(node_radius))