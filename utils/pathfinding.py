from typing import List, Tuple, Set, Dict
from queue import PriorityQueue

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

        # Clear entity's previous path
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
            for tile in self.entity_paths[entity]:
                if tile in self.reserved_tiles and self.reserved_tiles[tile] == entity:
                    del self.reserved_tiles[tile]
            # Clear path
            del self.entity_paths[entity]

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

def find_path(start: Tuple[int, int], end: Tuple[int, int], tilemap, game_state=None, entity=None) -> List[Tuple[int, int]]:
    """
    A* pathfinding algorithm with path reservation support
    Returns a list of tile coordinates from start to end, or None if no path exists
    """
    # Check if start and end are valid
    if not tilemap.is_walkable(*start):
        return None
        
    if not tilemap.is_walkable(*end):
        return None

    # Initialize data structures
    frontier = PriorityQueue()
    frontier.put((0, start))
    
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    # Get path reservation system if available
    path_system = getattr(game_state, 'path_reservation_system', None) if game_state else None
    
    while not frontier.empty():
        current = frontier.get()[1]
        
        if current == end:
            break
            
        # Check all adjacent tiles
        for next_pos in get_neighbors(current, tilemap):
            # Skip if tile is reserved by another entity
            if path_system and path_system.is_tile_reserved(next_pos, entity):
                continue
                
            new_cost = cost_so_far[current] + 1
            
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + manhattan_distance(next_pos, end)
                frontier.put((priority, next_pos))
                came_from[next_pos] = current
    
    # Build path
    if end not in came_from:
        return None
        
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    # Try to reserve the path if system is available
    if path_system and not path_system.reserve_path(entity, path):
        return None
    
    return path 