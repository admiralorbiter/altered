from typing import List, Tuple, Set, Dict
from queue import PriorityQueue

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
    A* pathfinding algorithm
    Returns a list of tile coordinates from start to end, or None if no path exists
    """
    print(f"\nPATHFINDING DEBUG:")
    print(f"Start tile: {start}")
    print(f"End tile: {end}")
    print(f"Start walkable: {tilemap.is_walkable(*start)}")
    print(f"End walkable: {tilemap.is_walkable(*end)}")
    
    # Check if start and end are valid
    if not tilemap.is_walkable(*start):
        print(f"ERROR: Start tile {start} is not walkable")
        return None
        
    if not tilemap.is_walkable(*end):
        print(f"ERROR: End tile {end} is not walkable")
        return None

    # Initialize data structures
    frontier = PriorityQueue()
    frontier.put((0, start))
    
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    nodes_explored = 0
    
    while not frontier.empty():
        current = frontier.get()[1]
        nodes_explored += 1
        
        if current == end:
            break
            
        # Check all adjacent tiles
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current[0] + dx, current[1] + dy
            next_pos = (next_x, next_y)
            
            # Skip if not walkable
            if not tilemap.is_walkable(next_x, next_y):
                continue
                
            new_cost = cost_so_far[current] + 1
            
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + manhattan_distance(next_pos, end)
                frontier.put((priority, next_pos))
                came_from[next_pos] = current
    
    print(f"Nodes explored: {nodes_explored}")
    
    # Build path
    if end not in came_from:
        print("ERROR: No path found!")
        return None
        
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    print(f"Path found with {len(path)} steps: {path}")
    return path 