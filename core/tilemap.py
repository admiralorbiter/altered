import pygame
from utils.config import *
from .tiles import TILES, TILE_FLOOR, Tile, ElectricalComponent

class TileMap:
    def __init__(self, width, height, game_state):
        self.width = width
        self.height = height
        self.game_state = game_state  # Store reference to game_state
        
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
        
    def set_electrical(self, x, y, component_type):
        """Set an electrical component at the given position"""
        print(f"Setting electrical at ({x}, {y}): {component_type}")
        if 0 <= x < self.width and 0 <= y < self.height:
            # Create the electrical component
            component = ElectricalComponent(component_type)
            # Store in both layer and dictionary
            self.electrical_layer[y][x] = TILES[component_type]
            self.electrical_components[(x, y)] = component
            print(f"Component stored at ({x}, {y})")
            print(f"Current components: {self.electrical_components}")
        else:
            print(f"Position out of bounds: ({x}, {y})")
            
    def get_electrical(self, x, y):
        """Get electrical component at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.electrical_layer[y][x]
        return None

    def render(self, surface, camera_x, camera_y):
        """Render visible tiles with zoom"""
        zoom_level = self.game_state.zoom_level
        
        # Calculate visible area
        start_x = max(0, int(camera_x // TILE_SIZE))
        start_y = max(0, int(camera_y // TILE_SIZE))
        end_x = min(self.width, int((camera_x + WINDOW_WIDTH / zoom_level) // TILE_SIZE) + 1)
        end_y = min(self.height, int((camera_y + WINDOW_HEIGHT / zoom_level) // TILE_SIZE) + 1)
        
        # First render tiles
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
        print(f"Electrical components: {self.electrical_components}")  # Debug print
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
        # Calculate screen position
        screen_x = int((tile_x * TILE_SIZE - camera_x) * zoom_level)
        screen_y = int((tile_y * TILE_SIZE - camera_y) * zoom_level)
        tile_size = int(TILE_SIZE * zoom_level)
        
        component = self.electrical_components.get((tile_x, tile_y))
        if not component:
            return
        
        # Colors based on construction state
        if component.under_construction:
            wire_color = (255, 165, 0)  # Orange
            glow_color = (255, 140, 0, 100)  # Darker orange with alpha
        else:
            wire_color = (0, 255, 255)  # Cyan
            glow_color = (0, 200, 200, 100)  # Darker cyan with alpha
        
        wire_width = max(4 * zoom_level, 2)
        
        # Calculate wire positions
        start_x = screen_x + int(tile_size * 0.2)
        start_y = screen_y + int(tile_size * 0.5)
        end_x = screen_x + int(tile_size * 0.8)
        end_y = screen_y + int(tile_size * 0.5)
        
        # Create a surface for the glow effect
        glow_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        
        # Draw outer glow
        for i in range(3):
            glow_width = wire_width + (i * 2)
            pygame.draw.line(glow_surface, glow_color,
                            (tile_size * 0.2, tile_size * 0.5),
                            (tile_size * 0.8, tile_size * 0.5),
                            int(glow_width))
        
        # Apply glow
        surface.blit(glow_surface, (screen_x, screen_y))
        
        # Draw main wire
        pygame.draw.line(surface, wire_color,
                        (start_x, start_y),
                        (end_x, end_y),
                        int(wire_width))
        
        # Draw sleek connection nodes
        node_radius = max(3 * zoom_level, 2)
        inner_radius = max(2 * zoom_level, 1)
        
        for pos in [(start_x, start_y), (end_x, end_y)]:
            # Outer glow
            pygame.draw.circle(surface, glow_color, pos, int(node_radius + 2))
            # Main node
            pygame.draw.circle(surface, wire_color, pos, int(node_radius))
            # Inner highlight
            pygame.draw.circle(surface, (255, 255, 255), pos, int(inner_radius))