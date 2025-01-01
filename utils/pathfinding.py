from typing import List, Tuple, Dict, Set
import heapq
from utils.config import *
import pygame

# Core pathfinding classes and functions for game entity movement
# Implements A* pathfinding with collision detection and path reservation system

class Node:
    """
    A node used in A* pathfinding algorithm.
    Stores position, costs (g, h, f), and parent node for path reconstruction.
    """
    def __init__(self, position: Tuple[int, int], g_cost: float = float('inf'), 
                 h_cost: float = 0):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = None
        
    def __lt__(self, other):
        return self.f_cost < other.f_cost

def manhattan_distance(start: Tuple[int, int], end: Tuple[int, int]) -> float:
    """
    Calculates the Manhattan distance between two points.
    Used as a heuristic function for A* pathfinding.
    
    Args:
        start: Starting coordinate tuple (x, y)
        end: Ending coordinate tuple (x, y)
    Returns:
        float: Manhattan distance between the points
    """
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def is_tile_occupied(position: Tuple[int, int], game_state, ignore_entity=None, check_reservations=True) -> bool:
    """
    Checks if a tile is currently occupied by any entity or reserved for future movement.
    
    Args:
        position: Tile coordinate to check (x, y)
        game_state: Current game state containing entity information
        ignore_entity: Entity to exclude from occupation check (optional)
        check_reservations: Whether to check the reservation system (default: True)
    
    Returns:
        bool: True if tile is occupied or reserved, False otherwise
    """
    tile_x, tile_y = position
    
    # Check current occupants
    for entity in game_state.current_level.entity_manager.entities:
        if entity == ignore_entity or not entity.active:
            continue
            
        entity_tile = (int(entity.position.x // TILE_SIZE),
                      int(entity.position.y // TILE_SIZE))
        if entity_tile == position:
            return True
            
        # Check if moving entities will pass through this tile
        if hasattr(entity, 'moving') and entity.moving and hasattr(entity, 'target_position'):
            target_tile = (int(entity.target_position.x // TILE_SIZE),
                          int(entity.target_position.y // TILE_SIZE))
            if target_tile == position:
                return True
    
    # Check reservations if enabled
    if check_reservations:
        current_time = game_state.current_time
        return game_state.path_reservation_system.is_tile_reserved(
            position, current_time, ignore_entity)
            
    return False

def find_path(start: Tuple[int, int], end: Tuple[int, int], tilemap, game_state=None, entity=None) -> List[Tuple[int, int]]:
    """
    Implements A* pathfinding to find the shortest path between two points.
    Accounts for obstacles, other entities, and tile reservations.
    
    Args:
        start: Starting coordinate tuple (x, y)
        end: Target coordinate tuple (x, y)
        tilemap: Game tilemap for checking walkable tiles
        game_state: Current game state for entity collision checking (optional)
        entity: Entity requesting the path, used for collision exclusion (optional)
    
    Returns:
        List[Tuple[int, int]]: List of coordinates forming the path, or empty list if no path found
    """
    
    # First verify the end position is valid
    if not tilemap.is_walkable(end[0], end[1]):
        return []
        
    if game_state and is_tile_occupied(end, game_state, entity):
        # Try adjacent tiles if target is occupied
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            alt_end = (end[0] + dx, end[1] + dy)
            if (tilemap.is_walkable(*alt_end) and 
                not is_tile_occupied(alt_end, game_state, entity)):
                end = alt_end
                break
        else:
            return []
    
    start_node = Node(start, 0, manhattan_distance(start, end))
    
    open_set = []
    heapq.heappush(open_set, start_node)
    
    closed_set: Set[Tuple[int, int]] = set()
    all_nodes: Dict[Tuple[int, int], Node] = {start: start_node}
    
    while open_set:
        current = heapq.heappop(open_set)
        
        if current.position == end:
            path = []
            while current.position != start:
                path.append(current.position)
                current = current.parent
            path.append(start)
            return path[::-1]
            
        closed_set.add(current.position)
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                neighbor_pos = (current.position[0] + dx, current.position[1] + dy)
                
                if (neighbor_pos in closed_set or 
                    not tilemap.is_walkable(*neighbor_pos) or
                    (game_state and is_tile_occupied(neighbor_pos, game_state, entity))):
                    continue
                
                movement_cost = 1.4 if dx != 0 and dy != 0 else 1.0
                new_g_cost = current.g_cost + movement_cost
                
                if (neighbor_pos not in all_nodes or 
                    new_g_cost < all_nodes[neighbor_pos].g_cost):
                    neighbor = Node(
                        neighbor_pos,
                        new_g_cost,
                        manhattan_distance(neighbor_pos, end)
                    )
                    neighbor.parent = current
                    all_nodes[neighbor_pos] = neighbor
                    heapq.heappush(open_set, neighbor)
    
    return [] 

class PathReservationSystem:
    """
    Manages future tile reservations for entity movement to prevent path conflicts.
    Allows entities to reserve tiles they plan to move through, helping avoid collisions.
    """
    
    def __init__(self):
        """Initialize an empty reservation system."""
        self.reserved_tiles = {}  # {(x,y): [entities planning to move here]}
        
    def reserve_tile(self, tile_pos, entity, arrival_time):
        """
        Reserve a tile for an entity at a specific arrival time.
        
        Args:
            tile_pos: Tile coordinate to reserve (x, y)
            entity: Entity reserving the tile
            arrival_time: Expected arrival time at the tile
        """
        if tile_pos not in self.reserved_tiles:
            self.reserved_tiles[tile_pos] = []
        self.reserved_tiles[tile_pos].append((entity, arrival_time))
        
    def clear_reservations(self, entity):
        """
        Remove all tile reservations for a specific entity.
        
        Args:
            entity: Entity whose reservations should be cleared
        """
        for tile_pos in list(self.reserved_tiles.keys()):
            self.reserved_tiles[tile_pos] = [
                (e, t) for e, t in self.reserved_tiles[tile_pos] if e != entity
            ]
            if not self.reserved_tiles[tile_pos]:
                del self.reserved_tiles[tile_pos]
                
    def is_tile_reserved(self, tile_pos, current_time, ignore_entity=None):
        """
        Check if a tile is reserved by any entity at or after the current time.
        
        Args:
            tile_pos: Tile coordinate to check (x, y)
            current_time: Current game time
            ignore_entity: Entity to exclude from reservation check (optional)
            
        Returns:
            bool: True if tile is reserved, False otherwise
        """
        if tile_pos not in self.reserved_tiles:
            return False
        return any(e != ignore_entity and t >= current_time 
                  for e, t in self.reserved_tiles[tile_pos]) 