from utils.pathfinding import find_path
import pygame
from utils.config import *

class AISystem:
    def __init__(self):
        self.update_interval = 0.5
        self.update_timer = 0
        self.wander_chance = 0.1  # 10% chance to start wandering when idle
        
    def update(self, dt, game_state):
        self.update_timer += dt
        if self.update_timer >= self.update_interval:
            self.update_timer = 0
            self.update_enemy_behaviors(dt, game_state)
            
    def find_nearest_target(self, enemy, game_state):
        """Find nearest valid target (alien or cat)"""
        min_distance = float('inf')
        nearest_target = None
        
        # Check aliens
        for alien in game_state.current_level.aliens:
            if alien.active:
                distance = (alien.position - enemy.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = alien
                    
        # Check cats
        for cat in game_state.current_level.cats:
            if cat.active and not cat.is_dead:
                distance = (cat.position - enemy.position).length()
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = cat
                    
        return nearest_target, min_distance
        
    def update_enemy_behaviors(self, dt, game_state):
        """Update all enemy AI behaviors"""
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
        """Handle patrol behavior"""
        if not enemy.moving and enemy.patrol_points:
            current_tile = (int(enemy.position.x // TILE_SIZE),
                          int(enemy.position.y // TILE_SIZE))
            target_point = enemy.patrol_points[enemy.current_patrol_index]
            
            # Find path to next patrol point
            enemy.path = find_path(current_tile, target_point, game_state.current_level.tilemap)
            if enemy.path:
                enemy.current_waypoint = 1 if len(enemy.path) > 1 else 0
                next_tile = enemy.path[enemy.current_waypoint]
                enemy.target_position = pygame.math.Vector2(
                    (next_tile[0] + 0.5) * TILE_SIZE,
                    (next_tile[1] + 0.5) * TILE_SIZE
                )
                enemy.moving = True
                
            # Move to next patrol point
            enemy.current_patrol_index = (enemy.current_patrol_index + 1) % len(enemy.patrol_points)
                
    def handle_chase_state(self, enemy, game_state):
        """Handle chase behavior"""
        if enemy.target and enemy.target.active:
            current_pos = enemy.position
            target_pos = enemy.target.position
            distance = (target_pos - current_pos).length()
            
            if distance > enemy.min_distance:
                current_tile = (int(current_pos.x // TILE_SIZE),
                              int(current_pos.y // TILE_SIZE))
                
                # Clear any existing reservations for this entity
                game_state.path_reservation_system.clear_reservations(enemy)
                
                # Calculate target position that maintains minimum distance
                direction = (target_pos - current_pos).normalize()
                chase_pos = target_pos - direction * enemy.min_distance
                
                # Convert chase position to tile coordinates
                target_tile = (int(chase_pos.x // TILE_SIZE),
                             int(chase_pos.y // TILE_SIZE))
                
                # Calculate arrival time based on distance and speed
                estimated_time = game_state.current_time + (distance / enemy.speed)
                
                # Try to find and reserve a path
                path = find_path(current_tile, target_tile,
                               game_state.current_level.tilemap,
                               game_state, enemy)
                               
                if path:
                    # Reserve all tiles along the path
                    for i, tile in enumerate(path):
                        arrival_time = estimated_time * (i / len(path))
                        game_state.path_reservation_system.reserve_tile(
                            tile, enemy, arrival_time)
                        
                    # Set the path and start moving
                    enemy.path = path
                    if len(path) > 1:
                        enemy.current_waypoint = 1
                        next_tile = path[enemy.current_waypoint]
                        enemy.target_position = pygame.math.Vector2(
                            (next_tile[0] + 0.5) * TILE_SIZE,
                            (next_tile[1] + 0.5) * TILE_SIZE
                        )
                        enemy.moving = True
            else:
                # Stop moving if we're at the minimum distance
                enemy.moving = False
                enemy.target_position = None
                enemy.path = None
                
    def handle_attack_state(self, enemy, game_state):
        """Handle attack behavior"""
        if enemy.target and enemy.target.active:
            enemy.attack(enemy.target) 