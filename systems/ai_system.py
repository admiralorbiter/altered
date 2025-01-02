from utils.pathfinding import find_path
import pygame
from utils.config import *

class AISystem:
    """
    Manages AI behavior for game entities, including patrolling, chasing, and combat.
    Handles pathfinding, target acquisition, and state transitions for enemies.
    """
    
    def __init__(self):
        """
        Initialize the AI system with timing controls and behavior parameters.
        Sets up update intervals and probability values for AI decision making.
        """
        # Controls how often the AI system updates (in seconds)
        self.update_interval = 0.5
        # Timer to track time between updates
        self.update_timer = 0
        # Probability that an idle enemy will start wandering
        self.wander_chance = 0.1  # 10% chance to start wandering when idle
        
    def update(self, dt, game_state):
        """
        Main update loop for the AI system.
        
        Args:
            dt (float): Delta time since last update in seconds
            game_state (GameState): Current game state containing all entity information
        """
        # Accumulate time since last update
        self.update_timer += dt
        # Check if it's time for an AI update
        if self.update_timer >= self.update_interval:
            self.update_timer = 0
            self.update_enemy_behaviors(dt, game_state)
            
    def find_nearest_target(self, enemy, game_state):
        """
        Locates the closest valid target (alien or cat) for an enemy.
        
        Args:
            enemy (Enemy): The enemy entity searching for a target
            game_state (GameState): Current game state containing all entities
            
        Returns:
            tuple: (nearest_target, min_distance) where:
                - nearest_target: The closest valid target entity or None if none found
                - min_distance: Float distance to the nearest target
        """
        # Initialize tracking variables for closest target
        min_distance = float('inf')
        nearest_target = None
        
        # First pass: Check all active aliens as potential targets
        for alien in game_state.current_level.aliens:
            if alien.active:
                distance = (alien.position - enemy.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = alien
                    
        # Second pass: Check all active, living cats as potential targets
        # If a cat is closer than the nearest alien, it becomes the target
        for cat in game_state.current_level.cats:
            if cat.active and not cat.is_dead:
                distance = (cat.position - enemy.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = cat
                    
        return nearest_target, min_distance
        
    def update_enemy_behaviors(self, dt, game_state):
        """
        Updates AI states and behaviors for all active enemies in the current level.
        
        Args:
            dt (float): Delta time since last update in seconds
            game_state (GameState): Current game state containing all entity information
        """
        for enemy in game_state.current_level.enemies:
            if not enemy.active:
                continue
                
            # Update AI state
            enemy.update_ai_state(dt, game_state)
            
            # Handle different states
            if enemy.state == 'patrol':
                self.handle_patrol_state(enemy, game_state)
            elif enemy.state == 'chase':
                self.handle_chase_state(enemy, game_state)
            elif enemy.state == 'attack':
                self.handle_attack_state(enemy, game_state)
                
    def handle_patrol_state(self, enemy, game_state):
        """
        Manages enemy patrol behavior, including pathfinding between patrol points.
        
        Args:
            enemy (Enemy): The enemy entity currently in patrol state
            game_state (GameState): Current game state containing level information
            
        Notes:
            - Calculates paths between patrol points using A* pathfinding
            - Converts between tile and world coordinates
            - Updates enemy movement and patrol point progression
        """
        # Only process patrol logic if the enemy isn't moving and has patrol points
        if not enemy.moving and enemy.patrol_points:
            # Convert current position to tile coordinates
            current_tile = (int(enemy.position.x // TILE_SIZE),
                          int(enemy.position.y // TILE_SIZE))
            target_point = enemy.patrol_points[enemy.current_patrol_index]
            
            # Calculate path to next patrol point using A* pathfinding
            enemy.path = find_path(current_tile, target_point, game_state.current_level.tilemap)
            if enemy.path:
                # Set next waypoint (skip first point if path has multiple points)
                enemy.current_waypoint = 1 if len(enemy.path) > 1 else 0
                next_tile = enemy.path[enemy.current_waypoint]
                # Convert tile coordinates to world position (centered in tile)
                enemy.target_position = pygame.math.Vector2(
                    (next_tile[0] + 0.5) * TILE_SIZE,
                    (next_tile[1] + 0.5) * TILE_SIZE
                )
                enemy.moving = True
                
            # Cycle to next patrol point in sequence
            enemy.current_patrol_index = (enemy.current_patrol_index + 1) % len(enemy.patrol_points)
                
    def handle_chase_state(self, enemy, game_state):
        """
        Manages enemy chase behavior, including target following and path reservation.
        
        Args:
            enemy (Enemy): The enemy entity currently in chase state
            game_state (GameState): Current game state containing level information
            
        Notes:
            - Maintains minimum distance from target
            - Uses path reservation system to avoid collisions with other entities
            - Calculates estimated arrival times for path coordination
        """
        # Only process chase logic if target exists and is active
        if enemy.target and enemy.target.active:
            current_pos = enemy.position
            target_pos = enemy.target.position
            distance = (target_pos - current_pos).length()
            
            # If target is beyond minimum distance, calculate path to chase
            if distance > enemy.min_distance:
                current_tile = (int(current_pos.x // TILE_SIZE),
                              int(current_pos.y // TILE_SIZE))
                
                # Calculate ideal position to maintain minimum distance from target
                direction = (target_pos - current_pos).normalize()
                chase_pos = target_pos - direction * enemy.min_distance
                chase_tile = (int(chase_pos.x // TILE_SIZE),
                             int(chase_pos.y // TILE_SIZE))
                
                # Find path to chase position
                path = find_path(current_tile, chase_tile, 
                               game_state.current_level.tilemap,
                               game_state)
                
                if path:
                    # Set next waypoint
                    enemy.current_waypoint = 1 if len(path) > 1 else 0
                    next_tile = path[enemy.current_waypoint]
                    enemy.target_position = pygame.math.Vector2(
                        (next_tile[0] + 0.5) * TILE_SIZE,
                        (next_tile[1] + 0.5) * TILE_SIZE
                    )
                    enemy.moving = True
            else:
                # Stop moving if already at minimum distance from target
                enemy.moving = False
                enemy.target_position = None
                enemy.path = None
                
    def handle_attack_state(self, enemy, game_state):
        """
        Manages enemy attack behavior when in range of their target.
        
        Args:
            enemy (Enemy): The enemy entity currently in attack state
            game_state (GameState): Current game state containing level information
            
        Notes:
            - Only executes attacks when target is active and in range
        """
        if enemy.target and enemy.target.active:
            enemy.attack(enemy.target) 