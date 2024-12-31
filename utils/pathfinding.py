from typing import List, Tuple, Dict, Set
import heapq
from utils.config import *
import pygame

class Node:
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
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def is_tile_occupied(position: Tuple[int, int], game_state, ignore_entity=None, check_reservations=True) -> bool:
    """Check if a tile is occupied or reserved"""
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
    """A* pathfinding implementation with entity collision checking"""
    # First verify the end position is valid
    if not tilemap.is_walkable(end[0], end[1]):
        print(f"End position {end} is not walkable!")
        return []
        
    if game_state and is_tile_occupied(end, game_state, entity):
        print(f"End position {end} is occupied!")
        return []
    
    print(f"Finding path from {start} to {end}")
    
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
    def __init__(self):
        self.reserved_tiles = {}  # {(x,y): [entities planning to move here]}
        
    def reserve_tile(self, tile_pos, entity, arrival_time):
        if tile_pos not in self.reserved_tiles:
            self.reserved_tiles[tile_pos] = []
        self.reserved_tiles[tile_pos].append((entity, arrival_time))
        
    def clear_reservations(self, entity):
        for tile_pos in list(self.reserved_tiles.keys()):
            self.reserved_tiles[tile_pos] = [
                (e, t) for e, t in self.reserved_tiles[tile_pos] if e != entity
            ]
            if not self.reserved_tiles[tile_pos]:
                del self.reserved_tiles[tile_pos]
                
    def is_tile_reserved(self, tile_pos, current_time, ignore_entity=None):
        if tile_pos not in self.reserved_tiles:
            return False
        return any(e != ignore_entity and t >= current_time 
                  for e, t in self.reserved_tiles[tile_pos]) 