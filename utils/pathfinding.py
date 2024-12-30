from typing import List, Tuple, Dict, Set
import heapq
from utils.config import *

class Node:
    def __init__(self, position: Tuple[int, int], g_cost: float = float('inf'), 
                 h_cost: float = 0):
        self.position = position
        self.g_cost = g_cost  # Cost from start to this node
        self.h_cost = h_cost  # Estimated cost from this node to end
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = None
        
    def __lt__(self, other):
        return self.f_cost < other.f_cost

def manhattan_distance(start: Tuple[int, int], end: Tuple[int, int]) -> float:
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def find_path(start: Tuple[int, int], end: Tuple[int, int], tilemap) -> List[Tuple[int, int]]:
    """A* pathfinding implementation"""
    if not tilemap.is_walkable(*end):
        return []
        
    # Initialize start node
    start_node = Node(start, 0, manhattan_distance(start, end))
    
    # Priority queue for open nodes
    open_set = []
    heapq.heappush(open_set, start_node)
    
    # Track visited nodes
    closed_set: Set[Tuple[int, int]] = set()
    
    # Track all nodes for path reconstruction
    all_nodes: Dict[Tuple[int, int], Node] = {start: start_node}
    
    while open_set:
        current = heapq.heappop(open_set)
        
        if current.position == end:
            # Reconstruct path
            path = []
            while current.position != start:
                path.append(current.position)
                current = current.parent
            path.append(start)
            return path[::-1]
            
        closed_set.add(current.position)
        
        # Check neighbors (including diagonals)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                neighbor_pos = (current.position[0] + dx, current.position[1] + dy)
                
                if (neighbor_pos in closed_set or 
                    not tilemap.is_walkable(*neighbor_pos)):
                    continue
                
                # Calculate new costs
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
    
    return []  # No path found 