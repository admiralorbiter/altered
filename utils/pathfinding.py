from typing import List, Tuple, Set, Dict, Optional
from queue import PriorityQueue

from utils.config import TILE_SIZE

class PathReservationSystem:
    """Manages path reservations to prevent entity collisions"""
    def __init__(self):
        self.reserved_tiles = {}  # {(x,y): entity}
        self.entity_paths = {}    # {entity: [(x,y), ...]}
        
    def reserve_path(self, entity, path: List[Tuple[int, int]]) -> bool:
        """
        Attempt to reserve a path for an entity
        Returns True if successful, False if path conflicts
        """
        if not path:
            return False
            
        # Clear entity's previous path first
        self.clear_entity_path(entity)
        
        # Check if any tiles are already reserved by other entities
        for tile in path:
            if tile in self.reserved_tiles and self.reserved_tiles[tile] != entity:
                return False
                
        # Reserve all tiles in the path
        for tile in path:
            self.reserved_tiles[tile] = entity
        self.entity_paths[entity] = path
        return True
        
    def clear_entity_path(self, entity) -> None:
        """Remove all path reservations for an entity"""
        if entity in self.entity_paths:
            # Clear tile reservations
            path = self.entity_paths[entity]
            for tile in path:
                if tile in self.reserved_tiles and self.reserved_tiles[tile] == entity:
                    del self.reserved_tiles[tile]
            # Clear path
            del self.entity_paths[entity]
            
    def clear_reservations(self, entity) -> None:
        """Alias for clear_entity_path for backwards compatibility"""
        self.clear_entity_path(entity)
        
    def is_tile_reserved(self, tile: Tuple[int, int], entity=None) -> bool:
        """Check if a tile is reserved by another entity"""
        if tile not in self.reserved_tiles:
            return False
        return self.reserved_tiles[tile] != entity

def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Calculate Manhattan distance between two points"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos: Tuple[int, int], tilemap) -> List[Tuple[int, int]]:
    """Get valid neighboring tiles"""
    x, y = pos
    neighbors = []
    
    # Check all adjacent tiles
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        new_x, new_y = x + dx, y + dy
        if tilemap.is_walkable(new_x, new_y):
            neighbors.append((new_x, new_y))
            
    return neighbors

def find_path(start: Tuple[int, int], end: Tuple[int, int], tilemap, game_state=None, entity=None) -> Optional[List[Tuple[int, int]]]:
    """A* pathfinding with entity collision avoidance"""
    
    def is_tile_occupied(tile: Tuple[int, int]) -> bool:
        """Check if a tile is occupied by any entity except the moving one"""
        if not game_state:
            return False
            
        for other in game_state.entity_manager.entities:
            if other == entity:
                continue
            other_tile = (
                int(other.position.x // TILE_SIZE),
                int(other.position.y // TILE_SIZE)
            )
            if (other_tile == tile and 
                (tile == end or tile != (int(entity.position.x // TILE_SIZE),
                                       int(entity.position.y // TILE_SIZE)))):
                return True
        return False

    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring tiles"""
        x, y = pos
        neighbors = []
        
        # Check cardinal directions first
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = x + dx, y + dy
            if (0 <= next_x < tilemap.width and 
                0 <= next_y < tilemap.height and 
                tilemap.is_walkable(next_x, next_y) and
                not is_tile_occupied((next_x, next_y))):
                neighbors.append((next_x, next_y))
                
        # If no valid cardinal moves, try diagonals
        if not neighbors:
            for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                next_x, next_y = x + dx, y + dy
                if (0 <= next_x < tilemap.width and 
                    0 <= next_y < tilemap.height and 
                    tilemap.is_walkable(next_x, next_y) and
                    not is_tile_occupied((next_x, next_y))):
                    neighbors.append((next_x, next_y))
        
        return neighbors

    # Early exit for invalid inputs
    if not tilemap or not start or not end:
        return None
        
    # Validate start position
    if not tilemap.is_walkable(*start):
        return None
        
    # Find nearest walkable end position if needed
    if not tilemap.is_walkable(*end):
        # Search in expanding radius for walkable tile
        for radius in range(1, 6):  # Try up to 5 tiles away
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    test_pos = (end[0] + dx, end[1] + dy)
                    if tilemap.is_walkable(*test_pos):
                        end = test_pos
                        break
                if tilemap.is_walkable(*end):
                    break
            if tilemap.is_walkable(*end):
                break
        else:
            return None

    # Initialize A* algorithm
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    # Get path reservation system if available
    path_system = getattr(game_state, 'path_reservation_system', None) if game_state else None
    
    # A* main loop
    while not frontier.empty():
        current = frontier.get()[1]
        
        if current == end:
            break
            
        for next_pos in get_neighbors(current):
            # Skip if tile is reserved by another entity
            if path_system and path_system.is_tile_reserved(next_pos, entity):
                continue
                
            new_cost = cost_so_far[current] + 1
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + manhattan_distance(next_pos, end)
                frontier.put((priority, next_pos))
                came_from[next_pos] = current

    # Reconstruct path
    if end not in came_from:
        return None
        
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    # Try to reserve path if system exists
    if path_system and entity:
        if not path_system.reserve_path(entity, path):
            return None
    
    return path 